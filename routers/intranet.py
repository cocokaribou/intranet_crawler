from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.params import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import PlainTextResponse
from typing_extensions import Annotated
import crawler as crawler
import fb
from models import Employee, Resource, ResourceType, ResourceResultCode
from typing import List
from enum import Enum

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
async def get_employee(index: int, token: str = Depends(oauth2_scheme)):
    return fb.get_intranet_user(index)


@router.post("/resource/{type}/list",
             tags=["Resource"],
             description="Get the booked resource list from the intranet."
             )
async def get_booked_resource_list(type: ResourceType = Path(description="Men `10` Women `20`\n"),
                                   token: str = Depends(oauth2_scheme)):
    return crawler.scrap_booked_resources(token, type)


@router.post("/resource/{type}/book",
             tags=["Resource"],
             description="Book resources from the intranet."
             )
async def book_resource(selected_blocks: list[int],
                        type: ResourceType = Path(description="Men `10` Women `20`\n"),
                        token: str = Depends(oauth2_scheme)):
    code = crawler.book_resources(token, type, selected_blocks)
    if code == ResourceResultCode.SUCCESS:
        return {
            "message": code.value
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=code.value
        )

"""
    no longer used as an api.
    will run the scraping process in batch mode.
"""
# @router.get("/pionworld",
#             tags=["PionWorld"],
#             response_class=PlainTextResponse)
# async def get_text_from_pion_world():
#     return crawler.scrap_and_save_pion_world_text()


@router.get("/chatbot",
            tags=["PionWorld"])
async def chatbot(query: str):
    # TODO chatbot api
    return f"🤖 <( {query} )"