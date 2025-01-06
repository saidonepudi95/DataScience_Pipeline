import requests
import json
from confluent_kafka import Producer

# Alpha Vantage API Configuration
API_KEY = "1PNA8NLPBRRMCHAF"  # Replace with your actual API key
BASE_URL = "https://www.alphavantage.co/query"

# Kafka Configuration
KAFKA_CONF = {
    'bootstrap.servers': 'localhost:9092'
}
KAFKA_TOPIC = "alpha_vantage_data"

# Initialize Kafka Producer
producer = Producer(KAFKA_CONF)

def delivery_report(err, msg):
    """Callback function to confirm message delivery."""
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(f"✅ Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def fetch_data(symbol, interval):
    """Fetch stock data from Alpha Vantage API."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        print("✅ Data fetched successfully from Alpha Vantage.")
        return response.json()
    else:
        print(f"❌ Failed to fetch data. HTTP Status Code: {response.status_code}")
        return None

def produce_to_kafka(data):
    """Send fetched data to Kafka."""
    time_series = data.get("Time Series (5min)", {})  # Adjust the key based on Alpha Vantage API response
    if not time_series:
        print("❌ No time series data found.")
        return

    print("🚀 Sending data to Kafka...")
    for timestamp, values in time_series.items():
        message = {
            "timestamp": timestamp,
            "open": values["1. open"],
            "high": values["2. high"],
            "low": values["3. low"],
            "close": values["4. close"],
            "volume": values["5. volume"]
        }
        producer.produce(
            KAFKA_TOPIC,
            key=timestamp,
            value=json.dumps(message),
            callback=delivery_report
        )
        producer.flush()  # Ensure message is sent before continuing
    print("✅ Data sent to Kafka successfully.")

def main():
    stock_symbol = "IBM"  # Example: Stock symbol
    time_interval = "5min"  # Example: Data interval

    print(f"Fetching data for {stock_symbol} at {time_interval} interval...")
    stock_data = fetch_data(stock_symbol, time_interval)
    if stock_data:
        produce_to_kafka(stock_data)
    else:
        print("❌ No data fetched. Exiting...")

if __name__ == "__main__":
    main()
