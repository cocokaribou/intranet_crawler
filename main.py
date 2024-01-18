from fastapi import FastAPI, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
import crawler
from model.Input import Input
from model.Employee import Employee
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return "Welcome!"


@app.post("/employee")
def get_employee_list(i: Input) -> list[Employee]:
    return crawler.scrap_employee_list(i.id, i.password)
