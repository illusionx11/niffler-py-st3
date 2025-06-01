import pytest
from faker import Faker
import random
import string
import time
import allure
from marks import TestData
from pages.register_page import RegisterPage
from utils.errors import ValidationErrors
from allure_data import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

LONG_USERNAME = "".join(random.choices(string.ascii_letters + string.digits, k=51))
LONG_PASSWORD = "".join(random.choices(string.ascii_letters + string.digits, k=13))
faker = Faker()

@pytest.mark.usefixtures("register_page")
@pytest.mark.registration
@allure.feature(Feature.register)
class TestRegistration:
    
    @TestData.username(["a", LONG_USERNAME])
    @allure.story(Story.errors)
    def test_incorrect_username(self, register_page: RegisterPage, username: str):
        register_page.open()
        register_page.should_be_register_page()
        password = faker.password(length=8)
        register_page.register_user(username, password)
        errors = {
            "username": [ValidationErrors.USERNAME_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        register_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.password(["a", LONG_PASSWORD])
    @allure.story(Story.errors)
    def test_incorrect_password(self, register_page: RegisterPage, password: str):
        register_page.open()
        register_page.should_be_register_page()
        username = faker.first_name()
        register_page.register_user(username, password)
        errors = {
            "password": [ValidationErrors.PASSWORD_LENGTH],
            "password_repeat": [ValidationErrors.PASSWORD_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        register_page.should_be_errors_in_validation(errors=errors)
    
    @pytest.mark.repeat(2)
    @allure.story(Story.errors)
    def test_wrong_passwords(self, register_page: RegisterPage):
        register_page.open()
        register_page.should_be_register_page()
        username = faker.first_name()
        password = faker.password(length=8)
        while True:
            password_repeat = faker.password(length=8)
            if password != password_repeat:
                break
        register_page.register_user(username, password, password_repeat)
        errors = {
            "username": [],
            "password": [ValidationErrors.DIFFERENT_PASSWORDS],
            "password_repeat": [],
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        register_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.register_data([
        {"username": "a", "password": "ababab", "password_repeat": "bababa"},
        {"username": "newuser", "password": "ababab", "password_repeat": "b"},
        {"username": "newuser", "password": LONG_PASSWORD, "password_repeat": "bababa"},
        {"username": "a", "password": "a", "password_repeat": LONG_PASSWORD},
        {"username": LONG_USERNAME, "password": "a", "password_repeat": "a"}
    ])
    @allure.story(Story.errors)
    def test_mixed_errors(self, register_page: RegisterPage, register_data: dict[str]):
        register_page.open()
        register_page.should_be_register_page()
        username = register_data["username"]
        password = register_data["password"]
        password_repeat = register_data["password_repeat"]
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
        register_page.register_user(username, password, password_repeat)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        register_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.register_user) 
    def test_correct_registration(self, register_page: RegisterPage):
        register_page.open()
        register_page.should_be_register_page()
        username = faker.first_name() + str(random.randint(100, 1000))
        password = faker.password(length=8)
        register_page.register_user(username, password)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        register_page.should_be_successful_registration()
        