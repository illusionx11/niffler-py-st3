import pytest
from models.config import ClientEnvs
from faker import Faker
import random
from utils.mock_data import MockData
from models.spend import SpendAdd, SpendGet
from models.category import Category, CategoryAdd
from clients.spends_client import SpendsClient
from databases.spends_db import SpendsDb
import logging
from pytest import FixtureRequest
from utils.generate_datetime import generate_random_datetime

################# For spending tests ####################

@pytest.fixture(scope="session")
def spendings_data(client_envs: ClientEnvs):
    faker = Faker()
    spendings = []
    for _ in range(10):
        amount = faker.random_number(digits=3)
        category_name = random.choice(MockData.CATEGORIES)
        currency = random.choice(MockData.CURRENCIES)
        description = faker.sentence(nb_words=2, variable_nb_words=True)
        spend_date = generate_random_datetime()
        data = SpendAdd(
            amount=amount,
            category=CategoryAdd(name=category_name),
            currency=currency,
            description=description,
            spendDate=spend_date,
            username=client_envs.test_username
        )
        spendings.append(data)
        
    return spendings

@pytest.fixture(scope="class")
def add_spendings(spends_client: SpendsClient, spendings_data: list[SpendAdd]):
    all_spendings = spends_client.get_all_spendings()
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
        spends_client.add_spending(data)
    yield
    
@pytest.fixture
def spendings_list(spends_client: SpendsClient) -> list[SpendGet]:
    return spends_client.get_all_spendings()

################# For profile tests ####################

@pytest.fixture(scope="class")
def cleanup(spends_client: SpendsClient, client_envs: ClientEnvs, spends_db: SpendsDb):
    spends_client.clear_spendings()
    spends_db.delete_user_categories(username=client_envs.test_username)
    logging.info("Cleanup before tests ended")
    yield
    spends_client.clear_spendings()
    spends_db.delete_user_categories(username=client_envs.test_username)
    logging.info("Cleanup after teardown ended")

@pytest.fixture
def clear_categories(client_envs: ClientEnvs, spends_db: SpendsDb):
    yield
    spends_db.delete_user_categories(username=client_envs.test_username)

@pytest.fixture(scope="function")
def all_categories(spends_client: SpendsClient):
    return spends_client.get_all_categories()

@pytest.fixture(params=[])
def category(request: FixtureRequest, spends_client: SpendsClient, spends_db: SpendsDb):
    category_name = request.param
    category_data = spends_client.add_category(category_name)
    yield category_name
    spends_db.delete_category(category_data.id)
    
@pytest.fixture(params=[])
def archived_category(request: FixtureRequest, spends_client: SpendsClient, all_categories: list[Category], spends_db: SpendsDb):
    category_name = request.param
    active_category = next((c for c in all_categories if c.name == category_name and c.archived == False), None)
    if not active_category:
        active_category = spends_client.add_category(category_name)
    active_category.archived = True
    spends_client.update_category(active_category)
    yield category_name
    spends_db.delete_category(active_category.id)
    
@pytest.fixture(scope="function")
def new_archived_categories(spends_client: SpendsClient, spends_db: SpendsDb):
    archived_categories = ["ArchivedCategory1", "ArchivedCategory2", "ArchivedCategory3"]
    categories = []
    for category_name in archived_categories:
        category_data = spends_client.add_category(category_name)
        category_data.archived = True
        spends_client.update_category(category_data)
        categories.append(category_data.id)
    yield archived_categories
    for cat_id in categories:
        spends_db.delete_category(cat_id)

@pytest.fixture(scope="function")
def mixed_categories(spends_client: SpendsClient, spends_db: SpendsDb):
    active_categories = [f"UniqueNewActiveCat{i}" for i in range(3)]
    archived_categories = [f"UniqueNewArchivedCat{i}" for i in range(3)]
    categories = {
        "active": [],
        "archived": []
    }
    for category_name in active_categories:
        active_category_data = spends_client.add_category(category_name)
        categories["active"].append(active_category_data.id)
    for category_name in archived_categories:
        archived_category_data = spends_client.add_category(category_name)
        archived_category_data.archived = True
        spends_client.update_category(archived_category_data)
        categories["archived"].append(archived_category_data.id)
    logging.info(f"Active categories: {categories['active']}, archived categories: {categories['archived']}")
    yield categories
    for cat_id in categories["active"]+categories["archived"]:
        spends_db.delete_category(cat_id)