import pytest
import allure
from utils.allure_data import Epic, Feature, Story
import time
from clients.oauth_client import OAuthClient
from clients.kafka_client import KafkaClient
from models.user import UserName
from http import HTTPStatus
from models.config import ClientEnvs
from databases.userdata_db import UserdataDb
from marks import TestData
from models.user import UserData

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "auth_client",
    "kafka_client",
    "userdata_db"
)
@pytest.mark.kafka
@pytest.mark.registration
@allure.feature(Feature.registration)
@allure.story(Story.register_user)
class TestAuthRegistrationKafka:
    
    @TestData.new_user([UserData(username="NifflerKafkaUser", password="PassWordGo0d")])
    def test_message_should_be_produced_to_kafka_after_successful_registration(
        self, 
        auth_client: OAuthClient, 
        kafka_client: KafkaClient,
        new_user: UserData
    ):
        topic_partitions = kafka_client.subscribe_listen_new_offsets("users")
        
        with allure.step("API Регистрация пользователя"):
            result = auth_client.register(new_user.username, new_user.password)
            assert result.status_code == HTTPStatus.CREATED
        
        with allure.step(f"Ожидание события в Kafka для {new_user.username}"):
            event = kafka_client.wait_for_user_event(topic_partitions, new_user.username, timeout=15)
        
        with allure.step("Проверка содержания сообщения"):
            UserName.model_validate(event)
            assert event['username'] == new_user.username
    
    @TestData.new_user([UserData(username="NifflerKafkaUser", password="PassWordGo0d")])
    def test_userdata_db_should_process_messages_from_kafka_producer(
        self, 
        kafka_client: KafkaClient, 
        userdata_db: UserdataDb,
        new_user: UserData
    ):
        msg = UserName(username=new_user.username).model_dump()
        
        with allure.step("Отправка сообщения через Kafka producer"):
            kafka_client.send_test_message(topic="users", message=msg)
        
        with allure.step("Проверка, что сообщение из kafka появилось в БД userdata"):
            # Механизм таймаута для параллельных тестов
            start_time = time.time()
            while time.time() - start_time < 10:
                userdata_db_user = userdata_db.get_user_by_name(new_user.username)
                if userdata_db_user is not None:
                    break
                time.sleep(0.5)
            assert userdata_db_user.username == new_user.username