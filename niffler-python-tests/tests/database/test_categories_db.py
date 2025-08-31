import pytest
import allure
from utils.allure_data import Epic, Feature, Story
from models.config import ClientEnvs
from clients.spends_client import SpendsClient
from databases.spends_db import SpendsDb
from marks import TestData

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "token_data",
    "spends_client",
    "spends_db",
    "client_envs"
)
@pytest.mark.profile
@pytest.mark.database
@allure.feature(Feature.categories)
class TestCategoriesDatabase:

    @TestData.new_category(["UniqueDatabaseCategory1"])
    @allure.story(Story.add_category)
    def test_added_category_in_database(
        self,
        spends_client: SpendsClient,
        client_envs: ClientEnvs,
        spends_db: SpendsDb,
        new_category: str
    ):
        spends_client.add_category(new_category)
        all_categories = spends_db.get_user_categories(username=client_envs.test_username)
        category = next((c for c in all_categories if c.name == new_category), None)
        with allure.step("Проверка, что категория добавлена в базу данных"):
            assert category is not None
        
    @TestData.new_category(["UniqueDatabaseCategory2"])
    @allure.story(Story.update_category)
    def test_updated_category_in_database(
        self,
        spends_client: SpendsClient,
        client_envs: ClientEnvs,
        spends_db: SpendsDb,
        new_category: str
    ):
        added_category_data = spends_client.add_category(new_category)
        new_category_name = "UniqueUpdatedDatabaseCategory2"
        added_category_data.name = new_category_name
        new_category_archived = True
        added_category_data.archived = new_category_archived
        spends_client.update_category(category_data=added_category_data)
        all_categories = spends_db.get_user_categories(username=client_envs.test_username)
        # c.id это UUID-объект
        category = next(
            (
                c for c in all_categories if str(c.id) == added_category_data.id \
                and c.name == new_category_name \
                and c.archived == new_category_archived
            ), 
            None
        )
        with allure.step("Проверка, что категория обновлена в базе данных"):
            assert category is not None