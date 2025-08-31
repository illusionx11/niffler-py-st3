# import pytest
# from models.config import ClientEnvs
# from clients.oauth_client import OAuthClient

# @pytest.fixture(scope="session", autouse=True)
# def token_data(client_envs: ClientEnvs, auth_client: OAuthClient, cleanup):
#     username = client_envs.test_username
#     password = client_envs.test_password
#     auth_client.register(username, password)
#     token_data = auth_client.get_token(username, password)
#     yield token_data