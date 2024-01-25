from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
