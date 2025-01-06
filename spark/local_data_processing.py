from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, to_date

# PostgreSQL Configuration
POSTGRES_CONF = {
    "url": "jdbc:postgresql://localhost:5432/feature_store",
    "driver": "org.postgresql.Driver",
    "user": "admin",
    "password": "admin"
}

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("LocalDataProcessing") \
        .config("spark.jars", "./postgresql-42.7.3.jar") \
        .getOrCreate()

    # Step 1: Load Data from PostgreSQL
    print("Loading data from PostgreSQL...")
    raw_df = spark.read.format("jdbc") \
        .option("url", POSTGRES_CONF["url"]) \
        .option("driver", POSTGRES_CONF["driver"]) \
        .option("dbtable", "kafka_features") \
        .option("user", POSTGRES_CONF["user"]) \
        .option("password", POSTGRES_CONF["password"]) \
        .load()

    print("Raw Data Schema:")
    raw_df.printSchema()

    # Step 2: Process Data
    print("Processing data...")
    processed_df = raw_df.withColumn("date", to_date(col("kafka_key"))) \
                         .groupBy("date") \
                         .agg(avg(col("kafka_value").getItem("volume").cast("double")).alias("avg_volume"))

    print("Processed Data Schema:")
    processed_df.printSchema()

    # Step 3: Write Processed Data Back to PostgreSQL
    print("Saving processed data to PostgreSQL...")
    processed_df.write.format("jdbc") \
        .option("url", POSTGRES_CONF["url"]) \
        .option("driver", POSTGRES_CONF["driver"]) \
        .option("dbtable", "processed_data") \
        .option("user", POSTGRES_CONF["user"]) \
        .option("password", POSTGRES_CONF["password"]) \
        .mode("overwrite") \
        .save()
    print("Data successfully saved!")

if __name__ == "__main__":
    main()
