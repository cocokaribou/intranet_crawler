from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from models import Input, Employee
from crawler import Crawler

# end point api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Intranet Crawler",
        version="1.0.0",
        summary="파이언넷 인트라넷을 크롬드라이버로 크롤링하는 API입니다.",
        routes=app.routes,
        servers=[{"url": "http://13.209.23.94:8000"}]
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

crawler = Crawler()


@app.get("/")
def root():
    return "Welcome!"


@app.get("/test")
def test():
    return "test"


@app.post("/login")
def login(i: Input):
    return crawler.login(i)


@app.post("/logout")
def logout():
    return crawler.logout()


@app.post("/employee")
def get_employee_list() -> list[Employee]:
    return crawler.scrap_employee_list()
