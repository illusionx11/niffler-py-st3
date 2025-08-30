from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from models.spend import Spend, SpendAdd
from utils.errors import ValidationErrors
from pages.base_page import BasePage
import allure

class MainPage(BasePage):
    
    CURRENCIES_MAPS = {
        "RUB": "₽",
        "USD": "$",
        "KZT": "₸",
        "EUR": "€"
    }
    
    LOGO_IMG = (By.CSS_SELECTOR, "img.logo-section__logo")
    LOGO_TEXT = (By.CSS_SELECTOR, "p.logo-section__text")
    SPENDINGS_DIV = (By.CSS_SELECTOR, "div#spendings")
    STATS_DIV = (By.CSS_SELECTOR, "div#stat")
    ADD_SPENDING_BTN = (By.CSS_SELECTOR, "a[href='/spending']")
    AMOUNT_INPUT = (By.CSS_SELECTOR, "input#amount")
    CURRENCY_SELECT = (By.CSS_SELECTOR, "div#currency")
    ALL_CURRENCIES = (By.CSS_SELECTOR, "#menu-currency li")
    CATEGORY_INPUT = (By.CSS_SELECTOR, "input#category")
    DESCRIPTION_INPUT = (By.CSS_SELECTOR, "input#description")
    CANCEL_BTN = (By.CSS_SELECTOR, "button#cancel")
    SAVE_BTN = (By.CSS_SELECTOR, "button#save")
    SPENDINGS_TABLE = (By.CSS_SELECTOR, "table")
    SPENDINGS_TABLE_ROWS = (By.CSS_SELECTOR, "table tbody tr")
    SPENDING_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    DELETE_SPENDING_BTN = (By.CSS_SELECTOR, "button#delete")
    DELETE_SPENDING_CONFIRM_BTN = (By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/button[2]")
    DELETE_MODAL_DIV = (By.CSS_SELECTOR, "div[role='dialog']")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[aria-label='search']")
    SEARCH_BTN = (By.CSS_SELECTOR, "button#input-submit")
    
    @allure.step("Проверка на валидность главной страницы")
    def should_be_mainpage(self):
        self.should_be_element(self.SPENDINGS_DIV)
        self.should_be_element(self.STATS_DIV)
        self.should_be_url("main")
    
    @allure.step("Добавление новой траты")
    def add_new_spending(self, data: SpendAdd):
        self.browser.find_element(*self.ADD_SPENDING_BTN).click()
        amount_input = self.browser.find_element(*self.AMOUNT_INPUT)
        self.clear_input(amount_input)
        if data.amount:
            amount_input.send_keys(data.amount)
        self.browser.find_element(*self.CURRENCY_SELECT).click()
        all_currencies = self.browser.find_elements(*self.ALL_CURRENCIES)
        for currency in all_currencies:
            if currency.get_attribute("data-value") == data.currency:
                currency.click()
                break
        category_input = self.get_element_clickable_safe(self.CATEGORY_INPUT)
        if data.category:
            self.clear_input(category_input)
            category_input.send_keys(data.category.name)
        description_input = self.browser.find_element(*self.DESCRIPTION_INPUT)
        if data.description:
            self.clear_input(description_input)
            description_input.send_keys(data.description)
        self.browser.find_element(*self.SAVE_BTN).click()
    
    @allure.step("Проверка на наличие добавленной траты в таблице")
    def should_be_new_spending_in_table(self, data: SpendAdd):
        
        def check_spending_added(table_rows: list) -> bool:
            for row in table_rows:
                row_data = row.find_elements(By.CSS_SELECTOR, "td")[1:] # пропускаем первый столбец с чекбоксом
                category = row_data[0].text
                amount, currency = row_data[1].text.split(" ")
                description = row_data[2].text
                data_amount = data.amount if not data.amount.is_integer() else int(data.amount)
                if data.category.name == category and str(data_amount) == amount \
                and self.CURRENCIES_MAPS[data.currency] == currency \
                and data.description == description:
                    return True
            return False
        
        table_rows = self.get_all_elements_presence_safe(self.SPENDINGS_TABLE_ROWS)
        is_spending_added = check_spending_added(table_rows)
        assert is_spending_added, f"Новый расход {data} не добавлен на странице {self.browser.current_url}"
    
    @allure.step("Удаление трат")
    def remove_spendings(self, indexes: list[int]):
        
        table_rows = self.get_all_elements_presence_safe(self.SPENDINGS_TABLE_ROWS)
        for index in indexes:
            row_to_delete = table_rows[index]
            row_to_delete.find_element(*self.SPENDING_CHECKBOX).click()
        self.get_element_clickable_safe(self.DELETE_SPENDING_BTN).click()
        self.get_element_presence_safe(self.DELETE_MODAL_DIV)
        self.get_element_clickable_safe(self.DELETE_SPENDING_CONFIRM_BTN).click()
    
    @allure.step("Проверка на исчезновение трат из таблицы")
    def should_not_be_deleted_spendings(self, spendings: list[Spend], indexes: list[int]):
        
        def check_spendings_deleted(new_table_rows: list) -> bool:
            self.get_all_elements_presence_safe((By.CSS_SELECTOR, "td"))
            for row in new_table_rows:
                row_data = row.find_elements(By.CSS_SELECTOR, "td")[1:] # пропускаем первый столбец с чекбоксом
                category = row_data[0].text
                amount, currency = row_data[1].text.split(" ")
                description = row_data[2].text
                for i in indexes:
                    if spendings[i].category.name == category and spendings[i].amount == float(amount) \
                    and self.CURRENCIES_MAPS[spendings[i].currency] == currency \
                    and spendings[i].description == description:
                        return False
            return True
        
        new_table_rows = self.get_all_elements_presence_safe(self.SPENDINGS_TABLE_ROWS)
        is_spendings_deleted = check_spendings_deleted(new_table_rows)
        assert is_spendings_deleted, f"Расходы не удалены на странице {self.browser.current_url}"
    
    @allure.step("Проверка на наличие ошибок валидации")
    def should_be_errors_in_validation(self, errors: dict[str, list[ValidationErrors]]):
        key = None
        if "amount" in errors and len(errors["amount"]) > 0:
            amount_error = self.get_element_presence_safe(
                (By.CSS_SELECTOR, "input#amount ~ span.input__helper-text")
            )
            element_text = amount_error.text
            key = "amount"
        
        if "category" in errors and len(errors["category"]) > 0:
            category_error = self.get_element_presence_safe(
                (By.CSS_SELECTOR, "input#category ~ span.input__helper-text")
            )
            element_text = category_error.text
            key = "category"
            
        for error_text in errors[key]:
            assert error_text.lower() in element_text.lower(), \
                f"Error text '{error_text}' not in '{element_text}'"
    
    @allure.step("Поиск по тратам")
    def make_search(self, query: str):
        search_input = self.get_element_presence_safe(self.SEARCH_INPUT)
        self.clear_input(search_input)
        search_input.send_keys(query)
        search_input.send_keys(Keys.RETURN)
    
    @allure.step("Проверка на результаты таблицы трат после поиска")
    def should_be_exact_search_results(self, query: str, valid_spendings: list[Spend]):

        table_rows = self.get_all_elements_presence_safe(self.SPENDINGS_TABLE_ROWS)
        assert len(table_rows) == len(valid_spendings), f"Количество расходов в таблице {len(table_rows)} не равно количеству расходов в списке {len(valid_spendings)}"
        for row in table_rows:
            is_spending_present = False
            row_data = row.find_elements(By.CSS_SELECTOR, "td")[1:] # пропускаем первый столбец с чекбоксом
            category = row_data[0].text
            amount, currency = row_data[1].text.split(" ")
            description = row_data[2].text
            for spending in valid_spendings:
                if spending.category.name == category and spending.amount == float(amount) \
                and self.CURRENCIES_MAPS[spending.currency] == currency \
                and spending.description == description:
                    is_spending_present = True
                    break
            
            assert is_spending_present is True, f"Расход {spending} не найден после поиска '{query}' на странице {self.browser.current_url}"
    
    @allure.step("Проверка на отсутствие результатов поиска трат")
    def should_be_no_search_results(self):
        assert self.is_element_not_present(*self.SPENDINGS_TABLE), "Ожидалось, что поиск не даст результатов, но они есть"