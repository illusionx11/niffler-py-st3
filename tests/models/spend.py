from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from pydantic import BaseModel
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

class Spend(SQLModel, table=True):
    id: str = Field(primary_key=True)
    amount: float
    username: str
    description: str
    category_id: str = Field(foreign_key="category.id")
    category: Category = Relationship(back_populates="spends")
    spend_date: datetime # json приходит с ключом spendDate, в БД название spend_date
    currency: str
    
class SpendAdd(BaseModel):
    id: Optional[str] = None
    amount: Optional[float] = None
    description: str
    category: Optional[CategoryAdd] = None
    spendDate: str # json приходит с ключом spendDate, в БД название spend_date
    currency: str
    username: Optional[str] = None

class SpendGet(BaseModel):
    id: str
    amount: float
    description: str
    category: CategoryGet
    spendDate: datetime # json приходит с ключом spendDate, в БД название spend_date
    currency: str
    username: str
    