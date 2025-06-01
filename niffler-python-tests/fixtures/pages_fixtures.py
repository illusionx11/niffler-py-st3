import pytest
from models.config import ServerEnvs
import allure
import logging
from clients.oauth_client import OAuthClient
from pages.login_page import LoginPage
from pages.main_page import MainPage
from pages.register_page import RegisterPage
from pages.profile_page import ProfilePage
from selenium import webdriver
from pytest import FixtureRequest
from selenium.webdriver.chrome.options import Options as ChromeOptions

@pytest.fixture(scope="session")
def browser(request: FixtureRequest, headless: str):
    options = ChromeOptions()
    if headless == "true":
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    yield browser
    try:
        if request.node.rep_setup.failed or request.node.rep_call.failed:
            allure.attach(
                browser.get_screenshot_as_png(),
                name=request.node.name,
                attachment_type=allure.attachment_type.PNG
            )
    except AttributeError:
        pass
    browser.close()
    
@pytest.fixture(scope="session")
def login_page(browser: webdriver.Chrome, server_envs: ServerEnvs):
    return LoginPage(browser, url=f"{server_envs.auth_url}/login")

@pytest.fixture(scope="session")
def register_page(browser: webdriver.Chrome, server_envs: ServerEnvs):
    return RegisterPage(browser, url=f"{server_envs.auth_url}/register")

@pytest.fixture(scope="session")
def main_page(browser: webdriver.Chrome, server_envs: ServerEnvs):
    return MainPage(browser, url=f"{server_envs.frontend_url}/main")

@pytest.fixture(scope="session")
def profile_page(browser: webdriver.Chrome, server_envs: ServerEnvs):
    return ProfilePage(browser, url=f"{server_envs.frontend_url}/profile")