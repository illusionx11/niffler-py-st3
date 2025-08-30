from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.errors import ValidationErrors
from pages.base_page import BasePage
import allure
import time

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
    
    @allure.step("Проверка на валидность страницы профиля")
    def should_be_profile_page(self):
        self.should_be_element(self.PROFILE_HEADING)
        self.should_be_element(self.CATEGORIES_HEADING)
        self.should_be_element(self.ADD_CATEGORY_INPUT)
        self.should_be_url("profile")
    
    @allure.step("Добавление новой категории")
    def add_new_category(self, name: str):
        category_input = self.browser.find_element(*self.ADD_CATEGORY_INPUT)
        self.clear_input(category_input)
        category_input.send_keys(name)
        category_input.send_keys(Keys.RETURN)
    
    @allure.step("Проверка наличия новой активной категории")
    def should_be_new_active_category(self, name: str):
        def check_category_present():
            active_categories = self.get_all_elements_presence_with_attributes_safe(
                self.ALL_CATEGORY_NAMES, "tabindex", "0"
            )
            category_names = []
            for c in active_categories:
                category_names.append(c.text)
            return name in category_names
        
        max_attempts = 3
        for attempt in range(max_attempts):
            if check_category_present():
                return
            if attempt < max_attempts - 1:
                time.sleep(0.3)
        
        raise AssertionError(f"Категория '{name}' не найдена среди активных категорий")
    
    @allure.step("Изменение имени профиля")
    def set_new_profile_name(self, name: str):
        name_input = self.get_element_presence_safe(self.PROFILE_NAME_INPUT)
        self.clear_input(name_input)
        name_input.send_keys(name)
        self.browser.find_element(*self.SUBMIT_PROFILE_DATA_BTN).click()
    
    @allure.step("Проверка наличия нового имени профиля") 
    def should_be_new_profile_name(self, name: str):
        name_input = self.get_element_presence_safe(self.PROFILE_NAME_INPUT)
        assert name == name_input.get_attribute("value"), \
            f"Имя профиля '{name}' не соответствует '{name_input.get_attribute('value')}'"
    
    @allure.step("Проверка на наличие ошибок валидации")
    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]], name: str = None):
        key = None
        if "profile_name" in errors and len(errors["profile_name"]) > 0:
            profile_name_error = self.get_element_presence_safe(
                (By.CSS_SELECTOR, "input#name ~ span.input__helper-text")
            )
            element_text = profile_name_error.text
            key = "profile_name"
        
        if "category_duplicate" in errors and len(errors["category_duplicate"]) > 0:
            duplicate_category_alert = self.get_element_presence_safe(
                (By.CSS_SELECTOR, "div[role='alert']")
            )
            element = duplicate_category_alert.find_element(By.CSS_SELECTOR, "div.MuiAlert-message div")
            element_text = element.text
            key = "category_duplicate"
                
        if "category_length" in errors and len(errors["category_length"]) > 0:
            category_error = self.get_element_presence_safe(
                (By.CSS_SELECTOR, "input#category ~ span.input__helper-text")
            )
            element_text = category_error.text
            key = "category_length"
            
        for error_text in errors[key]:
            assert error_text.lower() in element_text.lower(), f"Error text '{error_text}' not in '{element_text}'"
            if name:
                assert name in element_text, f"Name '{name}' not in '{element_text}' for key '{key}'"
    
    @allure.step("Проверка на наличие предупреждения о дубликате категории")
    def should_be_duplicate_category_alert_elements(self, alert_text: str, name: str = None):
        self.should_be_element(self.DUPLICATE_CATEGORY_ALERT_ICON)
        self.should_be_element(self.DUPLICATE_CATEGORY_ALERT_CLOSE_BTN)
        element_text = self.get_element_presence_safe(self.DUPLICATE_CATEGORY_ALERT).text
        assert alert_text in element_text, f"Alert text '{alert_text}' not in '{element_text}'"
        if name:
            assert name in element_text, f"Name '{name}' not in '{element_text}'"
    
    @allure.step("Изменение имени категории")
    def change_category_name(self, by: str, old_name: str, new_name: str):
        all_categories = self.browser.find_elements(*self.ALL_CATEGORY_NAMES)
        category = [c for c in all_categories if c.text == old_name][0]
        if by == "icon":
            category_parent = category.find_element(By.XPATH, "..")
            edit_icon = category_parent.find_element(By.CSS_SELECTOR, "button[aria-label='Edit category']")
            edit_icon.click()
        elif by == "click":
            category.click()
            
        edit_category_input = self.browser.find_element(*self.EDIT_CATEGORY_INPUT)
        self.clear_input(edit_category_input)
        edit_category_input.send_keys(new_name)
        edit_category_input.send_keys(Keys.RETURN)
    
    @allure.step("Проверка на отсутствие категории")
    def should_be_no_category(self, name: str):
        all_categories_names = self.get_all_elements_presence_with_text_safe(self.ALL_CATEGORY_NAMES)
        assert name not in all_categories_names
    
    @allure.step("Показ архивных категорий")
    def show_archived_categories(self):
        self.browser.find_element(*self.SHOW_ARCHIVED_BTN).click()
    
    @allure.step("Проверка наличия архивных категорий")
    def should_be_archived_categories(self, archived_categories: list[str]):
        all_categories = self.get_all_elements_presence_safe(self.ALL_CATEGORY_NAMES)
        archived_categories_names = [c.text for c in all_categories if c.get_attribute("tabindex") == "-1"]
        for cat_name in archived_categories:
            assert cat_name in archived_categories_names