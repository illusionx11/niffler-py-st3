import pytest
from models.config import ServerEnvs
import allure
from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.register_page import RegisterPage
from pages.profile_page import ProfilePage
from selenium import webdriver
from pytest import FixtureRequest
from selenium.webdriver.chrome.options import Options as ChromeOptions
from models.auth_user import TokenData

@pytest.fixture(scope="session")
def browser(request: FixtureRequest, headless: bool):
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.close()
    
@pytest.fixture
def login_page(
    browser: webdriver.Chrome, server_envs: ServerEnvs, token_data: TokenData
):
    return LoginPage(
        browser, url=f"{server_envs.auth_url}/login", token_data=token_data
    )

@pytest.fixture
def register_page(
    browser: webdriver.Chrome, server_envs: ServerEnvs, token_data: TokenData
):
    return RegisterPage(
        browser, url=f"{server_envs.auth_url}/register", token_data=token_data
    )

@pytest.fixture
def main_page(
    browser: webdriver.Chrome, server_envs: ServerEnvs, token_data: TokenData
):
    return MainPage(
        browser, url=f"{server_envs.frontend_url}/main", token_data=token_data
    )

@pytest.fixture
def profile_page(
    browser: webdriver.Chrome, server_envs: ServerEnvs, token_data: TokenData
):
    return ProfilePage(
        browser, url=f"{server_envs.frontend_url}/profile", token_data=token_data
    )