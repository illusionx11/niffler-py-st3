import pytest
from dotenv import load_dotenv, find_dotenv
import os
import logging
from selenium import webdriver
import random
from faker import Faker
from tests.utils.mock_data import MockData
from tests.databases.spends_db import SpendsDb
from tests.models.config import Envs
from tests.models.spend import Spend, SpendAdd, SpendGet, Category, CategoryAdd
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
def envs() -> Envs:
    load_dotenv(find_dotenv())
    return Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        auth_url=os.getenv("AUTH_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
        spends_db_url=os.getenv("SPENDS_DB_URL")
    )
    
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
def login_page(browser: webdriver.Chrome, envs: Envs):
    return LoginPage(browser, url=f"{envs.auth_url}/login")

@pytest.fixture(scope="session")
def register_page(browser: webdriver.Chrome, envs: Envs):
    return RegisterPage(browser, url=f"{envs.auth_url}/register")

@pytest.fixture(scope="session")
def main_page(browser: webdriver.Chrome, envs: Envs):
    return MainPage(browser, url=f"{envs.frontend_url}/main")

@pytest.fixture(scope="session")
def profile_page(browser: webdriver.Chrome, envs: Envs):
    return ProfilePage(browser, url=f"{envs.frontend_url}/profile")

@pytest.fixture(scope="session")
def niffler_api(envs: Envs):
    api: NifflerAPI = NifflerAPI(envs=envs)
    yield api
    api.session.close()
    
@pytest.fixture(scope="session", autouse=True)
def qa_user(niffler_api: NifflerAPI, envs: Envs, login_page: LoginPage, main_page: MainPage):
    username = envs.test_username
    password = envs.test_password
    niffler_api.register()
    login_page.log_in(username, password)
    main_page.should_be_mainpage()
    token = main_page.get_access_token()
    niffler_api.session.headers.update({"Authorization": f"Bearer {token}"})
    yield

################# Database ####################

@pytest.fixture(scope="session")
def spends_db(envs: Envs) -> SpendsDb:
    return SpendsDb(db_url=envs.spends_db_url)

################# Parametrization ####################

class TestData:   
    # Login tests
    login_data = lambda x: pytest.mark.parametrize("login_data", x, ids=lambda param: param["username"])
    # Registration tests
    register_data = lambda x: pytest.mark.parametrize("register_data", x, ids=lambda param: f"{param['username']} {param['password']} {param['password_repeat']}")
    username = lambda x: pytest.mark.parametrize("username", x)
    password = lambda x: pytest.mark.parametrize("password", x)
    # Spendings tests
    spending_data = lambda x: pytest.mark.parametrize("spending_data", x, ids=lambda param: f"{param.amount} {param.currency} {param.category} {param.description}")
    query = lambda x: pytest.mark.parametrize("query", x)
    # Profile tests
    direct_category = lambda x: pytest.mark.parametrize("direct_category", x)
    category = lambda x: pytest.mark.parametrize("category", x, indirect=True)
    archived_category = lambda x: pytest.mark.parametrize("archived_category", x, indirect=True)
    profile_name = lambda x: pytest.mark.parametrize("profile_name", x)

################# For spending tests ####################

@pytest.fixture(scope="session")
def spendings_data(envs: Envs):
    faker = Faker()
    spendings = []
    for _ in range(10):
        amount = faker.random_number(digits=3)
        category_name = random.choice(MockData.CATEGORIES)
        currency = random.choice(MockData.CURRENCIES)
        description = faker.sentence(nb_words=2, variable_nb_words=True)
        spend_date = faker.date_time().isoformat(timespec="milliseconds") + "Z"
        data = SpendAdd(
            amount=amount,
            category=CategoryAdd(name=category_name),
            currency=currency,
            description=description,
            spendDate=spend_date,
            username=envs.test_username
        )
        spendings.append(data)
        
    return spendings

@pytest.fixture(scope="class")
def add_spendings(niffler_api: NifflerAPI, spendings_data: list[SpendAdd]):
    all_spendings = niffler_api.get_all_spendings()
    for data in spendings_data:
        amount = data.amount
        category = data.category.name
        currency = data.currency
        description = data.description
        if any([amount in [s.amount for s in all_spendings], 
                category in [s.category.name for s in all_spendings], 
                currency in [s.currency for s in all_spendings], 
                description in [s.description for s in all_spendings]]):
            continue
        niffler_api.add_spending(data)
    yield
    
@pytest.fixture
def spendings_list(niffler_api: NifflerAPI) -> list[SpendGet]:
    return niffler_api.get_all_spendings()

################# For profile tests ####################

@pytest.fixture(scope="class")
def cleanup(niffler_api: NifflerAPI, envs: Envs, spends_db: SpendsDb):
    niffler_api.clear_all_spendings()
    spends_db.delete_user_categories(username=envs.test_username)
    logging.info("Cleanup before tests ended")
    yield
    niffler_api.clear_all_spendings()
    spends_db.delete_user_categories(username=envs.test_username)
    logging.info("Cleanup after teardown ended")

@pytest.fixture(scope="function")
def all_categories(niffler_api: NifflerAPI):
    return niffler_api.get_all_categories()

@pytest.fixture(params=[])
def category(request, niffler_api: NifflerAPI, spends_db: SpendsDb):
    category_name = request.param
    category_data = niffler_api.add_category(category_name)
    yield category_name
    spends_db.delete_category(category_data.id)
    
@pytest.fixture(params=[])
def archived_category(request, niffler_api: NifflerAPI, all_categories: list[Category], spends_db: SpendsDb):
    category_name = request.param
    active_category = next((c for c in all_categories if c.name == category_name and c.archived == False), None)
    if not active_category:
        active_category = niffler_api.add_category(category_name)
    active_category.archived = True
    niffler_api.update_category(active_category)
    yield category_name
    spends_db.delete_category(active_category.id)