import pytest
import allure
import time
from marks import TestData
from models.config import ClientEnvs
from pages.login_page import LoginPage
from pages.main_page import MainPage
from utils.errors import ValidationErrors
from utils.allure_data import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "login_page", 
    "main_page"
)
@pytest.mark.ui
@pytest.mark.login
@allure.feature(Feature.login)
@allure.story(Story.auth_user)
class TestLogin:
    
    @TestData.login_data([
        {"username": "a", "password": "a"},
        {"username": "wrongUserNonExistent!!", "password": "wrongPass"}
    ])
    def test_bad_credentials(self, login_page: LoginPage, login_data: dict[str, str]):
        username = login_data["username"]
        password = login_data["password"]
        login_page.log_in(username, password)
        errors = {
            "login": [ValidationErrors.LOGIN_BAD_CREDENTIALS]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        login_page.should_be_errors_in_validation(errors=errors)
    
    def test_successful_login(self, login_page: LoginPage, main_page: MainPage, client_envs: ClientEnvs):
        username = client_envs.test_username
        password = client_envs.test_password
        login_page.log_in(username, password)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_mainpage()
        
    