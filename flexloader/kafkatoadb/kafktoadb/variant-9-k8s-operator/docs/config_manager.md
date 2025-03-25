# ConfigManager

## Обзор

`ConfigManager` - компонент для управления конфигурацией приложения Kafka to ADB. Обеспечивает загрузку, валидацию и безопасное хранение настроек приложения.

## Основные возможности

- Загрузка конфигурации из файлов
- Валидация настроек
- Безопасное хранение секретов
- Динамическое обновление
- Поддержка разных форматов

## Структура

### Классы

#### ConfigValue
```python
@dataclass
class ConfigValue:
    value: Any                  # Значение конфигурации
    source: str                 # Источник значения
    last_updated: datetime      # Время последнего обновления
    is_sensitive: bool = False  # Флаг чувствительных данных
```

#### ConfigManager
```python
class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, ConfigValue] = {}
        self._lock = threading.Lock()
```

## Методы

### Основные операции
- `get(key: str, default: Any = None) -> Any`: Получение значения
- `set(key: str, value: Any, source: str = "runtime")`: Установка значения
- `get_all(include_sensitive: bool = False) -> Dict[str, Any]`: Получение всех значений
- `get_config_info() -> Dict[str, Dict[str, Any]]`: Получение информации о конфигурации

### Управление конфигурацией
- `_load_config()`: Загрузка конфигурации
- `reload()`: Перезагрузка конфигурации
- `save()`: Сохранение конфигурации
- `validate() -> bool`: Проверка валидности

### Утилиты
- `_is_sensitive_key(key: str) -> bool`: Проверка чувствительности ключа
- `get_sensitive_keys() -> list`: Получение чувствительных ключей

## Конфигурация

### Параметры
- `config_path`: Путь к файлу конфигурации
- `required_keys`: Обязательные ключи
- `sensitive_keywords`: Ключевые слова для чувствительных данных

### Пример конфигурации
```yaml
app_name: "kafka-to-adb"
environment: "production"
required_keys:
  - "app_name"
  - "environment"
  - "cert_path"
```

## Использование

### Базовое использование
```python
config_manager = ConfigManager("config.yaml")

# Получение значения
app_name = config_manager.get("app_name")
if app_name is None:
    print("Ошибка: app_name не найден")

# Установка значения
config_manager.set("debug_mode", True)
```

### Работа с секретами
```python
# Чувствительные данные
config_manager.set("db_password", "secret123", source="env")

# Получение всех нечувствительных данных
config = config_manager.get_all()
print(f"Configuration: {config}")

# Получение информации о конфигурации
info = config_manager.get_config_info()
for key, value in info.items():
    print(f"Key: {key}")
    print(f"Value: {'***' if value['is_sensitive'] else value['value']}")
    print(f"Source: {value['source']}")
```

### Валидация
```python
# Проверка валидности
if not config_manager.validate():
    print("Ошибка валидации конфигурации")
    sys.exit(1)

# Получение обязательных ключей
required_keys = config_manager.get("required_keys", [])
for key in required_keys:
    if not config_manager.get(key):
        print(f"Ошибка: отсутствует обязательный ключ {key}")
```

## Форматы конфигурации

### Поддерживаемые форматы
1. **YAML**
   ```yaml
   app_name: "kafka-to-adb"
   environment: "production"
   settings:
     debug: false
     timeout: 30
   ```

2. **JSON**
   ```json
   {
     "app_name": "kafka-to-adb",
     "environment": "production",
     "settings": {
       "debug": false,
       "timeout": 30
     }
   }
   ```

## Безопасность

### Защита секретов
- Маскирование чувствительных данных
- Безопасное хранение
- Контроль доступа

### Рекомендации
- Использовать переменные окружения
- Шифровать чувствительные данные
- Регулярно обновлять секреты

## Интеграция

### Интеграция с другими компонентами
- `CertificateManager`: Настройки сертификатов
- `ErrorHandler`: Настройки обработки ошибок
- `MetricsManager`: Настройки метрик

### Пример интеграции
```python
class Application:
    def __init__(self, config_path: str):
        self.config_manager = ConfigManager(config_path)
        self.cert_manager = CertificateManager(
            self.config_manager.get('cert_path')
        )
        self.error_handler = ErrorHandler(
            max_retries=self.config_manager.get('max_retries')
        )
```

## Тестирование

### Unit-тесты
```python
def test_config_loading():
    config_manager = ConfigManager("test_config.yaml")
    assert config_manager.get("app_name") == "test-app"

def test_sensitive_data():
    config_manager = ConfigManager("test_config.yaml")
    config_manager.set("password", "secret")
    info = config_manager.get_config_info()
    assert info["password"]["is_sensitive"] is True
```

### Интеграционные тесты
```python
def test_config_validation():
    config_manager = ConfigManager("test_config.yaml")
    assert config_manager.validate() is True
    assert "app_name" in config_manager.get_all()
```

## Логирование

### Формат логов
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Уровни логирования
- INFO: Загрузка и обновление
- WARNING: Проблемы с валидацией
- ERROR: Критические ошибки

## Рекомендации по использованию

1. **Инициализация**
   - Проверять наличие файла
   - Валидировать конфигурацию
   - Настраивать логирование

2. **Управление**
   - Использовать блокировки
   - Контролировать обновления
   - Сохранять изменения

3. **Безопасность**
   - Защищать секреты
   - Контролировать доступ
   - Логировать изменения

4. **Мониторинг**
   - Отслеживать изменения
   - Проверять валидность
   - Анализировать использование

## Известные ограничения

1. **Производительность**
   - Время загрузки файлов
   - Накладные расходы на валидацию
   - Влияние блокировок

2. **Масштабируемость**
   - Размер конфигурации
   - Количество ключей
   - Частота обновлений

3. **Безопасность**
   - Зависимость от файловой системы
   - Риски при обновлении
   - Уязвимости в хранении

## Планы развития

1. **Краткосрочные**
   - Улучшение производительности
   - Расширение форматов
   - Улучшение безопасности

2. **Долгосрочные**
   - Удаленное управление
   - Автоматическая валидация
   - Интеграция с системами управления 