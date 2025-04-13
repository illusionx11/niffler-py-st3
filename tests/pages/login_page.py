from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from tests.pages.urls import Urls
from tests.utils.errors import ValidationErrors
from .base_page import BasePage


class LoginPage(BasePage):
    
    class Locators:
        LOGO_IMG = (By.CSS_SELECTOR, "img.logo-section__logo")
        LOGO_TEXT = (By.CSS_SELECTOR, "p.logo-section__text")
        LOGIN_FORM = (By.CSS_SELECTOR, "form[action='/login']")
        LOGIN_FORM_ERROR = (By.CSS_SELECTOR, "p.form__error")
        LOGIN_HEADER = (By.CSS_SELECTOR, "h1.header")
        USERNAME_INPUT = (By.CSS_SELECTOR, "input[name='username']")
        PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
        PASSWORD_VISIBILITY_BTN = (By.CSS_SELECTOR, "button.form__password-button")
        SUBMIT_BTN = (By.CSS_SELECTOR, "button.form__submit")
        REGISTER_BTN = (By.CSS_SELECTOR, "a.form__register")
        
    def log_in(self, username: str, password: str):
        self.open()
        self.should_be_login_page()
        self.browser.find_element(*LoginPage.Locators.USERNAME_INPUT).send_keys(username)
        self.browser.find_element(*LoginPage.Locators.PASSWORD_INPUT).send_keys(password)
        self.browser.find_element(*LoginPage.Locators.SUBMIT_BTN).click()
        
    def should_be_login_page(self):
        self.should_be_login_heading()
        self.should_be_login_form()
        self.should_be_login_button()
        self.should_be_login_url()
        
    def should_be_login_url(self):
        assert "login" in self.browser.current_url
    
    def should_be_login_heading(self):
        header = self.browser.find_element(*LoginPage.Locators.LOGIN_HEADER)
        assert header.is_displayed()
        assert header.text.lower() == "log in"
    
    def should_be_login_form(self):
        assert self.is_element_present(*LoginPage.Locators.LOGIN_FORM)
    
    def should_be_login_button(self):
        assert self.is_element_present(*LoginPage.Locators.SUBMIT_BTN)

    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]]):
        if "login" in errors and len(errors["login"]) > 0:
            login_error = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(LoginPage.Locators.LOGIN_FORM_ERROR))
            for error_text in errors["login"]:
                assert error_text in login_error.text