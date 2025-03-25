# Конфигурация приложения

## Обзор

Конфигурация приложения Kafka to ADB хранится в YAML-файле и содержит все необходимые настройки для работы приложения. Конфигурация разделена на логические секции для удобства управления.

## Структура конфигурации

### Основные настройки
```yaml
app_name: "kafka-to-adb"
environment: "production"
version: "1.0.0"
```

### Сертификаты
```yaml
certificates:
  path: "/path/to/certs"
  refresh_interval: 3600  # секунды
  validation:
    check_expiry: true
    check_integrity: true
    check_revocation: true
```

### Обработка ошибок
```yaml
error_handling:
  max_retries: 3
  retry_delay: 5  # секунды
  auto_recovery: true
  recovery_interval: 300  # секунды
  severity_levels:
    low: ["connection_error", "timeout"]
    medium: ["data_error", "validation_error"]
    high: ["security_error", "certificate_error"]
    critical: ["system_error", "fatal_error"]
```

### Мониторинг
```yaml
monitoring:
  metrics_interval: 60  # секунды
  retention_period: 86400  # секунды
  thresholds:
    memory_usage: 80  # проценты
    cpu_usage: 70  # проценты
    error_rate: 0.01  # 1%
```

### Логирование
```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "app.log"
  max_size: 10485760  # 10MB
  backup_count: 5
```

### Безопасность
```yaml
security:
  ssl_verify: true
  ssl_cert_reqs: "CERT_REQUIRED"
  ssl_check_hostname: true
  sensitive_data:
    encryption: true
    key_path: "/path/to/key"
```

### Производительность
```yaml
performance:
  batch_size: 1000
  poll_interval: 1  # секунды
  max_poll_records: 500
  compression_type: "gzip"
```

### Восстановление
```yaml
recovery:
  enabled: true
  max_attempts: 3
  backoff_factor: 2
  max_backoff: 300  # секунды
```

### Метрики
```yaml
metrics:
  enabled: true
  retention_period: 86400  # секунды
  aggregation_interval: 300  # секунды
  export:
    prometheus: true
    statsd: false
```

## Обязательные параметры

### Основные
- `app_name`: Имя приложения
- `environment`: Окружение (development, staging, production)
- `version`: Версия приложения

### Сертификаты
- `certificates.path`: Путь к директории с сертификатами
- `certificates.refresh_interval`: Интервал обновления сертификатов

### Обработка ошибок
- `error_handling.max_retries`: Максимальное количество попыток
- `error_handling.retry_delay`: Задержка между попытками

### Мониторинг
- `monitoring.metrics_interval`: Интервал сбора метрик
- `monitoring.thresholds.memory_usage`: Порог использования памяти

## Рекомендуемые значения

### Производительность
```yaml
performance:
  batch_size: 1000  # Оптимально для большинства случаев
  poll_interval: 1  # Минимальная задержка
  max_poll_records: 500  # Баланс между производительностью и нагрузкой
```

### Мониторинг
```yaml
monitoring:
  metrics_interval: 60  # Частое обновление для точности
  retention_period: 86400  # 24 часа для анализа
  thresholds:
    memory_usage: 80  # Безопасный порог
    cpu_usage: 70  # Оптимальная нагрузка
```

### Восстановление
```yaml
recovery:
  max_attempts: 3  # Достаточно для большинства ошибок
  backoff_factor: 2  # Экспоненциальная задержка
  max_backoff: 300  # Максимальная задержка
```

## Безопасность

### Рекомендации
1. **Сертификаты**
   - Хранить в защищенном месте
   - Регулярно обновлять
   - Проверять целостность

2. **Чувствительные данные**
   - Использовать шифрование
   - Хранить ключи отдельно
   - Ограничивать доступ

3. **SSL/TLS**
   - Включать проверку сертификатов
   - Проверять hostname
   - Использовать современные протоколы

## Валидация

### Проверки
1. **Обязательные поля**
   ```python
   required_fields = [
       "app_name",
       "environment",
       "certificates.path",
       "error_handling.max_retries"
   ]
   ```

2. **Типы данных**
   ```python
   type_checks = {
       "app_name": str,
       "environment": str,
       "certificates.refresh_interval": int,
       "monitoring.thresholds.memory_usage": float
   }
   ```

3. **Диапазоны значений**
   ```python
   range_checks = {
       "monitoring.thresholds.memory_usage": (0, 100),
       "error_handling.max_retries": (1, 10),
       "performance.batch_size": (100, 10000)
   }
   ```

## Пример полной конфигурации

```yaml
app_name: "kafka-to-adb"
environment: "production"
version: "1.0.0"

certificates:
  path: "/etc/kafka-to-adb/certs"
  refresh_interval: 3600
  validation:
    check_expiry: true
    check_integrity: true
    check_revocation: true

error_handling:
  max_retries: 3
  retry_delay: 5
  auto_recovery: true
  recovery_interval: 300
  severity_levels:
    low: ["connection_error", "timeout"]
    medium: ["data_error", "validation_error"]
    high: ["security_error", "certificate_error"]
    critical: ["system_error", "fatal_error"]

monitoring:
  metrics_interval: 60
  retention_period: 86400
  thresholds:
    memory_usage: 80
    cpu_usage: 70
    error_rate: 0.01

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "app.log"
  max_size: 10485760
  backup_count: 5

security:
  ssl_verify: true
  ssl_cert_reqs: "CERT_REQUIRED"
  ssl_check_hostname: true
  sensitive_data:
    encryption: true
    key_path: "/etc/kafka-to-adb/keys"

performance:
  batch_size: 1000
  poll_interval: 1
  max_poll_records: 500
  compression_type: "gzip"

recovery:
  enabled: true
  max_attempts: 3
  backoff_factor: 2
  max_backoff: 300

metrics:
  enabled: true
  retention_period: 86400
  aggregation_interval: 300
  export:
    prometheus: true
    statsd: false
```

## Обновление конфигурации

### Динамическое обновление
```python
def update_config(self, new_config: Dict[str, Any]):
    # Проверка валидности
    self._validate_config(new_config)
    
    # Обновление значений
    with self._lock:
        self._config.update(new_config)
    
    # Применение изменений
    self._apply_config_changes()
```

### Перезагрузка
```python
def reload_config(self):
    # Чтение файла
    with open(self.config_path, 'r') as f:
        new_config = yaml.safe_load(f)
    
    # Обновление
    self.update_config(new_config)
```

## Рекомендации по использованию

1. **Разработка**
   - Использовать отдельные конфигурации
   - Включать подробное логирование
   - Отключать некоторые проверки

2. **Тестирование**
   - Проверять все параметры
   - Тестировать граничные случаи
   - Валидировать значения

3. **Продакшн**
   - Использовать безопасные значения
   - Включать все проверки
   - Настраивать мониторинг

4. **Обновление**
   - Проверять совместимость
   - Тестировать изменения
   - Планировать откат 