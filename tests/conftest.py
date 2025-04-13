import pytest
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import logging
from selenium import webdriver
from tests.utils.niffler_api import NifflerAPI
from tests.pages.login_page import LoginPage
from tests.pages.main_page import MainPage
from tests.pages.register_page import RegisterPage
from tests.pages.profile_page import ProfilePage
from selenium.webdriver.chrome.options import Options as ChromeOptions

def pytest_addoption(parser):
    parser.addoption("--headless", action="store", default="false", help="Run tests in headless mode: true/false (default false)")

@pytest.fixture(scope="session")
def headless(request):
    return request.config.getoption("--headless")

################# GENERAL ####################

@pytest.fixture(scope="session")
def config():
    return {
        "auth_url": os.getenv("AUTH_URL"),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "gateway_url": os.getenv("GATEWAY_URL"),
        "login_url": f"{os.getenv('AUTH_URL')}/login",
        "register_url": f"{os.getenv('AUTH_URL')}/register",
        "mainpage_url": f"{os.getenv('FRONTEND_URL')}/main",
        "profile_url": f"{os.getenv('FRONTEND_URL')}/profile",
        "username": os.getenv("NIFFLER_QA_USERNAME"),
        "password": os.getenv("NIFFLER_QA_PASSWORD")
    }
    
@pytest.fixture(scope="session")
def browser(headless: str):
    options = ChromeOptions()
    if headless == "true":
        options.add_argument("--headless")
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

@pytest.fixture(scope="session")
def profile_page(browser: webdriver.Chrome, config: dict[str, str]):
    return ProfilePage(browser, url=config["profile_url"])

@pytest.fixture(scope="session")
def token(config: dict[str, str], login_page: LoginPage, main_page: MainPage):
    username = config["username"]
    password = config["password"]
    login_page.log_in(username, password)
    
    main_page.should_be_mainpage()
    return main_page.get_access_token()

@pytest.fixture(scope="session")
def niffler_api(token: str, config: dict[str, str]):
    api: NifflerAPI = NifflerAPI(token=token, config=config)
    yield api
    api.session.close()
    
@pytest.fixture(scope="session")
def create_qa_user(niffler_api: NifflerAPI, config: dict[str, str]):
    username = config["username"]
    password = config["password"]
    niffler_api.register(username, password)

################# Parametrization ####################

class TestData:   
    # Login tests
    login_data = lambda x: pytest.mark.parametrize("login_data", x, ids=lambda param: param["username"])
    # Registration tests
    register_data = lambda x: pytest.mark.parametrize("register_data", x, ids=lambda param: f"{param['username']} {param['password']} {param['password_repeat']}")
    username = lambda x: pytest.mark.parametrize("username", x)
    password = lambda x: pytest.mark.parametrize("password", x)
    # Spendings tests
    spending_data = lambda x: pytest.mark.parametrize("spending_data", x, ids=lambda param: f"{param['amount']} {param['currency']} {param['category']} {param['description']}")
    query = lambda x: pytest.mark.parametrize("query", x)
    # Profile tests
    direct_category = lambda x: pytest.mark.parametrize("direct_category", x)
    category = lambda x: pytest.mark.parametrize("category", x, indirect=True)
    archived_category = lambda x: pytest.mark.parametrize("archived_category", x, indirect=True)
    profile_name = lambda x: pytest.mark.parametrize("profile_name", x)

################# For profile tests ####################

@pytest.fixture(scope="class")
def initialize(niffler_api: NifflerAPI):
    niffler_api.cleanup()
    logging.info("Cleanup before tests ended")
    yield
    niffler_api.cleanup()
    logging.info("Cleanup after teardown ended")

@pytest.fixture(scope="function")
def all_categories(niffler_api: NifflerAPI):
    return niffler_api.get_all_categories()

@pytest.fixture(params=[])
def category(request, niffler_api: NifflerAPI, all_categories: list[dict]):
    category_name = request.param
    current_categories = [c["name"] for c in all_categories]
    if category_name not in current_categories:
        category_data = niffler_api.add_category(category_name)
    yield category_name
    niffler_api.cleanup()
    
@pytest.fixture(params=[])
def archived_category(request, niffler_api: NifflerAPI, all_categories: list[dict]):
    category_name = request.param
    active_category = next((c for c in all_categories if c["name"] == category_name and c["archived"] == False), None)
    if not active_category:
        category_data = niffler_api.add_category(category_name)
        category_data["archived"] = True
        niffler_api.update_category(category_data)
    yield category_name
    niffler_api.cleanup()