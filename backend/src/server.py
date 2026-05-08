import pathlib

from fastapi import FastAPI, status, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from usecases import (
    add_subscription as add_subscription_usecase,
    get_subscriptions as get_subscriptions_usecase,
    list_recordings,
    list_users,
    remove_subscription as remove_subscription_usecase,
    start_recording as start_recording_usecase,
    stop_all_recordings as stop_all_recordings_usecase,
    stop_recording as stop_recording_usecase,
)

app = FastAPI()

PATH_FRONTEND_DIST = pathlib.Path(__file__).resolve().parent / "web"
PATH_FRONTEND_INDEX = PATH_FRONTEND_DIST / "index.html"
PATH_FRONTEND_ASSETS = PATH_FRONTEND_DIST / "assets"

if PATH_FRONTEND_ASSETS.exists():
    app.mount(
        '/assets',
        StaticFiles(directory=str(PATH_FRONTEND_ASSETS)),
        name='assets'
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


async def run_sync_usecase(func, *args):
    return await run_in_threadpool(func, *args)

def serve_frontend_index():
    if PATH_FRONTEND_INDEX.exists():
        return FileResponse(str(PATH_FRONTEND_INDEX))
    return JSONResponse({"error": "frontend not built"}, status_code=status.HTTP_404_NOT_FOUND)


@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return serve_frontend_index()


@app.get("/recordings", status_code=status.HTTP_200_OK)
async def get_records():
    return await run_sync_usecase(list_recordings)


@app.delete("/recordings", status_code=status.HTTP_200_OK)
async def stop_all_recordings():
    return await run_sync_usecase(stop_all_recordings_usecase)


@app.post("/recordings/{screen_id}", status_code=status.HTTP_200_OK)
async def start_recording(screen_id: str, response: Response):
    result = await run_sync_usecase(start_recording_usecase, screen_id)
    if not result.ok:
        response.status_code = result.status_code
        return {"error": result.error}
    return result.data


@app.delete("/recordings/{screen_id}", status_code=status.HTTP_200_OK)
async def stop_recording(screen_id: str, response: Response):
    result = await run_sync_usecase(stop_recording_usecase, screen_id)
    if not result.ok:
        response.status_code = result.status_code
        return {"error": result.error}
    return result.data


@app.get("/subscriptions", status_code=status.HTTP_200_OK)
async def get_subscriptions(response: Response):
    result = await run_sync_usecase(get_subscriptions_usecase)
    if not result.ok:
        response.status_code = result.status_code
        return {"error": result.error}
    return result.data


@app.post("/subscriptions/{screen_id}", status_code=status.HTTP_200_OK)
async def add_subscription(screen_id: str, response: Response):
    result = await run_sync_usecase(add_subscription_usecase, screen_id)
    if not result.ok:
        response.status_code = result.status_code
        return {"error": result.error}
    return result.data


@app.delete("/subscriptions/{screen_id}", status_code=status.HTTP_200_OK)
async def remove_subscription(screen_id: str, response: Response):
    result = await run_sync_usecase(remove_subscription_usecase, screen_id)
    if not result.ok:
        response.status_code = result.status_code
        return {"error": result.error}
    return result.data


@app.get("/users", status_code=status.HTTP_200_OK)
async def get_users():
    return await run_sync_usecase(list_users)


@app.get("/{path:path}", status_code=status.HTTP_200_OK)
async def spa_fallback(path: str):
    file_path = PATH_FRONTEND_DIST / path
    if file_path.is_file():
        return FileResponse(str(file_path))
    return serve_frontend_index()
