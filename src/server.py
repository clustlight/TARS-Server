from fastapi import FastAPI

from metadata import MetadataManager
from stream import StreamManager
from twitcasting import Twitcasting

stream_manager = StreamManager()
metadata_manager = MetadataManager()
twitcasting = Twitcasting()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "OK"}

@app.get("/records")
async def get_records():
    record_flags = stream_manager.events
    active_users = [key for key, value in record_flags.items() if not value.is_set()]
    non_active_users = [key for key, value in record_flags.items() if value.is_set()]
    metadata_manager.update(non_active_users)

    response = []
    for index, user_name in enumerate(active_users):
        user_data = metadata_manager.get(user_name)
        record = {
            "user_name": user_name,
            "live_title": user_data["live_title"],
            "live_subtitle": user_data["live_subtitle"],
            "start_time": user_data["start_time"]
        }
        response.append(record)

    return {"records": response}

@app.post("/records/{user_name}")
async def start_record(user_name: str):
    user_data_response  = twitcasting.get_user_info(user_name)
    if user_data_response[0]:
        if user_data_response[1]["user"]["is_live"]:
            live_id = user_data_response[1]["user"]["last_movie_id"]

            live_title = "title"
            live_subtitle = "subtitle"
            live_start_time = 0

            live_data_response = twitcasting.get_movie_info(live_id)

            if live_data_response[0]:
                live_title = live_data_response[1]["movie"]["title"]
                live_subtitle = live_data_response[1]["movie"]["subtitle"]
                live_start_time = live_data_response[1]["movie"]["created"]

            if stream_manager.start(user_name, live_id, live_title, live_subtitle):
                metadata_manager.add(user_name, live_title, live_subtitle, live_start_time)
                return {
                    "user": user_name,
                    "live_title": live_title,
                    "live_subtitle": live_subtitle
                }
            else:
                return {"error": "recording is on going..."}
        else:
            return {"error": "User is offline"}
    else:
        return {"error": user_data_response[1]["error"]["message"]}


@app.delete("/records/{user_name}")
async def stop_record(user_name: str):
    if stream_manager.stop(user_name):
        metadata_manager.remove(user_name)
        return {"user": user_name}
    else:
        return {"error": "record could not stop"}

@app.get("/subscriptions")
async def get_subscriptions():
    response = twitcasting.get_subscriptions()
    if response[0]:
        return response[1]
    else:
        return {"error": response[1]["error"]["message"]}

@app.post("/subscriptions/{user_name}")
async def add_subscription(user_name: str):
    user_data_response = twitcasting.get_user_info(user_name)
    if user_data_response[0]:
        subscription_response = twitcasting.add_subscription(user_data_response[1]["user"]["id"])
        if subscription_response[0]:
            return subscription_response[1]
        else:
            return {"error": subscription_response[1]["error"]["message"]}
    else:
        return {"error": user_data_response[1]["error"]["message"]}

@app.delete("/subscriptions/{user_name}")
async def remove_subscription(user_name: str):
    user_data_response = twitcasting.get_user_info(user_name)
    if user_data_response[0]:
        subscription_response = twitcasting.remove_subscription(user_data_response[1]["user"]["id"])
        if subscription_response[0]:
            return subscription_response[1]
        else:
            return {"error": subscription_response[1]["error"]["message"]}
    else:
        return {"error": user_data_response[1]["error"]["message"]}