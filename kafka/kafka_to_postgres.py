from confluent_kafka import Consumer, KafkaError
import psycopg2
import json
from datetime import datetime

POSTGRES_CONF = {
    "dbname": "feature_store",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

KAFKA_CONF = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'kafka_to_db_group',
    'auto.offset.reset': 'earliest'
}

KAFKA_TOPIC = "alpha_vantage_data"

def connect_postgres(config):
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL successfully.")
        return conn, cursor
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        return None, None

def store_data_postgres(cursor, conn, data, key):
    try:
        insert_query = """
            INSERT INTO kafka_features (kafka_key, kafka_value, ingested_at)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (key, json.dumps(data), datetime.now()))
        conn.commit()
        print("✅ Data inserted into PostgreSQL successfully.")
    except Exception as e:
        print(f"❌ Error inserting data into PostgreSQL: {e}")
        conn.rollback()

def main():
    conn, cursor = connect_postgres(POSTGRES_CONF)
    if not conn or not cursor:
        return

    consumer = Consumer(KAFKA_CONF)
    consumer.subscribe([KAFKA_TOPIC])

    print(f"🚀 Listening to Kafka topic: {KAFKA_TOPIC}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Kafka Error: {msg.error()}")
                break

            try:
                value = json.loads(msg.value().decode('utf-8'))
                key = msg.key().decode('utf-8') if msg.key() else None
                store_data_postgres(cursor, conn, value, key)
            except json.JSONDecodeError as e:
                print(f"❌ Failed to decode message: {e}")

    except KeyboardInterrupt:
        print("\n🛑 Shutting down consumer...")
    finally:
        consumer.close()
        cursor.close()
        conn.close()
        print("✅ All resources cleaned up.")

if __name__ == "__main__":
    main()
