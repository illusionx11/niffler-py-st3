import pytest
from dotenv import load_dotenv, find_dotenv
import os
import logging
import allure
from pathlib import Path
from allure_commons.reporter import AllureReporter
from allure_pytest.listener import AllureListener
from allure_commons.types import LabelType
from pytest import Item, FixtureDef, FixtureRequest
from models.config import ServerEnvs, ClientEnvs
from faker import Faker

pytest_plugins = [
    "fixtures.auth_fixtures", 
    "fixtures.client_fixtures",
    "fixtures.lock_fixtures",
    "fixtures.user_fixtures",
    "fixtures.pages_fixtures",
    "fixtures.profile_fixtures",
    "fixtures.spendings_fixtures",
    "fixtures.soap_fixtures"
]

################# Logging ####################

class UTF8FileHandler(logging.FileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, encoding="utf-8", **kwargs)

def pytest_configure():
    
    folder = Path(__file__).resolve().parent
    
    with open(f"{folder}/logs/logs.txt", "w", encoding="utf-8"):
        pass
        
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    logger.handlers.clear()
    
    file_handler = UTF8FileHandler(f"{folder}/logs/logs.txt")
    file_handler.setLevel(logging.INFO)


    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler) 

################# Allure ####################

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
        
def _capture_screenshot_on_failure(item: Item, error_type: str = "FAILED"):
    """Вспомогательная функция для создания скриншотов при ошибках"""
    if "browser" in item.fixturenames:
        try:
            browser = item._request.getfixturevalue("browser")
            screenshot = browser.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"Screenshot_{error_type}_{item.name}",
                attachment_type=allure.attachment_type.PNG
            )
            logging.info(f"Screenshot captured for {error_type} test: {item.name}")
        except Exception as e:
            logging.warning(f"Could not capture screenshot for {item.name}: {e}")

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item: Item):
    """Хук для обработки исключений во время выполнения тестов"""
    outcome = yield
    
    # Проверяем наличие исключений (включая StaleElementReferenceException)
    if outcome.excinfo is not None:
        exception_type = outcome.excinfo[0].__name__
        logging.warning(f"Exception in test {item.name}: {exception_type}")
        _capture_screenshot_on_failure(item, f"EXCEPTION_{exception_type}")

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown(item: Item):
    yield
    
    # Скриншот для упавших тестов (основная обработка)
    if hasattr(item, "rep_call") and item.rep_call.failed:
        _capture_screenshot_on_failure(item, "FAILED")
    
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
    parser.addoption("--headless", action="store_true", default=False, help="Run tests in headless mode (False if not specified)")
    parser.addoption("--mock", action="store_true", default=False, help="Run GRPC tests with mock data (False if not specified)")
    
@pytest.fixture(scope="session")
def headless(request: FixtureRequest) -> bool:
    return request.config.getoption("--headless")

@pytest.fixture(scope="session")
def mock(request: FixtureRequest) -> bool:
    return request.config.getoption("--mock")

################# ENVS ####################

@pytest.fixture(scope="session")
def server_envs() -> ServerEnvs:
    load_dotenv(find_dotenv("server.env"))
    envs_instance = ServerEnvs(
        frontend_url=os.getenv("FRONTEND_URL"),
        gateway_url=os.getenv("GATEWAY_URL"),
        auth_url=os.getenv("AUTH_URL"),
        userdata_url=os.getenv("USERDATA_URL"),
        spends_db_url=os.getenv("SPENDS_DB_URL"),
        userdata_db_url=os.getenv("USERDATA_DB_URL"),
        auth_db_url=os.getenv("AUTH_DB_URL"),
        kafka_address=os.getenv("KAFKA_ADDRESS"),
        currency_service_host=os.getenv("CURRENCY_SERVICE_HOST"),
        wiremock_host=os.getenv("WIREMOCK_HOST")
    )
    allure.attach(envs_instance.model_dump_json(indent=2), name="server_envs.json", attachment_type=allure.attachment_type.JSON)
    return envs_instance

@pytest.fixture(scope="session")
def client_envs() -> ClientEnvs:
    load_dotenv(find_dotenv("client.env"))
    envs_instance = ClientEnvs(
        test_username=os.getenv("TEST_USERNAME"),
        test_password=os.getenv("TEST_PASSWORD"),
    )
    allure.attach(envs_instance.model_dump_json(indent=2), name="client_envs.json", attachment_type=allure.attachment_type.JSON)
    return envs_instance

################# Fake data ####################

@pytest.fixture(scope="session")
def faker() -> Faker:
    faker = Faker()
    return faker