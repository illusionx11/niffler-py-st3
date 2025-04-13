import pytest
from faker import Faker
import random
import string
import os
from selenium import webdriver
from tests.pages.urls import Urls
from tests.pages.login_page import LoginPage
from tests.pages.main_page import MainPage
from tests.utils.errors import ValidationErrors

@pytest.mark.usefixtures("login_page", "main_page")
@pytest.mark.login
class TestRegistration:
    
    @pytest.mark.parametrize("data", [
        {"username": "a", "password": "a"},
        {"username": "wrongUserNonExistent!!", "password": "wrongPass"}
    ])
    def test_bad_credentials(self, login_page: LoginPage, data: dict[str, str]):
        username = data["username"]
        password = data["password"]
        login_page.log_in(username, password)
        errors = {
            "login": [ValidationErrors.LOGIN_BAD_CREDENTIALS]
        }
        login_page.should_be_errors_in_validation(errors=errors)
        
    def test_successful_login(self, login_page: LoginPage, main_page: MainPage):
        username = os.getenv("NIFFLER_QA_USERNAME")
        password = os.getenv("NIFFLER_QA_PASSWORD")
        login_page.log_in(username, password)
        
        main_page.should_be_mainpage()
        
    