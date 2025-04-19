import pytest
import random
import logging
import time
import random
from tests.models.spend import Spend, SpendGet, SpendAdd, CategoryAdd
from tests.conftest import TestData
from tests.pages.main_page import MainPage
from tests.utils.errors import ValidationErrors
from tests.databases.spends_db import SpendsDb
from tests.models.config import Envs
from tests.utils.niffler_api import NifflerAPI
from datetime import datetime
    
@pytest.mark.usefixtures(
    "main_page", 
    "cleanup",
    "add_spendings",
    "spendings_list"
)
@pytest.mark.spendings
class TestSpendings:
    
    @TestData.spending_data([
        SpendAdd(
            amount=100.5,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные ботинки",
            spendDate="2024-06-01T00:00:00.000Z",
        ),
        SpendAdd(
            amount=200,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные тапочки",
            spendDate="2024-06-01T00:00:00.000Z"
        ),
        SpendAdd(
            amount=235.35,
            category=CategoryAdd(name="Путешествия"),
            currency="KZT",
            description="Билеты на самолёт",
            spendDate="2024-06-01T00:00:00.000Z"
        )
    ])
    def test_add_new_spending(self, main_page: MainPage, spending_data: SpendAdd):
        main_page.open()
        main_page.should_be_mainpage()
        main_page.add_new_spending(spending_data)
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        main_page.should_be_new_spending_in_table(spending_data)
        
    @pytest.mark.repeat(2)
    def test_delete_single_spending(self, main_page: MainPage, spendings_list: list[SpendGet]):
        main_page.open()
        main_page.should_be_mainpage()
        index = random.randint(0, len(spendings_list) - 1)
        logging.info(f"Удаляем расход {spendings_list[index]}")
        main_page.remove_spendings(indexes=[index])
        time.sleep(0.3) # плохая практика, но без этого иногда ловится StaleElementReferenceException
        main_page.should_not_be_deleted_spendings(spendings_list, indexes=[index])
        
    @pytest.mark.repeat(2)
    def test_delete_multiple_spendings(self, main_page: MainPage, spendings_list: list[SpendGet]):
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
        amount_data = SpendAdd(
            amount=0,
            currency="RUB", 
            category=CategoryAdd(name="Продукты"), 
            description="Молоко", 
            spendDate="2022-05-01T00:00:00.000Z"
        )
        main_page.add_new_spending(amount_data)
        errors = {
            "amount": [ValidationErrors.LOW_AMOUNT]
        }
        main_page.should_be_errors_in_validation(errors=errors)
        
    def test_spending_category_validation(self, main_page: MainPage):
        main_page.open()
        main_page.should_be_mainpage()
        category_data = SpendAdd(
            amount=100, 
            currency="RUB",
            description="Что-то", 
            category=CategoryAdd(name=""), 
            spendDate="2022-05-01T00:00:00.000Z"
        )
        main_page.add_new_spending(category_data)
        errors = {
            "category": [ValidationErrors.NO_CATEGORY]
        }
        main_page.should_be_errors_in_validation(errors=errors)
        
    def test_spending_mixed_validation(self, main_page: MainPage):
        main_page.open()
        main_page.should_be_mainpage()
        mixed_data = SpendAdd(
            amount=0, 
            currency="KZT", 
            description="Аренда отеля", 
            category=CategoryAdd(name=""), 
            spendDate="2022-05-01T00:00:00.000Z"
        )
        main_page.add_new_spending(data=mixed_data)
        errors = {
            "amount": [ValidationErrors.LOW_AMOUNT],
            "category": [ValidationErrors.NO_CATEGORY]
        }
        main_page.should_be_errors_in_validation(errors=errors)
            
    @pytest.mark.repeat(2)
    def test_spendings_search_category(self, main_page: MainPage, spendings_list: list[SpendGet]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list).category.name
        valid_spendings = [s for s in spendings_list if s.category.name == query]
        main_page.make_search(query)
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
        
    @pytest.mark.repeat(2)
    def test_spendings_search_description(self, main_page: MainPage, spendings_list: list[SpendGet]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list).description
        valid_spendings = [s for s in spendings_list if s.description == query]
        main_page.make_search(query)
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
    
    @TestData.query(["Noneeeeeeee", "123", "Несуществ"])
    def test_nonexistent_spendings_search(self, main_page: MainPage, query: str):
        main_page.open()
        main_page.should_be_mainpage()
        main_page.make_search(query)
        main_page.should_be_no_search_results()

@pytest.mark.usefixtures(
    "cleanup",
    "niffler_api",
    "envs",
    "spends_db"
)
@pytest.mark.spendings
@pytest.mark.spendings_db
class TestSpendingsDatabase:
    
    @TestData.spending_data([
        SpendAdd(
            amount=1000.26,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные шляпы",
            spendDate="2024-06-07T00:00:00.000Z",
        )
    ])
    def test_added_spending_in_database(
        self, 
        niffler_api: NifflerAPI, 
        spending_data: SpendAdd, 
        envs: Envs,
        spends_db: SpendsDb
    ):
        added_spending_data = niffler_api.add_spending(data=spending_data)
        logging.info(f"Добавлен расход {added_spending_data}")
        all_spendings = spends_db.get_user_spendings(username=envs.test_username)
        spending = next(
            (
                s for s in all_spendings if s.amount == spending_data.amount \
                and s.category.name == spending_data.category.name \
                and s.currency == spending_data.currency \
                and s.description == spending_data.description \
                and s.spend_date == datetime.fromisoformat(spending_data.spendDate.replace("Z", "+00:00")).date()
            ),
            None
        )
        assert spending is not None
        
    @TestData.spending_data([
        SpendAdd(
            amount=162.23,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные кружки",
            spendDate="2024-06-07T00:00:00.000Z",
        )
    ])
    def test_deleted_spending_not_in_database(
        self,
        niffler_api: NifflerAPI,
        spending_data: SpendAdd,
        envs: Envs,
        spends_db: SpendsDb
    ):
        added_spending_data = niffler_api.add_spending(data=spending_data)
        logging.info(f"Добавлен расход {added_spending_data}")
        niffler_api.clear_spendings(ids=[added_spending_data.id])
        logging.info(f"Удален расход с id {added_spending_data.id}")
        all_spendings = spends_db.get_user_spendings(username=envs.test_username)
        spending = next(
            (
                s for s in all_spendings if s.id == added_spending_data.id
            ),
            None
        )
        assert spending is None