import uuid
from clients.oauth_client import OAuthClient
from faker import Faker
from databases.auth_db import AuthDb
from databases.userdata_db import UserdataDb
from models.user import UserData
from clients.soap_client import SoapClient
import logging
import pytest
import random

class SoapUserCreator:
    def __init__(
        self, auth_client: OAuthClient, soap_client: SoapClient, 
        userdata_db: UserdataDb, auth_db: AuthDb, faker: Faker
    ):
        self.auth_client = auth_client
        self.soap_client = soap_client
        self.userdata_db = userdata_db
        self.auth_db = auth_db
        self.faker = faker
        
    def add_friends(self, users: list[UserData], friends_user: str, count: int = None) -> list[UserData]:
        for idx, user in enumerate(users):
            if count and idx >= count:
                break
            self.soap_client.send_friend_invitation(user.username, friends_user)
            self.soap_client.accept_friend_invitation(friends_user, user.username)

    def register_users(self, count: int, is_friend: bool = False, is_actions: bool = False) -> list[UserData]:
        users = []
        add = ""
        if is_friend:
            add = "Friend_"
        elif is_actions:
            add = "Actions_"
        
        for i in range(count):
            number = random.randint(1000, 100000)
            username = f"{self.faker.first_name()}_{self.faker.word()}_{add}{number}_{i}"
            password = self.faker.password(length=10)
            self.auth_client.register(
                username = username, 
                password = password
            )
            users.append(UserData(username=username, password=password))
            
        return users

    def delete_users(self, users: list[UserData]) -> None:
        try:
            for user in users:
                db_user = self.userdata_db.get_user_by_name(user.username)
                if not db_user:
                    raise AssertionError(f"Пользователь с именем {user.username} не найден в Базе данных")
                self.userdata_db.delete_user(db_user.id)
                self.auth_db.delete_user(user.username)
            logging.info("Удаление Mock-пользователей для SOAP после тестов завершено")
        except (AssertionError, ValueError) as e:
            logging.warning(f"Ошибка при удалении пользователей: {e}")

    def create_users(self, count, friends_user: str = None, actions_user: str = None):
        try:
            if friends_user:
                users = self.register_users(count, is_friend=True)
                self.add_friends(users, friends_user)
            elif actions_user:
                users = self.register_users(count, is_actions=True)
                self.add_friends(users, actions_user, 5)
            else:
                users = self.register_users(count)
                
            logging.info("Mock-пользователи для SOAP созданы")
            return users
        except Exception as e:
            logging.error(f"Ошибка при создании пользователей: {e}", exc_info=True)
            pytest.fail(f"Ошибка при создании пользователей: {e}")