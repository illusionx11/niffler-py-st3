from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tests.models.spend import Spend
from tests.utils.errors import ValidationErrors
from .base_page import BasePage

class ProfilePage(BasePage):
    
    LOGO_IMG = (By.CSS_SELECTOR, "img[alt='Niffler logo]")
    LOGO_TEXT = (By.CSS_SELECTOR, "a.link[href='/main'] h1")
    ADD_SPENDING_BTN = (By.CSS_SELECTOR, "a[href='/spending']")
    PROFILE_BTN = (By.CSS_SELECTOR, "button[aria-label='Menu']")
    PROFILE_HEADING = (By.XPATH, "//h2[contains(text(), 'Profile')]")
    UPLOAD_PICTURE_BTN = (By.CSS_SELECTOR, "span[role='button']")
    USERNAME_INPUT = (By.CSS_SELECTOR, "input#username")
    USERNAME_LABEL = (By.CSS_SELECTOR, "label[for='username']")
    PROFILE_NAME_INPUT = (By.CSS_SELECTOR, "input#name")
    PROFILE_NAME_LABEL = (By.CSS_SELECTOR, "label[for='name']")
    SUBMIT_PROFILE_DATA_BTN = (By.CSS_SELECTOR, "button[type='submit']")
    CATEGORIES_HEADING = (By.XPATH, "//h2[contains(text(), 'Categories')]")
    SHOW_ARCHIVED_BTN = (By.CSS_SELECTOR, "label.MuiFormControlLabel-root")
    ADD_CATEGORY_INPUT = (By.CSS_SELECTOR, "input[placeholder='Add new category']")
    EDIT_CATEGORY_INPUT = (By.CSS_SELECTOR, "input[placeholder='Edit category']")
    ALL_CATEGORY_NAMES = (By.CSS_SELECTOR, "div[role='button']")
    #UNARCHIVE_CATEGORY_BTNS = (By.CSS_SELECTOR, "span[aria-label='Unarchive category']")
    DUPLICATE_CATEGORY_ALERT = (By.CSS_SELECTOR, "div[role='alert']")
    DUPLICATE_CATEGORY_ALERT_ICON = (By.CSS_SELECTOR, "svg[data-testid='ErrorOutlineIcon']")
    DUPLICATE_CATEGORY_ALERT_CLOSE_BTN = (By.CSS_SELECTOR, "button[title='Close']")
        
    def should_be_profile_page(self):
        self.should_be_element(ProfilePage.PROFILE_HEADING)
        self.should_be_element(ProfilePage.CATEGORIES_HEADING)
        self.should_be_element(ProfilePage.ADD_CATEGORY_INPUT)
        self.should_be_url("profile")
    
    def add_new_category(self, name: str):
        category_input = self.browser.find_element(*ProfilePage.ADD_CATEGORY_INPUT)
        self.clear_input(category_input)
        category_input.send_keys(name)
        category_input.send_keys(Keys.RETURN)
        
    def should_be_new_active_category(self, name: str):
        all_categories = self.browser.find_elements(*ProfilePage.ALL_CATEGORY_NAMES)
        active_categories = [c for c in all_categories if c.get_attribute("tabindex") == "0"]
        assert name in [c.text for c in active_categories]
        
    def set_new_profile_name(self, name: str):
        name_input = self.browser.find_element(*ProfilePage.PROFILE_NAME_INPUT)
        self.clear_input(name_input)
        name_input.send_keys(name)
        self.browser.find_element(*ProfilePage.SUBMIT_PROFILE_DATA_BTN).click()
        
    def should_be_new_profile_name(self, name: str):
        name_label = self.browser.find_element(*ProfilePage.PROFILE_NAME_INPUT)
        assert name == name_label.get_attribute("value")
    
    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]]):
        if "profile_name" in errors and len(errors["profile_name"]) > 0:
            profile_name_input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(ProfilePage.PROFILE_NAME_INPUT))
            profile_name_parent = profile_name_input.find_element(By.XPATH, "..")
            profile_name_error = profile_name_parent.find_element(By.CSS_SELECTOR, "span.input__helper-text")
            for error_text in errors["profile_name"]:
                assert error_text in profile_name_error.text
        
        if "category_duplicate" in errors and len(errors["category_duplicate"]) > 0:
            duplicate_category_alert = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(ProfilePage.DUPLICATE_CATEGORY_ALERT))
            for error_text in errors["category_duplicate"]:
                assert error_text in duplicate_category_alert.text
                
        if "category_length" in errors and len(errors["category_length"]) > 0:
            category_input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(ProfilePage.ADD_CATEGORY_INPUT))
            category_parent = category_input.find_element(By.XPATH, "..")
            category_error = category_parent.find_element(By.CSS_SELECTOR, "span.input__helper-text")
            for error_text in errors["category_length"]:
                assert error_text in category_error.text
    
    def should_be_duplicate_category_alert_elements(self, alert_text: str):
        self.should_be_element(ProfilePage.DUPLICATE_CATEGORY_ALERT)
        self.should_be_element(ProfilePage.DUPLICATE_CATEGORY_ALERT_ICON)
        self.should_be_element(ProfilePage.DUPLICATE_CATEGORY_ALERT_CLOSE_BTN)
        assert alert_text in self.browser.find_element(*ProfilePage.DUPLICATE_CATEGORY_ALERT).text
        
    def change_category_name(self, by: str, old_name: str, new_name: str):
        all_categories = self.browser.find_elements(*ProfilePage.ALL_CATEGORY_NAMES)
        category = [c for c in all_categories if c.text == old_name][0]
        if by == "icon":
            category_parent = category.find_element(By.XPATH, "..")
            edit_icon = category_parent.find_element(By.CSS_SELECTOR, "button[aria-label='Edit category']")
            edit_icon.click()
        elif by == "click":
            category.click()
            
        edit_category_input = self.browser.find_element(*ProfilePage.EDIT_CATEGORY_INPUT)
        self.clear_input(edit_category_input)
        edit_category_input.send_keys(new_name)
        edit_category_input.send_keys(Keys.RETURN)
        
    def should_be_no_category(self, name: str):
        all_categories = self.browser.find_elements(*ProfilePage.ALL_CATEGORY_NAMES)
        assert name not in [c.text for c in all_categories]
        
    def show_archived_categories(self):
        self.browser.find_element(*ProfilePage.SHOW_ARCHIVED_BTN).click()
    
    def should_be_archived_categories(self, archived_categories: list[str]):
        all_categories = self.browser.find_elements(*ProfilePage.ALL_CATEGORY_NAMES)
        archived_categories_names = [c.text for c in all_categories if c.get_attribute("tabindex") == "-1"]
        assert archived_categories_names == archived_categories