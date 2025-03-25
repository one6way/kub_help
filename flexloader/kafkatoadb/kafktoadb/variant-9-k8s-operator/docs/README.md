# Вариант 9: Kubernetes Operator для Spark с существующим Kafka кластером

## Описание

Данный вариант предполагает использование специализированного Kubernetes Operator для управления Spark-приложениями при работе с уже существующим Kafka кластером. Spark Operator представляет собой расширение Kubernetes, которое автоматизирует управление жизненным циклом Spark приложений.

В этом варианте мы применяем:
1. **Spark Operator** - для управления Spark-приложениями
2. **Cert-Manager** - для автоматического управления сертификатами (опционально)
3. **Существующий Kafka кластер** - с 4 bootstrap серверами

## Преимущества

- **Декларативное управление**: Spark-приложения описываются в виде YAML-манифестов
- **Автоматизация сложных операций**: Оператор берет на себя все задачи по настройке и управлению Spark
- **Управление состоянием**: Оператор отслеживает и управляет состоянием Spark-приложений
- **Обновление без простоев**: Поддержка безболезненных обновлений компонентов
- **Самовосстановление**: Автоматическое исправление проблем при сбоях
- **Интеграция с экосистемой Kubernetes**: Работа с Ingress, мониторингом, логированием
- **Использование существующего Kafka кластера**: Отсутствие необходимости развертывать и настраивать Kafka
- **Поддержка ScheduledSparkApplication**: Встроенное управление расписанием запуска задач без Airflow

## Недостатки

- **Сложность начальной настройки**: Требуется установка и настройка Spark Operator
- **Потребление ресурсов**: Оператор потребляет дополнительные ресурсы кластера
- **Кривая обучения**: Необходимость изучения API оператора и его возможностей
- **Ограниченный контроль**: Меньше возможностей по тонкой настройке, чем в Airflow
- **Зависимость от сообщества**: Актуальность и поддержка зависят от активности сообщества

## Схема взаимодействия

```
┌─────────────────────┐      ┌───────────────────────┐
│                     │      │                       │
│  Kubernetes Cluster │─────▶│  Spark Operator       │
│                     │      │                       │
└─────────────────────┘      └───────────────────────┘
                                       │
                                       ▼
                            ┌───────────────────────┐
                            │                       │
                            │  SparkApplication CR  │
                            │  (Spark-задание)      │
                            │                       │
                            └───────────────────────┘
                                       │
                                       │
                                       ▼
┌─────────────────────┐      ┌───────────────────────┐
│                     │      │                       │
│  Существующий       │◀────▶│  Spark Executor Pods  │
│  Kafka Cluster с    │      │                       │
│  4 bootstrap servers│      └───────────────────────┘
└─────────────────────┘                 │
         │                              │
         │                              ▼
         ▼                   ┌───────────────────────┐
┌─────────────────────┐      │                       │
│                     │      │  ADB                  │
│  Cert-Manager       │      │  (Целевое хранилище)  │
│  (опционально)      │      │                       │
└─────────────────────┘      └───────────────────────┘
         │
         ▼
┌─────────────────────┐
│                     │
│  TLS сертификаты    │
│  для Kafka          │
│                     │
└─────────────────────┘
```

## Процесс реализации

1. Установка и настройка Kubernetes Operators (Spark Operator, опционально Cert-Manager)
2. Получение сертификатов для подключения к существующему Kafka кластеру
3. Создание Kubernetes Secrets для хранения сертификатов
4. Настройка доступа к сертификатам для Spark-приложений
5. Создание SparkApplication для запуска задач обработки данных
6. Настройка расписания запуска или режима потоковой обработки
7. Настройка мониторинга и логирования с помощью операторов

## Описание ключевых файлов

### Установка Spark Operator

Файл `install-spark-operator.yaml` содержит команды для установки Spark Operator через Helm:

```yaml
# Установка Spark Operator
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: spark-operator
  namespace: spark-operator
spec:
  repo: https://googlecloudplatform.github.io/spark-on-k8s-operator
  chart: spark-operator
  version: 1.1.20
  targetNamespace: spark-operator
  valuesContent: |-
    webhook:
      enable: true
    metrics:
      enable: true
    sparkJobNamespace:
      - spark
```

### Создание секрета с сертификатами Kafka

Файл `kafka-certs-secret.yaml` создает секрет для хранения сертификатов Kafka:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-ssl-certs
  namespace: spark
type: Opaque
data:
  # Значения должны быть закодированы в base64
  keystore.jks: ${BASE64_ENCODED_KEYSTORE}
  truststore.jks: ${BASE64_ENCODED_TRUSTSTORE}
---
apiVersion: v1
kind: Secret
metadata:
  name: kafka-ssl-passwords
  namespace: spark
type: Opaque
data:
  # Значения должны быть закодированы в base64
  keystore-password: ${BASE64_ENCODED_KEYSTORE_PASSWORD}
  truststore-password: ${BASE64_ENCODED_TRUSTSTORE_PASSWORD}
```

### Spark Application для обработки данных

Файл `spark-kafka-to-adb.yaml` содержит определение Spark-приложения через CustomResource SparkApplication с настройкой для подключения к существующим bootstrap серверам Kafka:

```yaml
apiVersion: "sparkoperator.k8s.io/v1beta2"
kind: SparkApplication
metadata:
  name: kafka-to-adb
  namespace: spark
spec:
  type: Python
  mode: cluster
  image: "apache/spark:3.3.0"
  imagePullPolicy: IfNotPresent
  pythonVersion: "3"
  mainApplicationFile: "local:///opt/spark/work-dir/sparkapp.py"
  sparkVersion: "3.3.0"
  restartPolicy:
    type: OnFailure
    onFailureRetries: 3
    onFailureRetryInterval: 10
    onSubmissionFailureRetries: 3
    onSubmissionFailureRetryInterval: 20
  timeToLiveSeconds: 86400
  driver:
    cores: 1
    coreLimit: "1200m"
    memory: "2048m"
    labels:
      version: 3.3.0
    serviceAccount: spark-sa
    volumeMounts:
      - name: kafka-certs
        mountPath: /etc/kafka-certs
        readOnly: true
  executor:
    cores: 1
    instances: 2
    memory: "2048m"
    labels:
      version: 3.3.0
    volumeMounts:
      - name: kafka-certs
        mountPath: /etc/kafka-certs
        readOnly: true
  volumes:
    - name: kafka-certs
      secret:
        secretName: kafka-ssl-certs
  deps:
    packages:
      - org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0
      - org.postgresql:postgresql:42.3.3
  sparkConf:
    "spark.kubernetes.executor.podNamePrefix": "kafka-to-adb"
    "spark.kubernetes.driver.secrets.kafka-ssl-certs": "/etc/kafka-certs"
    "spark.kubernetes.executor.secrets.kafka-ssl-certs": "/etc/kafka-certs"
  envVars:
    # Указываем все 4 bootstrap сервера Kafka
    KAFKA_BOOTSTRAP_SERVERS: "kafka-broker1:9093,kafka-broker2:9093,kafka-broker3:9093,kafka-broker4:9093"
    KAFKA_TOPIC: "source-topic"
    KAFKA_SECURITY_PROTOCOL: "SSL"
    KAFKA_SSL_KEYSTORE_LOCATION: "/etc/kafka-certs/keystore.jks"
    KAFKA_SSL_KEYSTORE_TYPE: "JKS"
    KAFKA_SSL_TRUSTSTORE_LOCATION: "/etc/kafka-certs/truststore.jks"
    KAFKA_SSL_TRUSTSTORE_TYPE: "JKS"
    ADB_URL: "jdbc:postgresql://adb-host:5432/database"
    ADB_USER: "adb_user"
  envSecrets:
    KAFKA_SSL_KEYSTORE_PASSWORD:
      name: kafka-ssl-passwords
      key: keystore-password
    KAFKA_SSL_TRUSTSTORE_PASSWORD:
      name: kafka-ssl-passwords
      key: truststore-password
    ADB_PASSWORD:
      name: adb-credentials
      key: password
```

### Планирование запуска Spark-приложений

Для регулярного запуска Spark-приложений используется ScheduledSparkApplication:

```yaml
apiVersion: "sparkoperator.k8s.io/v1beta2"
kind: ScheduledSparkApplication
metadata:
  name: scheduled-kafka-to-adb
  namespace: spark
spec:
  schedule: "0 0 * * *"  # Запуск каждый день в полночь
  concurrencyPolicy: Forbid
  template:
    type: Python
    mode: cluster
    image: "apache/spark:3.3.0"
    imagePullPolicy: IfNotPresent
    pythonVersion: "3"
    mainApplicationFile: "local:///opt/spark/work-dir/sparkapp.py"
    sparkVersion: "3.3.0"
    restartPolicy:
      type: OnFailure
      onFailureRetries: 3
      onFailureRetryInterval: 10
      onSubmissionFailureRetries: 3
      onSubmissionFailureRetryInterval: 20
    driver:
      cores: 1
      coreLimit: "1200m"
      memory: "2048m"
      labels:
        version: 3.3.0
      serviceAccount: spark-sa
      volumeMounts:
        - name: kafka-certs
          mountPath: /etc/kafka-certs
          readOnly: true
    executor:
      cores: 1
      instances: 2
      memory: "2048m"
      labels:
        version: 3.3.0
      volumeMounts:
        - name: kafka-certs
          mountPath: /etc/kafka-certs
          readOnly: true
    volumes:
      - name: kafka-certs
        secret:
          secretName: kafka-ssl-certs
    deps:
      packages:
        - org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0
        - org.postgresql:postgresql:42.3.3
    sparkConf:
      "spark.kubernetes.executor.podNamePrefix": "sched-kafka-to-adb"
      "spark.kubernetes.driver.secrets.kafka-ssl-certs": "/etc/kafka-certs"
      "spark.kubernetes.executor.secrets.kafka-ssl-certs": "/etc/kafka-certs"
    envVars:
      # Указываем все 4 bootstrap сервера Kafka
      KAFKA_BOOTSTRAP_SERVERS: "kafka-broker1:9093,kafka-broker2:9093,kafka-broker3:9093,kafka-broker4:9093"
      KAFKA_TOPIC: "source-topic"
      KAFKA_SECURITY_PROTOCOL: "SSL"
      KAFKA_SSL_KEYSTORE_LOCATION: "/etc/kafka-certs/keystore.jks"
      KAFKA_SSL_KEYSTORE_TYPE: "JKS"
      KAFKA_SSL_TRUSTSTORE_LOCATION: "/etc/kafka-certs/truststore.jks"
      KAFKA_SSL_TRUSTSTORE_TYPE: "JKS"
      ADB_URL: "jdbc:postgresql://adb-host:5432/database"
      ADB_USER: "adb_user"
    envSecrets:
      KAFKA_SSL_KEYSTORE_PASSWORD:
        name: kafka-ssl-passwords
        key: keystore-password
      KAFKA_SSL_TRUSTSTORE_PASSWORD:
        name: kafka-ssl-passwords
        key: truststore-password
      ADB_PASSWORD:
        name: adb-credentials
        key: password
```

## Пример Python приложения

Файл `sparkapp.py` содержит код для обработки данных из Kafka и записи в ADB:

```python
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
        
        # Настройка SSL параметров для Kafka с указанием всех 4 bootstrap серверов
        kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
        kafka_topic = os.environ.get("KAFKA_TOPIC")
        security_protocol = os.environ.get("KAFKA_SECURITY_PROTOCOL", "SSL")
        ssl_keystore_location = os.environ.get("KAFKA_SSL_KEYSTORE_LOCATION")
        ssl_keystore_password = os.environ.get("KAFKA_SSL_KEYSTORE_PASSWORD")
        ssl_keystore_type = os.environ.get("KAFKA_SSL_KEYSTORE_TYPE", "JKS")
        ssl_truststore_location = os.environ.get("KAFKA_SSL_TRUSTSTORE_LOCATION")
        ssl_truststore_password = os.environ.get("KAFKA_SSL_TRUSTSTORE_PASSWORD")
        ssl_truststore_type = os.environ.get("KAFKA_SSL_TRUSTSTORE_TYPE", "JKS")
        
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
```

## Команды для управления

### Установка Spark Operator

```bash
# Создание пространств имен
kubectl create namespace spark-operator
kubectl create namespace spark

# Установка Spark Operator с помощью Helm
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm install spark-operator spark-operator/spark-operator --namespace spark-operator --set webhook.enable=true
```

### Создание секретов для сертификатов

```bash
# Создание секрета с сертификатами для Kafka
kubectl create secret generic kafka-ssl-certs \
  --from-file=keystore.jks=/path/to/keystore.jks \
  --from-file=truststore.jks=/path/to/truststore.jks \
  -n spark

# Создание секрета с паролями для сертификатов
kubectl create secret generic kafka-ssl-passwords \
  --from-literal=keystore-password=your_keystore_password \
  --from-literal=truststore-password=your_truststore_password \
  -n spark

# Создание секрета для подключения к ADB
kubectl create secret generic adb-credentials \
  --from-literal=password=your_adb_password \
  -n spark
```

### Запуск Spark-приложений

```bash
# Создание RBAC для Spark
kubectl apply -f spark-rbac.yaml

# Копирование Spark приложения в под Spark Operator
kubectl cp sparkapp.py spark-operator/spark-operator-pod:/opt/spark/work-dir/

# Создание и запуск Spark Application
kubectl apply -f spark-kafka-to-adb.yaml

# ИЛИ создание и запуск по расписанию
kubectl apply -f scheduled-spark-kafka-to-adb.yaml
```

### Мониторинг и отладка

```bash
# Проверка состояния Spark Application
kubectl get sparkapplications -n spark
kubectl describe sparkapplication kafka-to-adb -n spark

# Проверка логов драйвера Spark
kubectl logs -f <spark-driver-pod> -n spark

# Проверка секретов для сертификатов Kafka
kubectl get secret kafka-ssl-certs -n spark -o yaml

# Просмотр UI Spark (port-forward)
kubectl port-forward <spark-driver-pod> 4040:4040 -n spark
```

## Преимущества использования Spark Operator с существующим Kafka кластером

1. **Упрощение работы с существующей инфраструктурой** - не требуется разворачивать новый Kafka кластер
2. **Автоматизация управления жизненным циклом Spark-приложений** - оператор управляет всеми аспектами работы Spark
3. **Интеграция с облачной инфраструктурой** - легкая интеграция с облачными провайдерами
4. **Масштабируемость** - возможность горизонтального масштабирования Spark-компонентов
5. **Единый интерфейс управления** - все управление через Kubernetes API
6. **Встроенное расписание задач** - не требуется отдельный планировщик (Airflow)
7. **Интеграция мониторинга** - встроенные возможности мониторинга и метрики 