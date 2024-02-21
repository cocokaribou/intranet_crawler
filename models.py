from pydantic import BaseModel
from enum import Enum


class Employee(BaseModel):
    image: str
    idx: int
    id: str
    name: str
    position: str
    department: str

    def toJSON(self):
        return self.__dict__


class Resource(BaseModel):
    isBooked: str
    isMine: bool


class ResourceType(int, Enum):
    MEN = 10
    WOMEN = 20


class ResourceResultCode(str, Enum):
    SUCCESS = "저장되었습니다."
    EMPTY_LIST = "예약할 시간을 선택해주세요."
    OVER_THREE = "한 번에 30분까지 선택할 수 있습니다."
    OVER_SIX = "하루에 1시간까지 선택할 수 있습니다."
    WRONG_GENDER = "휴게실 성별이 다릅니다."
    ERROR = "오류가 생겼습니다. 다시 시도해주세요."
