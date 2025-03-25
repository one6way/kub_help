# Вариант 3: Интеграция с HashiCorp Vault

## Описание

Данный вариант предполагает использование HashiCorp Vault для безопасного хранения и управления сертификатами, которые используются Spark-приложениями для взаимодействия с Kafka. Vault обеспечивает централизованное хранилище секретов с контролем доступа, аудитом и возможностью автоматической ротации сертификатов.

## Преимущества

- **Централизованное управление**: Единое место для хранения и управления всеми сертификатами
- **Контроль доступа**: Детальные политики доступа на основе ролей
- **Аудит**: Полное протоколирование доступа к сертификатам
- **Автоматическая ротация**: Возможность автоматической замены сертификатов по истечении срока действия
- **Динамические сертификаты**: Возможность генерировать сертификаты по запросу
- **Интеграция с PKI**: Встроенная поддержка инфраструктуры открытых ключей

## Недостатки

- **Дополнительная инфраструктура**: Требуется развертывание и поддержка Vault
- **Сложность настройки**: Более сложная начальная настройка по сравнению с другими вариантами
- **Зависимость от внешнего сервиса**: Приложения зависят от доступности Vault
- **Задержки при запуске**: Время, затрачиваемое на получение сертификатов из Vault

## Схема взаимодействия

```
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  HashiCorp Vault    │◀────│  Администратор        │
│  (PKI/Secrets)      │     │  (загрузка сертификатов)│
└─────────────────────┘     └───────────────────────┘
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
│  Vault Agent        │◀────│  Kubernetes Auth      │
│  Injector           │     │  (ServiceAccount)     │
└─────────────────────┘     └───────────────────────┘
        │
        │
        ▼
┌─────────────────────┐
│  Init Container     │
│  (получение         │
│   сертификатов)     │
└─────────────────────┘
        │
        │
        ▼
┌─────────────────────┐     ┌───────────────────────┐
│                     │     │                       │
│  Spark Application  │────▶│  Kafka Cluster        │
│  Pod                │     │  (SSL/TLS)            │
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

1. Развертывание HashiCorp Vault в Kubernetes кластере
2. Настройка PKI или Secrets Engine для хранения сертификатов
3. Настройка Kubernetes Auth Method для аутентификации подов
4. Внедрение Vault Agent Injector для автоматического получения сертификатов
5. Настройка init-контейнера для получения сертификатов при запуске пода
6. Конфигурация Spark-приложения для использования сертификатов
7. Настройка Apache Airflow DAG для оркестрации процесса

## Описание ключевых файлов

### dag.py

Файл `dag.py` содержит DAG для Apache Airflow, который управляет процессом передачи данных из Kafka в ADB с использованием Spark. Ключевые особенности:

- Использует `KubernetesPodOperator` для запуска Spark-задания в Kubernetes
- Настраивает аннотации для Vault Agent Injector
- Реализует обработку ошибок и мониторинг статуса выполнения
- Настраивает ServiceAccount с необходимыми правами для аутентификации в Vault
- Обеспечивает передачу параметров между Airflow и Spark приложением
- Содержит конфигурацию для инициализации подключения к Vault

### sparkapp.py

Файл `sparkapp.py` содержит Spark-приложение, которое:

- Читает данные из Kafka с использованием SSL/TLS
- Обрабатывает и трансформирует данные
- Записывает результаты в ADB
- Использует сертификаты, полученные из Vault через Vault Agent
- Настраивает SSL-соединение с Kafka с помощью этих сертификатов
- Обеспечивает подробное логирование процесса
- Содержит логику обработки ошибок при недоступности сертификатов

Приложение обращается к сертификатам, смонтированным по пути `/vault/secrets/`, куда их автоматически помещает Vault Agent Injector.

## Пример конфигурации Vault

```hcl
# Включение PKI Secrets Engine
path "pki" {
  capabilities = ["read", "list"]
}

# Создание роли для Spark-приложений
path "pki/issue/spark-kafka-role" {
  capabilities = ["create", "update"]
}

# Политика доступа
path "secret/data/kafka-certs" {
  capabilities = ["read"]
}
```

## Пример конфигурации Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spark-application
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/agent-inject-secret-kafka-cert: "secret/data/kafka-certs"
        vault.hashicorp.com/agent-inject-template-kafka-cert: |
          {{- with secret "secret/data/kafka-certs" -}}
          {{ .Data.data.keystore_content }}
          {{- end -}}
        vault.hashicorp.com/role: "spark-app"
    spec:
      serviceAccountName: spark-vault-auth
      containers:
      - name: spark-app
        image: apache/spark:3.3.0
        env:
        - name: KAFKA_KEYSTORE_PATH
          value: /vault/secrets/kafka-keystore.jks
        - name: KAFKA_TRUSTSTORE_PATH
          value: /vault/secrets/kafka-truststore.jks
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

## Безопасные практики

1. Использование короткоживущих токенов для аутентификации в Vault
2. Настройка детальных политик доступа для разных приложений
3. Включение аудита всех операций с сертификатами
4. Настройка автоматической ротации сертификатов
5. Регулярное тестирование процедуры восстановления Vault 