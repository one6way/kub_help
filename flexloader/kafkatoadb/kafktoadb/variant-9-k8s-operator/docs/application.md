# Application

## Обзор

`Application` - основной класс приложения Kafka to ADB, который интегрирует все компоненты и управляет жизненным циклом приложения. Обеспечивает координацию между различными модулями и обработку системных событий.

## Основные возможности

- Управление жизненным циклом приложения
- Интеграция всех компонентов
- Мониторинг состояния
- Обработка системных сигналов
- Graceful shutdown

## Структура

### Компоненты
```python
class Application:
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.certificate_manager = CertificateManager(...)
        self.metrics_manager = MetricsManager()
        self.error_handler = ErrorHandler(...)
```

## Методы

### Управление жизненным циклом
- `start()`: Запуск приложения
- `stop()`: Остановка приложения
- `_handle_shutdown(signum, frame)`: Обработка сигналов завершения

### Мониторинг
- `_check_health()`: Проверка состояния
- `_check_critical_metrics(health_status: Dict[str, Any]) -> bool`: Проверка критических метрик
- `get_status() -> Dict[str, Any]`: Получение статуса

### Внутренние методы
- `_setup_logging()`: Настройка логирования
- `_start_certificate_monitoring()`: Запуск мониторинга сертификатов
- `_main_loop()`: Основной цикл приложения

## Конфигурация

### Параметры
- `config_path`: Путь к файлу конфигурации
- `metrics_interval`: Интервал сбора метрик
- `main_loop_interval`: Интервал основного цикла
- `cert_check_interval`: Интервал проверки сертификатов

### Пример конфигурации
```yaml
app_name: "kafka-to-adb"
environment: "production"
metrics_interval: 60
main_loop_interval: 1
cert_check_interval: 300
```

## Использование

### Базовое использование
```python
# Создание приложения
app = Application("config.yaml")

# Запуск приложения
try:
    app.start()
except KeyboardInterrupt:
    app.stop()
```

### Обработка сигналов
```python
# Регистрация обработчиков сигналов
signal.signal(signal.SIGTERM, app._handle_shutdown)
signal.signal(signal.SIGINT, app._handle_shutdown)
```

### Мониторинг состояния
```python
# Получение статуса
status = app.get_status()
print(f"Running: {status['is_running']}")
print(f"Uptime: {status['uptime']}")
print(f"Health: {status['health']}")
```

## Жизненный цикл

### Этапы запуска
1. Инициализация компонентов
2. Проверка конфигурации
3. Загрузка сертификатов
4. Запуск мониторинга
5. Запуск основного цикла

### Этапы остановки
1. Получение сигнала завершения
2. Остановка мониторинга
3. Закрытие соединений
4. Сохранение состояния
5. Завершение работы

## Мониторинг

### Проверяемые метрики
- Использование памяти
- Использование CPU
- Состояние сертификатов
- Количество ошибок
- Время работы

### Пример проверки
```python
def _check_health(self):
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "metrics": self.metrics_manager.get_health_status(),
        "certificates": self.certificate_manager.get_certificate_info(),
        "errors": self.error_handler.get_all_errors()
    }
    
    if self._check_critical_metrics(health_status):
        self.logger.info("Состояние приложения: здоровое")
    else:
        self.logger.warning("Обнаружены проблемы")
```

## Интеграция

### Компоненты
- `ConfigManager`: Управление настройками
- `CertificateManager`: Управление сертификатами
- `MetricsManager`: Сбор метрик
- `ErrorHandler`: Обработка ошибок

### Пример интеграции
```python
class Application:
    def __init__(self, config_path: str):
        # Инициализация компонентов
        self.config_manager = ConfigManager(config_path)
        self.certificate_manager = CertificateManager(
            self.config_manager.get('cert_path'),
            self.config_manager.get('cert_refresh_interval')
        )
        self.metrics_manager = MetricsManager()
        self.error_handler = ErrorHandler(
            max_retries=self.config_manager.get('max_retries'),
            retry_delay=self.config_manager.get('retry_delay')
        )
```

## Тестирование

### Unit-тесты
```python
def test_application_initialization():
    app = Application("test_config.yaml")
    assert app.config_manager is not None
    assert app.certificate_manager is not None
    assert app.metrics_manager is not None
    assert app.error_handler is not None

def test_health_check():
    app = Application("test_config.yaml")
    status = app.get_status()
    assert "is_running" in status
    assert "health" in status
```

### Интеграционные тесты
```python
def test_application_lifecycle():
    app = Application("test_config.yaml")
    
    # Запуск
    app.start()
    assert app.is_running is True
    
    # Проверка состояния
    status = app.get_status()
    assert status["is_running"] is True
    
    # Остановка
    app.stop()
    assert app.is_running is False
```

## Логирование

### Формат логов
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования
- INFO: Основные операции
- WARNING: Проблемы с состоянием
- ERROR: Критические ошибки

## Рекомендации по использованию

1. **Инициализация**
   - Проверять конфигурацию
   - Инициализировать компоненты
   - Настраивать логирование

2. **Управление**
   - Корректно обрабатывать сигналы
   - Сохранять состояние
   - Логировать события

3. **Мониторинг**
   - Регулярно проверять состояние
   - Анализировать метрики
   - Реагировать на проблемы

4. **Безопасность**
   - Защищать данные
   - Контролировать доступ
   - Логировать действия

## Известные ограничения

1. **Производительность**
   - Накладные расходы на мониторинг
   - Влияние на ресурсы
   - Задержки операций

2. **Масштабируемость**
   - Ограничения компонентов
   - Объем данных
   - Частота проверок

3. **Надежность**
   - Зависимость от компонентов
   - Риски при остановке
   - Восстановление состояния

## Планы развития

1. **Краткосрочные**
   - Улучшение производительности
   - Расширение мониторинга
   - Улучшение восстановления

2. **Долгосрочные**
   - Распределенная работа
   - Автоматическая оптимизация
   - Интеграция с внешними системами 