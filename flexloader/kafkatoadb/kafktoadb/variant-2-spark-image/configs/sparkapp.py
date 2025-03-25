import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, schema_of_json
from pyspark.sql.types import StructType, StringType
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_spark_session():
    """Создание и настройка SparkSession"""
    try:
        # Получаем пути к сертификатам из переменных окружения или используем встроенные пути
        keystore_location = os.environ.get("SPARK_KAFKA_KEYSTORE_LOCATION", "/opt/spark/conf/certs/kafka.client.keystore.jks")
        truststore_location = os.environ.get("SPARK_KAFKA_TRUSTSTORE_LOCATION", "/opt/spark/conf/certs/kafka.client.truststore.jks")
        
        return SparkSession.builder \
            .appName("KafkaToADB") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23") \
            .config("spark.sql.debug.maxToStringFields", 100) \
            .config("spark.executor.memory", "2g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", 10) \
            .config("spark.default.parallelism", 10) \
            .config("spark.kafka.ssl.truststore.location", truststore_location) \
            .config("spark.kafka.ssl.keystore.location", keystore_location) \
            .config("spark.kafka.ssl.truststore.password", os.environ.get("KAFKA_TRUSTSTORE_PASSWORD")) \
            .config("spark.kafka.ssl.keystore.password", os.environ.get("KAFKA_KEYSTORE_PASSWORD")) \
            .config("spark.kafka.security.protocol", "SSL") \
            .getOrCreate()
    except Exception as e:
        logger.error(f"Ошибка при создании SparkSession: {str(e)}")
        sys.exit(1)

def read_from_kafka(spark, kafka_bootstrap_servers, kafka_topic):
    """Чтение данных из Kafka с обработкой ошибок"""
    try:
        logger.info(f"Начало чтения из топика Kafka: {kafka_topic}")
        return spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("subscribe", kafka_topic) \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()
    except Exception as e:
        logger.error(f"Ошибка при чтении из Kafka: {str(e)}")
        raise

def process_data(df):
    """Обработка данных из Kafka"""
    try:
        logger.info("Начало обработки данных")
        
        # Определение схемы данных (замените на вашу схему)
        schema = StructType() \
            .add("field1", StringType()) \
            .add("field2", StringType())

        # Преобразование JSON данных
        df = df.selectExpr("CAST(value AS STRING) as json_value")
        df = df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")
        
        # Добавьте здесь дополнительную обработку данных
        
        logger.info(f"Обработано записей: {df.count()}")
        return df
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {str(e)}")
        raise

def write_to_adb(df, adb_properties):
    """Запись данных в ADB с обработкой ошибок"""
    try:
        logger.info(f"Начало записи в таблицу: {adb_properties['dbtable']}")
        
        df.write \
            .format("jdbc") \
            .option("url", adb_properties["url"]) \
            .option("dbtable", adb_properties["dbtable"]) \
            .option("user", adb_properties["user"]) \
            .option("password", adb_properties["password"]) \
            .option("driver", adb_properties["driver"]) \
            .option("batchsize", 1000) \
            .option("isolationLevel", "READ_COMMITTED") \
            .mode("append") \
            .save()
        
        logger.info("Запись в ADB успешно завершена")
    except Exception as e:
        logger.error(f"Ошибка при записи в ADB: {str(e)}")
        raise

def main():
    """Основная функция приложения"""
    try:
        # Создание SparkSession
        spark = create_spark_session()
        
        # Параметры подключения к Kafka
        kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka-service:9092")
        kafka_topic = os.environ.get("KAFKA_TOPIC", "your_topic_name")
        
        # Параметры подключения к ADB (получаем из webhook в коннекторе Airflow)
        adb_properties = {
            "url": f"jdbc:postgresql://{os.environ['ADB_URL']}/your_database",
            "dbtable": os.environ.get("ADB_TABLE", "your_schema.your_table"),
            "user": os.environ["ADB_USER"],
            "password": os.environ["ADB_PASSWORD"],
            "driver": "org.postgresql.Driver"
        }
        
        # Чтение данных из Kafka
        df = read_from_kafka(spark, kafka_bootstrap_servers, kafka_topic)
        
        # Обработка данных
        df = process_data(df)
        
        # Запись в ADB
        write_to_adb(df, adb_properties)
        
        logger.info("Обработка данных успешно завершена")
    except Exception as e:
        logger.error(f"Критическая ошибка в приложении: {str(e)}")
        sys.exit(1)
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("SparkSession остановлен")

if __name__ == "__main__":
    main() 