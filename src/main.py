# main.py
from confluent_kafka import Consumer, KafkaError
from config import POSTGRESQL_CONFIG, CASSANDRA_CONFIG, KAFKA_CONFIG
from db_handlers import DatabaseHandler
from message_processor import MessageProcessor
import json

def main():
    # Initialize components
    db_handler = DatabaseHandler(POSTGRESQL_CONFIG, CASSANDRA_CONFIG)
    processor = MessageProcessor()
    consumer = Consumer(KAFKA_CONFIG)
    consumer.subscribe(['alpha_vantage_data'])

    try:
        print("Consuming messages from Kafka...")
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Error: {msg.error()}")
                    break

            # Process message
            key, value = processor.process_message(msg)
            if value is None:
                continue

            print(f"Received message: {value}")

            try:
                # Route to appropriate database
                if processor.is_structured(value):
                    db_handler.store_structured_data(key, value)
                    print("Inserted into PostgreSQL")
                else:
                    db_handler.store_unstructured_data(key, value)
                    print("Inserted into Cassandra")
            except Exception as e:
                print(f"Error storing message: {e}")

    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
        db_handler.cleanup()
        print("Resources cleaned up.")

if __name__ == "__main__":
    main()
