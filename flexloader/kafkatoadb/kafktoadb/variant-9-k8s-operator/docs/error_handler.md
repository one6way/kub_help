# ErrorHandler

## Обзор

`ErrorHandler` - компонент для обработки, классификации и управления ошибками в приложении Kafka to ADB. Обеспечивает надежную обработку ошибок, автоматическое восстановление и мониторинг состояния системы.

## Основные возможности

- Классификация ошибок по важности
- Автоматические повторные попытки
- Логирование и отслеживание ошибок
- Механизмы восстановления
- Мониторинг состояния ошибок

## Структура

### Классы

#### ErrorSeverity
```python
class ErrorSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
```

#### ErrorInfo
```python
@dataclass
class ErrorInfo:
    timestamp: datetime
    error: Exception
    severity: ErrorSeverity
    context: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[datetime] = None
```

#### ErrorHandler
```python
class ErrorHandler:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.errors: Dict[str, ErrorInfo] = {}
        self._lock = threading.Lock()
```

## Методы

### Основные операции
- `handle_error(error: Exception, severity: ErrorSeverity, context: Optional[Dict[str, Any]] = None) -> str`: Обработка ошибки
- `resolve_error(error_id: str)`: Отметить ошибку как разрешенную
- `get_error_info(error_id: str) -> Optional[Dict[str, Any]]`: Получение информации об ошибке
- `get_all_errors() -> Dict[str, Dict[str, Any]]`: Получение всех ошибок

### Обработчики ошибок
- `_handle_low_severity(error_info: ErrorInfo)`: Обработка ошибок низкой важности
- `_handle_medium_severity(error_info: ErrorInfo)`: Обработка ошибок средней важности
- `_handle_high_severity(error_info: ErrorInfo)`: Обработка ошибок высокой важности
- `_handle_critical_severity(error_info: ErrorInfo)`: Обработка критических ошибок

### Утилиты
- `register_error_handler(severity: ErrorSeverity, handler: Callable)`: Регистрация обработчика
- `retry_operation(operation: Callable, *args, **kwargs) -> Any`: Повторная попытка операции

## Конфигурация

### Параметры
- `max_retries`: Максимальное количество попыток
- `retry_delay`: Задержка между попытками
- `auto_recovery`: Автоматическое восстановление
- `recovery_interval`: Интервал восстановления

### Пример конфигурации
```yaml
error_handling:
  max_retries: 3
  retry_delay: 5
  auto_recovery: true
  recovery_interval: 300
```

## Использование

### Базовое использование
```python
error_handler = ErrorHandler(max_retries=3, retry_delay=5)

# Обработка ошибки
try:
    # Код, который может вызвать ошибку
    raise Exception("Test error")
except Exception as e:
    error_id = error_handler.handle_error(
        error=e,
        severity=ErrorSeverity.MEDIUM,
        context={"operation": "test"}
    )
```

### Повторные попытки
```python
def test_operation():
    # Код операции
    raise Exception("Temporary error")

# Автоматические повторные попытки
result = error_handler.retry_operation(test_operation)
```

### Мониторинг ошибок
```python
# Получение информации об ошибке
error_info = error_handler.get_error_info(error_id)
if error_info:
    print(f"Error: {error_info['error']}")
    print(f"Severity: {error_info['severity']}")
    print(f"Context: {error_info['context']}")

# Получение всех ошибок
all_errors = error_handler.get_all_errors()
for error_id, info in all_errors.items():
    print(f"Error ID: {error_id}")
    print(f"Status: {'Resolved' if info['resolved'] else 'Active'}")
```

## Классификация ошибок

### Уровни важности
1. **LOW**
   - Временные проблемы
   - Не влияют на работу
   - Автоматическое восстановление

2. **MEDIUM**
   - Проблемы с производительностью
   - Частичная функциональность
   - Требуют внимания

3. **HIGH**
   - Критические проблемы
   - Потеря функциональности
   - Требуют немедленного внимания

4. **CRITICAL**
   - Критические сбои
   - Потеря данных
   - Требуют экстренного вмешательства

## Обработка ошибок

### Стратегии обработки
1. **Автоматическое восстановление**
   - Повторные попытки
   - Альтернативные пути
   - Восстановление состояния

2. **Уведомления**
   - Логирование
   - Алерты
   - Мониторинг

3. **Изоляция**
   - Ограничение влияния
   - Защита данных
   - Graceful degradation

### Примеры обработки
```python
# Регистрация пользовательского обработчика
def custom_handler(error_info: ErrorInfo):
    logger.error(f"Custom handling: {error_info.error}")
    # Дополнительная логика

error_handler.register_error_handler(
    ErrorSeverity.HIGH,
    custom_handler
)
```

## Интеграция

### Интеграция с другими компонентами
- `ConfigManager`: Получение настроек
- `MetricsManager`: Сбор метрик
- `Application`: Основное приложение

### Пример интеграции
```python
class Application:
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.error_handler = ErrorHandler(
            max_retries=self.config_manager.get('max_retries'),
            retry_delay=self.config_manager.get('retry_delay')
        )
```

## Тестирование

### Unit-тесты
```python
def test_error_handling():
    error_handler = ErrorHandler()
    error_id = error_handler.handle_error(
        Exception("Test"),
        ErrorSeverity.LOW
    )
    assert error_id is not None
    assert error_handler.get_error_info(error_id) is not None

def test_error_resolution():
    error_handler = ErrorHandler()
    error_id = error_handler.handle_error(
        Exception("Test"),
        ErrorSeverity.MEDIUM
    )
    error_handler.resolve_error(error_id)
    info = error_handler.get_error_info(error_id)
    assert info["resolved"] is True
```

### Интеграционные тесты
```python
def test_error_recovery():
    error_handler = ErrorHandler()
    def failing_operation():
        raise Exception("Test")
    
    result = error_handler.retry_operation(failing_operation)
    assert result is not None
```

## Логирование

### Формат логов
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования
- INFO: Обработка ошибок
- WARNING: Проблемы средней важности
- ERROR: Критические ошибки

## Рекомендации по использованию

1. **Классификация**
   - Правильно определять важность
   - Использовать контекст
   - Документировать решения

2. **Обработка**
   - Реализовывать восстановление
   - Настраивать уведомления
   - Мониторить состояние

3. **Мониторинг**
   - Отслеживать тренды
   - Анализировать причины
   - Улучшать обработку

4. **Безопасность**
   - Защищать данные
   - Контролировать доступ
   - Логировать действия

## Известные ограничения

1. **Производительность**
   - Накладные расходы на обработку
   - Влияние на память
   - Задержки восстановления

2. **Масштабируемость**
   - Ограничения на количество ошибок
   - Объем логов
   - Скорость обработки

3. **Точность**
   - Ложные срабатывания
   - Пропуск ошибок
   - Неправильная классификация

## Планы развития

1. **Краткосрочные**
   - Улучшение классификации
   - Оптимизация обработки
   - Расширение метрик

2. **Долгосрочные**
   - Машинное обучение для анализа
   - Автоматическая оптимизация
   - Интеграция с внешними системами 