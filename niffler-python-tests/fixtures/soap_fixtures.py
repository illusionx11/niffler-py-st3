import logging
import pytest
from utils.user_creator import SoapUserCreator
from clients.oauth_client import OAuthClient
from clients.soap_client import SoapClient
from databases.userdata_db import UserdataDb
from databases.auth_db import AuthDb
from faker import Faker

@pytest.fixture(scope="session")
def soap_user_creator(
    auth_client: OAuthClient,
    soap_client: SoapClient,
    userdata_db: UserdataDb,
    auth_db: AuthDb,
    faker: Faker
):
    return SoapUserCreator(
        auth_client,
        soap_client,
        userdata_db,
        auth_db,
        faker
    )

@pytest.fixture(scope="function")
def mock_users(
    soap_user_creator: SoapUserCreator
):
    """Фикстура для создания mock-пользователей"""
    logging.info("Создание mock-пользователей для SOAP")
    users = soap_user_creator.create_users(10)
    yield users
    soap_user_creator.delete_users(users)

@pytest.fixture(scope="function")
def mock_friends(soap_user_creator: SoapUserCreator, soap_friends_user: str):
    """Создаёт друзей для конкретного soap_user"""
    logging.info(f"Создание mock-друзей для {soap_friends_user}")
    users = soap_user_creator.create_users(10, friends_user=soap_friends_user)
    yield users
    soap_user_creator.delete_users(users)
    
@pytest.fixture(scope="function")
def mock_friends_actions(
    soap_user_creator: SoapUserCreator,
    soap_actions_user: str
):
    """Фикстура для создания mock-пользователей (actions)"""
    logging.info("Создание mock-пользователей (actions) для SOAP перед началом тестов")
    users = soap_user_creator.create_users(10, actions_user=soap_actions_user)
    yield users
    soap_user_creator.delete_users(users)