from fastapi import FastAPI

from stream import StreamManager

stream_manager = StreamManager()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "OK"}


@app.post("/record/{user_name}")
async def start_record(user_name):
    if stream_manager.start(user_name):
        return {"user": user_name}
    else:
        return {"error": "recording is on going..."}


@app.delete("/record/{user_name}")
async def stop_record(user_name):
    if stream_manager.stop(user_name):
        return {"user": user_name}
    else:
        return {"error": "record could not stop"}
