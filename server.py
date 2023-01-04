from fastapi import FastAPI

from stream import StreamManager

stream_manager = StreamManager()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "OK"}


@app.post("/record/{user_name}")
async def start_record(user_name):
    stream_manager.start(user_name)
    return {"user": user_name}


@app.delete("/record/{user_name}")
async def stop_record(user_name):
    stream_manager.stop(user_name)
    return {"user": user_name}
