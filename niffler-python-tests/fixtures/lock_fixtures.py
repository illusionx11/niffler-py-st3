import pytest
import logging
from clients.lock_client import LockManager
from databases.spends_db import SpendsDb
from databases.auth_db import AuthDb
from databases.userdata_db import UserdataDb
from models.config import ClientEnvs
from clients.lock_client import LockManager
from clients.oauth_client import OAuthClient
from models.auth_user import TokenData

@pytest.fixture(scope="session")
def lock_manager() -> LockManager:
    return LockManager()


@pytest.fixture(scope="session", autouse=True)
def cleanup(
    lock_manager: LockManager,
    spends_db: SpendsDb,
    auth_db: AuthDb,
    userdata_db: UserdataDb,
    client_envs: ClientEnvs
):
    
    def clear_stand():
        from utils.cleaner import StandCleaner
        stand_cleaner = StandCleaner(
            spends_db,
            auth_db,
            userdata_db,
            client_envs
        )
        stand_cleaner.clean()
        logging.info("Очистка стенда завершена")
    
    logging.info("Очистка стенда перед началом тестов")
    
    for users in lock_manager.acquire_lock(
        lock_file_path="cleanup.lock",
        lock_count_path="cleanup.count",
        create_func=clear_stand,
        cleanup_func=clear_stand,
        name="cleanup"
    ):
        yield users
        
@pytest.fixture(scope="session", autouse=True)
def token_data(
    client_envs: ClientEnvs, auth_client: OAuthClient, cleanup, lock_manager: LockManager
):
    
    def get_token_data():
        username = client_envs.test_username
        password = client_envs.test_password
        auth_client.register(username, password)
        token_data = auth_client.get_token(username, password)
        return token_data.model_dump()
    
    for token_data in lock_manager.acquire_lock(
        lock_file_path="token_data.lock",
        lock_data_path="token_data.json",
        lock_count_path="token_data.count",
        name="token_data",
        create_func=get_token_data
    ):
        yield TokenData(
            access_token=token_data["access_token"],
            code_verifier=token_data["code_verifier"],
            code_challenge=token_data["code_challenge"],
            id_token=token_data["id_token"],
            cookies=token_data["cookies"]
        )

@pytest.fixture(scope="function")
def delete_spendings_lock(lock_manager: LockManager):
    """Фикстура для блокировки тестов удаления расходов"""
    
    for _ in lock_manager.acquire_lock(
        lock_file_path="delete_spendings.lock",
        name="delete_spendings"
    ):
        yield

@pytest.fixture(scope="function")
def profile_name_lock(lock_manager: LockManager):
    """Фикстура для блокировки тестов изменения имени в профиле"""
    
    for _ in lock_manager.acquire_lock(
        lock_file_path="profile_name.lock",
        name="profile_name"
    ):
        yield