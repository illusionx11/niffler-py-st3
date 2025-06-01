import pytest
import allure
import json
import logging
from allure_data import Epic, Feature, Story
from faker import Faker
from clients.oauth_client import OAuthClient
from clients.kafka_client import KafkaClient
from models.user import UserName, User
from http import HTTPStatus
from models.config import ClientEnvs
from databases.userdata_db import UserdataDb

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.fixture(scope="module")
def clear_users(userdata_db: UserdataDb, client_envs: ClientEnvs):  
    yield
    for user in userdata_db.get_users():
        if user.username == client_envs.test_username:
            continue
        userdata_db.delete_user(user.id)
    logging.info("Cleaned users on test teardown")

@pytest.mark.usefixtures(
    "auth_client",
    "kafka_client",
    "userdata_db",
    "clear_users"
)
@pytest.mark.kafka
@allure.feature(Feature.kafka)
class TestAuthRegistrationKafka:
    
    @allure.story(Story.register_user)
    def test_message_should_be_produced_to_kafka_after_successful_registration(
        self, 
        auth_client: OAuthClient, 
        kafka_client: KafkaClient
    ):
        username = Faker().first_name()
        password = Faker().password(special_chars=False)
        
        topic_partitions = kafka_client.subscribe_listen_new_offsets("users")
        
        with allure.step("API Регистрация пользователя"):
            result = auth_client.register(username, password)
            assert result.status_code == HTTPStatus.CREATED
        
        event = kafka_client.log_msg_and_json(topic_partitions)
        
        with allure.step("Проверка, что сообщение из kafka существует"):
            assert event != '' and event != b''
        
        with allure.step("Проверка содержания сообщения"):
            decoded_event = json.loads(event.decode('utf8'))
            UserName.model_validate(decoded_event)
            assert decoded_event['username'] == username
    
    def test_userdata_db_should_process_messages_from_kafka_producer(
        self, 
        kafka_client: KafkaClient, 
        userdata_db: UserdataDb
    ):
        username = Faker().first_name()
        msg = UserName(username=username).model_dump()
        
        with allure.step("Отправка сообщения через Kafka producer"):
            kafka_client.send_test_message(topic="users", message=msg)
        
        with allure.step("Проверка, что сообщение из kafka появилось в БД userdata"):
            userdata_db_user = userdata_db.get_user_by_name(username)
            assert userdata_db_user.username == username