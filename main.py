from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from models import Input, Employee, LoginResult
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


@app.get("/",
         tags=["GET"],
         summary="api 루트",
         description="api 루트입니다.")
def root():
    return "Welcome!"


@app.get("/test",
         tags=["GET"],
         summary="테스트용",
         description="테스트용 api입니다.")
def test():
    return "test"


@app.post("/login",
          tags=["POST"],
          summary="인트라넷 로그인",
          response_model=LoginResult,
          description="크롬 드라이버로 인트라넷에 로그인합니다.<br><u>로그인 세션을 유지해야</u> `employee` api 값을 받을 수 있습니다.",
          response_description="로그인<br>성공 - `\"code\":1000`<br>실패 - `\"code\":9999`")
def login(i: Input):
    return crawler.login(i)


@app.post("/logout",
          tags=["POST"],
          summary="인트라넷 로그아웃",
          response_model=LoginResult,
          description="`PION_JSESSIONID`쿠키를 삭제하여 로그아웃 시킵니다.",
          response_description="로그아웃<br>성공 - `\"code\":1000`<br>실패- `\"code\":9999`")
def logout():
    return crawler.logout()


@app.post("/employee",
          tags=["POST"],
          summary="직원목록 크롤링 (로그인 세션 유지해야 함)",
          response_model=List[Employee],
          description="인트라넷 로그인된 상태로 직원목록을 가져옵니다.<br> ⚠️**시간이 좀 걸립니다. (개선예정)**",
          response_description="채팅에 필요한 직원정보 목록")
def get_employee_list():
    return crawler.scrap_employee_list()
