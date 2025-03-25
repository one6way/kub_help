import os
import sys
import signal
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Флаг для корректного завершения при получении сигнала
is_terminating = False

# Обработчик сигналов для корректного завершения
def handle_sigterm(signum, frame):
    global is_terminating
    logger.info("Получен сигнал завершения, приложение будет остановлено...")
    is_terminating = True

# Регистрация обработчиков сигналов
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def create_spark_session():
    """Создание и настройка SparkSession для Structured Streaming."""
    try:
        spark = SparkSession.builder \
            .appName("KafkaToADBStructuredStreaming") \
            .config("spark.sql.shuffle.partitions", "10") \
            .config("spark.streaming.kafka.consumer.cache.enabled", "false") \
            .getOrCreate()
        
        # Настройка уровня логирования
        spark.sparkContext.setLogLevel("INFO")
        logger.info("SparkSession успешно создана")
        return spark
    except Exception as e:
        logger.error(f"Ошибка при создании SparkSession: {str(e)}")
        raise

def create_kafka_stream(spark):
    """Создание потока данных из Kafka."""
    try:
        bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        topic = os.environ.get("KAFKA_TOPIC", "source-topic")
        
        logger.info(f"Создание потока из Kafka: {bootstrap_servers}, тема: {topic}")
        
        df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", bootstrap_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("kafka.security.protocol", "SSL") \
            .option("failOnDataLoss", "false") \
            .load()
        
        return df
    except Exception as e:
        logger.error(f"Ошибка при создании потока из Kafka: {str(e)}")
        raise

def process_stream(df):
    """Обработка потоковых данных."""
    try:
        # Определение схемы для JSON-данных
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("value", StringType(), True),
            StructField("timestamp", TimestampType(), True)
        ])
        
        # Преобразование из JSON
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Дополнительная обработка данных (пример)
        processed_df = parsed_df \
            .filter(col("id").isNotNull()) \
            .withColumn("processing_time", to_timestamp(col("timestamp")))
        
        return processed_df
    except Exception as e:
        logger.error(f"Ошибка при обработке потока: {str(e)}")
        raise

def write_to_adb_foreach(df):
    """Запись данных в ADB с использованием foreachBatch."""
    def foreach_batch_function(batch_df, epoch_id):
        if batch_df.count() > 0:
            try:
                # Получение параметров для подключения к ADB
                url = os.environ.get("ADB_URL", "")
                user = os.environ.get("ADB_USER", "")
                password = os.environ.get("ADB_PASSWORD", "")
                
                # Запись батча в ADB
                batch_df.write \
                    .format("jdbc") \
                    .option("url", url) \
                    .option("dbtable", "processed_data") \
                    .option("user", user) \
                    .option("password", password) \
                    .option("driver", "org.postgresql.Driver") \
                    .mode("append") \
                    .save()
                
                logger.info(f"Батч {epoch_id} успешно записан в ADB. Количество записей: {batch_df.count()}")
            except Exception as e:
                logger.error(f"Ошибка при записи батча {epoch_id} в ADB: {str(e)}")
                raise
    
    return df.writeStream \
        .foreachBatch(foreach_batch_function) \
        .option("checkpointLocation", "/checkpoint") \
        .trigger(processingTime="5 seconds") \
        .start()

def main():
    """Основная функция приложения."""
    spark = None
    query = None
    
    try:
        # Создание SparkSession
        spark = create_spark_session()
        
        # Создание потока из Kafka
        kafka_df = create_kafka_stream(spark)
        
        # Обработка потока
        processed_df = process_stream(kafka_df)
        
        # Запись результатов в ADB
        query = write_to_adb_foreach(processed_df)
        
        logger.info("Приложение успешно запущено и ожидает данных")
        
        # Мониторинг состояния приложения
        while not is_terminating and query.isActive:
            query_status = query.status
            logger.info(f"Статус потока: {query_status}")
            time.sleep(30)  # Проверка каждые 30 секунд
        
        # Корректное завершение потока
        if query and query.isActive:
            logger.info("Остановка потока...")
            query.stop()
            logger.info("Поток остановлен")
        
        logger.info("Приложение завершает работу")
        return 0
    except Exception as e:
        logger.error(f"Критическая ошибка в приложении: {str(e)}")
        return 1
    finally:
        # Остановка потока при выходе
        if query and query.isActive:
            try:
                query.stop()
                logger.info("Поток остановлен")
            except Exception as e:
                logger.error(f"Ошибка при остановке потока: {str(e)}")
        
        # Остановка SparkSession
        if spark:
            try:
                spark.stop()
                logger.info("SparkSession остановлена")
            except Exception as e:
                logger.error(f"Ошибка при остановке SparkSession: {str(e)}")

if __name__ == "__main__":
    sys.exit(main()) 