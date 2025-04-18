from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

class BasePage:
    def __init__(self, browser: Chrome | Firefox | Safari | Edge | ChromiumEdge | Ie, url: str, timeout: int = 4):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)
        
    def open(self):
        self.browser.get(self.url)

    def clear_input(self, element):
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
    
    def should_be_element(self, locator: tuple[str, str]):
        assert self.is_element_present(*locator)
    
    def should_be_url(self, arg: str):
        assert arg in self.browser.current_url
    
    def is_element_present(self, by, locator: str) -> bool:
        try:
            self.browser.find_element(by, locator)     
        except NoSuchElementException:
            return False
        return True   
    
    def is_element_not_present(self, by, locator: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return True
        return False
    
    def is_element_disappeared(self, by, locator: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout, 1, TimeoutException).\
                until_not(EC.presence_of_element_located((by, locator)))
        except TimeoutException:
            return False

        return True
    
    def get_access_token(self) -> str:
        return self.browser.execute_script("return window.localStorage.getItem('access_token')")
            