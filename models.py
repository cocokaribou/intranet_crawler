from pydantic import BaseModel


class Input(BaseModel):
    id: str
    password: str


class Employee(BaseModel):
    idx: int
    id: str
    name: str
    position: str
    department: str

    @classmethod
    def from_string(cls, string):
        parts = string.split()
        return cls(
            idx=parts[0],
            name=parts[1],
            id=parts[3],
            position=parts[5],
            department=parts[13]
        )


class LoginResult(BaseModel):
    # 성공 1000 / 실패 9999
    code: int

    # 성공할 경우 빈 메세지
    msg: str = ""
