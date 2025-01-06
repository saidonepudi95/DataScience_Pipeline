from confluent_kafka import Consumer, KafkaError
from cassandra.cluster import Cluster
import json
import uuid
from datetime import datetime

# Kafka Configuration
KAFKA_CONF = {'bootstrap.servers': 'localhost:9092', 'group.id': 'kafka_to_cassandra', 'auto.offset.reset': 'earliest'}
KAFKA_TOPIC = "alpha_vantage_data"

# Cassandra Configuration
CASSANDRA_CONF = {"hosts": ["localhost"], "port": 9042, "keyspace": "kafka_keyspace"}

def connect_cassandra(config):
    cluster = Cluster(config["hosts"], port=config["port"])
    session = cluster.connect()
    session.set_keyspace(config["keyspace"])
    session.execute("""
        CREATE TABLE IF NOT EXISTS kafka_unstructured (
            id uuid PRIMARY KEY, kafka_key text, kafka_value text, ingested_at timestamp
        )
    """)
    print("✅ Connected to Cassandra successfully.")
    return session

def main():
    consumer = Consumer(KAFKA_CONF)
    consumer.subscribe([KAFKA_TOPIC])
    cassandra_session = connect_cassandra(CASSANDRA_CONF)

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
                cassandra_session.execute(
                    "INSERT INTO kafka_unstructured (id, kafka_key, kafka_value, ingested_at) VALUES (%s, %s, %s, %s)",
                    (uuid.uuid4(), key, json.dumps(value), datetime.now())
                )
                print("✅ Data inserted into Cassandra.")
            except Exception as e:
                print(f"❌ Error processing message: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down consumer.")
    finally:
        consumer.close()
        print("✅ Consumer closed.")

if __name__ == "__main__":
    main()
