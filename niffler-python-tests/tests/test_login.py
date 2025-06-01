import pytest
import allure
from marks import TestData
from models.config import ClientEnvs
from pages.login_page import LoginPage
from pages.main_page import MainPage
from utils.errors import ValidationErrors
from allure_data import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "login_page", 
    "main_page"
)
@pytest.mark.login
@allure.feature(Feature.login)
class TestLogin:
    
    @TestData.login_data([
        {"username": "a", "password": "a"},
        {"username": "wrongUserNonExistent!!", "password": "wrongPass"}
    ])
    @allure.story(Story.errors)
    def test_bad_credentials(self, login_page: LoginPage, login_data: dict[str, str]):
        username = login_data["username"]
        password = login_data["password"]
        login_page.log_in(username, password)
        errors = {
            "login": [ValidationErrors.LOGIN_BAD_CREDENTIALS]
        }
        login_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.auth_user)
    def test_successful_login(self, login_page: LoginPage, main_page: MainPage, client_envs: ClientEnvs):
        username = client_envs.test_username
        password = client_envs.test_password
        login_page.log_in(username, password)
        
        main_page.should_be_mainpage()
        
    