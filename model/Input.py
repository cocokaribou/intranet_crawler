from pydantic import BaseModel


class Input(BaseModel):
    id: str
    password: str
