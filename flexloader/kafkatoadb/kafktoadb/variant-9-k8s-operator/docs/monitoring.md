# Мониторинг приложения

## Обзор

Документация по мониторингу приложения Kafka to ADB описывает систему мониторинга, метрики, алерты и инструменты для отслеживания состояния приложения.

## Метрики

### 1. Системные метрики
```python
# Системные метрики
system_metrics = {
    "memory_usage": "kafka_to_adb_memory_usage_bytes",
    "cpu_usage": "kafka_to_adb_cpu_usage_percent",
    "disk_usage": "kafka_to_adb_disk_usage_bytes",
    "network_io": "kafka_to_adb_network_io_bytes"
}
```

### 2. Бизнес-метрики
```python
# Бизнес-метрики
business_metrics = {
    "processed_messages": "kafka_to_adb_processed_messages_total",
    "failed_messages": "kafka_to_adb_failed_messages_total",
    "processing_time": "kafka_to_adb_message_processing_seconds",
    "queue_size": "kafka_to_adb_queue_size"
}
```

### 3. Метрики безопасности
```python
# Метрики безопасности
security_metrics = {
    "certificate_expiry": "kafka_to_adb_certificate_expiry_seconds",
    "ssl_errors": "kafka_to_adb_ssl_errors_total",
    "auth_failures": "kafka_to_adb_auth_failures_total"
}
```

## Prometheus интеграция

### 1. Конфигурация
```yaml
# prometheus.yaml
scrape_configs:
  - job_name: 'kafka-to-adb'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### 2. Метрики
```python
# metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Счетчики
processed_messages = Counter(
    'kafka_to_adb_processed_messages_total',
    'Total number of processed messages'
)

# Гейджи
memory_usage = Gauge(
    'kafka_to_adb_memory_usage_bytes',
    'Current memory usage in bytes'
)

# Гистограммы
processing_time = Histogram(
    'kafka_to_adb_message_processing_seconds',
    'Message processing time in seconds'
)
```

### 3. Запросы
```promql
# Запросы PromQL
# Использование памяти
kafka_to_adb_memory_usage_bytes

# Скорость обработки сообщений
rate(kafka_to_adb_processed_messages_total[5m])

# Время обработки
histogram_quantile(0.95, rate(kafka_to_adb_message_processing_seconds_bucket[5m]))
```

## Grafana дашборды

### 1. Системные метрики
```json
{
  "dashboard": {
    "title": "System Metrics",
    "panels": [
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "kafka_to_adb_memory_usage_bytes"
          }
        ]
      },
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "kafka_to_adb_cpu_usage_percent"
          }
        ]
      }
    ]
  }
}
```

### 2. Бизнес-метрики
```json
{
  "dashboard": {
    "title": "Business Metrics",
    "panels": [
      {
        "title": "Message Processing Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(kafka_to_adb_processed_messages_total[5m])"
          }
        ]
      },
      {
        "title": "Processing Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(kafka_to_adb_message_processing_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Алерты

### 1. Конфигурация
```yaml
# alerts.yaml
groups:
  - name: kafka-to-adb
    rules:
      - alert: HighMemoryUsage
        expr: kafka_to_adb_memory_usage_bytes > 1.5e9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage
          description: Memory usage is above 1.5GB

      - alert: HighErrorRate
        expr: rate(kafka_to_adb_failed_messages_total[5m]) / rate(kafka_to_adb_processed_messages_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate
          description: Error rate is above 1%
```

### 2. Уведомления
```yaml
# notification.yaml
receivers:
  - name: team-slack
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
        title: '{{ template "slack.default.title" . }}'
        text: '{{ template "slack.default.text" . }}'
```

## Логирование

### 1. Конфигурация
```python
# logging.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Структурированные логи
```python
# structured_logging.py
import structlog

logger = structlog.get_logger()

def process_message(message):
    logger.info("processing_message",
                message_id=message.id,
                topic=message.topic,
                size=len(message.value))
```

## Мониторинг производительности

### 1. Профилирование
```python
# profiling.py
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats()
        return result
    return wrapper
```

### 2. Трассировка
```python
# tracing.py
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

def process_message(message):
    with tracer.start_as_current_span("process_message") as span:
        span.set_attribute("message_id", message.id)
        try:
            result = process(message)
            span.set_status(Status(StatusCode.OK))
            return result
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR))
            raise
```

## Мониторинг безопасности

### 1. Аудит
```python
# audit.py
import logging

audit_logger = logging.getLogger('audit')

def log_security_event(event_type, details):
    audit_logger.info("security_event",
                     event_type=event_type,
                     details=details,
                     timestamp=datetime.now().isoformat())
```

### 2. Проверка сертификатов
```python
# certificate_monitoring.py
def check_certificates():
    metrics = {
        'expiry_days': get_certificate_expiry_days(),
        'last_rotation': get_last_rotation_time(),
        'validation_status': check_certificate_validity()
    }
    return metrics
```

## Рекомендации по мониторингу

### 1. Метрики
- Собирать релевантные метрики
- Использовать правильные типы метрик
- Настраивать агрегацию

### 2. Алерты
- Устанавливать разумные пороги
- Настраивать уведомления
- Регулярно проверять

### 3. Логирование
- Использовать структурированные логи
- Настраивать ротацию
- Хранить историю

### 4. Производительность
- Мониторить ресурсы
- Отслеживать задержки
- Анализировать узкие места

## Инструменты

### 1. Мониторинг
- Prometheus
- Grafana
- Alertmanager

### 2. Логирование
- ELK Stack
- Graylog
- Loki

### 3. Трассировка
- Jaeger
- Zipkin
- OpenTelemetry

### 4. Профилирование
- cProfile
- line_profiler
- memory_profiler 