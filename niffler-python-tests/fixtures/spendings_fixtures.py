import pytest
from faker import Faker
import random
from models.spend import SpendAdd, CategoryAdd
from models.spend import SpendGet
from utils.generate_datetime import generate_random_datetime
from utils.mock_data import MockData
from clients.spends_client import SpendsClient
from models.config import ClientEnvs
from clients.lock_client import LockManager

################# For spending tests ####################

@pytest.fixture(scope="function")
def spendings_lock(lock_manager: LockManager):
    try:
        lock_manager.acquire_lock(lock_filename="spendings.lock")
        yield
    finally:
        lock_manager.release_lock()

@pytest.fixture(scope="session")
def spendings_data(client_envs: ClientEnvs, faker: Faker):
    spendings: list[SpendAdd] = []
    for _ in range(10):
        while True:
            amount = faker.random_number(digits=3)
            if len(spendings) == 0:
                break
            elif len(spendings) > 0 and amount not in [s.amount for s in spendings]:
                break
        category_name = random.choice(MockData.CATEGORIES)
        currency = random.choice(MockData.CURRENCIES)
        description = faker.sentence(nb_words=2, variable_nb_words=True)
        spend_date = generate_random_datetime()
        data = SpendAdd(
            amount=amount,
            category=CategoryAdd(name=category_name),
            currency=currency,
            description=description,
            spendDate=spend_date,
            username=client_envs.test_username
        )
        spendings.append(data)
        
    return spendings

@pytest.fixture(scope="class")
def add_spendings(spends_client: SpendsClient, spendings_data: list[SpendAdd]):
    all_spendings = spends_client.get_all_spendings()
    for data in spendings_data:
        amount = data.amount
        category = data.category.name
        currency = data.currency
        description = data.description
        if any([amount in [s.amount for s in all_spendings], 
                category in [s.category.name for s in all_spendings], 
                currency in [s.currency for s in all_spendings], 
                description in [s.description for s in all_spendings]]):
            continue
        spends_client.add_spending(data)
    yield
    
@pytest.fixture(scope="function")
def spendings_list(spends_client: SpendsClient) -> list[SpendGet]:
    return spends_client.get_all_spendings()