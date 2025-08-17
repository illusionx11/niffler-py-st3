from typing import Sequence
from sqlalchemy import create_engine, Engine, event, delete
from sqlmodel import Session, select
from models.spend import Spend
from models.category import Category
from sqlalchemy.orm import selectinload
import logging
import allure
from models.config import ServerEnvs
from models.auth_user import User, Authority

class AuthDb:
    
    engine: Engine
    
    def __init__(self, server_envs: ServerEnvs):
        self.engine = create_engine(server_envs.auth_db_url)
        event.listen(self.engine, "do_execute", fn=self.attach_sql)
        
    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        sql_name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(statement_with_params, name=sql_name, attachment_type=allure.attachment_type.TEXT)
    
    def get_users(self) -> Sequence[User] | None:
        with Session(self.engine) as session:
            statement = select(User)
            users = session.exec(statement).all()
            logging.info(f"Получен список всех пользователей")
            return users
        
    def get_user_by_name(self, username: str) -> User | None:
         with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            logging.info(f"Получен пользователь {user.username}")
            return user
    
    def delete_all_users(self, exclude: list[str] = []) -> bool:
        with Session(self.engine) as session:
            statement = delete(Authority)
            session.exec(statement)
            if len(exclude) > 0:
                statement = delete(User).where(~User.username.in_(exclude))
                add_text = f", кроме следующих: {exclude}"
            else:
                statement = delete(User)
                add_text = ""
            session.exec(statement)
            session.commit()
            logging.info(f"Удалены все пользователи{add_text}")
            return True
    
    def delete_user(self, username: str) -> bool:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if not user:
                raise ValueError(f"Пользователь {username} не найден")
            statement = delete(Authority).where(Authority.user_id == user.id)
            session.exec(statement)
            statement = delete(User).where(User.username == username)
            session.exec(statement)
            session.commit()
            logging.info(f"Удален пользователь {username} в БД auth")
            return True