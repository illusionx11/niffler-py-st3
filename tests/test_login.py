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

@pytest.mark.usefixtures("browser")
@pytest.mark.login
class TestRegistration:
    
    @pytest.mark.parametrize("data", [
        {"username": "a", "password": "a"},
        {"username": "wrongUserNonExistent!!", "password": "wrongPass"}
    ])
    def test_bad_credentials(self, browser: webdriver.Chrome, data: dict[str, str]):
        page = LoginPage(browser, url=Urls.LOGIN_URL)
        username = data["username"]
        password = data["password"]
        page.log_in(username, password)
        errors = {
            "login": [ValidationErrors.LOGIN_BAD_CREDENTIALS]
        }
        page.should_be_errors_in_validation(errors=errors)
        
    def test_successful_login(self, browser: webdriver.Chrome):
        page = LoginPage(browser, url=Urls.LOGIN_URL)
        username = os.getenv("NIFFLER_QA_USERNAME")
        password = os.getenv("NIFFLER_QA_PASSWORD")
        page.log_in(username, password)
        
        mainpage = MainPage(browser, url=Urls.FRONTEND_URL)
        mainpage.should_be_mainpage()
        
    