from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import allure

class BasePage:
    def __init__(self, browser: Chrome | Firefox | Safari | Edge | ChromiumEdge | Ie, url: str, timeout: int = 4):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)
    
    @allure.step("Открыть страницу")
    def open(self):
        self.browser.get(self.url)

    @allure.step("Очистить поле input")
    def clear_input(self, element):
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
    
    @allure.step("Проврека на присутствие элемента")
    def should_be_element(self, locator: tuple[str, str]):
        assert self.is_element_present(*locator)
    
    @allure.step("Проверка на наличие строки в URL")
    def should_be_url(self, arg: str):
        assert arg in self.browser.current_url
    
    @allure.step("Проверка на наличие объекта")
    def is_element_present(self, by, locator: str) -> bool:
        try:
            self.browser.find_element(by, locator)     
        except NoSuchElementException:
            return False
        return True   
    
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
    
    @allure.step("Получение access_token")
    def get_access_token(self) -> str:
        return self.browser.execute_script("return window.localStorage.getItem('access_token')")
            