API_KEY = "1PNA8NLPBRRMCHAF"

# config.py
POSTGRESQL_CONFIG = {
    "dbname": "feature_store",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

CASSANDRA_CONFIG = {
    "contact_points": ['127.0.0.1'],
    "port": 9042,
    "auth_provider": {
        "username": "cassandra",
        "password": "cassandra"
    }
}

KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'alpha_vantage_consumer_group',
    'auto.offset.reset': 'earliest'
}
