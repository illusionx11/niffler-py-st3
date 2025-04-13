import pytest
import random
import logging
import time
import random
from faker import Faker
from tests.conftest import TestData
from tests.utils.niffler_api import NifflerAPI
from tests.utils.mock_data import MockData
from tests.pages.main_page import MainPage
from tests.utils.errors import ValidationErrors

@pytest.fixture(scope="class")
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

@pytest.fixture(scope="class")
def add_spendings(niffler_api: NifflerAPI, spendings_data: list[dict]):
    niffler_api.clear_all_spendings()
    all_spendings = niffler_api.get_all_spendings()
    for data in spendings_data:
        amount = data["amount"]
        category = data["category"]["name"]
        currency = data["currency"]
        description = data["description"]
        if any([amount in [s["amount"] for s in all_spendings], 
                category in [s["category"]["name"] for s in all_spendings], 
                currency in [s["currency"] for s in all_spendings], 
                description in [s["description"] for s in all_spendings]]):
            continue
        niffler_api.add_spending(data)
    yield
    niffler_api.clear_all_spendings()
    
@pytest.fixture
def spendings_list(niffler_api: NifflerAPI):
    return niffler_api.get_all_spendings()
    
@pytest.mark.usefixtures(
    "main_page", 
    "create_qa_user",
    "add_spendings",
    "spendings_list"
)
@pytest.mark.spendings
class TestSpendings:
    
    @TestData.spending_data([
        {"amount": "100", "currency": "RUB", "category": "Уникальное", "description": "Уникальные ботинки"},
        {"amount": "200", "currency": "RUB", "category": "Уникальное", "description": "Уникальные тапочки"},
        {"amount": "235", "currency": "KZT", "category": "Путешествия", "description": "Билеты на самолёт"}
    ])
    def test_add_new_spending(self, main_page: MainPage, spending_data: dict[str]):
        main_page.open()
        main_page.should_be_mainpage()
        main_page.add_new_spending(spending_data)
        main_page.should_be_new_spending_in_table(spending_data)
        
    @pytest.mark.repeat(2)
    def test_delete_single_spending(self, main_page: MainPage, spendings_list: list[dict]):
        main_page.open()
        main_page.should_be_mainpage()
        index = random.randint(0, len(spendings_list) - 1)
        logging.info(f"Удаляем расход {spendings_list[index]}")
        main_page.remove_spendings(indexes=[index])
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        main_page.should_not_be_deleted_spendings(spendings_list, indexes=[index])
        
    @pytest.mark.repeat(2)
    def test_delete_multiple_spendings(self, main_page: MainPage, spendings_list: list[dict]):
        main_page.open()
        main_page.should_be_mainpage()
        indexes = random.sample(range(0, len(spendings_list) - 1), 2)
        logging.info(f"Удаляем расходы {spendings_list[indexes[0]]}\nи\n{spendings_list[indexes[1]]}")
        main_page.remove_spendings(indexes)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        main_page.should_not_be_deleted_spendings(spendings_list, indexes)
        
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
            
    @pytest.mark.repeat(2)
    def test_spendings_search_category(self, main_page: MainPage, spendings_list: list[dict]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list)["category"]["name"]
        valid_spendings = [s for s in spendings_list if s["category"]["name"] == query]
        main_page.make_search(query)
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
        
    @pytest.mark.repeat(2)
    def test_spendings_search_description(self, main_page: MainPage, spendings_list: list[dict]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list)["description"]
        valid_spendings = [s for s in spendings_list if s["description"] == query]
        main_page.make_search(query)
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
    
    @TestData.query(["Noneeeeeeee", "123", "Несуществ"])
    def test_nonexistent_spendings_search(self, main_page: MainPage, query: str):
        main_page.open()
        main_page.should_be_mainpage()
        main_page.make_search(query)
        main_page.should_be_no_search_results()