from typing import Sequence
from sqlalchemy import create_engine, Engine
from sqlmodel import Session, select
from tests.models.spend import Spend, Category
from sqlalchemy.orm import selectinload
import logging

class SpendsDb:
    
    engine: Engine
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
    
    def get_user_spendings(self, username: str) -> Sequence[Spend]:
        with Session(self.engine) as session:
            statement = select(Spend).options(selectinload(Spend.category)).where(Spend.username == username)
            return session.exec(statement).all()
    
    def get_user_categories(self, username: str) -> Sequence[Category]:
        with Session(self.engine) as session:
            statement = select(Category).where(Category.username == username)
            return session.exec(statement).all()
    
    def delete_category(self, category_id: str) -> Category:
        with Session(self.engine) as session:
            category = session.get(Category, category_id)
            if not category:
                return None
            session.delete(category)
            session.commit()
            return category
        
    def delete_user_categories(self, username: str):
        user_categories = self.get_user_categories(username)
        for category in user_categories:
            logging.info(f"Deleting category {category}")
            self.delete_category(category.id)