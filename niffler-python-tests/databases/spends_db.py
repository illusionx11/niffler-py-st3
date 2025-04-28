from typing import Sequence
from sqlalchemy import create_engine, Engine, event
from sqlmodel import Session, select
from models.spend import Spend
from models.category import Category
from sqlalchemy.orm import selectinload
import logging
import allure
from models.config import ServerEnvs

class SpendsDb:
    
    engine: Engine
    
    def __init__(self, server_envs: ServerEnvs):
        self.engine = create_engine(server_envs.spends_db_url)
        event.listen(self.engine, "do_execute", fn=self.attach_sql)
        
    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        sql_name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(statement_with_params, name=sql_name, attachment_type=allure.attachment_type.TEXT)
    
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