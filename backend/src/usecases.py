import os
from dataclasses import dataclass
from typing import Any

import database
import utils
from discord import Discord
from stream import StreamManager
from twitcasting_api import TwitcastingApiClient, TwitcastingApiResult


@dataclass(slots=True)
class UseCaseResult:
    ok: bool
    data: Any = None
    error: str | None = None
    status_code: int = 200


stream_manager = StreamManager()
twitcasting = TwitcastingApiClient()
discord = Discord()


def _is_enabled(name: str) -> bool:
    return (os.environ.get(name) or "").lower() in ('true', 'enable', 'on')


def _build_recording_response(session) -> dict[str, Any]:
    return {
        "live_id": session.live_id,
        "screen_id": session.screen_id,
        "user_name": session.user_name,
        "profile_image": session.profile_image,
        "live_title": session.live_title,
        "live_subtitle": session.live_subtitle,
        "start_time": session.start_time
    }


def _build_user_response(user: database.User) -> dict[str, Any]:
    return {
        "user_id": user.id,
        "screen_id": user.screen_id,
        "user_name": user.name,
        "profile_image": user.profile_image,
        "profile_description": user.profile_description,
        "level": user.level,
        "supporter_count": user.supporter_count,
        "supporting_count": user.supporting_count
    }


def _api_error_result(api_result: TwitcastingApiResult, default_status: int = 502) -> UseCaseResult:
    return UseCaseResult(
        ok=False,
        error=api_result.error or "TwitCasting API request failed",
        status_code=api_result.status_code or default_status,
    )


def list_recordings() -> dict[str, list[dict[str, Any]]]:
    return {
        "recordings": [
            _build_recording_response(session)
            for session in stream_manager.list_active_sessions()
        ]
    }


def stop_all_recordings() -> dict[str, str]:
    for session in stream_manager.list_active_sessions():
        stream_manager.stop(session.live_id)

    return {"message": "ok"}


def refresh_user(user_ref: str, status_code: int = 500) -> UseCaseResult:
    user_data_response = twitcasting.get_user_info(user_ref)
    if not user_data_response.ok:
        return _api_error_result(user_data_response, default_status=status_code)

    database.update_user(user_data_response.data)
    return UseCaseResult(ok=True, data=user_data_response.data)


def start_recording(screen_id: str, upstream_error_status: int = 502) -> UseCaseResult:
    user_result = refresh_user(screen_id, status_code=upstream_error_status)
    if not user_result.ok:
        return user_result

    user = user_result.data["user"]
    if not user["is_live"]:
        return UseCaseResult(ok=False, error="User is offline", status_code=404)

    utils.create_user_directory(utils.escape_characters(screen_id))

    live_id = user["last_movie_id"]
    user_name = user["name"]
    profile_image = user["image"]

    live_title = "title"
    live_subtitle = "subtitle"
    live_start_time = 0

    live_data_response = twitcasting.get_movie_info(live_id)
    if live_data_response.ok:
        live_title = live_data_response.data["movie"]["title"]
        live_subtitle = live_data_response.data["movie"]["subtitle"]
        live_start_time = live_data_response.data["movie"]["created"]

    if not stream_manager.start(
        screen_id,
        user_name,
        profile_image,
        live_id,
        live_title,
        live_subtitle,
        live_start_time,
    ):
        return UseCaseResult(ok=False, error="recording is on going...", status_code=409)

    if _is_enabled("DISCORD_WEBHOOK"):
        discord.push_start_notification(
            screen_id,
            user_name,
            profile_image,
            live_id,
            live_title,
            live_subtitle
        )

    return UseCaseResult(
        ok=True,
        data={
            "live_id": live_id,
            "screen_id": screen_id,
            "user_name": user_name,
            "profile_image": profile_image,
            "live_title": live_title,
            "live_subtitle": live_subtitle,
            "live_start_time": live_start_time
        }
    )


def stop_recording(screen_id: str, upstream_error_status: int = 502) -> UseCaseResult:
    user_data_response = twitcasting.get_user_info(screen_id)
    if not user_data_response.ok:
        return _api_error_result(user_data_response, default_status=upstream_error_status)

    if not user_data_response.data["user"]["is_live"]:
        return UseCaseResult(ok=False, error="User is offline", status_code=404)

    live_id = user_data_response.data["user"]["last_movie_id"]
    if not stream_manager.stop(live_id):
        return UseCaseResult(ok=False, error="recording not found", status_code=404)

    return UseCaseResult(ok=True, data={"screen_id": screen_id})


def get_subscriptions() -> UseCaseResult:
    api_response = twitcasting.get_subscriptions()
    if not api_response.ok:
        return _api_error_result(api_response)

    subscriptions = {"users": []}
    for subscription in api_response.data["webhooks"]:
        subscriptions["users"].append(subscription["user_id"])

    return UseCaseResult(ok=True, data=subscriptions)


def sync_subscriptions() -> UseCaseResult:
    subscriptions_result = get_subscriptions()
    if not subscriptions_result.ok:
        return subscriptions_result

    for user_id in subscriptions_result.data["users"]:
        database.set_subscription_user(user_id)

    return subscriptions_result


def add_subscription(screen_id: str) -> UseCaseResult:
    user_result = refresh_user(screen_id)
    if not user_result.ok:
        return user_result

    user_id = user_result.data["user"]["id"]
    database.set_subscription_user(user_id)
    subscription_response = twitcasting.add_subscription(user_id)
    if not subscription_response.ok:
        return _api_error_result(subscription_response)

    user = database.get_user(user_id)
    return UseCaseResult(ok=True, data=_build_user_response(user))


def remove_subscription(screen_id: str) -> UseCaseResult:
    user_result = refresh_user(screen_id)
    if not user_result.ok:
        return user_result

    user_id = user_result.data["user"]["id"]
    database.unset_subscription_user(user_id)
    subscription_response = twitcasting.remove_subscription(user_id)
    if not subscription_response.ok:
        return _api_error_result(subscription_response)

    user = database.get_user(user_id)
    return UseCaseResult(ok=True, data=_build_user_response(user))


def list_users() -> dict[str, list[dict[str, Any]]]:
    response = {"users": []}
    for user in database.get_subscription_users():
        response["users"].append(_build_user_response(user))

    return response