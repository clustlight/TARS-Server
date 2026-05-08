import base64
import json
import logging
import os
from dataclasses import dataclass

import dotenv
import requests

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TwitcastingApiResult:
    ok: bool
    status_code: int
    data: dict | None = None
    error: str | None = None
    error_code: str | None = None


class TwitcastingApiClient:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.timeout = float(os.environ.get("TWITCASTING_API_TIMEOUT", "10"))
        self.session = requests.Session()
        self.token = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        self.headers = {
            "Accept": "application/json",
            "X-Api-Version": "2.0",
            "Authorization": f"Basic {self.token}"
        }

    def _request(self, method: str, path: str, **kwargs):
        try:
            return self.session.request(
                method,
                f"https://apiv2.twitcasting.tv{path}",
                headers=self.headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.Timeout:
            logger.error(f"API Timeout: {method} {path}")
            return TwitcastingApiResult(
                ok=False,
                status_code=504,
                error="TwitCasting API request timed out",
                error_code="timeout",
            )
        except requests.RequestException as exc:
            logger.error(f"API Request Failed: {method} {path} ({exc})")
            return TwitcastingApiResult(
                ok=False,
                status_code=502,
                error="Failed to connect to TwitCasting API",
                error_code="request_failed",
            )

    def _parse_json(self, response) -> tuple[dict | None, TwitcastingApiResult | None]:
        try:
            return response.json(), None
        except json.JSONDecodeError:
            logger.error(
                f"API Invalid JSON: ({response.status_code}) {response.request.method} {response.request.url}"
            )
            return None, TwitcastingApiResult(
                ok=False,
                status_code=502,
                error="TwitCasting API returned an invalid response",
                error_code="invalid_json",
            )

    def _handle_response(self, response) -> TwitcastingApiResult:
        if isinstance(response, TwitcastingApiResult):
            return response

        data, parse_error = self._parse_json(response)
        if parse_error is not None:
            return parse_error

        if response.ok:
            return TwitcastingApiResult(ok=True, status_code=response.status_code, data=data)

        error_payload = data.get("error", {}) if isinstance(data, dict) else {}
        error_message = error_payload.get("message") or "TwitCasting API request failed"
        error_code = error_payload.get("code")
        logger.error(f"API Error: ({response.status_code}) {error_message}")
        return TwitcastingApiResult(
            ok=False,
            status_code=response.status_code,
            data=data,
            error=error_message,
            error_code=error_code,
        )

    def get_subscriptions(self) -> TwitcastingApiResult:
        response = self._request("GET", "/webhooks")
        if isinstance(response, TwitcastingApiResult) or not response.ok:
            return self._handle_response(response)

        data, parse_error = self._parse_json(response)
        if parse_error is not None:
            return parse_error

        users = data["webhooks"]
        if data["all_count"] > 50:
            count = data["all_count"] - 50
            page_index = 1
            while count > 0:
                page_response = self._request("GET", f"/webhooks?offset={50 * page_index}")
                if isinstance(page_response, TwitcastingApiResult) or not page_response.ok:
                    return self._handle_response(page_response)

                page_data, parse_error = self._parse_json(page_response)
                if parse_error is not None:
                    return parse_error
                page_index += 1
                count -= 50
                users += page_data["webhooks"]

        return TwitcastingApiResult(ok=True, status_code=response.status_code, data=data)

    def add_subscription(self, user_id: str) -> TwitcastingApiResult:
        payloads = {
            "user_id": user_id,
            "events": ["livestart"]
        }
        response = self._request("POST", "/webhooks", data=json.dumps(payloads))
        if isinstance(response, TwitcastingApiResult):
            return response
        if response.status_code in (200, 201):
            return self._handle_response(response)

        return self._handle_response(response)

    def remove_subscription(self, user_id: str) -> TwitcastingApiResult:
        response = self._request(
            "DELETE",
            f"/webhooks?user_id={user_id}&events[]=livestart",
        )
        if isinstance(response, TwitcastingApiResult):
            return response
        if response.status_code == 200:
            return self._handle_response(response)

        return self._handle_response(response)

    def get_user_info(self, screen_id: str) -> TwitcastingApiResult:
        response = self._request("GET", f"/users/{screen_id}")
        return self._handle_response(response)

    def get_movie_info(self, movie_id: str) -> TwitcastingApiResult:
        response = self._request("GET", f"/movies/{movie_id}")
        return self._handle_response(response)