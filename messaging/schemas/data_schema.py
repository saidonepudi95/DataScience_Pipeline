# src/schema/data_schema.py
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

# Define the Avro schema for structured data
STRUCTURED_SCHEMA = """
{
    "type": "record",
    "name": "StockData",
    "fields": [
        {"name": "timestamp", "type": "string"},
        {"name": "open", "type": "string"},
        {"name": "high", "type": "string"},
        {"name": "low", "type": "string"},
        {"name": "close", "type": "string"},
        {"name": "volume", "type": "string"}
    ]
}
"""

# Schema Registry client
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)
