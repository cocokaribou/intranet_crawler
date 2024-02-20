from fastapi import APIRouter, Depends, Request
from fastapi.params import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated
import crawler as crawler
import fb
from models import Employee, Resource
from typing import List

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@router.post("/login",
             summary="Intranet login",
             tags=["Auth"],
             description="Login to the intranet using an internal Chrome browser.")
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = crawler.login(form.username, form.password)
    return {"access_token": f"{access_token}", "token_type": "bearer"}


@router.post("/user/list",
             summary="Intranet employee list",
             tags=["User"],
             response_model=List[Employee],
             description="Get the employee list from the intranet.")
async def get_employee_list(token: str = Depends(oauth2_scheme)):
    return fb.get_intranet_user()


@router.post("/user/my",
             summary="Intranet my employee number",
             tags=["User"],
             response_model=int,
             description="Get the user information of the currently logged-in user.")
async def get_my_employee_number(token: str = Depends(oauth2_scheme)):
    return crawler.scrap_my_employee_number(token)


@router.post("/user/{index}",
             summary="Intranet single employee",
             tags=["User"],
             response_model=Employee,
             description="Get the single employee information.")
async def get_employee(index: int, request: Request, token: str = Depends(oauth2_scheme)):
    return fb.get_intranet_user(index)


@router.post("/resource/list",
             tags=["Resource"],
             description="Get the booked resource list from the intranet."
             )
async def get_booked_resource_list(type: int = 20,
                                   token: str = Depends(oauth2_scheme)):
    return crawler.scrap_booked_resources(token, type)


@router.post("/resource/my",
             tags=["Resource"],
             response_model=List[Resource],
             description="Get my booked resource list from the intranet."
             )
async def get_my_booked_resource(token: str = Depends(oauth2_scheme)):
    return []


@router.post("/resource/book",
             tags=["Resource"],
             description="Book resources from the intranet."
             )
async def book_resource(token: str = Depends(oauth2_scheme)):
    return "test"
