from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from pathlib import Path

from starlette.staticfiles import StaticFiles

from routers.intranet import router as intranet_router

import uvicorn

app = FastAPI(
    description="Endpoint APIs for getting web scrapped data from the intranet",
    title="Intranet Crawler"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(intranet_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Intranet Crawler",
        version="1.0.0",
        description="Endpoint APIs for getting web scrapped data from the intranet",
        routes=app.routes
    )
    openapi_schema["paths"]["/login"] = {}  # use authorize feature of open api doc instead
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
def home():
    home_path = Path("html/index.html")
    return FileResponse(home_path)


@app.get("/test",
         tags=["GET"],
         summary="test",
         description="test api")
def test():
    return "test"


# test htmls
@app.get("/1")
def page1():
    return FileResponse(Path("html/1.html"))


@app.get("/2")
def page2():
    return FileResponse(Path("html/2.html"))


@app.get("/3")
def page3():
    return FileResponse(Path("html/3.html"))

@app.get("/test_json")
def test_json():
    return FileResponse(Path('test.json'))