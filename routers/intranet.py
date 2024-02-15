from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated
import crawler
from models import LoginResult, Input, Employee
from typing import List

router = APIRouter(
    tags=["POST"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/login",
             summary="Intranet login",
             description="Login to the intranet using an internal Chrome browser.")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = crawler.login(form.username, form.password)
    return {"access_token": f"{access_token}", "token_type": "bearer"}


# @router.post("/logout",
#              summary="Intranet logout",
#              description="Logout from the intranet by deleting session cookies.")
# async def logout():
#     return crawler.logout()


@router.post("/employee",
             summary="Intranet employee list",
             response_model=List[Employee],
             description="Get the employee list from the intranet.<br>"
                         "Returns an empty list when the user is not logged in.")
async def get_employee_list(token: str = Depends(oauth2_scheme)):
    return crawler.scrap_employee_list(token)


@router.post("/my-info",
             summary="Intranet my information",
             response_model=Employee,
             description="Get the user information of the currently logged-in user.<br>"
                         "Returns empty information when the user is not logged in.")
async def get_my_info(token: str = Depends(oauth2_scheme)):
    return crawler.scrap_my_information(token)
