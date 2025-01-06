-- Create the feature store database
CREATE DATABASE feature_store;

-- Connect to the database
\c feature_store;

-- Create table for structured data
CREATE TABLE kafka_features (
    id SERIAL PRIMARY KEY,
    kafka_key TEXT,
    kafka_value JSONB,
    ingested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_kafka_features_key ON kafka_features(kafka_key);
CREATE INDEX idx_kafka_features_ingested_at ON kafka_features(ingested_at);
CREATE INDEX idx_kafka_features_value ON kafka_features USING gin (kafka_value);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
