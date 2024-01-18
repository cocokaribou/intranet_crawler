from fastapi import FastAPI, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
import crawler


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


@app.post("/employee/")
async def get_employee_list(id: str, pwd: str):
    return crawler.scrap_employee_list(id, pwd)
