from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql import functions

"""
kafka version: kafka_2.11-2.4.1
export SPARK_HOME=/usr/lib/spark-2.3.4-bin-hadoop2.6
$SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.4 structured_streaming_kafka.py
Note: this code has been successfully tested with 2.3.4-bin-hadoop2.7, but it does not work with spark 2.4.*
export SPARK_HOME=/home/cloudera/spark-2.3.4-bin-hadoop2.7
bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.4 structured_streaming_kafka.py
"""


def main():
    conf = SparkConf().setMaster("local[*]")

    spark = (SparkSession
             .builder
             .config(conf=conf)
             .appName("StructuredStreamingWithKafka")
             .getOrCreate())

    topic = "demo"
    # Source: subscribe to 1 topic in Kafka
    raw = (spark
           .readStream
           .format("kafka")
           .option("kafka.bootstrap.servers", "localhost:9092")
           .option("subscribe", topic)
           .option("startingOffsets", "earliest")
           .option("maxOffsetsPerTrigger","100")
           .option("failOnDataLoss", "false")
           .load())
    
    # transformation
    enriched = (raw
               .withColumn("key", functions.expr("CAST(key AS STRING)"))
               .withColumn("value", functions.expr("CAST(value AS STRING)")))

    # sink
    (enriched
     .writeStream
     .format("console")
     .option("truncate", False)
     .option("numRows", 1000)
     .start())

    spark.streams.awaitAnyTermination()
    print("Process is complete")
    spark.stop()

if __name__ == "__main__":
    main()
