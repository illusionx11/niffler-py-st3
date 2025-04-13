import pytest
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
from selenium import webdriver
from faker import Faker
from tests.utils.niffler_api import NifflerAPI
from tests.pages.login_page import LoginPage
from tests.pages.main_page import MainPage
from tests.pages.register_page import RegisterPage
from selenium.webdriver.chrome.options import Options as ChromeOptions

@pytest.fixture(scope="session")
def config():
    return {
        "auth_url": os.getenv("AUTH_URL"),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "gateway_url": os.getenv("GATEWAY_URL"),
        "login_url": f"{os.getenv('AUTH_URL')}/login",
        "register_url": f"{os.getenv('AUTH_URL')}/register",
        "mainpage_url": f"{os.getenv('FRONTEND_URL')}/main",
        "username": os.getenv("NIFFLER_QA_USERNAME"),
        "password": os.getenv("NIFFLER_QA_PASSWORD")
    }

@pytest.fixture(scope="session")
def niffler_api():
    api: NifflerAPI = NifflerAPI()
    yield api
    api.session.close()

@pytest.fixture(scope="session", autouse=True)
def create_qa_user(niffler_api: NifflerAPI, config: dict[str, str]):
    username = config["username"]
    password = config["password"]
    niffler_api.register(username, password)
    
@pytest.fixture(scope="session")
def browser():
    options = ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()
    
@pytest.fixture(scope="session")
def login_page(browser: webdriver.Chrome, config: dict[str, str]):
    return LoginPage(browser, url=config["login_url"])

@pytest.fixture(scope="session")
def register_page(browser: webdriver.Chrome, config: dict[str, str]):
    return RegisterPage(browser, url=config["register_url"])

@pytest.fixture(scope="session")
def main_page(browser: webdriver.Chrome, config: dict[str, str]):
    return MainPage(browser, url=config["mainpage_url"])
