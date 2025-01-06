from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("TestScript") \
    .getOrCreate()

print("Spark session created successfully!")
