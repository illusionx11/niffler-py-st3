import pytest
from dotenv import load_dotenv, find_dotenv
import os
import logging
from selenium import webdriver
import random
import allure
from allure_commons.reporter import AllureReporter
from allure_pytest.listener import AllureListener
from allure_commons.types import LabelType
from pytest import Item, FixtureDef, FixtureRequest
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

def allure_logger(config) -> AllureReporter:
    listener: AllureListener = config.pluginmanager.get_plugin("allure_listener")
    return listener.allure_logger if listener else None

################# Hooks ####################

@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_call(item: Item):
    yield
    allure.dynamic.title(" ".join(item.name.split("_")[1:]).title())
    
@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_fixture_setup(fixturedef: FixtureDef, request: FixtureRequest):
    yield
    logger = allure_logger(request.config)
    item = logger.get_last_item(None)
    scope_letter = fixturedef.scope[0].upper()
    item.name = f"[{scope_letter}] " + " ".join(fixturedef.argname.split("_")).title()

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    Модифицирует отчет Allure, убирая тег usefixtures из меток.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    # Получаем текущий тест в Allure
    logger = allure_logger(item.config)
    if logger:
        test_case = logger.get_test(None)
        if test_case:
            # Фильтруем метки, убирая usefixtures
            test_case.labels = [
                label for label in test_case.labels
                if not (label.name == LabelType.TAG and "pytest.mark.usefixtures" in label.value)
            ]
        
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown(item: Item):
    yield
    reporter = allure_logger(item.config)
    if reporter:
        try:
            test = reporter.get_test(None)
            test.labels = list(filter(lambda x: x.name not in ("suite", "subSuite", "parentSuite"), test.labels))
        except Exception as e:
            logging.warning(f"Ошибка при обработке меток Allure: {e}")

@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    """
    Модифицирует список маркеров тестов, убирая маркер usefixtures из тегов тестов и классов.
    """
    for item in items:
        # Получаем маркеры теста
        test_markers = list(item.iter_markers())
        # Получаем маркеры класса, если тест принадлежит классу
        class_markers = list(item.parent.iter_markers()) if hasattr(item.parent, 'iter_markers') else []
        # Очищаем маркеры теста
        item.own_markers[:] = []
        # Добавляем обратно маркеры теста, кроме usefixtures
        for marker in test_markers:
            if marker.name != "usefixtures":
                item.add_marker(pytest.mark.__getattr__(marker.name)(*marker.args, **marker.kwargs))
        # Добавляем обратно маркеры класса, кроме usefixtures
        for marker in class_markers:
            if marker.name != "usefixtures":
                item.add_marker(pytest.mark.__getattr__(marker.name)(*marker.args, **marker.kwargs))

################# Arguments ####################

def pytest_addoption(parser):
    parser.addoption("--headless", action="store", default="false", help="Run tests in headless mode: true/false (default false)")

@pytest.fixture(scope="session")
def headless(request: FixtureRequest):
    return request.config.getoption("--headless")

################# GENERAL ####################

@pytest.fixture(scope="session")
def envs() -> Envs:
    load_dotenv(find_dotenv())
    envs_instance = Envs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        auth_url=os.getenv("AUTH_URL"),
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
        spends_db_url=os.getenv("SPENDS_DB_URL")
    )
    allure.attach(envs_instance.model_dump_json(indent=2), name="envs.json", attachment_type=allure.attachment_type.JSON)
    return envs_instance
    
@pytest.fixture(scope="class")
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
    
@pytest.fixture(scope="class")
def login_page(browser: webdriver.Chrome, envs: Envs):
    return LoginPage(browser, url=f"{envs.auth_url}/login")

@pytest.fixture(scope="class")
def register_page(browser: webdriver.Chrome, envs: Envs):
    return RegisterPage(browser, url=f"{envs.auth_url}/register")

@pytest.fixture(scope="class")
def main_page(browser: webdriver.Chrome, envs: Envs):
    return MainPage(browser, url=f"{envs.frontend_url}/main")

@pytest.fixture(scope="class")
def profile_page(browser: webdriver.Chrome, envs: Envs):
    return ProfilePage(browser, url=f"{envs.frontend_url}/profile")

@pytest.fixture(scope="class")
def niffler_api(envs: Envs):
    api: NifflerAPI = NifflerAPI(envs=envs)
    yield api
    api.session.close()
    
@pytest.fixture(scope="class", autouse=True)
def qa_user(niffler_api: NifflerAPI, envs: Envs, login_page: LoginPage, main_page: MainPage):
    username = envs.test_username
    password = envs.test_password
    niffler_api.register()
    login_page.log_in(username, password)
    main_page.should_be_mainpage()
    token = main_page.get_access_token()
    allure.attach(token, name="token.txt", attachment_type=allure.attachment_type.TEXT)
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
    niffler_api.clear_spendings()
    spends_db.delete_user_categories(username=envs.test_username)
    logging.info("Cleanup before tests ended")
    yield
    niffler_api.clear_spendings()
    spends_db.delete_user_categories(username=envs.test_username)
    logging.info("Cleanup after teardown ended")

@pytest.fixture(scope="function")
def all_categories(niffler_api: NifflerAPI):
    return niffler_api.get_all_categories()

@pytest.fixture(params=[])
def category(request: FixtureRequest, niffler_api: NifflerAPI, spends_db: SpendsDb):
    category_name = request.param
    category_data = niffler_api.add_category(category_name)
    yield category_name
    spends_db.delete_category(category_data.id)
    
@pytest.fixture(params=[])
def archived_category(request: FixtureRequest, niffler_api: NifflerAPI, all_categories: list[Category], spends_db: SpendsDb):
    category_name = request.param
    active_category = next((c for c in all_categories if c.name == category_name and c.archived == False), None)
    if not active_category:
        active_category = niffler_api.add_category(category_name)
    active_category.archived = True
    niffler_api.update_category(active_category)
    yield category_name
    spends_db.delete_category(active_category.id)
