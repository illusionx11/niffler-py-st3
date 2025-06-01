from typing import Sequence
from sqlalchemy import create_engine, Engine, event
from sqlmodel import Session, select
import allure
from models.config import ServerEnvs
from models.user import User

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
            return session.exec(statement).all()
        
    def get_user_by_name(self, username: str) -> User | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()
        
    def delete_user(self, user_id: str) -> bool | None:
        with Session(self.engine) as session:
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            if not user:
                return None
            session.delete(user)
            session.commit()
            return True