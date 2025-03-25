# Вариант 8: Spark Structured Streaming в Kubernetes StatefulSet

## Описание

Данный вариант предполагает использование Spark Structured Streaming в режиме демона (постоянно работающего сервиса), запущенного на Kubernetes с помощью StatefulSet. Этот подход обеспечивает непрерывную обработку данных из Kafka в ADB без необходимости периодического запуска заданий.

## Преимущества

- **Потоковая обработка**: Непрерывная обработка данных в режиме реального времени
- **Отсутствие задержек**: Нет ожидания следующего запуска задания для обработки новых данных
- **Стабильность**: StatefulSet обеспечивает устойчивую идентичность подов при перезапуске
- **Встроенная отказоустойчивость**: Kubernetes автоматически восстанавливает упавшие поды
- **Эффективное использование ресурсов**: Отсутствие накладных расходов на запуск/остановку заданий
- **Горизонтальное масштабирование**: Возможность увеличения числа обработчиков при росте нагрузки
- **Отсутствие оркестратора**: Нет зависимости от Airflow или других внешних планировщиков

## Недостатки

- **Расход ресурсов**: Постоянная работа требует выделения ресурсов даже при отсутствии данных для обработки
- **Сложность управления состоянием**: Требуется настройка механизмов чекпоинтинга для отказоустойчивости
- **Потенциальное накопление ошибок**: Длительно работающие сервисы могут накапливать проблемы со временем
- **Сложность обновления**: Требуются специальные стратегии для обновления без потери данных
- **Увеличенная сложность мониторинга**: Необходимо отслеживать состояние долгоживущих процессов

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Kubernetes Cluster │────▶│  StatefulSet с        │
│                     │     │  Spark-приложением    │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Secret с           │────▶│  Persistent Volume    │
│  сертификатами      │     │  для чекпоинтов       │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark Structured   │────▶│  Kafka Cluster        │
│  Streaming внутри   │     │  (SSL/TLS)            │
│  контейнера         │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐
│                     │
│  ADB                │
│  (Целевое хранилище)│
│                     │
└─────────────────────┘
```

## Процесс реализации

1. Создание Kubernetes Secret с сертификатами для подключения к Kafka
2. Настройка Persistent Volume для хранения чекпоинтов Spark Structured Streaming
3. Разработка Dockerfile для контейнера со Spark и Structured Streaming приложением
4. Создание StatefulSet для запуска и управления Spark-приложением
5. Настройка мониторинга и логирования для долгоживущего процесса

## Описание ключевых файлов

### spark-streaming-statefulset.yaml

Файл `spark-streaming-statefulset.yaml` содержит описание Kubernetes StatefulSet ресурса, который:

- Обеспечивает стабильную идентичность подов и порядок создания/удаления
- Монтирует Persistent Volume для хранения чекпоинтов
- Монтирует секреты с сертификатами и параметрами подключения
- Настраивает параметры отказоустойчивости и перезапуска
- Задает ресурсные ограничения для контейнера

### structured-streaming-app.py

Файл `structured-streaming-app.py` содержит Spark-приложение с использованием Structured Streaming, которое:

- Настраивает непрерывное соединение с Kafka с использованием SSL/TLS
- Обрабатывает потоковые данные в реальном времени
- Сохраняет результаты в ADB с помощью forEach sink
- Использует чекпоинтинг для обеспечения отказоустойчивости
- Обеспечивает механизм корректного завершения при получении сигналов остановки

## Пример конфигурации StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: spark-streaming
  namespace: spark
spec:
  serviceName: "spark-streaming"
  replicas: 1
  selector:
    matchLabels:
      app: spark-streaming
  template:
    metadata:
      labels:
        app: spark-streaming
    spec:
      terminationGracePeriodSeconds: 120
      serviceAccountName: spark-sa
      containers:
      - name: spark-streaming
        image: spark-streaming:latest
        imagePullPolicy: IfNotPresent
        command:
        - /bin/bash
        - -c
        - |
          spark-submit \
          --master local[*] \
          --conf spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23 \
          --conf spark.sql.streaming.checkpointLocation=/checkpoint \
          --conf spark.kafka.ssl.keystore.location=/etc/kafka/ssl/keystore.jks \
          --conf spark.kafka.ssl.truststore.location=/etc/kafka/ssl/truststore.jks \
          --conf spark.kafka.ssl.keystore.password=${KEYSTORE_PASSWORD} \
          --conf spark.kafka.ssl.truststore.password=${TRUSTSTORE_PASSWORD} \
          /app/structured-streaming-app.py
        env:
        - name: KEYSTORE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: kafka-ssl-passwords
              key: keystore-password
        - name: TRUSTSTORE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: kafka-ssl-passwords
              key: truststore-password
        - name: ADB_URL
          valueFrom:
            secretKeyRef:
              name: adb-credentials
              key: url
        - name: ADB_USER
          valueFrom:
            secretKeyRef:
              name: adb-credentials
              key: username
        - name: ADB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: adb-credentials
              key: password
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: "kafka-broker:9093"
        - name: KAFKA_TOPIC
          value: "source-topic"
        volumeMounts:
        - name: checkpoint-storage
          mountPath: /checkpoint
        - name: kafka-certs
          mountPath: /etc/kafka/ssl
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - ps -ef | grep spark-submit | grep -v grep
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - ps -ef | grep spark-submit | grep -v grep
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: kafka-certs
        secret:
          secretName: kafka-ssl-certs
          items:
          - key: keystore.jks
            path: keystore.jks
          - key: truststore.jks
            path: truststore.jks
  volumeClaimTemplates:
  - metadata:
      name: checkpoint-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 10Gi
```

## Пример Dockerfile

```dockerfile
FROM apache/spark:3.3.0

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install pyspark==3.3.0 psycopg2-binary

# Копирование приложения
COPY structured-streaming-app.py /app/

# Настройка рабочей директории
WORKDIR /app

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Добавление пользователя с ограниченными правами
USER 185
```

## Пример приложения Structured Streaming

```python
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
```

## Service для доступа к приложению

```yaml
apiVersion: v1
kind: Service
metadata:
  name: spark-streaming
  namespace: spark
  labels:
    app: spark-streaming
spec:
  ports:
  - port: 4040
    name: ui
    targetPort: 4040
  selector:
    app: spark-streaming
  type: ClusterIP
```

## Команды для управления

### Создание ресурсов

```bash
# Создание Secret с сертификатами
kubectl create secret generic kafka-ssl-certs \
  --from-file=keystore.jks=/path/to/keystore.jks \
  --from-file=truststore.jks=/path/to/truststore.jks \
  -n spark

# Создание Secret с паролями
kubectl create secret generic kafka-ssl-passwords \
  --from-literal=keystore-password=mykeystorepassword \
  --from-literal=truststore-password=mytruststorepassword \
  -n spark

# Создание Secret с данными для подключения к ADB
kubectl create secret generic adb-credentials \
  --from-literal=url=jdbc:postgresql://adb-host:5432/database \
  --from-literal=username=adb_user \
  --from-literal=password=adb_password \
  -n spark

# Сборка и публикация Docker образа
docker build -t spark-streaming:latest .
# для миникуба:
eval $(minikube docker-env)
docker build -t spark-streaming:latest .

# Создание StatefulSet и Service
kubectl apply -f spark-streaming-statefulset.yaml
kubectl apply -f spark-streaming-service.yaml
```

### Мониторинг

```bash
# Просмотр статуса StatefulSet
kubectl get statefulset -n spark

# Просмотр запущенных подов
kubectl get pods -n spark

# Просмотр логов приложения
kubectl logs -f spark-streaming-0 -n spark

# Проверка состояния приложения
kubectl exec -it spark-streaming-0 -n spark -- ps -ef | grep spark-submit

# Доступ к Spark UI (требуется port-forward)
kubectl port-forward svc/spark-streaming 4040:4040 -n spark
# После этого Spark UI будет доступен по адресу http://localhost:4040
```

### Масштабирование и обновление

```bash
# Масштабирование количества реплик (для параллельной обработки разных тем)
kubectl scale statefulset spark-streaming --replicas=3 -n spark

# Обновление образа
kubectl set image statefulset/spark-streaming spark-streaming=spark-streaming:new-version -n spark

# Проверка статуса обновления
kubectl rollout status statefulset/spark-streaming -n spark

# Откат обновления в случае проблем
kubectl rollout undo statefulset/spark-streaming -n spark
```

## Другие варианты реализации демона в Kubernetes

1. **Kubernetes Deployment** - менее предпочтителен для Spark Structured Streaming из-за отсутствия стабильной идентичности контейнеров, но может использоваться для более простых случаев

2. **Kubernetes DaemonSet** - для запуска приложения на каждом узле кластера, если требуется локальная обработка данных

3. **Job с infinite loop** - технически возможно, но не рекомендуется, так как не обеспечивает автоматическое восстановление после сбоев и не является идиоматическим для Kubernetes 