import pytest
from models.config import ServerEnvs, ClientEnvs
from clients.oauth_client import OAuthClient
from clients.spends_client import SpendsClient
from clients.users_client import UsersClient
from databases.spends_db import SpendsDb

@pytest.fixture(scope="session")
def auth_client(server_envs: ServerEnvs):
    auth_client: OAuthClient = OAuthClient(server_envs=server_envs)
    yield auth_client
    auth_client.session.close()

@pytest.fixture(scope="session")
def spends_client(server_envs: ServerEnvs, client_envs: ClientEnvs, auth_api_token: str):
    spends_client: SpendsClient = SpendsClient(server_envs=server_envs, client_envs=client_envs, token=auth_api_token)
    yield spends_client
    
@pytest.fixture(scope="session")
def users_client(server_envs: ServerEnvs, auth_api_token: str):
    users_client: UsersClient = UsersClient(server_envs=server_envs, token=auth_api_token)
    yield users_client
    
################# Database ####################

@pytest.fixture(scope="session")
def spends_db(server_envs: ServerEnvs) -> SpendsDb:
    return SpendsDb(server_envs=server_envs)