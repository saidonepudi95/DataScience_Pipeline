"""PostgreSQL database operations."""
import psycopg2
import json
from datetime import datetime
from config.database import PG_CONFIG

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(**PG_CONFIG)
        self.cursor = self.conn.cursor()
    
    def insert_data(self, key, value):
        """Insert structured data into PostgreSQL."""
        try:
            self.cursor.execute(
                """
                INSERT INTO kafka_features (kafka_key, kafka_value, ingested_at)
                VALUES (%s, %s, %s)
                """,
                (key, json.dumps(value), datetime.now())
            )
            self.conn.commit()
        except Exception as e:
            print(f"PostgreSQL Error: {e}")
            self.conn.rollback()
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()