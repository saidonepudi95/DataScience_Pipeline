from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# PostgreSQL Configuration
POSTGRESQL_CONF = {
    "url": "jdbc:postgresql://postgres:5432/feature_store",
    "table": "kafka_features",
    "user": "admin",
    "password": "admin",
    "driver": "org.postgresql.Driver"
}

PROCESSED_TABLE = "processed_data"

def main():
    spark = None
    try:
        # Initialize SparkSession
        spark = SparkSession.builder \
            .appName("Data Processing with Spark") \
            .getOrCreate()
        
        logger.info("✅ Spark session initialized.")

        # Read data from PostgreSQL
        logger.info(f"📥 Reading data from PostgreSQL table: {POSTGRESQL_CONF['table']}")
        df = spark.read.format("jdbc") \
            .option("url", POSTGRESQL_CONF["url"]) \
            .option("dbtable", POSTGRESQL_CONF["table"]) \
            .option("user", POSTGRESQL_CONF["user"]) \
            .option("password", POSTGRESQL_CONF["password"]) \
            .option("driver", POSTGRESQL_CONF["driver"]) \
            .load()

        logger.info("✅ Data successfully loaded from PostgreSQL.")
        
        # Display schema and initial records (optional for debugging)
        df.printSchema()
        df.show(5)

        # Perform processing (example: filter and add a new column)
        logger.info("🔄 Processing data...")
        processed_df = df.filter(col("kafka_value").isNotNull()) \
            .withColumn("processed_at", current_timestamp())

        logger.info("✅ Data processing completed.")

        # Write processed data back to PostgreSQL
        logger.info(f"📤 Writing processed data back to PostgreSQL table: {PROCESSED_TABLE}")
        processed_df.write.format("jdbc") \
            .option("url", POSTGRESQL_CONF["url"]) \
            .option("dbtable", PROCESSED_TABLE) \
            .option("user", POSTGRESQL_CONF["user"]) \
            .option("password", POSTGRESQL_CONF["password"]) \
            .option("driver", POSTGRESQL_CONF["driver"]) \
            .mode("overwrite") \
            .save()

        logger.info("✅ Processed data successfully saved to PostgreSQL.")
    except Exception as e:
        logger.error(f"❌ Error during data processing: {e}")
    finally:
        # Stop Spark session
        if spark:
            spark.stop()
            logger.info("✅ Spark session stopped.")

if __name__ == "__main__":
    main()
