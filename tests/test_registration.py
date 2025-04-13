import pytest
from faker import Faker
import random
import string
from selenium import webdriver
from tests.pages.urls import Urls
from tests.pages.register_page import RegisterPage
from tests.utils.errors import ValidationErrors

LONG_USERNAME = "".join(random.choices(string.ascii_letters + string.digits, k=51))
LONG_PASSWORD = "".join(random.choices(string.ascii_letters + string.digits, k=13))
faker = Faker()

@pytest.mark.usefixtures("browser")
@pytest.mark.registration
class TestRegistration:
    
    @pytest.mark.parametrize("username", ["a", LONG_USERNAME])
    def test_incorrect_username(self, browser: webdriver.Chrome, username: str):
        page = RegisterPage(browser, url=Urls.REGISTER_URL)
        page.open()
        page.should_be_register_page()
        password = faker.password(length=8)
        page.register_user(username, password)
        errors = {
            "username": [ValidationErrors.USERNAME_LENGTH],
            "password": [],
            "password_repeat": []
        }
        page.should_be_errors_in_validation(errors=errors)
        
    @pytest.mark.parametrize("password", ["a", LONG_PASSWORD])
    def test_incorrect_password(self, browser: webdriver.Chrome, password: str):
        page = RegisterPage(browser, url=Urls.REGISTER_URL)
        page.open()
        page.should_be_register_page()
        username = faker.first_name()
        page.register_user(username, password)
        errors = {
            "username": [],
            "password": [ValidationErrors.PASSWORD_LENGTH],
            "password_repeat": [ValidationErrors.PASSWORD_LENGTH]
        }
        page.should_be_errors_in_validation(errors=errors)
    
    @pytest.mark.parametrize("repeat", [0, 1])
    def test_wrong_passwords(self, browser: webdriver.Chrome, repeat: int):
        page = RegisterPage(browser, url=Urls.REGISTER_URL)
        page.open()
        page.should_be_register_page()
        username = faker.first_name()
        password = faker.password(length=8)
        while True:
            password_repeat = faker.password(length=8)
            if password != password_repeat:
                break
        page.register_user(username, password, password_repeat)
        errors = {
            "username": [],
            "password": [ValidationErrors.DIFFERENT_PASSWORDS],
            "password_repeat": [],
        }
        page.should_be_errors_in_validation(errors=errors)
    
    @pytest.mark.parametrize("data", [
        {"username": "a", "password": "ababab", "password_repeat": "bababa"},
        {"username": "newuser", "password": "ababab", "password_repeat": "b"},
        {"username": "newuser", "password": LONG_PASSWORD, "password_repeat": "bababa"},
        {"username": "a", "password": "a", "password_repeat": LONG_PASSWORD},
        {"username": LONG_USERNAME, "password": "a", "password_repeat": "a"}
    ])
    def test_mixed_errors(self, browser: webdriver.Chrome, data: dict[str]):
        page = RegisterPage(browser, url=Urls.REGISTER_URL)
        page.open()
        page.should_be_register_page()
        username = data["username"]
        password = data["password"]
        password_repeat = data["password_repeat"]
        errors = {
            "username": [],
            "password": [],
            "password_repeat": []
        }
        if len(username) < 3 or len(username) > 50:
            errors["username"].append(ValidationErrors.USERNAME_LENGTH)
        if len(password) < 3 or len(password) > 12:
            errors["password"].append(ValidationErrors.PASSWORD_LENGTH)
        if len(password_repeat) < 3 or len(password_repeat) > 12:
            errors["password_repeat"].append(ValidationErrors.PASSWORD_LENGTH)
        if password != password_repeat:
            errors["password"].append(ValidationErrors.DIFFERENT_PASSWORDS)
        page.register_user(username, password, password_repeat)
        page.should_be_errors_in_validation(errors=errors)
        
    def test_correct_registration(self, browser: webdriver.Chrome):
        page = RegisterPage(browser, url=Urls.REGISTER_URL)
        page.open()
        page.should_be_register_page()
        username = faker.first_name() + str(random.randint(100, 1000))
        password = faker.password(length=8)
        page.register_user(username, password)
        page.should_be_successful_registration()
        