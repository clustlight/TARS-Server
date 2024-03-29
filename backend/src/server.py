import os
import pathlib

from fastapi import FastAPI, status, Response, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from metadata import MetadataManager
import utils
import database
from stream import StreamManager
from twitcasting import Twitcasting
from discord import Discord

stream_manager = StreamManager()
metadata_manager = MetadataManager()
twitcasting = Twitcasting()
discord = Discord()
app = FastAPI()

PATH_STATIC = str(pathlib.Path(__file__).resolve().parent / "templates")
templates = Jinja2Templates(directory=PATH_STATIC)

PATH_STATIC_NEXT = str(pathlib.Path(__file__).resolve().parent / "templates/_next")

app.mount(
    '/_next',
    StaticFiles(directory=PATH_STATIC_NEXT),
    name='next'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

port = os.environ.get("PORT")


@app.get("/", status_code=status.HTTP_200_OK)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request
    })


@app.get("/recordings", status_code=status.HTTP_200_OK)
async def get_records():
    record_flags = stream_manager.events
    active_streams = [key for key, value in record_flags.items() if not value.is_set()]
    non_active_streams = [key for key, value in record_flags.items() if value.is_set()]
    metadata_manager.update(non_active_streams)

    response = []
    for index, live_id in enumerate(active_streams):
        user_data = metadata_manager.get(live_id)
        record = {
            "live_id": live_id,
            "screen_id": user_data["screen_id"],
            "user_name": user_data["user_name"],
            "profile_image": user_data["profile_image"],
            "live_title": user_data["live_title"],
            "live_subtitle": user_data["live_subtitle"],
            "start_time": user_data["start_time"]
        }
        response.append(record)

    return {"recordings": response}


@app.delete("/recordings", status_code=status.HTTP_200_OK)
async def stop_all_recordings():
    record_flags = stream_manager.events
    active_streams = [key for key, value in record_flags.items() if not value.is_set()]
    non_active_streams = [key for key, value in record_flags.items() if value.is_set()]
    metadata_manager.update(non_active_streams)

    for live_id in active_streams:
        if stream_manager.stop(live_id):
            metadata_manager.remove(live_id)

    return {"message": "ok"}


@app.post("/recordings/{screen_id}", status_code=status.HTTP_200_OK)
async def start_recording(screen_id: str, response: Response):
    user_data_response = twitcasting.get_user_info(screen_id)
    if user_data_response[0]:
        database.update_user(user_data_response[1])
        if user_data_response[1]["user"]["is_live"]:
            utils.create_user_directory(utils.escape_characters(screen_id))

            live_id = user_data_response[1]["user"]["last_movie_id"]
            user_name = user_data_response[1]["user"]["name"]
            profile_image = user_data_response[1]["user"]["image"]

            live_title = "title"
            live_subtitle = "subtitle"
            live_start_time = 0

            live_data_response = twitcasting.get_movie_info(live_id)

            if live_data_response[0]:
                live_title = live_data_response[1]["movie"]["title"]
                live_subtitle = live_data_response[1]["movie"]["subtitle"]
                live_start_time = live_data_response[1]["movie"]["created"]

            if stream_manager.start(screen_id, live_id, live_title, live_subtitle):
                metadata_manager.add(screen_id, user_name, profile_image, live_id, live_title, live_subtitle,
                                     live_start_time)

                if os.environ.get("DISCORD_WEBHOOK").lower() in ('true', 'enable', 'on'):
                    discord.push_start_notification(screen_id, user_name, profile_image, live_id, live_title, live_subtitle)

                return {
                    "live_id": live_id,
                    "screen_id": screen_id,
                    "user_name": user_name,
                    "profile_image": profile_image,
                    "live_title": live_title,
                    "live_subtitle": live_subtitle,
                    "live_start_time": live_start_time
                }
            else:
                response.status_code = status.HTTP_409_CONFLICT
                return {"error": "recording is on going..."}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"error": "User is offline"}
    else:
        return {"error": user_data_response[1]["error"]["message"]}


@app.delete("/recordings/{screen_id}", status_code=status.HTTP_200_OK)
async def stop_recording(screen_id: str, response: Response):
    user_data_response = twitcasting.get_user_info(screen_id)
    if user_data_response[0]:
        if user_data_response[1]["user"]["is_live"]:
            live_id = user_data_response[1]["user"]["last_movie_id"]

            if stream_manager.stop(live_id):
                metadata_manager.remove(live_id)
                return {"screen_id": screen_id}
            else:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"error": "recording not found"}
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"error": "User is offline"}
    else:
        return {"error": user_data_response[1]["error"]["message"]}


@app.get("/subscriptions", status_code=status.HTTP_200_OK)
async def get_subscriptions(response: Response):
    api_response = twitcasting.get_subscriptions()
    if api_response[0]:
        subscriptions = {
            "users": []
        }
        for subscription in api_response[1]["webhooks"]:
            subscriptions["users"].append(subscription["user_id"])
        return subscriptions
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": api_response[1]["error"]["message"]}


@app.post("/subscriptions/{screen_id}", status_code=status.HTTP_200_OK)
async def add_subscription(screen_id: str, response: Response):
    user_data_response = twitcasting.get_user_info(screen_id)
    if user_data_response[0]:
        database.update_user(user_data_response[1])
        database.set_subscription_user(user_data_response[1]["user"]["id"])
        subscription_response = twitcasting.add_subscription(user_data_response[1]["user"]["id"])
        if subscription_response[0]:
            user = database.get_user(user_data_response[1]["user"]["id"])
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
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": subscription_response[1]["error"]["message"]}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": user_data_response[1]["error"]["message"]}


@app.delete("/subscriptions/{screen_id}", status_code=status.HTTP_200_OK)
async def remove_subscription(screen_id: str, response: Response):
    user_data_response = twitcasting.get_user_info(screen_id)
    if user_data_response[0]:
        database.update_user(user_data_response[1])
        database.unset_subscription_user(user_data_response[1]["user"]["id"])
        subscription_response = twitcasting.remove_subscription(user_data_response[1]["user"]["id"])
        if subscription_response[0]:
            user = database.get_user(user_data_response[1]["user"]["id"])
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
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": subscription_response[1]["error"]["message"]}
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": user_data_response[1]["error"]["message"]}


@app.get("/users", status_code=status.HTTP_200_OK)
async def get_users():
    response = {
        "users": []
    }
    users = database.get_subscription_users()
    for user in users:
        response["users"] += [
            {
                "user_id": user.id,
                "screen_id": user.screen_id,
                "user_name": user.name,
                "profile_image": user.profile_image,
                "profile_description": user.profile_description,
                "level": user.level,
                "supporter_count": user.supporter_count,
                "supporting_count": user.supporting_count
            }
        ]

    return response
