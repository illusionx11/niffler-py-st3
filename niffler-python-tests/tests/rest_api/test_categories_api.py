import pytest
import allure
from utils.allure_data import Epic, Feature, Story
from clients.spends_client import SpendsClient
from marks import TestData

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]
            
@pytest.mark.usefixtures(
    "auth_api_token",
    "spends_client",
    "all_categories"
)
@pytest.mark.api
@pytest.mark.profile
@pytest.mark.categories
@allure.feature(Feature.categories)
class TestCategoriesAPI:
    
    @pytest.mark.xdist_group("02_category")
    @TestData.new_category(["UniqueCategory1"])
    @allure.story(Story.add_category)
    def test_add_new_category(self, spends_client: SpendsClient, new_category: str):
        category_data = spends_client.add_category(new_category)
        with allure.step("Проверка, что категория добавлена"):
            assert category_data.name == new_category
            assert category_data.archived == False
            assert category_data.username == spends_client.client_envs.test_username
    
    @pytest.mark.xdist_group("02_category")
    @TestData.category(["UniqueCategory2"])
    @allure.story(Story.add_category)
    def test_add_existing_category(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.add_category(category)
        with allure.step("Проверка, что категория не добавлена"):
            assert isinstance(category_data, dict)
            assert category_data["status"] == 409
            assert category_data["title"] == "Conflict"
            assert category_data["detail"] == "Cannot save duplicates"
            assert category_data["instance"] == spends_client.ADD_CATEGORY_ENDPOINT
            assert category_data["type"] == "niffler-spend: Bad request "
            
    @TestData.archived_category(["UniqueArchivedCategory1"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.add_category)
    def test_add_existing_archived_category(self, spends_client: SpendsClient, archived_category: str):
        category_data = spends_client.add_category(archived_category)
        with allure.step("Проверка, что категория не добавлена"):
            assert category_data["status"] == 409
            assert category_data["title"] == "Conflict"
            assert category_data["detail"] == "Cannot save duplicates"
            assert category_data["instance"] == spends_client.ADD_CATEGORY_ENDPOINT
            assert category_data["type"] == "niffler-spend: Bad request "
    
    @pytest.mark.xdist_group("02_category")
    @TestData.category(["UniqueCategory3"])
    @allure.story(Story.update_category)
    def test_update_category_name(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.name = "UniqueUpdatedCategory3"
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == category_data.name
            assert updated_category_data.archived == category_data.archived
            assert updated_category_data.username == category_data.username
    
    @TestData.category(["UniqueCategory4"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.update_category)
    def test_update_category_archived(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.archived = True
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == category_data.name
            assert updated_category_data.archived == True
            assert updated_category_data.username == category_data.username
            
    @TestData.category(["UniqueCategory5"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.update_category)
    def test_update_category_name_and_archived(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.name = "UniqueUpdatedCategory5"
        category_data.archived = True
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == category_data.name
            assert updated_category_data.archived == True
            assert updated_category_data.username == category_data.username
            
    @allure.story(Story.get_category)
    @pytest.mark.xdist_group("02_category")
    def test_get_active_categories(self, spends_client: SpendsClient, mixed_categories: dict[str, list[str]]):
        active_categories = spends_client.get_all_categories(exclude_archived=True)
        with allure.step("Проверка, что активные категории получены"):
            for category_id in mixed_categories["active"]:
                assert category_id in [cat.id for cat in active_categories]
    
    @allure.story(Story.get_category)
    @pytest.mark.xdist_group("02_category")
    def test_get_all_categories(self, spends_client: SpendsClient, mixed_categories: dict[str, list[str]]):
        all_categories = spends_client.get_all_categories()
        with allure.step("Проверка, что все категории получены"):
            for category_id in mixed_categories["active"] + mixed_categories["archived"]:
                assert category_id in [cat.id for cat in all_categories]
    