"""Main entry point for the application."""
import os
from src.services.alpha_vantage import AlphaVantageService
from src.services.kafka_producer import KafkaProducerService
from src.services.data_consumer import DataConsumerService

def main():
    # Initialize services
    alpha_vantage = AlphaVantageService(api_key="1PNA8NLPBRRMCHAF")
    kafka_producer = KafkaProducerService()
    data_consumer = DataConsumerService()
    
    # Start the consumer service
    data_consumer.start_consuming()

if __name__ == "__main__":
    main()