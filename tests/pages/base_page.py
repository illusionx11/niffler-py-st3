from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait

class BasePage:
    def __init__(self, browser: Chrome | Firefox | Safari | Edge | ChromiumEdge | Ie, url: str, timeout: int = 4):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)
        
    def open(self):
        self.browser.get(self.url)

    def is_element_present(self, by, what: str) -> bool:
        try:
            self.browser.find_element(by, what)     
        except NoSuchElementException:
            return False
        return True   
    
    def is_element_not_present(self, by, what: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((by, what)))
        except TimeoutException:
            return True
        return False
    
    def is_element_disappeared(self, by, what: str, timeout: int = 4) -> bool:
        try:
            WebDriverWait(self.browser, timeout, 1, TimeoutException).\
                until_not(EC.presence_of_element_located((by, what)))
        except TimeoutException:
            return False

        return True