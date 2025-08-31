from pydantic import BaseModel, field_serializer
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserName(BaseModel):
    username: str

class UserData(BaseModel):
    username: str
    password: str
    password_repeat: Optional[str] = None
    
class User(SQLModel, table=True):
    id: UUID = Field(default=None, primary_key=True)
    username: str
    currency: str
    firstname: Optional[str] = None
    surname: Optional[str] = None
    photo: Optional[str] = None
    photo_small: Optional[str] = None
    full_name: Optional[str] = None
    
    @field_serializer('id')
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)
    
class Friendship(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    requester_id: str
    addressee_id: str
    status: str
    created_date: datetime
    
    @field_serializer('created_date')
    def serialize_created_date(self, created_date: datetime, _info) -> str:
        return str(created_date)