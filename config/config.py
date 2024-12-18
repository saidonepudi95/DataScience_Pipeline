API_KEY = "1PNA8NLPBRRMCHAF"

KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092'
}

POSTGRESQL_CONFIG = {
    "dbname": "feature_store",
    "user": "admin",
    "password": "admin",
    "host": "localhost",
    "port": "5432"
}

CASSANDRA_CONFIG = {
    "hosts": ["localhost"],
    "keyspace": "kafka_keyspace"
}
