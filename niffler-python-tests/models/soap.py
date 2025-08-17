from pydantic import BaseModel
from typing import Optional
from models.enums import Direction

class SoapUser(BaseModel):
    id: str
    username: str
    currency: str
    firstname: Optional[str] = None
    surname: Optional[str] = None
    photo: Optional[str] = None
    photo_small: Optional[str] = None
    full_name: Optional[str] = None
    friendship_status: Optional[str] = None

class PageInfo(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None
    sort: Optional[Direction] = None