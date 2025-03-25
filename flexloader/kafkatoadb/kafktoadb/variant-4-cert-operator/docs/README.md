# Вариант 4: Управление сертификатами с помощью cert-manager

## Описание

Данный вариант предполагает использование cert-manager - Kubernetes-нативного решения для автоматизации управления и выдачи сертификатов. Cert-manager интегрируется с различными источниками сертификатов (Let's Encrypt, HashiCorp Vault, самоподписанные CA) и автоматически обновляет сертификаты перед истечением срока действия.

## Преимущества

- **Автоматическая ротация**: Автоматическое обновление сертификатов перед истечением срока действия
- **Kubernetes-нативное решение**: Использует стандартные Kubernetes ресурсы и API
- **Масштабируемость**: Эффективно работает в больших кластерах с множеством сертификатов
- **Поддержка различных источников**: Let's Encrypt, Vault, собственный CA и другие источники сертификатов
- **Стандартизация**: Единый подход к управлению всеми сертификатами в кластере
- **Уведомления**: Возможность настройки уведомлений о проблемах с сертификатами

## Недостатки

- **Только для Kubernetes**: Решение ограничено средой Kubernetes
- **Требуется дополнительный компонент**: Необходимо развернуть и поддерживать cert-manager в кластере
- **Сложность диагностики**: Иногда бывает сложно диагностировать проблемы с выдачей сертификатов
- **Требуется настройка**: Требуется начальная настройка Issuers/ClusterIssuers

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Cert-Manager       │────▶│  Certificate Authority│
│  Controller         │     │  (внутренний или      │
│                     │◀────│   внешний)            │
└─────────────────────┘     └───────────────────────┘
        │
        │ 
        ▼
┌─────────────────────┐
│                     │
│  Certificate CRD    │
│  (запрос на выдачу) │
└─────────────────────┘
        │
        │
        ▼
┌─────────────────────┐
│                     │
│  Secret с           │
│  сертификатом       │
└─────────────────────┘
        │
        │
        ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Airflow            │────▶│  Запуск DAG           │
│                     │     │                       │
└─────────────────────┘     └───────────────────────┘
        │
        ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark Application  │────▶│  Kafka Cluster        │
│  (монтирует Secret) │     │  (SSL/TLS)            │
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

1. Установка cert-manager в Kubernetes кластер
2. Настройка Issuer/ClusterIssuer для выдачи сертификатов
3. Создание Certificate ресурса для Kafka-клиентских сертификатов
4. Настройка Spark-приложения для монтирования созданных секретов
5. Конфигурация автоматических уведомлений об истечении срока действия
6. Настройка Apache Airflow DAG для оркестрации процесса

## Описание ключевых файлов

### dag.py

Файл `dag.py` содержит DAG для Apache Airflow, который управляет процессом передачи данных из Kafka в ADB с использованием Spark. Ключевые особенности:

- Использует `KubernetesPodOperator` для запуска Spark-задания в Kubernetes
- Монтирует сертификаты, сгенерированные cert-manager, в Spark-под
- Реализует обработку ошибок и мониторинг статуса выполнения
- Настраивает переменные окружения для доступа к Kafka и ADB
- Обеспечивает передачу параметров между Airflow и Spark приложением
- Включает мониторинг срока действия сертификатов и предупреждения

### sparkapp.py

Файл `sparkapp.py` содержит Spark-приложение, которое:

- Читает данные из Kafka с использованием SSL/TLS
- Обрабатывает и трансформирует данные
- Записывает результаты в ADB
- Использует сертификаты, автоматически сгенерированные cert-manager
- Настраивает SSL-соединение с Kafka с помощью этих сертификатов
- Обеспечивает подробное логирование процесса
- Включает проверку срока действия используемых сертификатов

Приложение получает доступ к сертификатам, смонтированным из Secret, который автоматически обновляется cert-manager при приближении срока истечения.

## Пример определения Certificate

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: kafka-client-cert
  namespace: spark
spec:
  secretName: kafka-client-certs
  duration: 2160h # 90 дней
  renewBefore: 360h # 15 дней до истечения
  subject:
    organizations:
      - Spark Application
  isCA: false
  privateKey:
    algorithm: RSA
    encoding: PKCS8
    size: 2048
  usages:
    - client auth
  dnsNames:
    - kafka-client
  issuerRef:
    name: kafka-ca-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```

## Пример Issuer

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: kafka-ca-issuer
spec:
  ca:
    secretName: kafka-ca-key-pair
```

## Пример SparkApplication с использованием сертификатов

```yaml
apiVersion: "sparkoperator.k8s.io/v1beta2"
kind: SparkApplication
metadata:
  name: kafka-spark-adb
  namespace: spark
spec:
  type: Scala
  mode: cluster
  image: "apache/spark:3.3.0"
  mainClass: org.example.KafkaSparkADB
  driver:
    cores: 1
    memory: "1g"
    serviceAccount: spark
    volumeMounts:
      - name: kafka-certs
        mountPath: /etc/kafka/certs
    env:
      - name: KAFKA_KEYSTORE_PATH
        value: /etc/kafka/certs/keystore.jks
      - name: KAFKA_TRUSTSTORE_PATH
        value: /etc/kafka/certs/truststore.jks
  executor:
    cores: 1
    instances: 2
    memory: "1g"
    volumeMounts:
      - name: kafka-certs
        mountPath: /etc/kafka/certs
    env:
      - name: KAFKA_KEYSTORE_PATH
        value: /etc/kafka/certs/keystore.jks
      - name: KAFKA_TRUSTSTORE_PATH
        value: /etc/kafka/certs/truststore.jks
  volumes:
    - name: kafka-certs
      secret:
        secretName: kafka-client-certs
```

## Конфигурация SparkSession

```python
spark = SparkSession.builder \
    .appName("Kafka-Spark-ADB") \
    .config("spark.kafka.ssl.keystore.location", os.environ.get("KAFKA_KEYSTORE_PATH")) \
    .config("spark.kafka.ssl.truststore.location", os.environ.get("KAFKA_TRUSTSTORE_PATH")) \
    .config("spark.kafka.ssl.keystore.password", os.environ.get("KEYSTORE_PASSWORD")) \
    .config("spark.kafka.ssl.truststore.password", os.environ.get("TRUSTSTORE_PASSWORD")) \
    .getOrCreate()
```

## Автоматизация преобразования сертификатов

Поскольку cert-manager создает сертификаты в формате PEM, а Kafka часто требует JKS, можно создать Job для преобразования:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: cert-converter
  namespace: spark
spec:
  template:
    spec:
      containers:
      - name: cert-converter
        image: adoptopenjdk/openjdk11:alpine
        command:
        - /bin/sh
        - -c
        - |
          keytool -importcert -file /certs/tls.crt -keystore /output/truststore.jks -storepass ${STORE_PASSWORD} -noprompt
          openssl pkcs12 -export -in /certs/tls.crt -inkey /certs/tls.key -out /tmp/keystore.p12 -name kafka -password pass:${STORE_PASSWORD}
          keytool -importkeystore -srckeystore /tmp/keystore.p12 -srcstoretype PKCS12 -srcstorepass ${STORE_PASSWORD} -destkeystore /output/keystore.jks -deststorepass ${STORE_PASSWORD} -destkeypass ${STORE_PASSWORD}
        env:
        - name: STORE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: kafka-store-password
              key: password
        volumeMounts:
        - name: certs
          mountPath: /certs
        - name: output
          mountPath: /output
      volumes:
      - name: certs
        secret:
          secretName: kafka-client-certs
      - name: output
        emptyDir: {}
      restartPolicy: OnFailure
``` 