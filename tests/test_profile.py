import pytest
import logging
import time
import allure
from tests.models.spend import Category
from tests.utils.niffler_api import NifflerAPI
from tests.pages.profile_page import ProfilePage
from tests.utils.errors import ValidationErrors
from tests.conftest import TestData
from tests.models.config import Envs
from tests.utils.niffler_api import NifflerAPI
from tests.databases.spends_db import SpendsDb
from tests.allure_data import Epic, Feature, Story

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.fixture(scope="function")
def archived_categories(niffler_api: NifflerAPI):
    archived_categories = ["ArchivedCategory1", "ArchivedCategory2", "ArchivedCategory3"]
    for category_name in archived_categories:
        category_data = niffler_api.add_category(category_name)
        category_data.archived = True
        niffler_api.update_category(category_data)
    return archived_categories

@pytest.mark.usefixtures(
    "profile_page",
    "cleanup",
    "all_categories"
)
@pytest.mark.profile
@pytest.mark.categories
@allure.feature(Feature.categories)
class TestProfileCategories:

    @TestData.direct_category(["NewCategory1", "NewCategory2", "NewCategory3"])
    @allure.story(Story.add_category)
    def test_add_new_category(self, profile_page: ProfilePage, direct_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(direct_category)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_new_active_category(direct_category)
    
    @TestData.category(["DuplicateCategory"])
    @allure.story(Story.errors)
    def test_add_duplicate_category(self, profile_page: ProfilePage, category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        logging.info(f"category: {category}")
        profile_page.add_new_category(category)
        errors = {
            "category": [ValidationErrors.CATEGORY_DUPLICATE.format(category_name=category)]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.archived_category(["DuplicateArchivedCategory"])
    @allure.story(Story.errors)
    def test_add_duplicate_archived_category(self, profile_page: ProfilePage, archived_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(archived_category)
        errors = {
            "category": [ValidationErrors.CATEGORY_DUPLICATE.format(category_name=archived_category)]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
    
    @TestData.category(["DuplicateCategory"])
    @allure.story(Story.errors)
    def test_duplicate_category_alert_elements(self, profile_page: ProfilePage, category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(category)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_duplicate_category_alert_elements(
            alert_text=ValidationErrors.CATEGORY_DUPLICATE.format(category_name=category)
        )
    
    @TestData.category(["ChangeMyNameWithIcon"])
    @allure.story(Story.update_category)
    def test_change_category_name_with_icon(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithIcon"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="icon", old_name=category, new_name=new_name)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
        
    @TestData.category(["ChangeMyNameWithClick"])    
    @allure.story(Story.update_category)
    def test_change_category_name_with_click(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithClick"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="click", old_name=category, new_name=new_name)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
    
    @TestData.direct_category(["a", pytest.param("a"*51, marks=pytest.mark.xfail(reason="Появляется сайдбар вместо сообщения под input"))])
    @allure.story(Story.errors)
    def test_add_incorrect_category(self, profile_page: ProfilePage, direct_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(direct_category)
        errors = {
            "category_length": [ValidationErrors.CATEGORY_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.display_category)
    def test_show_archived_categories(self, profile_page: ProfilePage, archived_categories: list):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.show_archived_categories()
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_archived_categories(archived_categories)

@pytest.mark.usefixtures(
    "profile_page",
)
@pytest.mark.profile
@pytest.mark.profile_data
@allure.feature(Feature.user_profile)
class TestProfileData:
    
    @TestData.profile_name(["Testname", "Имя", "Andrew"])
    @allure.story(Story.update_profile)
    def test_set_new_profile_name(self, profile_page: ProfilePage, profile_name: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        profile_page.open()
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_new_profile_name(profile_name)
        
    @TestData.profile_name(["a"*51])
    @allure.story(Story.errors)
    def test_profile_name_validation(self, profile_page: ProfilePage, profile_name: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        errors = {
            "profile_name": [ValidationErrors.PROFILE_NAME_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
        
@pytest.mark.usefixtures(
    "cleanup",
    "niffler_api",
    "spends_db",
    "envs"
)
@pytest.mark.profile
@pytest.mark.categories_db
@allure.feature(Feature.categories)
class TestCategoriesDatabase:

    @TestData.direct_category(["UniqueCategory1"])
    @allure.story(Story.database)
    def test_added_category_in_database(
        self,
        niffler_api: NifflerAPI,
        envs: Envs,
        spends_db: SpendsDb,
        direct_category: str
    ):
        niffler_api.add_category(direct_category)
        all_categories = spends_db.get_user_categories(username=envs.test_username)
        category = next((c for c in all_categories if c.name == direct_category), None)
        with allure.step("Проверка, что категория добавлена в базу данных"):
            assert category is not None
        
    @TestData.direct_category(["UniqueCategory2"])
    @allure.story(Story.database)
    def test_updated_category_in_database(
        self,
        niffler_api: NifflerAPI,
        envs: Envs,
        spends_db: SpendsDb,
        direct_category: str
    ):
        added_category_data = niffler_api.add_category(direct_category)
        new_category_name = "UniqueUpdatedCategory2"
        added_category_data.name = new_category_name
        new_category_archived = True
        added_category_data.archived = new_category_archived
        niffler_api.update_category(category_data=added_category_data)
        all_categories = spends_db.get_user_categories(username=envs.test_username)
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