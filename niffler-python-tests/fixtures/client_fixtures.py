import pytest
from models.config import ServerEnvs, ClientEnvs
from clients.oauth_client import OAuthClient
from clients.spends_client import SpendsClient
from clients.users_client import UsersClient
from clients.soap_client import SoapClient
from clients.kafka_client import KafkaClient
from databases.spends_db import SpendsDb
from databases.userdata_db import UserdataDb
from databases.auth_db import AuthDb
import grpc
from grpc import insecure_channel
from internal.grpc.interceptors.logging import LoggingInterceptor
from internal.grpc.interceptors.allure import AllureInterceptor
from internal.pb.niffler_currency_pb2_pbreflect import NifflerCurrencyServiceClient
from models.auth_user import TokenData

INTERCEPTORS = [
    LoggingInterceptor(),
    AllureInterceptor()
]

@pytest.fixture(scope="session")
def auth_client(server_envs: ServerEnvs):
    auth_client: OAuthClient = OAuthClient(server_envs=server_envs)
    yield auth_client
    auth_client.session.close()

@pytest.fixture(scope="session")
def spends_client(server_envs: ServerEnvs, client_envs: ClientEnvs, token_data: TokenData):
    spends_client: SpendsClient = SpendsClient(server_envs=server_envs, client_envs=client_envs, token=token_data.access_token)
    yield spends_client
    
@pytest.fixture(scope="session")
def users_client(server_envs: ServerEnvs, token_data: TokenData):
    users_client: UsersClient = UsersClient(server_envs=server_envs, token=token_data.access_token)
    yield users_client
    users_client.session.close()

@pytest.fixture(scope="session")
def soap_client(server_envs: ServerEnvs, client_envs: ClientEnvs):
    """Raw XML SOAP клиент для работы с niffler-userdata сервисом (без авторизации)"""
    soap_client: SoapClient = SoapClient(
        server_envs=server_envs, 
        client_envs=client_envs
    )
    yield soap_client
    soap_client.close()

################# Kafka ####################

@pytest.fixture(scope="session")
def kafka_client(server_envs: ServerEnvs):
    """Взаимодействие с Kafka"""
    with KafkaClient(server_envs) as k:
        yield k
    
################# GRPC ####################
@pytest.fixture(scope="session")
def grpc_client(server_envs: ServerEnvs, mock: bool) -> NifflerCurrencyServiceClient:
    host = server_envs.currency_service_host
    if mock:
        host = server_envs.wiremock_host 
    channel = insecure_channel(host)
    intercepted_channel = grpc.intercept_channel(channel, *INTERCEPTORS)
    return NifflerCurrencyServiceClient(intercepted_channel)

################# Database ####################

@pytest.fixture(scope="session")
def spends_db(server_envs: ServerEnvs) -> SpendsDb:
    return SpendsDb(server_envs=server_envs)

@pytest.fixture(scope="session")
def userdata_db(server_envs: ServerEnvs) -> UserdataDb:
    return UserdataDb(server_envs=server_envs)

@pytest.fixture(scope="session")
def auth_db(server_envs: ServerEnvs) -> AuthDb:
    return AuthDb(server_envs=server_envs)