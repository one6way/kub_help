from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Запуск Spark приложения для обработки данных из Kafka в ADB")
        
        # Настройка SSL параметров для Kafka
        kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
        kafka_topic = os.environ.get("KAFKA_TOPIC")
        security_protocol = os.environ.get("KAFKA_SECURITY_PROTOCOL", "SSL")
        ssl_keystore_location = os.environ.get("KAFKA_SSL_KEYSTORE_LOCATION")
        ssl_keystore_password = os.environ.get("KAFKA_SSL_KEYSTORE_PASSWORD")
        ssl_keystore_type = os.environ.get("KAFKA_SSL_KEYSTORE_TYPE", "PKCS12")
        ssl_truststore_location = os.environ.get("KAFKA_SSL_TRUSTSTORE_LOCATION")
        ssl_truststore_password = os.environ.get("KAFKA_SSL_TRUSTSTORE_PASSWORD")
        ssl_truststore_type = os.environ.get("KAFKA_SSL_TRUSTSTORE_TYPE", "PKCS12")
        
        # Настройка ADB параметров
        adb_url = os.environ.get("ADB_URL")
        adb_user = os.environ.get("ADB_USER")
        adb_password = os.environ.get("ADB_PASSWORD")
        
        logger.info(f"Подключение к Kafka: {kafka_bootstrap_servers}, тема: {kafka_topic}")
        
        # Создание SparkSession
        spark = SparkSession.builder \
            .appName("KafkaToADB") \
            .getOrCreate()
        
        # Установка уровня логирования
        spark.sparkContext.setLogLevel("INFO")
        
        # Чтение данных из Kafka с SSL
        logger.info("Чтение данных из Kafka...")
        df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
            .option("subscribe", kafka_topic) \
            .option("startingOffsets", "earliest") \
            .option("endingOffsets", "latest") \
            .option("kafka.security.protocol", security_protocol) \
            .option("kafka.ssl.keystore.location", ssl_keystore_location) \
            .option("kafka.ssl.keystore.password", ssl_keystore_password) \
            .option("kafka.ssl.keystore.type", ssl_keystore_type) \
            .option("kafka.ssl.truststore.location", ssl_truststore_location) \
            .option("kafka.ssl.truststore.password", ssl_truststore_password) \
            .option("kafka.ssl.truststore.type", ssl_truststore_type) \
            .load()
        
        # Определение схемы для JSON данных в Kafka
        logger.info("Определение схемы данных...")
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        
        # Преобразование данных
        logger.info("Преобразование данных...")
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Вывод схемы для отладки
        logger.info("Схема данных после разбора:")
        parsed_df.printSchema()
        
        # Получение количества записей
        count = parsed_df.count()
        logger.info(f"Получено {count} записей из Kafka")
        
        # Обработка данных (пример)
        logger.info("Обработка данных...")
        processed_df = parsed_df.filter(col("id").isNotNull())
        
        # Проверка наличия данных перед записью
        if processed_df.count() > 0:
            # Запись результатов в ADB
            logger.info(f"Запись данных в ADB: {adb_url}")
            processed_df.write \
                .format("jdbc") \
                .option("url", adb_url) \
                .option("dbtable", "processed_data") \
                .option("user", adb_user) \
                .option("password", adb_password) \
                .option("driver", "org.postgresql.Driver") \
                .mode("append") \
                .save()
            
            logger.info("Данные успешно записаны в ADB")
        else:
            logger.warning("Нет данных для записи в ADB")
        
        # Остановка Spark сессии
        spark.stop()
        logger.info("Обработка данных завершена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {str(e)}", exc_info=True)
        # Выход с ошибкой
        raise

if __name__ == "__main__":
    main()