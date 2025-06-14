import pytest
import random
import logging
import time
import random
import allure
from utils.mock_data import MockData
from allure_data import Epic, Feature, Story
from models.spend import SpendGet, SpendAdd
from models.category import CategoryAdd
from clients.spends_client import SpendsClient
from marks import TestData
from pages.main_page import MainPage
from utils.errors import ValidationErrors
from databases.spends_db import SpendsDb
from models.config import ClientEnvs
from datetime import datetime
from utils.generate_datetime import generate_random_datetime
from faker import Faker

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_api_token",
    "spends_client",
    "cleanup",
    "add_spendings",
    "spendings_list"
)
@pytest.mark.api
@pytest.mark.spendings
@allure.feature(Feature.spendings)
class TestSpendingsAPI:
    
    @TestData.spending_data([
        SpendAdd(
            amount=round(random.uniform(0, 10000), 3),
            category=CategoryAdd(name="Уникальное"),
            currency=random.choice(MockData.CURRENCIES),
            description="Уникальная вещь1",
            spendDate=generate_random_datetime()
        ),
        SpendAdd(
            amount=round(random.uniform(0, 10000), 3),
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальная вещь2",
            spendDate=generate_random_datetime()
        ),
        SpendAdd(
            amount=round(random.uniform(0, 10000), 3),
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальная вещь3",
            spendDate=generate_random_datetime()
        )
    ])
    @allure.story(Story.add_spending)
    def test_add_new_spend(self, spends_client: SpendsClient, spending_data: SpendAdd):
        added_spending_data = spends_client.add_spending(data=spending_data)
        with allure.step("Проверка, что расход добавлен"):
            assert added_spending_data.amount == spending_data.amount
            assert added_spending_data.category.name == spending_data.category.name
            assert added_spending_data.currency == spending_data.currency
            assert added_spending_data.description == spending_data.description
            assert added_spending_data.spendDate.replace('+00:00', 'Z') == spending_data.spendDate
    
    @pytest.mark.repeat(2)
    @allure.story(Story.get_spending)
    def test_get_spend_by_id(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        received_spend = spends_client.get_spending_by_id(spend.id)
        with allure.step("Проверка, что получен правильный расход"):
            assert received_spend.id == spend.id
            assert received_spend.amount == spend.amount
            assert received_spend.category.name == spend.category.name
            assert received_spend.currency == spend.currency
            assert received_spend.description == spend.description
            assert received_spend.spendDate.split("T")[0] == spend.spendDate.split("T")[0]
    
    @TestData.spending_data([
        SpendAdd(
            amount=round(random.uniform(0, 10000), 3),
            category=CategoryAdd(name="Уникальное"),
            currency=random.choice(MockData.CURRENCIES),
            description="Уникальная вещь4",
            spendDate=generate_random_datetime()
        )
    ])
    @allure.story(Story.get_spending)
    def test_get_spend_after_add(self, spends_client: SpendsClient, spending_data: SpendAdd):
        added_spending_data = spends_client.add_spending(data=spending_data)
        received_spend = spends_client.get_spending_by_id(added_spending_data.id)
        with allure.step("Проверка, что получен правильный расход"):
            assert received_spend.id == added_spending_data.id
            assert received_spend.amount == added_spending_data.amount
            assert received_spend.category.name == added_spending_data.category.name
            assert received_spend.currency == added_spending_data.currency
            assert received_spend.description == added_spending_data.description
            assert added_spending_data.spendDate.split("T")[0] == spending_data.spendDate.split("T")[0]
    
    @pytest.mark.repeat(2)
    @allure.story(Story.update_spending)
    def test_update_spending_amount(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_amount = round(random.uniform(0, 10000), 3)
            if new_amount != spend.amount:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=new_amount,
                category=CategoryAdd(name=spend.category.name),
                currency=spend.currency,
                description=spend.description,
                spendDate=spend.spendDate
            )
        )
        with allure.step("Проверка, что у расхода обновлена сумма"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == new_amount
            assert updated_spend.category.name == spend.category.name
            assert updated_spend.currency == spend.currency
            assert updated_spend.description == spend.description
            assert updated_spend.spendDate == spend.spendDate
            
    @pytest.mark.repeat(2)
    @allure.story(Story.update_spending)
    def test_update_spending_currency(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_currency = random.choice(MockData.CURRENCIES)
            if new_currency != spend.currency:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=spend.amount,
                category=CategoryAdd(name=spend.category.name),
                currency=new_currency,
                description=spend.description,
                spendDate=spend.spendDate
            )
        )
        with allure.step("Проверка, что у расхода обновлена валюта"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == spend.amount
            assert updated_spend.category.name == spend.category.name
            assert updated_spend.currency == new_currency
            assert updated_spend.description == spend.description
            assert updated_spend.spendDate == spend.spendDate
            
    @pytest.mark.repeat(2)
    @allure.story(Story.update_spending)
    def test_update_spending_description(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_description = Faker().sentence(nb_words=2, variable_nb_words=True)
            if new_description != spend.description:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=spend.amount,
                category=CategoryAdd(name=spend.category.name),
                currency=spend.currency,
                description=new_description,
                spendDate=spend.spendDate
            )
        )
        with allure.step("Проверка, что у расхода обновлено описание"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == spend.amount
            assert updated_spend.category.name == spend.category.name
            assert updated_spend.currency == spend.currency
            assert updated_spend.description == new_description
            assert updated_spend.spendDate == spend.spendDate
            
    @pytest.mark.repeat(2)
    @allure.story(Story.update_spending)
    def test_update_spending_category(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_category = random.choice(MockData.CATEGORIES)
            if new_category != spend.category.name:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=spend.amount,
                category=CategoryAdd(name=new_category),
                currency=spend.currency,
                description=spend.description,
                spendDate=spend.spendDate
            )
        )
        with allure.step("Проверка, что у расхода обновлена категория"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == spend.amount
            assert updated_spend.category.name == new_category
            assert updated_spend.currency == spend.currency
            assert updated_spend.description == spend.description
            assert updated_spend.spendDate == spend.spendDate
    
    @pytest.mark.repeat(2)
    @allure.story(Story.update_spending)
    def test_update_spending_date(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_date = generate_random_datetime()
            if new_date.split("T")[0] != spend.spendDate.split("T")[0]:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=spend.amount,
                category=CategoryAdd(name=spend.category.name),
                currency=spend.currency,
                description=spend.description,
                spendDate=new_date
            )
        )
        with allure.step("Проверка, что у расхода обновлена дата"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == spend.amount
            assert updated_spend.category.name == spend.category.name
            assert updated_spend.currency == spend.currency
            assert updated_spend.description == spend.description
            assert updated_spend.spendDate.split("T")[0] == new_date.split("T")[0]
        
    @allure.story(Story.update_spending)
    def test_update_spending_multiple_fields(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_amount = round(random.uniform(0, 10000), 3)
            new_currency = random.choice(MockData.CURRENCIES)
            new_category = random.choice(MockData.CATEGORIES)
            if new_amount != spend.amount \
            and new_currency != spend.currency \
            and new_category != spend.category.name:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=new_amount,
                category=CategoryAdd(name=new_category),
                currency=new_currency,
                description=spend.description,
                spendDate=spend.spendDate
            )
        )
        with allure.step("Проверка, что у расхода обновлена сумма, валюта и категория"):
            assert updated_spend.id == spend.id
            assert updated_spend.amount == new_amount
            assert updated_spend.category.name == new_category
            assert updated_spend.currency == new_currency
            assert updated_spend.description == spend.description
            assert updated_spend.spendDate == spend.spendDate
    
    @pytest.mark.xfail(reason="Добавляется один день к дате")
    @allure.story(Story.get_spending)
    def test_get_spending_after_update(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend = random.choice(spendings_list)
        while True:
            new_amount = round(random.uniform(0, 10000), 3)
            new_description = Faker().sentence(nb_words=2, variable_nb_words=True)
            new_date = generate_random_datetime()
            if new_amount != spend.amount \
            and new_description != spend.description \
            and new_date.split("T")[0] != spend.spendDate.split("T")[0]:
                break
        updated_spend = spends_client.update_spending(
            data=SpendAdd(
                id=spend.id,
                amount=new_amount,
                category=CategoryAdd(name=spend.category.name),
                currency=spend.currency,
                description=new_description,
                spendDate=new_date
            )
        )
        received_spend = spends_client.get_spending_by_id(updated_spend.id)
        with allure.step("Проверка, что получен правильный расход после обновления"):
            assert received_spend.id == updated_spend.id
            assert received_spend.amount == new_amount
            assert received_spend.category.name == spend.category.name
            assert received_spend.currency == spend.currency
            assert received_spend.description == new_description
            assert received_spend.spendDate.split("T")[0] == new_date.split("T")[0]
    
    @pytest.mark.repeat(2)     
    @allure.story(Story.delete_spending)
    def test_delete_single_spending(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spend_id = random.choice(spendings_list).id
        spends_client.clear_spendings(ids=[spend_id])
        all_spends = spends_client.get_all_spendings()
        all_spends_ids = [spend.id for spend in all_spends]
        with allure.step("Проверка, что расход удален"):
            assert spend_id not in all_spends_ids
            
    @allure.story(Story.delete_spending)
    def test_delete_multiple_spendings(self, spends_client: SpendsClient, spendings_list: list[SpendGet]):
        spends_ids = random.sample([spend.id for spend in spendings_list], 2)
        spends_client.clear_spendings(ids=spends_ids)
        all_spends = spends_client.get_all_spendings()
        all_spends_ids = [spend.id for spend in all_spends]
        with allure.step("Проверка, что расходы удалены"):
            assert all(spend_id not in all_spends_ids for spend_id in spends_ids)
            
@pytest.mark.usefixtures(
    "auth_api_token",
    "spends_client",
    "cleanup",
    "all_categories"
)
@pytest.mark.api
@pytest.mark.profile
@pytest.mark.categories
@allure.feature(Feature.categories)
class TestCategoriesAPI:
    
    @TestData.direct_category(["UniqueCategory1", "UniqueCategory2", "UniqueCategory3"])
    @allure.story(Story.add_category)
    def test_add_new_category(self, spends_client: SpendsClient, direct_category: str):
        category_data = spends_client.add_category(direct_category)
        with allure.step("Проверка, что категория добавлена"):
            assert category_data.name == direct_category
            assert category_data.archived == False
            assert category_data.username == spends_client.client_envs.test_username
            
    @TestData.direct_category(["UniqueCategory1"])
    @allure.story(Story.errors)
    def test_add_existing_category(self, spends_client: SpendsClient, direct_category: str, clear_categories):
        category_data = spends_client.add_category(direct_category)
        with allure.step("Проверка, что категория не добавлена"):
            assert category_data["status"] == 409
            assert category_data["title"] == "Conflict"
            assert category_data["detail"] == "Cannot save duplicates"
            assert category_data["instance"] == spends_client.ADD_CATEGORY_ENDPOINT
            assert category_data["type"] == "niffler-spend: Bad request "
            
    @TestData.archived_category(["UniqueArchivedCategory1"])
    @allure.story(Story.errors)
    def test_add_existing_archived_category(self, spends_client: SpendsClient, archived_category: str):
        category_data = spends_client.add_category(archived_category)
        with allure.step("Проверка, что категория не добавлена"):
            assert category_data["status"] == 409
            assert category_data["title"] == "Conflict"
            assert category_data["detail"] == "Cannot save duplicates"
            assert category_data["instance"] == spends_client.ADD_CATEGORY_ENDPOINT
            assert category_data["type"] == "niffler-spend: Bad request "
            
    @TestData.category(["UniqueCategory4"])
    @allure.story(Story.update_category)
    def test_update_category_name(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.name = "UniqueUpdatedCategory4"
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == "UniqueUpdatedCategory4"
            assert updated_category_data.archived == category_data.archived
            assert updated_category_data.username == category_data.username
    
    @TestData.category(["UniqueCategory5"])
    @allure.story(Story.update_category)
    def test_update_category_archived(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.archived = True
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == category_data.name
            assert updated_category_data.archived == True
            assert updated_category_data.username == category_data.username
            
    @TestData.category(["UniqueCategory6"])
    @allure.story(Story.update_category)
    def test_update_category_name_and_archived(self, spends_client: SpendsClient, category: str):
        category_data = spends_client.get_category_by_name(category)
        category_data.name = "UniqueUpdatedCategory6"
        category_data.archived = True
        updated_category_data = spends_client.update_category(category_data)
        with allure.step("Проверка, что категория обновлена"):
            assert updated_category_data.id == category_data.id
            assert updated_category_data.name == "UniqueUpdatedCategory6"
            assert updated_category_data.archived == True
            assert updated_category_data.username == category_data.username
            
    @allure.story(Story.get_category)
    def test_get_active_categories(self, spends_client: SpendsClient, mixed_categories: dict[str, list[str]]):
        active_categories = spends_client.get_all_categories(exclude_archived=True)
        with allure.step("Проверка, что активные категории получены"):
            for category in active_categories:
                assert category.id in mixed_categories["active"]
    
    @allure.story(Story.get_category)
    def test_get_all_categories(self, spends_client: SpendsClient, mixed_categories: dict[str, list[str]]):
        all_categories = spends_client.get_all_categories()
        with allure.step("Проверка, что все категории получены"):
            for category in all_categories:
                assert category.id in mixed_categories["active"] + mixed_categories["archived"]
    