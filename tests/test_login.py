import pytest
import os
from tests.conftest import TestData
from tests.models.config import Envs
from tests.pages.login_page import LoginPage
from tests.pages.main_page import MainPage
from tests.utils.errors import ValidationErrors

@pytest.mark.usefixtures("login_page", "main_page")
@pytest.mark.login
class TestRegistration:
    
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
        login_page.should_be_errors_in_validation(errors=errors)
        
    def test_successful_login(self, login_page: LoginPage, main_page: MainPage, envs: Envs):
        username = envs.test_username
        password = envs.test_password
        login_page.log_in(username, password)
        
        main_page.should_be_mainpage()
        
    