import pytest
import time
from pytest import FixtureRequest
from databases.userdata_db import UserdataDb
from models.user import UserData
from clients.oauth_client import OAuthClient
import uuid

@pytest.fixture(scope="function")
def new_user(request: FixtureRequest, userdata_db: UserdataDb):
    """Только удаляет пользователя, не добавляет"""
    user_data: UserData = request.param
    yield user_data
    start_time = time.time()
    user = None
    while time.time() - start_time < 5:
        user = userdata_db.get_user_by_name(user_data.username)
        if user:
            break
        time.sleep(0.3)
    if not user:
        assert False, f"Пользователь {user_data.username} не найден в Базе данных за 5 секунд"
    
    user_id = user.id
    userdata_db.delete_user(user_id)
    
@pytest.fixture(scope="function")
def soap_user(auth_client: OAuthClient):
    """Создаёт уникального пользователя под каждый тест"""
    username = f"soap_user_{uuid.uuid4()}"
    password = "P@ssW0rd"
    auth_client.register(username, password)
    return username

@pytest.fixture(scope="function")
def soap_friends_user(auth_client: OAuthClient):
    """Создаёт уникального пользователя под каждый тест для friends"""
    username = f"soap_friends_{uuid.uuid4()}"
    password = "P@ssW0rd"
    auth_client.register(username, password)
    return username

@pytest.fixture(scope="function")
def soap_actions_user(auth_client: OAuthClient):
    """Создаёт уникального пользователя под каждый тест для friends actions"""
    username = f"soap_actions_{uuid.uuid4()}"
    password = "P@ssW0rd"
    auth_client.register(username, password)
    return username