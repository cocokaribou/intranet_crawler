from pydantic import BaseModel
import json


class Input(BaseModel):
    id: str
    password: str

    # default value for open api document
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "",
                    "password": ""
                }
            ]
        }
    }


class Employee(BaseModel):
    image: str = ""
    idx: int = 0
    id: str = ""
    name: str = ""
    position: str = ""
    department: str = ""

    def toJSON(self):
        return self.__dict__


class LoginResult(BaseModel):
    # success 1000 / fail 9999
    code: int

    # empty when the result is success
    msg: str = ""


class Resource(BaseModel):
    isBooked: str
    isMine: bool


resource_type = {
    "남자휴게실": 10,
    "여자휴게실": 20
}
