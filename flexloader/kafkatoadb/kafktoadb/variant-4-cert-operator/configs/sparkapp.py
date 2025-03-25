import os
import sys
import json
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_spark_session():
    """
    Создает и настраивает SparkSession с конфигурацией SSL для Kafka.
    Использует сертификаты, управляемые через cert-manager.
    """
    try:
        # Получение путей к хранилищам и паролей из переменных окружения
        keystore_path = os.getenv("KAFKA_KEYSTORE_PATH", "/etc/kafka/certs/keystore.jks")
        truststore_path = os.getenv("KAFKA_TRUSTSTORE_PATH", "/etc/kafka/certs/truststore.jks")
        keystore_password = os.getenv("KAFKA_KEYSTORE_PASSWORD", "")
        truststore_password = os.getenv("KAFKA_TRUSTSTORE_PASSWORD", "")
        
        # Проверка доступности файлов сертификатов
        if not os.path.exists(keystore_path):
            logger.error(f"Keystore path not found: {keystore_path}")
            raise FileNotFoundError(f"Keystore path not found: {keystore_path}")
        
        if not os.path.exists(truststore_path):
            logger.error(f"Truststore path not found: {truststore_path}")
            raise FileNotFoundError(f"Truststore path not found: {truststore_path}")
        
        logger.info("Создание сессии Spark с настройками SSL для Kafka")
        # Создание SparkSession с необходимыми конфигурациями
        spark = SparkSession.builder \
            .appName("KafkaToADBWithCertManager") \
            .config("spark.sql.shuffle.partitions", "10") \
            .config("spark.executor.memory", "2g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23") \
            .config("spark.kafka.ssl.enabled", "true") \
            .config("spark.kafka.ssl.keystore.location", keystore_path) \
            .config("spark.kafka.ssl.keystore.password", keystore_password) \
            .config("spark.kafka.ssl.truststore.location", truststore_path) \
            .config("spark.kafka.ssl.truststore.password", truststore_password) \
            .config("spark.kafka.ssl.protocol", "TLSv1.2") \
            .getOrCreate()
        
        # Установка уровня логирования
        spark.sparkContext.setLogLevel("INFO")
        logger.info("SparkSession успешно создана")
        return spark
    except Exception as e:
        logger.error(f"Ошибка при создании SparkSession: {str(e)}")
        raise

def read_from_kafka(spark):
    """
    Читает данные из указанной темы Kafka.
    """
    try:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        topic = os.getenv("KAFKA_TOPIC", "default-topic")
        
        logger.info(f"Чтение данных из Kafka: {bootstrap_servers}, тема: {topic}")
        
        # Настройка параметров Kafka для чтения данных
        kafka_options = {
            "kafka.bootstrap.servers": bootstrap_servers,
            "subscribe": topic,
            "startingOffsets": "earliest",
            "kafka.security.protocol": "SSL",
            "failOnDataLoss": "false",
            "maxOffsetsPerTrigger": "10000"
        }
        
        # Чтение данных из Kafka
        df = spark.read.format("kafka") \
            .options(**kafka_options) \
            .load()
        
        # Преобразование значений из байтов в строки
        df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        logger.info(f"Прочитано {df.count()} записей из Kafka")
        
        return df
    except Exception as e:
        logger.error(f"Ошибка при чтении данных из Kafka: {str(e)}")
        raise

def process_data(df):
    """
    Обрабатывает данные из Kafka, преобразуя их в нужный формат.
    """
    try:
        logger.info("Обработка данных")
        
        # Определение схемы для JSON-данных
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        
        # Преобразование JSON в колонки DataFrame
        parsed_df = df.select(
            from_json(col("value"), schema).alias("data")
        ).select("data.*")
        
        # Дополнительная обработка данных (пример)
        processed_df = parsed_df.filter(col("id").isNotNull())
        
        logger.info(f"Обработано {processed_df.count()} записей")
        return processed_df
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {str(e)}")
        raise

def write_to_adb(df):
    """
    Записывает данные в ADB.
    """
    try:
        # Получение параметров для подключения к ADB из переменных окружения
        adb_url = os.getenv("ADB_URL", "")
        adb_user = os.getenv("ADB_USER", "")
        adb_password = os.getenv("ADB_PASSWORD", "")
        
        if not adb_url or not adb_user or not adb_password:
            logger.error("Отсутствуют необходимые параметры для подключения к ADB")
            raise ValueError("Отсутствуют необходимые параметры для подключения к ADB")
        
        logger.info(f"Запись данных в ADB: {adb_url}")
        
        # Настройка параметров для подключения к ADB
        db_properties = {
            "user": adb_user,
            "password": adb_password,
            "driver": "org.postgresql.Driver"
        }
        
        # Запись данных в ADB
        df.write \
            .format("jdbc") \
            .option("url", adb_url) \
            .option("dbtable", "processed_data") \
            .option("user", adb_user) \
            .option("password", adb_password) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        
        logger.info("Данные успешно записаны в ADB")
    except Exception as e:
        logger.error(f"Ошибка при записи данных в ADB: {str(e)}")
        raise

def main():
    """
    Основная функция для запуска процесса обработки данных.
    """
    spark = None
    try:
        # Создание сессии Spark
        spark = create_spark_session()
        
        # Чтение данных из Kafka
        kafka_df = read_from_kafka(spark)
        
        # Обработка данных
        processed_df = process_data(kafka_df)
        
        # Запись данных в ADB
        write_to_adb(processed_df)
        
        logger.info("Операция завершена успешно")
        return 0
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {str(e)}")
        return 1
    finally:
        # Закрытие сессии Spark
        if spark:
            logger.info("Закрытие сессии Spark")
            spark.stop()

if __name__ == "__main__":
    sys.exit(main()) 