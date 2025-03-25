# MetricsManager

## Обзор

`MetricsManager` - компонент для сбора, хранения и анализа метрик приложения Kafka to ADB. Обеспечивает мониторинг производительности, состояния системы и бизнес-метрик.

## Основные возможности

- Сбор системных метрик (CPU, память)
- Отслеживание производительности операций
- Хранение исторических данных
- Агрегация метрик
- Мониторинг состояния приложения

## Структура

### Классы

#### MetricValue
```python
@dataclass
class MetricValue:
    value: float                # Значение метрики
    timestamp: datetime         # Время измерения
    labels: Dict[str, str]     # Метки для группировки
```

#### MetricsManager
```python
class MetricsManager:
    def __init__(self):
        self.metrics: Dict[str, Dict[str, MetricValue]] = defaultdict(dict)
        self._lock = threading.Lock()
        self._start_time = time.time()
```

## Методы

### Основные операции
- `record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None)`: Запись метрики
- `get_metric(name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]`: Получение значения метрики
- `get_all_metrics() -> Dict[str, Dict[str, Any]]`: Получение всех метрик
- `get_health_status() -> Dict[str, Any]`: Получение статуса здоровья

### Специализированные методы
- `record_latency(operation: str, duration: float)`: Запись латентности
- `record_error(operation: str)`: Запись ошибки
- `record_success(operation: str)`: Запись успешной операции
- `record_memory_usage()`: Запись использования памяти
- `record_cpu_usage()`: Запись использования CPU

### Мониторинг
- `start_monitoring(interval: int = 60)`: Запуск мониторинга
- `get_uptime() -> float`: Получение времени работы

## Конфигурация

### Параметры
- `metrics_interval`: Интервал сбора метрик
- `retention_period`: Период хранения метрик
- `aggregation_interval`: Интервал агрегации

### Пример конфигурации
```yaml
metrics:
  enabled: true
  retention_period: 86400
  aggregation_interval: 60
```

## Использование

### Базовое использование
```python
metrics_manager = MetricsManager()

# Запись метрики
metrics_manager.record_metric(
    name="messages_processed",
    value=100,
    labels={"topic": "test"}
)

# Получение метрики
value = metrics_manager.get_metric(
    name="messages_processed",
    labels={"topic": "test"}
)
```

### Мониторинг системы
```python
# Запуск мониторинга
metrics_manager.start_monitoring(interval=60)

# Получение статуса
status = metrics_manager.get_health_status()
print(f"Uptime: {status['uptime']}")
print(f"Memory usage: {status['memory_usage']}")
print(f"CPU usage: {status['cpu_usage']}")
```

## Метрики

### Системные метрики
- Использование CPU
- Использование памяти
- Время работы
- Количество потоков

### Бизнес-метрики
- Количество обработанных сообщений
- Латентность операций
- Количество ошибок
- Успешность операций

### Пример получения метрик
```python
# Получение всех метрик
all_metrics = metrics_manager.get_all_metrics()

# Анализ метрик
for name, values in all_metrics.items():
    print(f"Metric: {name}")
    for labels, data in values.items():
        print(f"  Labels: {labels}")
        print(f"  Value: {data['value']}")
        print(f"  Timestamp: {data['timestamp']}")
```

## Обработка ошибок

### Типы ошибок
- Ошибки записи метрик
- Ошибки чтения метрик
- Ошибки мониторинга
- Ошибки агрегации

### Пример обработки
```python
try:
    metrics_manager.record_metric("test_metric", 1.0)
except Exception as e:
    logger.error(f"Ошибка записи метрики: {str(e)}")
```

## Интеграция

### Интеграция с другими компонентами
- `ConfigManager`: Получение настроек
- `ErrorHandler`: Обработка ошибок
- `Application`: Основное приложение

### Пример интеграции
```python
class Application:
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.metrics_manager = MetricsManager()
        self.metrics_manager.start_monitoring(
            interval=self.config_manager.get('metrics_interval')
        )
```

## Тестирование

### Unit-тесты
```python
def test_metric_recording():
    metrics_manager = MetricsManager()
    metrics_manager.record_metric("test", 1.0)
    assert metrics_manager.get_metric("test") == 1.0

def test_metric_labels():
    metrics_manager = MetricsManager()
    metrics_manager.record_metric("test", 1.0, {"label": "value"})
    assert metrics_manager.get_metric("test", {"label": "value"}) == 1.0
```

### Интеграционные тесты
```python
def test_system_monitoring():
    metrics_manager = MetricsManager()
    metrics_manager.start_monitoring()
    time.sleep(2)  # Ждем сбора метрик
    status = metrics_manager.get_health_status()
    assert "memory_usage" in status
    assert "cpu_usage" in status
```

## Логирование

### Формат логов
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования
- INFO: Основные операции
- DEBUG: Детальная информация
- ERROR: Критические ошибки

## Рекомендации по использованию

1. **Инициализация**
   - Создавать экземпляр в начале работы приложения
   - Настраивать интервалы мониторинга

2. **Мониторинг**
   - Регулярно проверять состояние
   - Анализировать тренды
   - Настраивать алерты

3. **Хранение**
   - Контролировать объем данных
   - Регулярно очищать старые метрики
   - Резервное копирование

4. **Анализ**
   - Использовать агрегацию
   - Отслеживать аномалии
   - Строить графики

## Известные ограничения

1. **Производительность**
   - Накладные расходы на сбор метрик
   - Ограничения памяти
   - Влияние на CPU

2. **Масштабируемость**
   - Ограничения на количество метрик
   - Объем хранимых данных
   - Скорость агрегации

3. **Точность**
   - Погрешность измерений
   - Задержка сбора
   - Потеря данных

## Планы развития

1. **Краткосрочные**
   - Улучшение производительности
   - Расширение метрик
   - Улучшение агрегации

2. **Долгосрочные**
   - Интеграция с внешними системами
   - Машинное обучение для анализа
   - Автоматическая оптимизация 