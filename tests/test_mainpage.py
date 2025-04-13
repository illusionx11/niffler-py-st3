import os
import pytest
from faker import Faker
import random
from selenium import webdriver
import logging
import time
from tests.pages.urls import Urls
from tests.utils.mock_data import MockData
from tests.pages.login_page import LoginPage
from tests.pages.main_page import MainPage
from tests.utils.niffler_api import NifflerAPI
from tests.utils.errors import ValidationErrors

@pytest.fixture(scope="module")
def spendings_data():
    faker = Faker()
    spendings = []
    for _ in range(10):
        amount = faker.random_number(digits=3)
        category_name = random.choice(MockData.CATEGORIES)
        currency = random.choice(MockData.CURRENCIES)
        description = faker.sentence(nb_words=2, variable_nb_words=True)
        spend_date = faker.date_time().isoformat(timespec="milliseconds") + "Z"
        data = {
            "amount": amount,
            "category": {
                "name": category_name
            },
            "currency": currency,
            "description": description,
            "spendDate": spend_date
        }
        spendings.append(data)
        
    return spendings

@pytest.fixture
def spendings(niffler_api: NifflerAPI):
    return niffler_api.get_all_spendings()
    
@pytest.mark.usefixtures("login_page", "main_page", "niffler_api", "config")
@pytest.mark.main_page
class TestMainPage:
    
    @pytest.fixture(scope="module", autouse=True)
    def setup(
        self, 
        login_page: LoginPage, 
        main_page: MainPage, 
        niffler_api: NifflerAPI, 
        config: dict[str, str], 
        spendings_data: list[dict]
    ):
        username = config["username"]
        password = config["password"]
        login_page.log_in(username, password)
        
        main_page.should_be_mainpage()
        token = main_page.get_access_token()
        
        niffler_api.set_token(token)
        niffler_api.clear_all_spendings()
        for data in spendings_data:
            niffler_api.add_spending(data)
            
        yield
        
        niffler_api.clear_all_spendings()
    
    @pytest.mark.spendings
    class TestSpendings:
        
        @pytest.mark.parametrize("data", [
            {"amount": "100", "currency": "RUB", "category": "Уникальное", "description": "Уникальные ботинки"},
            {"amount": "200", "currency": "RUB", "category": "Уникальное", "description": "Уникальные тапочки"},
            {"amount": "235", "currency": "KZT", "category": "Путешествия", "description": "Билеты на самолёт"}
        ])
        def test_add_new_spending(self, main_page: MainPage, data: dict[str]):
            main_page.open()
            main_page.should_be_mainpage()
            main_page.add_new_spending(data)
            main_page.should_be_new_spending_in_table(data)
            
        @pytest.mark.parametrize("repeat", [0, 1])
        def test_delete_single_spending(self, main_page: MainPage, spendings: list[dict], repeat: int):
            main_page.open()
            main_page.should_be_mainpage()
            index = random.randint(0, len(spendings) - 1)
            logging.info(f"Удаляем расход {spendings[index]}")
            main_page.remove_spendings(indexes=[index])
            time.sleep(1) # плохая практика, но без этого иногда ловится StaleElementReferenceException
            main_page.should_not_be_deleted_spendings(spendings, indexes=[index])
            
        @pytest.mark.parametrize("repeat", [0, 1])
        def test_delete_multiple_spendings(self, main_page: MainPage, spendings: list[dict], repeat: int):
            main_page.open()
            main_page.should_be_mainpage()
            indexes = random.sample(range(0, len(spendings) - 1), 2)
            logging.info(f"Удаляем расходы {spendings[indexes[0]]}\nи\n{spendings[indexes[1]]}")
            main_page.remove_spendings(indexes)
            time.sleep(1) # плохая практика, но без этого иногда ловится StaleElementReferenceException
            main_page.should_not_be_deleted_spendings(spendings, indexes)
            
        def test_spending_amount_validation(self, main_page: MainPage):
            main_page.open()
            main_page.should_be_mainpage()
            amount_data = {"amount": "", "currency": "RUB", "category": "Продукты", "description": "Молоко"}
            main_page.add_new_spending(amount_data)
            errors = {
                "amount": [ValidationErrors.LOW_AMOUNT]
            }
            main_page.should_be_errors_in_validation(errors=errors)
            
        def test_spending_category_validation(self, main_page: MainPage):
            main_page.open()
            main_page.should_be_mainpage()
            category_data = {"amount": "100", "currency": "RUB", "category": "", "description": "Что-то"}
            main_page.add_new_spending(category_data)
            errors = {
                "category": [ValidationErrors.NO_CATEGORY]
            }
            main_page.should_be_errors_in_validation(errors=errors)
            
        def test_spending_mixed_validation(self, main_page: MainPage):
            main_page.open()
            main_page.should_be_mainpage()
            mixed_data = {"amount": "", "currency": "KZT", "category": "", "description": "Аренда отеля"}
            main_page.add_new_spending(data=mixed_data)
            errors = {
                "amount": [ValidationErrors.LOW_AMOUNT],
                "category": [ValidationErrors.NO_CATEGORY]
            }
            main_page.should_be_errors_in_validation(errors=errors)
                
        @pytest.mark.parametrize("repeat", [0, 1])
        def test_spendings_search_category(self, main_page: MainPage, spendings: list[dict], repeat: int):
            main_page.open()
            main_page.should_be_mainpage()
            query = random.choice(spendings)["category"]["name"]
            valid_spendings = [s for s in spendings if s["category"]["name"] == query]
            main_page.make_search(query)
            main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
            
        @pytest.mark.parametrize("repeat", [0, 1])
        def test_spendings_search_description(self, main_page: MainPage, spendings: list[dict], repeat: int):
            main_page.open()
            main_page.should_be_mainpage()
            query = random.choice(spendings)["description"]
            valid_spendings = [s for s in spendings if s["description"] == query]
            main_page.make_search(query)
            main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
        
        @pytest.mark.parametrize("query", ["Noneeeeeeee", "123", "Несуществ"])
        def test_nonexistent_spendings_search(self, main_page: MainPage, query: str):
            main_page.open()
            main_page.should_be_mainpage()
            main_page.make_search(query)
            main_page.should_be_no_search_results()
        