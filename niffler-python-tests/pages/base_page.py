from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, 
    ElementNotInteractableException, StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import allure
import logging
import time

class BasePage:
    def __init__(
        self, 
        browser: Chrome | Firefox | Safari | Edge | ChromiumEdge | Ie, 
        url: str,
        timeout: int = 4,
        
    ):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)
    
    @allure.step("Открыть страницу")
    def open(self):
        logging.info(f"Opening {self.url}")
        self.browser.get(self.url)

    @allure.step("Очистить поле input")
    def clear_input(self, element):
        WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable(element)
        )
        try:
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.BACKSPACE)
        except ElementNotInteractableException:
            self.browser.execute_script("arguments[0].value = '';", element)
    
    @allure.step("Проврека на присутствие элемента")
    def should_be_element(self, locator: tuple[str, str]):
        self.get_element_presence_safe(locator)
        assert True
    
    @allure.step("Проверка на наличие строки в URL")
    def should_be_url(self, arg: str):
        assert arg in self.browser.current_url
    
    @allure.step("Проверка на отсутствие объекта")
    def is_element_not_present(self, by, locator: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return True
        return False
    
    @allure.step("Проверка на исчезновение объекта")
    def is_element_disappeared(self, by, locator: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout, 1, TimeoutException).\
                until_not(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return False

        return True
    
    @allure.step("Получение access token через браузер")
    def get_access_token(self):
        return self.browser.execute_script("return localStorage.getItem('access_token');")
    
    @allure.step("Получение Web элемента")
    def get_element_presence_safe(self, locator: tuple[str, str], timeout: int = 10):
        for i in range(10):
            try:
                element = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
            except NoSuchElementException:
                raise
    
    @allure.step("Получение выбранных Web элементов")
    def get_all_elements_presence_safe(self, locator: tuple[str, str], timeout: int = 10):
        for i in range(10):
            try:
                elements = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_all_elements_located(locator)
                )
                return elements
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
            except NoSuchElementException:
                raise
            
    @allure.step("Получение кликабельного Web элемента")
    def get_element_clickable_safe(self, locator: tuple[str, str], timeout: int = 10):
        for i in range(10):
            try:
                element = WebDriverWait(self.browser, timeout).until(
                    EC.element_to_be_clickable(locator)
                )
                return element
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
            except NoSuchElementException:
                raise
    
    @allure.step("Получение выбранных Web элементов с атрибутами")
    def get_all_elements_presence_with_attributes_safe(
        self, locator: tuple[str, str], attribute: str, value: str, timeout: int = 10
    ):
        for i in range(10):
            try:
                elements = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_all_elements_located(locator)
                )
                elements = [e for e in elements if e.get_attribute(attribute) == value]
                return elements
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
            except NoSuchElementException:
                raise
            
    @allure.step("Получение выбранных Web элементов с текстом")
    def get_all_elements_presence_with_text_safe(self, locator: tuple[str, str], timeout: int = 10):
        for i in range(10):
            try:
                result = [
                    e.text for e in WebDriverWait(self.browser, timeout).until(
                        EC.presence_of_all_elements_located(locator)
                    )
                ]
                return result
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
            except NoSuchElementException:
                raise