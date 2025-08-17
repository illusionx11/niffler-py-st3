import pytest
import random
import logging
import random
import allure
import time
from utils.allure_data import Epic, Feature, Story
from models.spend import SpendGet, SpendAdd
from models.category import CategoryAdd
from marks import TestData
from pages.main_page import MainPage
from utils.errors import ValidationErrors
from utils.generate_datetime import generate_random_datetime

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_front_token",
    "main_page", 
    "add_spendings",
    "spendings_list"
)
@pytest.mark.spendings
@pytest.mark.ui
@allure.feature(Feature.spendings)
class TestSpendings:
    
    @TestData.spending_data([
        SpendAdd(
            amount=100.5,
            category=CategoryAdd(name="Уникальное"),
            currency="USD",
            description="Уникальные ботинки",
            spendDate=generate_random_datetime(),
        ),
        SpendAdd(
            amount=200,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные тапочки",
            spendDate=generate_random_datetime()
        ),
        SpendAdd(
            amount=235.35,
            category=CategoryAdd(name="Путешествия"),
            currency="KZT",
            description="Билеты на самолёт",
            spendDate=generate_random_datetime()
        )
    ])
    @allure.story(Story.add_spending)
    def test_add_new_spending(self, main_page: MainPage, spending_data: SpendAdd):
        
        main_page.open()
        main_page.should_be_mainpage()
        main_page.add_new_spending(spending_data)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_new_spending_in_table(spending_data)
    
    @allure.story(Story.delete_spending)
    @pytest.mark.xdist_group("06_spendings_ui_delete_01")
    def test_delete_single_spending_ui(
        self, 
        main_page: MainPage, 
        spendings_list: list[SpendGet],
        delete_spendings_lock
    ):
        main_page.open()
        main_page.should_be_mainpage()
        max_index = len(spendings_list) - 1 if len(spendings_list) <= 10 else 9
        index = random.randint(0, max_index)
        logging.info(f"Удаляем расход {spendings_list[index]}")
        main_page.remove_spendings(indexes=[index])
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_not_be_deleted_spendings(spendings_list, indexes=[index])
    
    @allure.story(Story.delete_spending)
    @pytest.mark.xdist_group("06_spendings_ui_delete_02")
    def test_delete_multiple_spendings_ui(
        self, 
        main_page: MainPage, 
        spendings_list: list[SpendGet],
        delete_spendings_lock
    ):
        main_page.open()
        main_page.should_be_mainpage()
        max_index = len(spendings_list) - 1 if len(spendings_list) <= 10 else 9
        indexes = random.sample(range(0, max_index), 2)
        logging.info(f"Удаляем расходы:\n{spendings_list[indexes[0]]}\nи\n{spendings_list[indexes[1]]}")
        main_page.remove_spendings(indexes)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_not_be_deleted_spendings(spendings_list, indexes)
    
    @allure.story(Story.add_spending)
    def test_spending_amount_validation(self, main_page: MainPage):
        main_page.open()
        main_page.should_be_mainpage()
        amount_data = SpendAdd(
            amount=0,
            currency="RUB", 
            category=CategoryAdd(name="Продукты"), 
            description="Молоко", 
            spendDate=generate_random_datetime()
        )
        main_page.add_new_spending(amount_data)
        errors = {
            "amount": [ValidationErrors.LOW_AMOUNT]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.add_spending)
    def test_spending_category_validation(self, main_page: MainPage):
        main_page.open()
        main_page.should_be_mainpage()
        category_data = SpendAdd(
            amount=100, 
            currency="RUB",
            description="Что-то", 
            category=CategoryAdd(name=""), 
            spendDate=generate_random_datetime()
        )
        main_page.add_new_spending(category_data)
        errors = {
            "category": [ValidationErrors.NO_CATEGORY]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.add_spending)
    def test_spending_mixed_validation(self, main_page: MainPage):
        main_page.open()
        main_page.should_be_mainpage()
        mixed_data = SpendAdd(
            amount=0, 
            currency="KZT", 
            description="Аренда отеля", 
            category=CategoryAdd(name=""), 
            spendDate=generate_random_datetime()
        )
        main_page.add_new_spending(data=mixed_data)
        errors = {
            "amount": [ValidationErrors.LOW_AMOUNT],
            "category": [ValidationErrors.NO_CATEGORY]
        }
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_errors_in_validation(errors=errors)
    
    @allure.story(Story.search_spending)
    def test_spendings_search_category(self, main_page: MainPage, spendings_list: list[SpendGet]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list).category.name
        valid_spendings = [s for s in spendings_list if s.category.name == query]
        main_page.make_search(query)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
    
    @allure.story(Story.search_spending)
    def test_spendings_search_description(self, main_page: MainPage, spendings_list: list[SpendGet]):
        main_page.open()
        main_page.should_be_mainpage()
        query = random.choice(spendings_list).description
        valid_spendings = [s for s in spendings_list if s.description == query]
        main_page.make_search(query)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_exact_search_results(query, valid_spendings=valid_spendings)
    
    @allure.story(Story.search_spending)
    @TestData.query(["Noneeeeeeee", "123", "Несуществ"])
    def test_nonexistent_spendings_search(self, main_page: MainPage, query: str):
        main_page.open()
        main_page.should_be_mainpage()
        main_page.make_search(query)
        time.sleep(0.3) # Чтобы избежать Stale Element Reference
        main_page.should_be_no_search_results()