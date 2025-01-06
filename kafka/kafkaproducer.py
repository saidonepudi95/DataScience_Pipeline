"""Kafka producer service."""
import json
from confluent_kafka import Producer
try:
    from src.config.kafka_config import PRODUCER_CONFIG, STOCK_DATA_TOPIC
except ImportError:
    from config.kafka_config import PRODUCER_CONFIG, STOCK_DATA_TOPIC

class KafkaProducerService:
    def __init__(self):
        self.producer = Producer(PRODUCER_CONFIG)
        self.topic = STOCK_DATA_TOPIC
    
    def delivery_report(self, err, msg):
        if err:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def send_message(self, key, value):
        """Send message to Kafka topic."""
        self.producer.produce(
            self.topic,
            key=key,
            value=json.dumps(value),
            callback=self.delivery_report
        )
        self.producer.flush()