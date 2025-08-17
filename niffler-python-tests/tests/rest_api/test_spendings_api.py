import pytest
import random
import allure
from utils.mock_data import MockData
from utils.allure_data import Epic, Feature, Story
from models.spend import SpendGet, SpendAdd
from models.category import CategoryAdd
from clients.spends_client import SpendsClient
from marks import TestData

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_api_token",
    "spends_client",
    "add_spendings",
    "spendings_list"
)
@pytest.mark.api
@pytest.mark.spendings
@allure.feature(Feature.spendings)
class TestSpendingsAPI:
    
    @TestData.spending_data([
        SpendAdd(
            amount=1500.25,
            category=CategoryAdd(name="Уникальное"),
            currency="EUR",
            description="Уникальная вещь1",
            spendDate="2024-01-15T10:30:00.000Z"
        ),
        SpendAdd(
            amount=2750.50,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальная вещь2",
            spendDate="2024-02-20T14:45:00.000Z"
        ),
        SpendAdd(
            amount=3200.75,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальная вещь3",
            spendDate="2024-03-10T09:15:00.000Z"
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
            amount=4500.99,
            category=CategoryAdd(name="Уникальное"),
            currency="USD",
            description="Уникальная вещь4",
            spendDate="2024-04-25T16:20:00.000Z"
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
    
    @allure.story(Story.update_spending)
    def test_update_spending_amount(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
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
    def test_update_spending_currency(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
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
    def test_update_spending_description(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
        spend = random.choice(spendings_list)
        new_description = "Updated test description"
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
    def test_update_spending_category(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
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
    def test_update_spending_date(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
        spend = random.choice(spendings_list)
        new_date = "2024-12-31T23:59:59.000Z"
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
    def test_update_spending_multiple_fields(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
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
    
    @allure.story(Story.get_spending)
    @pytest.mark.xfail(reason="Добавляется один день к дате")
    def test_get_spending_after_update(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
        spend = random.choice(spendings_list)
        new_amount = 9999.99
        new_description = "Multiple fields updated"
        new_date = "2024-06-15T12:00:00.000Z"
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

    @allure.story(Story.delete_spending)
    @pytest.mark.xdist_group("05_spendings_api_delete_1")
    def test_delete_single_spending(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
        spend_id = random.choice(spendings_list).id
        spends_client.clear_spendings(ids=[spend_id])
        all_spends = spends_client.get_all_spendings()
        all_spends_ids = [spend.id for spend in all_spends]
        with allure.step("Проверка, что расход удален"):
            assert spend_id not in all_spends_ids
            
    @allure.story(Story.delete_spending)
    @pytest.mark.xdist_group("05_spendings_api_delete_2")
    def test_delete_multiple_spendings_api(
        self, spends_client: SpendsClient, spendings_list: list[SpendGet], delete_spendings_lock
    ):
        spends_ids = random.sample([spend.id for spend in spendings_list], 2)
        spends_client.clear_spendings(ids=spends_ids)
        all_spends = spends_client.get_all_spendings()
        all_spends_ids = [spend.id for spend in all_spends]
        with allure.step("Проверка, что расходы удалены"):
            assert all(spend_id not in all_spends_ids for spend_id in spends_ids)