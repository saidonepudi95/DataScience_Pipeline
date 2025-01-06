from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
from confluent_kafka import Producer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'alpha_vantage': {
        'api_key': "1PNA8NLPBRRMCHAF",
        'base_url': "https://www.alphavantage.co/query",
        'default_symbol': 'IBM',
        'default_interval': '5min'
    },
    'kafka': {
        'bootstrap.servers': 'localhost:9092',
        'topic': "alpha_vantage_data"
    }
}

class AlphaVantageKafkaPipeline:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': CONFIG['kafka']['bootstrap.servers'],
            'client.id': 'alpha_vantage_producer',
            'linger.ms': 100,  # Reduce wait time for batching
            'batch.num.messages': 1000  # Increase batch size
        })

    def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    def fetch_stock_data(self, symbol, interval):
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": CONFIG['alpha_vantage']['api_key']
            }
            start_time = datetime.now()
            response = requests.get(CONFIG['alpha_vantage']['base_url'], params=params, timeout=10)
            logger.info(f"API fetch time: {datetime.now() - start_time}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def process_and_send_to_kafka(self, time_series):
        start_time = datetime.now()
        for timestamp, values in time_series.items():
            try:
                message = {
                    "timestamp": timestamp,
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"])
                }
                self.producer.produce(
                    CONFIG['kafka']['topic'],
                    key=timestamp,
                    value=json.dumps(message),
                    callback=self.delivery_report
                )
                self.producer.poll(0)
            except (ValueError, KeyError) as e:
                logger.error(f"Error processing data for timestamp {timestamp}: {str(e)}")
                continue
        logger.info(f"Kafka production time: {datetime.now() - start_time}")

    def fetch_and_produce_data(self, **kwargs):
        stock_symbol = kwargs.get('stock_symbol', CONFIG['alpha_vantage']['default_symbol'])
        time_interval = kwargs.get('time_interval', CONFIG['alpha_vantage']['default_interval'])

        try:
            logger.info(f"Fetching data for {stock_symbol} at {time_interval} interval")
            data = self.fetch_stock_data(stock_symbol, time_interval)
            time_series_key = f"Time Series ({time_interval})"
            time_series = data.get(time_series_key)

            if not time_series:
                logger.error("No time series data found in the response")
                return

            logger.info("Processing and sending data to Kafka")
            self.process_and_send_to_kafka(time_series)

            self.producer.flush()
            logger.info("Successfully completed data pipeline execution")

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            raise

# DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=10)
}

with DAG(
    'api_to_kafka_pipeline',
    default_args=default_args,
    description='Fetch data from Alpha Vantage API and send to Kafka',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['stock_data', 'kafka']
) as dag:

    pipeline = AlphaVantageKafkaPipeline()

    send_data_to_kafka = PythonOperator(
        task_id='fetch_and_produce_data',
        python_callable=pipeline.fetch_and_produce_data,
        op_kwargs={
            'stock_symbol': 'IBM',
            'time_interval': '5min'
        }
    )

    send_data_to_kafka
