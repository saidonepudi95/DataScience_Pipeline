-- Create keyspace for unstructured data
CREATE KEYSPACE IF NOT EXISTS kafka_keyspace
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- Use the keyspace
USE kafka_keyspace;

-- Create table for unstructured data
CREATE TABLE IF NOT EXISTS kafka_features (
    id uuid PRIMARY KEY,
    kafka_key text,
    kafka_value text,
    ingested_at timestamp,
    created_at timestamp DEFAULT toTimestamp(now())
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS ON kafka_features(kafka_key);
CREATE INDEX IF NOT EXISTS ON kafka_features(ingested_at);

-- Create materialized view for time-based queries
CREATE MATERIALIZED VIEW IF NOT EXISTS kafka_features_by_time AS
    SELECT * FROM kafka_features
    WHERE ingested_at IS NOT NULL AND id IS NOT NULL
    PRIMARY KEY (ingested_at, id);