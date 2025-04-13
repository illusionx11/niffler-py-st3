import pytest
import logging
import time
from tests.utils.niffler_api import NifflerAPI
from tests.pages.profile_page import ProfilePage
from tests.utils.errors import ValidationErrors
from tests.conftest import TestData

@pytest.mark.usefixtures(
    "profile_page",
    "create_qa_user",
    "initialize",
    "all_categories"
)
@pytest.mark.profile
class TestProfilePage:

    @TestData.direct_category(["NewCategory1", "NewCategory2", "NewCategory3"])
    def test_add_new_category(self, profile_page: ProfilePage, direct_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(direct_category)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_new_active_category(direct_category)
    
    @TestData.category(["DuplicateCategory"])
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
    def test_duplicate_category_alert_elements(self, profile_page: ProfilePage, category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(category)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_duplicate_category_alert_elements(
            alert_text=ValidationErrors.CATEGORY_DUPLICATE.format(category_name=category)
        )
    
    @TestData.category(["ChangeMyNameWithIcon"])
    def test_change_category_name_with_icon(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithIcon"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="icon", old_name=category, new_name=new_name)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
        
    @TestData.category(["ChangeMyNameWithClick"])    
    def test_change_category_name_with_click(self, profile_page: ProfilePage, category: str):
        new_name = "NameChangedWithClick"
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.change_category_name(by="click", old_name=category, new_name=new_name)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_no_category(category)
        profile_page.should_be_new_active_category(new_name)
    
    @TestData.direct_category(["a", pytest.param("a"*51, marks=pytest.mark.xfail(reason="Появляется сайдбар вместо сообщения под input"))])
    def test_add_incorrect_category(self, profile_page: ProfilePage, direct_category: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.add_new_category(direct_category)
        errors = {
            "category_length": [ValidationErrors.CATEGORY_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
        
    @TestData.profile_name(["Testname", "Имя", "Andrew"])
    def test_set_new_profile_name(self, profile_page: ProfilePage, profile_name: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        profile_page.open()
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_new_profile_name(profile_name)
        
    @TestData.profile_name(["a"*51])
    def test_profile_name_validation(self, profile_page: ProfilePage, profile_name: str):
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.set_new_profile_name(profile_name)
        errors = {
            "profile_name": [ValidationErrors.PROFILE_NAME_LENGTH]
        }
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_errors_in_validation(errors=errors)
    
    def test_show_archived_categories(self, profile_page: ProfilePage, all_categories: list[dict]):
        archived_categories = [c["name"] for c in all_categories if c["archived"] == True]
        profile_page.open()
        profile_page.should_be_profile_page()
        profile_page.show_archived_categories()
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        profile_page.should_be_archived_categories(archived_categories)
        
