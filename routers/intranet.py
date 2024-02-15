from fastapi import APIRouter, Request, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing_extensions import Annotated
import crawler
from models import Employee, Resource, Input
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
    return crawler.scrap_employee_list(token)


@router.post("/user/my",
             summary="Intranet my information",
             tags=["User"],
             response_model=Employee,
             description="Get the user information of the currently logged-in user.")
async def get_my_info(token: str = Depends(oauth2_scheme)):
    return crawler.scrap_my_information(token)


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
