from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from tests.utils.errors import ValidationErrors
from .base_page import BasePage

class RegisterPage(BasePage):
    
    LOGO_IMG = (By.CSS_SELECTOR, "img.logo-section__logo")
    LOGO_TEXT = (By.CSS_SELECTOR, "p.logo-section__text")
    REGISTER_HEADER = (By.CSS_SELECTOR, "h1.header")
    REGISTER_FORM = (By.CSS_SELECTOR, "form#register-form")
    USERNAME_INPUT = (By.CSS_SELECTOR, "input#username")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input#password")
    PASSWORD_VISIBILITY_BTN = (By.CSS_SELECTOR, "button#passwordBtn")
    PASSWORD_REPEAT_INPUT = (By.CSS_SELECTOR, "input#passwordSubmit")
    PASSWORD_REPEAT_VISIBILITY_BTN = (By.CSS_SELECTOR, "button#passwordSubmitBtn")
    SUBMIT_BTN = (By.CSS_SELECTOR, "button.form__submit")
    LOGIN_BTN = (By.CSS_SELECTOR, "a.form__link")
    REGISTER_SUCCESS_HEADER = (By.CSS_SELECTOR, "p.form__paragraph_success")
    REGISTER_SUCCESS_LOGIN_BTN = (By.CSS_SELECTOR, "a.form_sign-in")
        
    def should_be_register_page(self):
        self.should_be_register_heading()
        self.should_be_element(RegisterPage.REGISTER_FORM)
        self.should_be_element(RegisterPage.PASSWORD_REPEAT_INPUT)
        self.should_be_element(RegisterPage.SUBMIT_BTN)
        self.should_be_url("register")
        
    def should_be_register_heading(self):
        header = self.browser.find_element(*RegisterPage.REGISTER_HEADER)
        assert header.is_displayed()
        assert header.text.lower() == "sign up"
        
    def register_user(self, username: str, password: str, password_repeat: str | None = None):
        username_input = self.browser.find_element(*RegisterPage.USERNAME_INPUT)
        username_input.send_keys(username)
        password_input = self.browser.find_element(*RegisterPage.PASSWORD_INPUT)
        password_input.send_keys(password)
        password_repeat_input = self.browser.find_element(*RegisterPage.PASSWORD_REPEAT_INPUT)
        if password_repeat is None:
            password_repeat = password
        password_repeat_input.send_keys(password_repeat)
        self.browser.find_element(*RegisterPage.SUBMIT_BTN).click()
    
    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]]):
        if "username" in errors and len(errors["username"]) > 0:
            username_input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(RegisterPage.USERNAME_INPUT))
            username_parent = username_input.find_element(By.XPATH, "..")
            username_error = username_parent.find_element(By.CSS_SELECTOR, "span.form__error")
            for error_text in errors["username"]:
                assert error_text in username_error.text
        
        if "password" in errors and len(errors["password"]) > 0:
            password_input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(RegisterPage.PASSWORD_INPUT))
            password_parent = password_input.find_element(By.XPATH, "..")
            password_error = password_parent.find_element(By.CSS_SELECTOR, "span.form__error")
            for error_text in errors["password"]:
                assert error_text in password_error.text
        
        if "password_repeat" in errors and len(errors["password_repeat"]) > 0:
            password_repeat_input = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(RegisterPage.PASSWORD_REPEAT_INPUT))
            password_repeat_parent = password_repeat_input.find_element(By.XPATH, "..")
            password_repeat_error = password_repeat_parent.find_element(By.CSS_SELECTOR, "span.form__error")
            for error_text in errors["password_repeat"]:
                assert error_text in password_repeat_error.text
                
    def should_be_successful_registration(self):
        assert self.is_element_present(*RegisterPage.REGISTER_SUCCESS_HEADER)
        assert self.is_element_present(*RegisterPage.REGISTER_SUCCESS_LOGIN_BTN)