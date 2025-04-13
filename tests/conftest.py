import pytest
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
from selenium import webdriver
from faker import Faker
from tests.utils.niffler_api import NifflerAPI
from selenium.webdriver.chrome.options import Options as ChromeOptions

QA_USERNAME = os.getenv("NIFFLER_QA_USERNAME")
QA_PASSWORD = os.getenv("NIFFLER_QA_PASSWORD")
    
@pytest.fixture(scope="session", autouse=True)
def niffler_api():
    api: NifflerAPI = NifflerAPI()
    yield api
    api.session.close()

@pytest.fixture(scope="session", autouse=True)
def create_qa_user(niffler_api: NifflerAPI):
    niffler_api.register(QA_USERNAME, QA_PASSWORD)
    
@pytest.fixture(scope="class")
def browser():
    options = ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()
    
