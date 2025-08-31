from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel, Field
from typing import Optional, Any
import requests
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
    
class Authority(SQLModel, table=True):
    metadata = MetaData()
    id: str = Field(default=None, primary_key=True)
    user_id: str
    authority: str
    
class TokenData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    access_token: str
    code_verifier: str
    code_challenge: str
    id_token: str
    cookies: list[dict[str, Any]]