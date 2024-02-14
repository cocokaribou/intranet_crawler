from fastapi import APIRouter, Request
from crawler import Crawler
from models import LoginResult, Input, Employee
from typing import List

router = APIRouter(
    tags=["POST"]
)
crawler = Crawler()


@router.post("/login",
             summary="Intranet login",
             response_model=LoginResult,
             description="Login to the intranet using an internal Chrome browser.",
             response_description="success: `\"code\":1000` fail: `\"code\":9999`")
async def login(i: Input, request: Request):
    return crawler.login(i)


@router.post("/logout",
             summary="Intranet logout",
             response_model=LoginResult,
             description="Logout from the intranet by deleting session cookies.",
             response_description="success: `\"code\":1000` fail: `\"code\":9999`")
async def logout():
    return crawler.logout()


@router.post("/employee",
             summary="Intranet employee list",
             response_model=List[Employee],
             description="Get the employee list from the intranet.<br>"
                         "Returns an empty list when the user is not logged in.")
async def get_employee_list():
    return crawler.scrap_employee_list()


@router.post("/my-info",
             summary="Intranet my information",
             response_model=Employee,
             description="Get the user information of the currently logged-in user.<br>"
                         "Returns empty information when the user is not logged in.")
async def get_my_info():
    return crawler.scrap_my_information()
