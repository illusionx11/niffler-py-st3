from selenium.webdriver import Chrome, Firefox, Safari, Edge, ChromiumEdge, Ie
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, 
    ElementNotInteractableException, StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
import allure
import logging
import time
from models.auth_user import TokenData
from urllib.parse import urlparse

_ANIM_WAIT_JS = r"""
const el = arguments[0];
const subtree = Boolean(arguments[1]);
const done = arguments[arguments.length - 1];

try {
const list = el.getAnimations ? el.getAnimations({subtree}) : [];
if (!list || list.length === 0) return done(true);

Promise.allSettled(list.map(a => a.finished.catch(()=>{}))).then(() => {
    requestAnimationFrame(() => requestAnimationFrame(() => done(true)));
});
} catch (e) {
done(true);
}
"""


class BasePage:
    
    def __init__(
        self, 
        browser: Chrome | Firefox | Safari | Edge | ChromiumEdge | Ie, 
        url: str,
        token_data: TokenData,
        timeout: int = 4,        
    ):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)
        self.token_data = token_data
    
    @allure.step("Открыть страницу")
    def open(self, set_localstorage: bool = True, add_domain: bool = False):
        """
        Открывает страницу с правильной настройкой OAuth2 авторизации
        
        Args:
            set_localstorage: Устанавливать ли localStorage и cookies
            add_domain: Добавлять ли домен к cookies (для проблемных случаев)
        """
        logging.info(f"Opening {self.url}")
        self.browser.get(self.url)
        
        if set_localstorage:
            self.browser.delete_all_cookies()
            self.browser.execute_script("window.localStorage.clear();")
            current_domain = urlparse(self.url).netloc
            logging.info(f"Current page domain: {current_domain}")
            logging.info(f"Available cookies: {self.token_data.cookies}")
            relevant_cookies = []
            cookie_names_added = set()
            
            for c in self.token_data.cookies:
                if c["name"] in cookie_names_added:
                    logging.info(f"Skipping duplicate cookie {c["name"]} (domain: {c["domain"]})")
                    continue
                
                if current_domain == "frontend.niffler.dc":
                    if c["domain"] and "auth.niffler.dc" in c["domain"]:
                        logging.info(f"Skipping auth server cookie {c["name"]} (domain: {c["domain"]})")
                        continue
                    elif not c["domain"] or c["domain"] == current_domain or c["domain"] == "frontend.niffler.dc":
                        relevant_cookies.append(c)
                        cookie_names_added.add(c["name"])
                        logging.info(f"Using cookie {c["name"]} (domain: {c["domain"] or 'None'})")
                    else:
                        logging.info(f"Skipping wrong domain cookie {c["name"]} (domain: {c["domain"]})")
                else:
                    relevant_cookies.append(c)
                    cookie_names_added.add(c["name"])
            
            for c in relevant_cookies:
                cookie_dict = {
                    "name": c["name"],
                    "value": c["value"],
                    "path": c["path"] or "/",
                }
                
                if add_domain and c["domain"] and c["domain"] == current_domain:
                    cookie_dict["domain"] = c["domain"]
                
                self.browser.add_cookie(cookie_dict)
            
            oauth_data = {
                "access_token": self.token_data.access_token,
                "id_token": self.token_data.id_token, 
                "codeVerifier": self.token_data.code_verifier,
                "codeChallenge": self.token_data.code_challenge
            }
            
            self.browser.execute_script("""
                const oauthData = arguments[0];
                for (const [key, value] of Object.entries(oauthData)) {
                    if (value) {
                        window.localStorage.setItem(key, String(value));
                    }
                }
            """, oauth_data)
            
            logging.info("Session cookies and OAuth tokens configured")
            
            self.browser.get(self.url)
            WebDriverWait(self.browser, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            current_url = self.browser.current_url
            
            if "/authorized" in current_url:
                logging.info(f"OAuth2 callback detected: {current_url}")
                
                try:
                    WebDriverWait(self.browser, 15).until(
                        lambda driver: "/authorized" not in driver.current_url and "/login" not in driver.current_url
                    )
                    if self.url != self.browser.current_url: # /authorized редиректит на /main вместо /profile
                        logging.info(f"Redirecting to {self.url}")
                        self.browser.get(self.url)
                        WebDriverWait(self.browser, 10).until(
                            lambda driver: driver.execute_script("return document.readyState") == "complete"
                        )
                    final_url = self.browser.current_url
                    logging.info(f"OAuth2 flow completed, redirected to: {final_url}")
                except Exception as e:
                    logging.warning(f"OAuth2 redirect timeout, staying on: {self.browser.current_url}")
            
            elif "/login" in current_url or "/oauth2/authorize" in current_url:
                logging.warning(f"Redirected to auth page: {current_url}")
                raise Exception(f"Authentication failed - redirected to: {current_url}")
            
            else:
                logging.info(f"Page loaded directly: {current_url}")
            
            
            logging.info(f"Authentication successful, final URL: {self.browser.current_url}")
            
        else:
            WebDriverWait(self.browser, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

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
            
    @allure.step("Получение Web элемента с текстом")
    def get_element_presence_with_text_safe(self, locator: tuple[str, str], timeout: int = 10):
        for i in range(10):
            try:
                result = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_element_located(locator)
                ).text
                return result
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
    
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
                
    @allure.step("Получение текста из ячейки таблицы")
    def get_row_cells_text(self, row: WebElement) -> tuple[str]:
        for i in range(30): # увеличил кол-во retry из-за ненадежности row.find_elements
            try:
                row_data = row.find_elements(By.CSS_SELECTOR, "td")
                category = row_data[1].text
                amount, currency = row_data[2].text.split(" ")
                description = row_data[3].text
                date = row_data[4].text
                return category, amount, currency, description, date
            except StaleElementReferenceException:
                if i == 29:
                    raise
                time.sleep(0.1)
    
    @allure.step("Получение текста из элемента")
    def get_element_text_safe(self, locator: tuple[str, str], text: str):
        for i in range(10):
            try:
                element = WebDriverWait(self.browser, 10).until(
                    EC.text_to_be_present_in_element(locator, text)
                )
                return element
            except StaleElementReferenceException:
                if i == 9:
                    raise
                time.sleep(0.1)
                
    @allure.step("Ожидание завершения анимации")
    def wait_for_animations_finish(
        self, element: WebElement, timeout: int = 10, include_subtree: bool = True
    ):
        self.browser.set_script_timeout(timeout)
        WebDriverWait(self.browser, timeout).until(
            lambda d: d.execute_async_script(_ANIM_WAIT_JS, element, include_subtree)
        )
                