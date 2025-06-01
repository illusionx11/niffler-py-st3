from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import Optional
from sqlalchemy import MetaData
    
class User(SQLModel, table=True):
    metadata = MetaData()
    id: str = Field(default=None, primary_key=True)
    username: str
    password: str
    enabled: bool
    account_non_expired: bool
    account_non_locked: bool
    credentials_non_expired: bool