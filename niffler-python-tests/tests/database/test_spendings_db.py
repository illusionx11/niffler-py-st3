import pytest
import allure
from utils.allure_data import Epic, Feature, Story
from models.config import ClientEnvs
from models.spend import SpendAdd, CategoryAdd
from clients.spends_client import SpendsClient
from databases.spends_db import SpendsDb
from marks import TestData
from utils.generate_datetime import generate_random_datetime
import logging
from datetime import datetime

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_api_token",
    "spends_client",
    "client_envs",
    "spends_db"
)
@pytest.mark.spendings
@pytest.mark.database
@allure.feature(Feature.spendings)
class TestSpendingsDatabase:
    
    @TestData.spending_data([
        SpendAdd(
            amount=1000.26,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные шляпы",
            spendDate="2009-10-13T22:05:31.000+00:00"
        )
    ])
    @pytest.mark.xfail(reason="spendDate записывается в БД с ошибкой, добавляется +1 день")
    @allure.story(Story.add_spending)
    def test_added_spending_in_database(
        self, 
        spends_client: SpendsClient, 
        spending_data: SpendAdd, 
        spends_db: SpendsDb
    ):
        added_spending = spends_client.add_spending(data=spending_data)
        user_spending = spends_db.get_spending_by_id(id=added_spending.id)
        with allure.step(f"Проверка, что расход есть в базе данных"):
            assert user_spending is not None
            assert user_spending.amount == spending_data.amount
            assert user_spending.currency == spending_data.currency
            assert user_spending.description == spending_data.description
            assert user_spending.spend_date == datetime.fromisoformat(spending_data.spendDate).date()
        
    @TestData.spending_data([
        SpendAdd(
            amount=162.23,
            category=CategoryAdd(name="Уникальное"),
            currency="RUB",
            description="Уникальные кружки",
            spendDate="2015-10-13T22:05:31.000+00:00"
        )
    ])
    @allure.story(Story.delete_spending)
    def test_deleted_spending_not_in_database(
        self,
        spends_client: SpendsClient,
        spending_data: SpendAdd,
        client_envs: ClientEnvs,
        spends_db: SpendsDb
    ):
        added_spending_data = spends_client.add_spending(data=spending_data)
        logging.info(f"Добавлен расход {added_spending_data}")
        spends_client.clear_spendings(ids=[added_spending_data.id])
        logging.info(f"Удален расход с id {added_spending_data.id}")
        all_spendings = spends_db.get_user_spendings(username=client_envs.test_username)
        spending = next(
            (
                s for s in all_spendings if s.id == added_spending_data.id
            ),
            None
        )
        with allure.step(f"Проверка, что расхода нет в базе данных"):
            assert spending is None