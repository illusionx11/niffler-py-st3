from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import BaseModel
# from models.spend import Spend
from typing import Optional, List

class Category(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    username: str
    archived: bool
    spends: List["Spend"] = Relationship(back_populates="category")

class CategoryAdd(BaseModel):
    id: Optional[str] = None
    name: str
    username: Optional[str] = None
    archived: Optional[bool] = False
    
class CategoryGet(BaseModel):
    id: str
    name: str
    username: str
    archived: bool