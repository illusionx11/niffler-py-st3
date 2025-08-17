import logging
from typing import Sequence
from models.config import ServerEnvs
from confluent_kafka import TopicPartition, Consumer, Producer
from confluent_kafka.admin import AdminClient
from models.user import UserName
import json

from utils.waiters import wait_until_timeout

class KafkaClient:
    """Класс для взаимодействия с кафкой"""

    def __init__(
            self,
            server_envs: ServerEnvs,
            client_id: str = 'tester',
            group_id: str = 'tester',

    ):
        self.server = server_envs.kafka_address
        self.admin = AdminClient(
            {"bootstrap.servers": f"{self.server}:9092"}
        )
        self.producer = Producer(
            {"bootstrap.servers": f"{self.server}:9092"}
        )
        self.consumer = Consumer(
            {
                "bootstrap.servers": f"{self.server}:9092",
                "group.id": group_id,
                "client.id": client_id,
                "auto.offset.reset": "latest",
                "enable.auto.commit": False,
                "enable.ssl.certificate.verification": False
            }
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.consumer.close()
        self.producer.flush()

    def list_topics_names(self, attempts: int = 5):
        """Вернуть список доступных топиков"""
        try:
            topics = self.admin.list_topics(timeout=attempts).topics
            return [topics.get(item).topic for item in topics]
        except RuntimeError:
            logging.error("no topics in kafka")

    @wait_until_timeout
    def consume_message(self, partitions, **kwargs):
        """Вернуть последнее после определенной позиции сообщение"""
        self.consumer.assign(partitions)
        try:
            message = self.consumer.poll(1.0)
            return message.value()
        except AttributeError:
            pass

    def get_last_offset(self, topic: str = "", partition_id=0):
        """Вернуть последнюю позицию партиции"""
        partition = TopicPartition(topic, partition_id)
        try:
            low, high = self.consumer.get_watermark_offsets(partition, timeout=10)
            return high
        except Exception as err:
            logging.error("probably no such topic: %s: %s", topic, err)

    def log_msg_and_json(self, topic_partitions):
        msg = self.consume_message(topic_partitions, timeout=25)
        logging.info(msg)
        return msg

    def subscribe_listen_new_offsets(self, topic):
        
        self.consumer.subscribe([topic])
        p_ids = self.consumer.list_topics(topic).topics[topic].partitions.keys()
        partitions_offsets_event = {k: self.get_last_offset(topic, k) for k in p_ids}
        logging.info(f'{topic} offsets: {partitions_offsets_event}')
        topic_partitions = [TopicPartition(topic, k, v) for k, v in partitions_offsets_event.items()]
        return topic_partitions
    
    def delivery_callback(self, err, msg):
        """Callback для отчёта о доставке сообщений"""
        if err:
            logging.error(f"ERROR: Message failed delivery: {err}")
        else:
            logging.info(f"Message delivered to {msg.topic()} [partition {msg.partition()}] | Offset {msg.offset()}")
            
    def send_test_message(self, topic: str, message: dict):
        """Отправить тестовое сообщение в указанный топик"""
        try:
            self.producer.produce(
                topic,
                json.dumps(message).encode("utf-8"),
                on_delivery=self.delivery_callback,
                headers={"__TypeId__": "guru.qa.niffler.model.UserJson"}
            )
            self.producer.flush()
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            raise
        
    def wait_for_user_event(self, topic_partitions, expected_username: str, timeout: int = 10):
        """Ждать событие для конкретного пользователя"""
        import time
        end_time = time.time() + timeout

        self.consumer.assign(topic_partitions)
        while time.time() < end_time:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue

            try:
                decoded = json.loads(msg.value().decode("utf-8"))
            except Exception:
                continue

            if decoded.get("username") == expected_username:
                return decoded

        raise AssertionError(f"Не дождались события в Kafka для {expected_username}")