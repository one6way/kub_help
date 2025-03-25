# CertificateManager

## Обзор

`CertificateManager` - компонент для управления SSL/TLS сертификатами в приложении Kafka to ADB. Обеспечивает безопасную работу с сертификатами, их валидацию и автоматическую ротацию.

## Основные возможности

- Автоматическая загрузка сертификатов
- Проверка валидности и целостности
- Мониторинг состояния сертификатов
- Автоматическая ротация
- Логирование операций

## Структура

### Классы

#### CertificateInfo
```python
@dataclass
class CertificateInfo:
    path: str                    # Путь к файлу сертификата
    expiration_date: datetime    # Дата истечения срока действия
    checksum: str               # Контрольная сумма файла
    last_updated: datetime      # Время последнего обновления
```

#### CertificateManager
```python
class CertificateManager:
    def __init__(self, cert_path: str, refresh_interval: int = 3600):
        self.cert_path = cert_path
        self.refresh_interval = refresh_interval
        self.cert_info: Optional[CertificateInfo] = None
```

## Методы

### Инициализация и настройка
- `_setup_logging()`: Настройка системы логирования
- `_calculate_checksum(file_path: str) -> str`: Вычисление контрольной суммы файла
- `_validate_certificate(cert_path: str) -> bool`: Проверка валидности сертификата
- `_get_certificate_expiration(cert_path: str) -> datetime`: Получение даты истечения

### Основные операции
- `load_certificate() -> bool`: Загрузка сертификата
- `check_certificate() -> bool`: Проверка состояния сертификата
- `get_certificate_info() -> Dict[str, Any]`: Получение информации о сертификате
- `monitor_certificate()`: Мониторинг состояния сертификата

## Конфигурация

### Параметры
- `cert_path`: Путь к файлу сертификата
- `refresh_interval`: Интервал обновления (в секундах)

### Пример конфигурации
```yaml
cert_path: "/etc/certs/kafka.cert"
cert_refresh_interval: 3600
cert_check_interval: 300
```

## Использование

### Базовое использование
```python
cert_manager = CertificateManager(
    cert_path="/path/to/cert.pem",
    refresh_interval=3600
)

# Загрузка сертификата
if cert_manager.load_certificate():
    print("Сертификат успешно загружен")
else:
    print("Ошибка загрузки сертификата")

# Проверка состояния
if cert_manager.check_certificate():
    print("Сертификат валиден")
else:
    print("Проблема с сертификатом")
```

### Мониторинг
```python
# Запуск мониторинга в отдельном потоке
thread = threading.Thread(
    target=cert_manager.monitor_certificate,
    daemon=True
)
thread.start()
```

## Метрики

### Основные метрики
- Время загрузки сертификата
- Количество ошибок валидации
- Статус сертификата
- Время до истечения срока действия

### Пример получения метрик
```python
cert_info = cert_manager.get_certificate_info()
print(f"Путь: {cert_info['path']}")
print(f"Истекает: {cert_info['expiration_date']}")
print(f"Последнее обновление: {cert_info['last_updated']}")
```

## Обработка ошибок

### Типы ошибок
- Ошибки загрузки файла
- Ошибки валидации
- Ошибки проверки целостности
- Ошибки мониторинга

### Пример обработки
```python
try:
    if not cert_manager.check_certificate():
        logger.error("Проблема с сертификатом")
        # Дополнительная логика обработки
except Exception as e:
    logger.error(f"Ошибка при проверке сертификата: {str(e)}")
```

## Безопасность

### Меры безопасности
- Проверка целостности файлов
- Валидация сертификатов
- Безопасное хранение
- Контроль доступа

### Рекомендации
- Регулярное обновление сертификатов
- Мониторинг состояния
- Логирование всех операций
- Резервное копирование

## Интеграция

### Интеграция с другими компонентами
- `ConfigManager`: Получение настроек
- `ErrorHandler`: Обработка ошибок
- `MetricsManager`: Сбор метрик

### Пример интеграции
```python
class Application:
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.cert_manager = CertificateManager(
            self.config_manager.get('cert_path'),
            self.config_manager.get('cert_refresh_interval')
        )
```

## Тестирование

### Unit-тесты
```python
def test_certificate_validation():
    cert_manager = CertificateManager("test_cert.pem")
    assert cert_manager._validate_certificate("test_cert.pem")

def test_certificate_expiration():
    cert_manager = CertificateManager("test_cert.pem")
    expiration = cert_manager._get_certificate_expiration("test_cert.pem")
    assert expiration > datetime.now()
```

### Интеграционные тесты
```python
def test_certificate_monitoring():
    cert_manager = CertificateManager("test_cert.pem")
    cert_manager.load_certificate()
    assert cert_manager.check_certificate()
```

## Логирование

### Формат логов
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования
- INFO: Основные операции
- WARNING: Проблемы с сертификатом
- ERROR: Критические ошибки

## Рекомендации по использованию

1. **Инициализация**
   - Создавать экземпляр в начале работы приложения
   - Проверять успешность инициализации

2. **Мониторинг**
   - Запускать мониторинг в отдельном потоке
   - Регулярно проверять состояние

3. **Обработка ошибок**
   - Всегда проверять результаты операций
   - Логировать все ошибки
   - Иметь план восстановления

4. **Безопасность**
   - Регулярно обновлять сертификаты
   - Проверять права доступа
   - Использовать безопасные пути

## Известные ограничения

1. **Производительность**
   - Проверка целостности может быть медленной
   - Мониторинг создает дополнительную нагрузку

2. **Безопасность**
   - Зависимость от файловой системы
   - Необходимость доступа к файлам

3. **Масштабируемость**
   - Ограничения на количество сертификатов
   - Зависимость от системных ресурсов

## Планы развития

1. **Краткосрочные**
   - Улучшение производительности
   - Расширение метрик
   - Улучшение обработки ошибок

2. **Долгосрочные**
   - Поддержка удаленных сертификатов
   - Интеграция с системами управления сертификатами
   - Автоматическое обновление 