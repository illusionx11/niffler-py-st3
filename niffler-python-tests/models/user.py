from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import MetaData

class UserName(BaseModel):
    username: str
    
class User(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    username: str
    currency: str
    firstname: Optional[str] = None
    surname: Optional[str] = None
    photo: Optional[str] = None
    photo_small: Optional[str] = None
    full_name: Optional[str] = None