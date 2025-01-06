"""Cassandra database operations."""
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import json
from datetime import datetime
from src.config.database import CASSANDRA_CONFIG

class CassandraDB:
    def __init__(self):
        auth_provider = PlainTextAuthProvider(
            username=CASSANDRA_CONFIG['username'],
            password=CASSANDRA_CONFIG['password']
        )
        self.cluster = Cluster(
            contact_points=CASSANDRA_CONFIG['contact_points'],
            port=CASSANDRA_CONFIG['port'],
            auth_provider=auth_provider,
            protocol_version=CASSANDRA_CONFIG['protocol_version']
        )
        self.session = self.cluster.connect('kafka_keyspace')
        self.insert_query = self.session.prepare("""
            INSERT INTO kafka_features (id, kafka_key, kafka_value, ingested_at)
            VALUES (?, ?, ?, ?)
        """)
    
    def insert_data(self, id, key, value):
        """Insert unstructured data into Cassandra."""
        try:
            self.session.execute(
                self.insert_query,
                (id, key, json.dumps(value), datetime.now())
            )
        except Exception as e:
            print(f"Cassandra Error: {e}")
    
    def close(self):
        """Close database connection."""
        if self.cluster:
            self.cluster.shutdown()