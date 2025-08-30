import pytest
from faker import Faker
import allure
from marks import TestData
from pages.register_page import RegisterPage
from utils.errors import ValidationErrors
from utils.allure_data import Epic, Feature, Story
from models.user import UserData

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

LONG_USERNAME = "a" * 51
LONG_PASSWORD = "a" * 13

@pytest.mark.usefixtures("register_page", "faker")
@pytest.mark.registration
@pytest.mark.ui
@allure.feature(Feature.registration)
@allure.story(Story.register_user)
class TestRegistration:
    
    @TestData.username(["a", LONG_USERNAME])
    def test_incorrect_username(self, register_page: RegisterPage, username: str, faker: Faker):
        register_page.open()
        register_page.should_be_register_page()
        password = faker.password(length=8)
        register_page.register_user(username, password)
        errors = {
            "username": [ValidationErrors.USERNAME_LENGTH]
        }
        register_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.password(["a", LONG_PASSWORD])
    def test_incorrect_password(self, register_page: RegisterPage, password: str, faker: Faker):
        register_page.open()
        register_page.should_be_register_page()
        username = faker.first_name()
        register_page.register_user(username, password)
        errors = {
            "password": [ValidationErrors.PASSWORD_LENGTH],
            "password_repeat": [ValidationErrors.PASSWORD_LENGTH]
        }
        register_page.should_be_errors_in_validation(errors=errors)
    
    @pytest.mark.repeat(2)
    def test_wrong_passwords(self, register_page: RegisterPage, faker: Faker):
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
        register_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.register_data([
        UserData(username="a", password="ababab", password_repeat="bababa"),
        UserData(username="newuser", password="ababab", password_repeat="b"),
        UserData(username="newuser", password=LONG_PASSWORD, password_repeat="bababa"),
        UserData(username="a", password="a", password_repeat=LONG_PASSWORD),
        UserData(username=LONG_USERNAME, password="a", password_repeat="a")
    ])
    def test_registration_mixed_errors(self, register_page: RegisterPage, register_data: UserData):
        register_page.open()
        register_page.should_be_register_page()
        username = register_data.username
        password = register_data.password
        password_repeat = register_data.password_repeat
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
        register_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.new_user([UserData(username="NifflerUser", password="PassWordGo0d")])
    def test_correct_registration(self, register_page: RegisterPage, new_user: UserData):
        register_page.open()
        register_page.should_be_register_page()
        register_page.register_user(new_user.username, new_user.password)
        register_page.should_be_successful_registration()
        