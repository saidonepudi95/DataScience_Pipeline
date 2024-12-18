# src/main.py
from config.config import KAFKA_CONFIG, POSTGRES_CONFIG, CASSANDRA_CONFIG
from src.api.alpha_vantage import AlphaVantageHandler
import sys
from src.database.postgres_handler import PostgresHandler
from src.database.cassandra_handler import CassandraHandler

def main():
    # Initialize handlers
    api_handler = AlphaVantageHandler(API_KEY, KAFKA_CONFIG)
    pg_handler = PostgresHandler(POSTGRES_CONFIG)
    cassandra_handler = CassandraHandler(CASSANDRA_CONFIG)

    # Fetch and process data
    api_handler.fetch_and_produce("IBM", "5min")

if __name__ == "__main__":
    main()
