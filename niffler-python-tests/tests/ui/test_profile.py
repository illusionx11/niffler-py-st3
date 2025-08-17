import pytest
import logging
import allure
from pages.profile_page import ProfilePage
from utils.errors import ValidationErrors
from marks import TestData
from utils.allure_data import Epic, Feature, Story
import time

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_front_token",
    "profile_page",
    "all_categories"
)
@pytest.mark.ui
@pytest.mark.profile
@pytest.mark.categories
@allure.feature(Feature.categories)
class TestProfileCategories:

    @TestData.new_category(["NewCategory1"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.add_category)
    def test_add_new_category(self, profile_page: ProfilePage, new_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(new_category)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_new_active_category(new_category)
    
    @TestData.category(["DuplicateCategory"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.add_category)
    def test_add_duplicate_category(self, profile_page: ProfilePage, category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        logging.info(f"category: {category}")
        profile_page.add_new_category(category)
        errors = {
            "category_duplicate": [ValidationErrors.CATEGORY_DUPLICATE]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_errors_in_validation(errors=errors, name=category)
    
    @TestData.archived_category(["DuplicateArchivedCategory"])
    @pytest.mark.xdist_group("03_archived_category")
    @allure.story(Story.add_category)
    def test_add_duplicate_archived_category(self, profile_page: ProfilePage, archived_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(archived_category)
        errors = {
            "category_duplicate": [ValidationErrors.CATEGORY_DUPLICATE]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_errors_in_validation(errors=errors, name=archived_category)
    
    @TestData.category(["DuplicateCategoryNifflerUnique"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.add_category)
    def test_duplicate_category_alert_elements(self, profile_page: ProfilePage, category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(category)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_duplicate_category_alert_elements(
            alert_text=ValidationErrors.CATEGORY_DUPLICATE,
            name=category
        )
    
    @TestData.category(["ChangeMyNameWithIcon"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.update_category)
    def test_change_category_name_with_icon(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithIcon"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="icon", old_name=category, new_name=new_name)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
        
    @TestData.category(["ChangeMyNameWithClick"])
    @pytest.mark.xdist_group("02_category")
    @allure.story(Story.update_category)
    def test_change_category_name_with_click(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithClick"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="click", old_name=category, new_name=new_name)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
    
    @TestData.new_category([
        "a", 
        pytest.param("a"*51, marks=pytest.mark.xfail(
            reason="Появляется сайдбар вместо сообщения под input"
        ))
    ])
    @allure.story(Story.add_category)
    def test_add_incorrect_category(self, profile_page: ProfilePage, new_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(new_category)
        errors = {
            "category_length": [ValidationErrors.CATEGORY_LENGTH]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.display_category)
    @pytest.mark.xdist_group("03_archived_category")
    def test_show_archived_categories(self, profile_page: ProfilePage, new_archived_categories: list):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.show_archived_categories()
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_archived_categories(new_archived_categories)

@pytest.mark.usefixtures(
    "auth_front_token",
    "profile_page",
)
@pytest.mark.profile
@pytest.mark.profile_data
@allure.feature(Feature.user_profile)
@allure.story(Story.update_profile)
class TestProfileData:
    
    @TestData.profile_name(["Testname", "Имя", "Andrew"])
    def test_set_new_profile_name(self, profile_page: ProfilePage, profile_name: str, profile_name_lock):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        profile_page.open()
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_new_profile_name(profile_name)
        
    @TestData.profile_name(["a"*51])
    def test_profile_name_validation(self, profile_page: ProfilePage, profile_name: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        errors = {
            "profile_name": [ValidationErrors.PROFILE_NAME_LENGTH]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        profile_page.should_be_errors_in_validation(errors=errors)