# Вариант 1: Использование Kubernetes Secrets

## Описание

Данный вариант предполагает использование Kubernetes Secrets для хранения и монтирования сертификатов в Spark-поды для взаимодействия с Kafka через SSL/TLS. Kubernetes Secrets обеспечивают базовый уровень безопасности для хранения чувствительной информации, такой как сертификаты и ключи.

## Преимущества

- **Встроенное решение**: Kubernetes Secrets являются встроенным механизмом К8s для хранения секретов
- **Простота использования**: Относительно просто создавать и использовать в сравнении с другими решениями
- **Интеграция с RBAC**: Возможность контроля доступа к секретам через Kubernetes RBAC
- **Масштабируемость**: Хорошо масштабируется для большого количества приложений
- **Знакомый механизм**: Большинство DevOps-инженеров знакомы с Kubernetes Secrets

## Недостатки

- **Ограниченная безопасность**: Секреты хранятся в etcd в нешифрованном или слабо зашифрованном виде по умолчанию
- **Ручное обновление**: Требуется ручное обновление секретов при смене сертификатов
- **Отсутствие версионирования**: Нет встроенного механизма версионирования секретов
- **Ручная ротация**: Нет автоматической ротации сертификатов

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Администратор      │────▶│  Создание Kubernetes  │
│                     │     │  Secret с сертификатами│
└─────────────────────┘     └───────────────────────┘
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
│  Spark Application  │◀────│  Kubernetes Pod       │
│  Definition         │     │  (монтирование Secret)│
└─────────────────────┘     └───────────────────────┘
        │
        │
        ▼
┌─────────────────────┐
│                     │
│  Spark Driver/      │
│  Executor Pods      │
└─────────────────────┘
        │
        │
        ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark Application  │────▶│  Kafka Cluster        │
│  (использование     │     │  (SSL/TLS)            │
│   сертификатов)     │     │                       │
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

1. Создание Kubernetes Secret, содержащего необходимые keystores/truststores
2. Настройка SparkApplication CRD для монтирования Secret в Spark-поды
3. Настройка RBAC для ограничения доступа к Secret
4. Конфигурация Spark для использования сертификатов при подключении к Kafka
5. Настройка Apache Airflow DAG для оркестрации процесса

## Описание ключевых файлов

### dag.py

Файл `dag.py` содержит DAG для Apache Airflow, который управляет процессом передачи данных из Kafka в ADB с использованием Spark. Ключевые особенности:

- Использует `KubernetesPodOperator` для запуска Spark-задания в Kubernetes
- Монтирует сертификаты из Kubernetes Secrets в Spark-под
- Реализует обработку ошибок и мониторинг статуса выполнения
- Настраивает переменные окружения для доступа к Kafka и ADB
- Обеспечивает передачу параметров между Airflow и Spark приложением
- Содержит конфигурацию ресурсов и параметров безопасности для Spark-пода

### sparkapp.py

Файл `sparkapp.py` содержит Spark-приложение, которое:

- Читает данные из Kafka с использованием SSL/TLS
- Обрабатывает и трансформирует данные
- Записывает результаты в ADB
- Использует сертификаты, монтированные из Kubernetes Secrets
- Настраивает SSL-соединение с Kafka с помощью сертификатов
- Обеспечивает подробное логирование процесса

Приложение обращается к сертификатам, смонтированным по пути `/etc/kafka/ssl/`, и использует пароли, переданные через переменные окружения.

## Пример создания Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-ssl-certs
  namespace: spark
type: Opaque
data:
  keystore.jks: |
    /u3+7QAAAAIAAAAA.... # base64-закодированное содержимое keystore
  truststore.jks: |
    /u3+7QAAAAIAAAAA.... # base64-закодированное содержимое truststore
  keystore-password: cGFzc3dvcmQ= # base64-закодированный пароль
  truststore-password: cGFzc3dvcmQ= # base64-закодированный пароль
```

## Пример SparkApplication CRD

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
        mountPath: /etc/kafka/ssl
    env:
      - name: KEYSTORE_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kafka-ssl-certs
            key: keystore-password
      - name: TRUSTSTORE_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kafka-ssl-certs
            key: truststore-password
  executor:
    cores: 1
    instances: 2
    memory: "1g"
    volumeMounts:
      - name: kafka-certs
        mountPath: /etc/kafka/ssl
    env:
      - name: KEYSTORE_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kafka-ssl-certs
            key: keystore-password
      - name: TRUSTSTORE_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kafka-ssl-certs
            key: truststore-password
  volumes:
    - name: kafka-certs
      secret:
        secretName: kafka-ssl-certs
        items:
          - key: keystore.jks
            path: keystore.jks
          - key: truststore.jks
            path: truststore.jks
```

## Пример RBAC для ограничения доступа

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: spark-kafka-secrets-reader
  namespace: spark
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["kafka-ssl-certs"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: spark-kafka-secrets-reader-binding
  namespace: spark
subjects:
- kind: ServiceAccount
  name: spark
  namespace: spark
roleRef:
  kind: Role
  name: spark-kafka-secrets-reader
  apiGroup: rbac.authorization.k8s.io
```

## Конфигурация SparkSession

```python
spark = SparkSession.builder \
    .appName("Kafka-Spark-ADB") \
    .config("spark.kafka.ssl.keystore.location", "/etc/kafka/ssl/keystore.jks") \
    .config("spark.kafka.ssl.truststore.location", "/etc/kafka/ssl/truststore.jks") \
    .config("spark.kafka.ssl.keystore.password", os.environ.get("KEYSTORE_PASSWORD")) \
    .config("spark.kafka.ssl.truststore.password", os.environ.get("TRUSTSTORE_PASSWORD")) \
    .getOrCreate()
```

## Безопасные практики

1. Включение шифрования etcd для защиты секретов на диске
2. Регулярная ротация сертификатов и секретов
3. Применение принципа наименьших привилегий для доступа к секретам
4. Аудит доступа к секретам
5. Резервное копирование секретов
6. Рассмотрение возможности использования внешнего хранилища секретов (Vault) для повышения безопасности 