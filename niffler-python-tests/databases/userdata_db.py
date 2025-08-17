from typing import Sequence
from sqlalchemy import create_engine, Engine, event, or_
from sqlmodel import Session, select, delete
import allure
from models.config import ServerEnvs
from models.user import User, Friendship
import logging

class UserdataDb:
    
    engine: Engine
    
    def __init__(self, server_envs: ServerEnvs):
        self.engine = create_engine(server_envs.userdata_db_url)
        event.listen(self.engine, "do_execute", fn=self.attach_sql)
        
    @staticmethod
    def attach_sql(cursor, statement, parameters, context):
        statement_with_params = statement % parameters
        sql_name = statement.split(" ")[0] + " " + context.engine.url.database
        allure.attach(statement_with_params, name=sql_name, attachment_type=allure.attachment_type.TEXT)
    
    def get_users(self) -> Sequence[User] | None:
        with Session(self.engine) as session:
            statement = select(User)
            all_users = session.exec(statement).all()
            logging.info(f"Получен список всех пользователей")
            return all_users
        
    def get_user_by_name(self, username: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            logging.info(f"Получен пользователь {username}")
            return user
    
    def delete_all_users(self, exclude: list[str] = []) -> bool:
        with Session(self.engine) as session:
            statement = delete(Friendship)
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
    
    def delete_user(self, user_id: str) -> bool | None:
        with Session(self.engine) as session:
            statement = delete(Friendship).where(
                or_(
                    Friendship.addressee_id == user_id,
                    Friendship.requester_id == user_id
                )
            )
            session.exec(statement)
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            if not user:
                return None
            session.delete(user)
            session.commit()
            logging.info(f"Удален пользователь {user.username} в БД userdata")
            return True