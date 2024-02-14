from pydantic import BaseModel


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

    @classmethod
    def init_from_list(cls, image: str, input_string):
        parts = input_string.split()
        return cls(
            image=image,
            idx=parts[0],
            name=parts[1],
            id=parts[3],
            position=parts[5],
            department=parts[13]
        )


class LoginResult(BaseModel):
    # success 1000 / fail 9999
    code: int

    # empty when the result is success
    msg: str = ""
