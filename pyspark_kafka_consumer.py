import os
from datetime import datetime

from pyspark.sql.types import *
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, lit, col
from pyspark.sql import functions as F

# replace 3.2.1
spark_version = "3.2.1"
kafka_topic = "twitch-streams"
os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:{spark_version},org.apache.spark:spark-sql-kafka-0-10_2.12:{spark_version} pyspark-shell'

spark = SparkSession \
          .builder \
          .appName("spark_kafka_consumer") \
          .getOrCreate()

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "earliest") \
    .load()

query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .format("console") \
    .option("checkpointLocation", "pyspark_logs/") \
    .start()

query.awaitTermination()