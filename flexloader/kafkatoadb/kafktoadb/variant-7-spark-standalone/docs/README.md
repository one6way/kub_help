# Вариант 7: Apache Spark Standalone без Airflow

## Описание

Данный вариант предполагает использование Apache Spark Standalone кластера для запуска задач обработки данных между Kafka и ADB, без использования Airflow или Kubernetes. Запуск заданий осуществляется с помощью cron или другого планировщика непосредственно на серверах, где установлен Spark.

## Преимущества

- **Простота настройки**: Не требуется Kubernetes или Airflow, только сам Spark
- **Легковесность**: Минимальные требования к инфраструктуре
- **Независимость от внешних систем**: Отсутствие зависимости от оркестраторов
- **Прямое управление ресурсами**: Четкий контроль над выделением ресурсов для Spark
- **Простота масштабирования**: Добавление и удаление worker-узлов без сложных конфигураций
- **Быстрота развертывания**: Быстрый запуск и настройка всей инфраструктуры

## Недостатки

- **Ручное управление отказоустойчивостью**: Требуется дополнительная настройка для обеспечения высокой доступности
- **Ограниченные возможности планирования**: Базовые возможности планирования через cron
- **Ручная настройка мониторинга**: Необходимо дополнительно настраивать системы мониторинга
- **Отсутствие встроенной изоляции**: Нет контейнеризации и изоляции по умолчанию
- **Сложности динамического масштабирования**: Нет автоматического масштабирования в зависимости от нагрузки

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Cron Job /         │────▶│  Запуск spark-submit  │
│  Планировщик        │     │  на узле мастера      │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark Master       │────▶│  Распределение задачи │
│                     │     │  по Worker-узлам      │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Директория с       │────▶│  Spark Worker Nodes   │
│  сертификатами      │     │  (Выполнение задачи)  │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Подключение к      │────▶│  Kafka Cluster        │
│  Kafka с SSL/TLS    │     │  (SSL/TLS)            │
│                     │     │                       │
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

1. Развертывание Apache Spark Standalone кластера (Master и Worker узлы)
2. Настройка безопасного хранения сертификатов на всех узлах Spark
3. Разработка скрипта запуска spark-submit с необходимыми параметрами
4. Настройка планировщика (cron) для регулярного запуска Spark-задания
5. Настройка мониторинга и логирования выполнения заданий

## Описание ключевых файлов

### start-spark-job.sh

Файл `start-spark-job.sh` содержит скрипт для запуска Spark-задания, который:

- Настраивает переменные окружения для Spark
- Обеспечивает передачу параметров для подключения к Kafka и ADB
- Запускает spark-submit с необходимыми параметрами
- Обрабатывает возможные ошибки выполнения
- Настраивает логирование процесса

### sparkapp.py

Файл `sparkapp.py` содержит Spark-приложение, которое:

- Читает данные из Kafka с использованием SSL/TLS
- Обрабатывает и трансформирует данные
- Записывает результаты в ADB
- Использует сертификаты для подключения к Kafka
- Обеспечивает подробное логирование процесса

## Пример скрипта запуска

```bash
#!/bin/bash

# Настройка переменных окружения
export SPARK_HOME=/opt/spark
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$SPARK_HOME/bin:$PATH

# Параметры подключения
KAFKA_BOOTSTRAP_SERVERS="kafka-broker:9093"
KAFKA_TOPIC="source-topic"
KEYSTORE_PATH="/etc/kafka/ssl/keystore.jks"
TRUSTSTORE_PATH="/etc/kafka/ssl/truststore.jks"
KEYSTORE_PASSWORD="keystore_password"
TRUSTSTORE_PASSWORD="truststore_password"
ADB_URL="jdbc:postgresql://adb-host:5432/database"
ADB_USER="adb_user"
ADB_PASSWORD="adb_password"

# Директория логов
LOG_DIR="/var/log/spark"
mkdir -p $LOG_DIR

# Запуск Spark-задания
spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode cluster \
  --conf "spark.executor.instances=2" \
  --conf "spark.executor.memory=2g" \
  --conf "spark.driver.memory=1g" \
  --conf "spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23" \
  --conf "spark.kafka.ssl.keystore.location=$KEYSTORE_PATH" \
  --conf "spark.kafka.ssl.truststore.location=$TRUSTSTORE_PATH" \
  --conf "spark.kafka.ssl.keystore.password=$KEYSTORE_PASSWORD" \
  --conf "spark.kafka.ssl.truststore.password=$TRUSTSTORE_PASSWORD" \
  --conf "spark.executor.extraJavaOptions=-Dlog4j.configuration=file:///opt/spark/conf/log4j.properties" \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:///opt/spark/conf/log4j.properties" \
  --files "/opt/spark/conf/log4j.properties" \
  /opt/spark/jobs/sparkapp.py \
  $KAFKA_BOOTSTRAP_SERVERS \
  $KAFKA_TOPIC \
  $ADB_URL \
  $ADB_USER \
  $ADB_PASSWORD \
  > $LOG_DIR/spark-job-$(date +"%Y-%m-%d").log 2>&1

# Проверка результата выполнения
if [ $? -eq 0 ]; then
  echo "Spark job completed successfully at $(date)"
  exit 0
else
  echo "Spark job failed at $(date)"
  exit 1
fi
```

## Пример приложения sparkapp.py

```python
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# Получение параметров из аргументов командной строки
kafka_bootstrap_servers = sys.argv[1]
kafka_topic = sys.argv[2]
adb_url = sys.argv[3]
adb_user = sys.argv[4]
adb_password = sys.argv[5]

# Создание SparkSession
spark = SparkSession.builder \
    .appName("KafkaToADBStandalone") \
    .getOrCreate()

# Настройка уровня логирования
spark.sparkContext.setLogLevel("INFO")

# Чтение данных из Kafka
df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "earliest") \
    .option("kafka.security.protocol", "SSL") \
    .load()

# Определение схемы и преобразование данных
schema = StructType([
    StructField("id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("value", StringType(), True)
])

# Преобразование сообщений Kafka в структурированные данные
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Запись данных в ADB
parsed_df.write \
    .format("jdbc") \
    .option("url", adb_url) \
    .option("dbtable", "processed_data") \
    .option("user", adb_user) \
    .option("password", adb_password) \
    .option("driver", "org.postgresql.Driver") \
    .mode("append") \
    .save()

# Завершение сессии
spark.stop()
```

## Настройка планировщика cron

Для регулярного запуска можно добавить запись в crontab:

```
# Запуск каждый день в 2:00
0 2 * * * /opt/spark/scripts/start-spark-job.sh
```

## Мониторинг и управление

### Полезные команды

```bash
# Проверка статуса Spark-кластера
$SPARK_HOME/sbin/spark-daemon.sh status org.apache.spark.deploy.master.Master 1

# Запуск Spark Master
$SPARK_HOME/sbin/start-master.sh

# Запуск Spark Worker
$SPARK_HOME/sbin/start-slave.sh spark://spark-master:7077

# Доступ к веб-интерфейсу Spark
# http://spark-master:8080

# Просмотр логов Spark
cat /var/log/spark/spark-job-*.log

# Остановка всех компонентов Spark
$SPARK_HOME/sbin/stop-all.sh
```

### Обеспечение безопасности сертификатов

1. Разместите сертификаты в директории с ограниченным доступом:
   ```bash
   sudo mkdir -p /etc/kafka/ssl
   sudo chown -R spark:spark /etc/kafka/ssl
   sudo chmod 700 /etc/kafka/ssl
   ```

2. Скопируйте сертификаты на все узлы кластера:
   ```bash
   sudo scp /etc/kafka/ssl/* spark-worker1:/etc/kafka/ssl/
   sudo scp /etc/kafka/ssl/* spark-worker2:/etc/kafka/ssl/
   ```

3. Установите правильные разрешения:
   ```bash
   sudo chmod 400 /etc/kafka/ssl/*.jks
   ``` 