from fastapi import FastAPI

from metadata import MetadataManager
from stream import StreamManager

stream_manager = StreamManager()
metadata_manager = MetadataManager()
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
        record = {"user_name": user_name, "start_time": user_data["start_time"]}
        response.append(record)

    return {"records": response}

@app.post("/records/{user_name}")
async def start_record(user_name: str):
    if stream_manager.start(user_name):
        metadata_manager.add(user_name, 0)
        return {"user": user_name}
    else:
        return {"error": "recording is on going..."}


@app.delete("/records/{user_name}")
async def stop_record(user_name: str):
    if stream_manager.stop(user_name):
        metadata_manager.remove(user_name)
        return {"user": user_name}
    else:
        return {"error": "record could not stop"}
