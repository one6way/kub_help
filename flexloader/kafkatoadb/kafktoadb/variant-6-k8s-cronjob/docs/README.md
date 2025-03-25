# Вариант 6: Kubernetes CronJob без Airflow

## Описание

Данный вариант предполагает использование стандартного ресурса Kubernetes CronJob для регулярного запуска Spark-заданий, обрабатывающих данные из Kafka в ADB. В отличие от варианта с Airflow, здесь используется нативная функциональность Kubernetes без необходимости дополнительной оркестрации через Airflow.

## Преимущества

- **Нативное решение Kubernetes**: Не требуется установка и поддержка Apache Airflow
- **Минимальная инфраструктура**: Сокращение количества компонентов в инфраструктуре
- **Снижение сложности**: Меньше уровней абстракции
- **Легкость мониторинга**: Прямой доступ к логам и статусам заданий через стандартные инструменты Kubernetes
- **Отказоустойчивость**: Kubernetes автоматически перезапускает неудачные задания согласно политике backoffLimit
- **Более простая отладка**: Прозрачная модель выполнения и отладки прямо в Kubernetes

## Недостатки

- **Ограниченная функциональность**: Нет возможности создавать сложные DAG с зависимостями между заданиями
- **Ручное управление зависимостями**: При необходимости связать несколько задач требуется дополнительная логика
- **Ограниченный UI**: Отсутствие удобного интерфейса для мониторинга и управления заданиями
- **Меньше инструментов для отчетности**: Нет встроенных средств для создания отчетов и уведомлений
- **Сложнее динамическое параметризование**: Ограниченные возможности для передачи параметров между запусками

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Kubernetes Cluster │     │  CronJob Resource     │
│                     │────▶│  (планирование        │
│                     │     │   запусков)           │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Secret с           │─────│  Job/Pod создание     │
│  сертификатами      │     │  (при наступлении     │
│                     │     │   времени)            │
└─────────────────────┘     └───────────────────────┘
                                      │
                                      ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark-submit в     │────▶│  Spark Driver/        │
│  контейнере         │     │  Executor Pods        │
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

1. Создание Kubernetes Secret с сертификатами для подключения к Kafka
2. Подготовка образа контейнера с Spark и необходимыми зависимостями
3. Разработка конфигурационного файла для CronJob с настройкой расписания
4. Настройка механизма логирования и мониторинга заданий
5. Настройка параметров Spark для обеспечения отказоустойчивости

## Описание ключевых файлов

### spark-job-cronjob.yaml

Файл `spark-job-cronjob.yaml` содержит описание Kubernetes CronJob ресурса, который:

- Определяет расписание запуска Spark-заданий
- Настраивает контейнер с образом Spark
- Монтирует секреты с сертификатами
- Определяет команду запуска Spark-приложения
- Настраивает политику перезапуска при ошибках
- Задает ресурсные ограничения для контейнера

### sparkapp.py

Файл `sparkapp.py` содержит Spark-приложение, которое:

- Читает данные из Kafka с использованием SSL/TLS
- Обрабатывает и трансформирует данные
- Записывает результаты в ADB
- Использует сертификаты для подключения к Kafka
- Обеспечивает подробное логирование процесса

## Пример конфигурации CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: kafka-spark-adb-job
  namespace: spark
spec:
  schedule: "0 2 * * *"  # Запуск каждый день в 2:00
  concurrencyPolicy: Forbid  # Запретить параллельные запуски
  successfulJobsHistoryLimit: 3  # Хранить историю 3 последних успешных заданий
  failedJobsHistoryLimit: 5  # Хранить историю 5 последних неудачных заданий
  jobTemplate:
    spec:
      backoffLimit: 3  # Количество повторных попыток при ошибке
      activeDeadlineSeconds: 7200  # Максимальное время выполнения (2 часа)
      template:
        spec:
          restartPolicy: OnFailure
          serviceAccountName: spark-sa
          containers:
          - name: spark-job
            image: apache/spark:3.3.0
            args:
              - /bin/bash
              - -c
              - >
                spark-submit
                --master k8s://https://kubernetes.default.svc:443
                --deploy-mode cluster
                --conf spark.kubernetes.container.image=apache/spark:3.3.0
                --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark-sa
                --conf spark.executor.instances=2
                --conf spark.jars.packages=org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.postgresql:postgresql:42.2.23
                --conf spark.driver.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties
                --conf spark.executor.extraJavaOptions=-Dlog4j.configuration=file:///log4j.properties
                --conf spark.kafka.ssl.keystore.location=/etc/kafka/ssl/keystore.jks
                --conf spark.kafka.ssl.truststore.location=/etc/kafka/ssl/truststore.jks
                --conf spark.kafka.ssl.keystore.password=${KEYSTORE_PASSWORD}
                --conf spark.kafka.ssl.truststore.password=${TRUSTSTORE_PASSWORD}
                /opt/spark/work-dir/sparkapp.py
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
              - name: spark-app
                mountPath: /opt/spark/work-dir
              - name: kafka-certs
                mountPath: /etc/kafka/ssl
            resources:
              requests:
                memory: "1Gi"
                cpu: "500m"
              limits:
                memory: "2Gi"
                cpu: "1000m"
          volumes:
            - name: spark-app
              configMap:
                name: spark-app-files
            - name: kafka-certs
              secret:
                secretName: kafka-ssl-certs
                items:
                  - key: keystore.jks
                    path: keystore.jks
                  - key: truststore.jks
                    path: truststore.jks
```

## ConfigMap для Spark-приложения

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: spark-app-files
  namespace: spark
data:
  sparkapp.py: |
    import os
    import sys
    from pyspark.sql import SparkSession
    
    # Создание SparkSession
    spark = SparkSession.builder \
        .appName("KafkaToADB") \
        .getOrCreate()
    
    # Чтение данных из Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", os.environ.get("KAFKA_BOOTSTRAP_SERVERS")) \
        .option("subscribe", os.environ.get("KAFKA_TOPIC")) \
        .option("startingOffsets", "latest") \
        .option("kafka.security.protocol", "SSL") \
        .load()
    
    # Обработка данных
    # ...
    
    # Запись в ADB
    # ...
    
    # Запуск потока
    query = df.writeStream \
        .format("console") \
        .start()
    
    query.awaitTermination()
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

# Создание ConfigMap с Spark-приложением
kubectl create configmap spark-app-files --from-file=sparkapp.py=/path/to/sparkapp.py -n spark

# Создание CronJob
kubectl apply -f spark-job-cronjob.yaml -n spark
```

### Мониторинг

```bash
# Проверка статуса CronJob
kubectl get cronjobs -n spark

# Просмотр созданных Job
kubectl get jobs -n spark

# Просмотр запущенных Pod
kubectl get pods -n spark

# Просмотр логов выполнения
kubectl logs <pod-name> -n spark

# Ручной запуск Job
kubectl create job --from=cronjob/kafka-spark-adb-job manual-run-$(date +%s) -n spark
``` 