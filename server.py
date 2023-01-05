from fastapi import FastAPI

from stream import StreamManager

stream_manager = StreamManager()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "OK"}

@app.get("/records")
async def get_records():
    record_flags = stream_manager.events
    keys = [key for key, value in record_flags.items() if not value.is_set()]
    response = []
    for index, key in enumerate(keys):
        record = {"user_name": key}
        response.append(record)

    return {"records": response}

@app.post("/records/{user_name}")
async def start_record(user_name: str):
    if stream_manager.start(user_name):
        return {"user": user_name}
    else:
        return {"error": "recording is on going..."}


@app.delete("/records/{user_name}")
async def stop_record(user_name: str):
    if stream_manager.stop(user_name):
        return {"user": user_name}
    else:
        return {"error": "record could not stop"}
