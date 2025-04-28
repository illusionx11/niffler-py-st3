import logging
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from utils.errors import ValidationErrors
from .base_page import BasePage
import allure

class LoginPage(BasePage):
    
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
    
    @allure.step("Авторизация в сервис")
    def log_in(self, username: str, password: str):
        self.open()
        self.should_be_login_page()
        logging.info(f"Logging in as {username}")
        self.browser.find_element(*self.USERNAME_INPUT).send_keys(username)
        logging.info(f"Password: {password}")
        self.browser.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.browser.find_element(*self.SUBMIT_BTN).click()
    
    @allure.step("Проверка на валидность страницы авторизации")
    def should_be_login_page(self):
        self.should_be_login_heading()
        self.should_be_element(self.LOGIN_FORM)
        self.should_be_element(self.SUBMIT_BTN)
        self.should_be_url("login")
    
    @allure.step("Проверка на наличие заголовка авторизации")
    def should_be_login_heading(self):
        header = self.browser.find_element(*self.LOGIN_HEADER)
        assert header.is_displayed()
        assert header.text.lower() == "log in"

    @allure.step("Проверка на наличие ошибок валидации")
    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]]):
        if "login" in errors and len(errors["login"]) > 0:
            login_error = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(self.LOGIN_FORM_ERROR))
            for error_text in errors["login"]:
                assert error_text in login_error.text