import pytest
from models.config import ClientEnvs
from models.category import Category
from clients.spends_client import SpendsClient
from databases.spends_db import SpendsDb
import logging
from pytest import FixtureRequest

################# For profile tests ####################

@pytest.fixture(scope="function")
def clear_categories(client_envs: ClientEnvs, spends_db: SpendsDb):
    yield
    spends_db.delete_user_categories(username=client_envs.test_username)

@pytest.fixture(scope="function")
def all_categories(spends_client: SpendsClient):
    return spends_client.get_all_categories()

@pytest.fixture(scope="function")
def new_category(request: FixtureRequest, spends_db: SpendsDb):
    """Только удаляет категорию, не добавляет"""
    category_name = request.param
    yield category_name
    spends_db.delete_category_by_name(category_name)

@pytest.fixture(scope="function")
def category(request: FixtureRequest, spends_client: SpendsClient, spends_db: SpendsDb):
    category_name = request.param
    category_data = spends_client.add_category(category_name)
    yield category_name
    spends_db.delete_category(category_data.id)
    
@pytest.fixture(scope="function")
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
    archived_categories = ["ArchivedCategory1", "ArchivedCategory2"]
    categories = []
    for category_name in archived_categories:
        category_data = spends_client.add_category(category_name)
        category_data.archived = True
        spends_client.update_category(category_data)
        categories.append(category_data.id)
    yield archived_categories
    for cat_id in categories:
        spends_db.delete_category(cat_id)

@pytest.fixture(scope="class")
def mixed_categories(spends_client: SpendsClient, spends_db: SpendsDb):
    active_categories = [f"UniqueNewActiveCat{i}" for i in range(2)]
    archived_categories = [f"UniqueNewArchivedCat{i}" for i in range(2)]
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