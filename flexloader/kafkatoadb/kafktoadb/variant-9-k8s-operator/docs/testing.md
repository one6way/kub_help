# Тестирование приложения

## Обзор

Документация по тестированию приложения Kafka to ADB описывает различные уровни тестирования, инструменты и методологии, используемые для обеспечения качества кода.

## Уровни тестирования

### 1. Unit-тесты
- Тестирование отдельных компонентов
- Изолированное тестирование
- Моки и стабы

### 2. Интеграционные тесты
- Тестирование взаимодействия компонентов
- Тестирование с реальными зависимостями
- Проверка интеграций

### 3. Системные тесты
- Тестирование всей системы
- End-to-end тестирование
- Проверка производительности

## Инструменты

### 1. pytest
```python
# conftest.py
import pytest
from kafka_to_adb import Application, ConfigManager

@pytest.fixture
def config_manager():
    return ConfigManager("test_config.yaml")

@pytest.fixture
def app(config_manager):
    return Application(config_manager)
```

### 2. pytest-cov
```bash
# Запуск тестов с покрытием
pytest --cov=kafka_to_adb tests/
```

### 3. pytest-mock
```python
# test_certificate_manager.py
def test_certificate_loading(mocker):
    mock_open = mocker.patch('builtins.open')
    mock_open.return_value.__enter__.return_value.read.return_value = "test_cert"
    
    cert_manager = CertificateManager("test_cert.pem")
    assert cert_manager.load_certificate() == "test_cert"
```

## Тестовые сценарии

### 1. CertificateManager
```python
# test_certificate_manager.py
def test_certificate_validation():
    cert_manager = CertificateManager("test_cert.pem")
    assert cert_manager.validate_certificate() is True

def test_certificate_expiry():
    cert_manager = CertificateManager("test_cert.pem")
    assert cert_manager.check_expiry() is True

def test_certificate_rotation():
    cert_manager = CertificateManager("test_cert.pem")
    assert cert_manager.rotate_certificate() is True
```

### 2. MetricsManager
```python
# test_metrics_manager.py
def test_metrics_recording():
    metrics_manager = MetricsManager()
    metrics_manager.record_metric("test_metric", 1.0)
    assert metrics_manager.get_metric("test_metric") == 1.0

def test_metrics_aggregation():
    metrics_manager = MetricsManager()
    metrics_manager.record_metric("test_metric", [1.0, 2.0, 3.0])
    assert metrics_manager.get_aggregated_metric("test_metric") == 2.0
```

### 3. ErrorHandler
```python
# test_error_handler.py
def test_error_classification():
    error_handler = ErrorHandler()
    error = Exception("test error")
    assert error_handler.classify_error(error) == "LOW"

def test_error_retry():
    error_handler = ErrorHandler()
    assert error_handler.should_retry(Exception("test error")) is True
```

### 4. ConfigManager
```python
# test_config_manager.py
def test_config_loading():
    config_manager = ConfigManager("test_config.yaml")
    assert config_manager.get("app_name") == "kafka-to-adb"

def test_config_validation():
    config_manager = ConfigManager("test_config.yaml")
    assert config_manager.validate_config() is True
```

## Интеграционные тесты

### 1. Kafka интеграция
```python
# test_kafka_integration.py
def test_kafka_connection():
    kafka_client = KafkaClient("test_broker")
    assert kafka_client.is_connected() is True

def test_kafka_message_consumption():
    kafka_client = KafkaClient("test_broker")
    messages = kafka_client.consume_messages("test_topic")
    assert len(messages) > 0
```

### 2. ADB интеграция
```python
# test_adb_integration.py
def test_adb_connection():
    adb_client = ADBClient("test_host")
    assert adb_client.is_connected() is True

def test_adb_data_insertion():
    adb_client = ADBClient("test_host")
    assert adb_client.insert_data("test_table", [{"id": 1}]) is True
```

## Системные тесты

### 1. Производительность
```python
# test_performance.py
def test_message_processing_speed():
    app = Application("test_config.yaml")
    start_time = time.time()
    app.process_messages(1000)
    end_time = time.time()
    assert (end_time - start_time) < 10.0

def test_memory_usage():
    app = Application("test_config.yaml")
    initial_memory = psutil.Process().memory_info().rss
    app.process_messages(10000)
    final_memory = psutil.Process().memory_info().rss
    assert (final_memory - initial_memory) < 100 * 1024 * 1024  # 100MB
```

### 2. Надежность
```python
# test_reliability.py
def test_error_recovery():
    app = Application("test_config.yaml")
    app.simulate_error()
    assert app.is_healthy() is True

def test_certificate_rotation():
    app = Application("test_config.yaml")
    app.simulate_certificate_expiry()
    assert app.is_healthy() is True
```

## CI/CD интеграция

### 1. GitHub Actions
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest --cov=kafka_to_adb tests/
```

### 2. Jenkins Pipeline
```groovy
// Jenkinsfile
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'python -m pip install -r requirements.txt'
                sh 'pytest --cov=kafka_to_adb tests/'
            }
        }
    }
}
```

## Рекомендации по тестированию

### 1. Разработка
- Писать тесты параллельно с кодом
- Использовать TDD где возможно
- Поддерживать актуальность тестов

### 2. Организация
- Структурировать тесты логически
- Использовать фикстуры
- Избегать дублирования кода

### 3. Покрытие
- Стремиться к высокому покрытию
- Тестировать граничные случаи
- Проверять обработку ошибок

### 4. CI/CD
- Автоматизировать тестирование
- Интегрировать с CI/CD
- Мониторить результаты

## Метрики качества

### 1. Покрытие кода
```bash
# Проверка покрытия
pytest --cov=kafka_to_adb --cov-report=term-missing tests/
```

### 2. Время выполнения
```bash
# Измерение времени
pytest --durations=10 tests/
```

### 3. Статический анализ
```bash
# Проверка стиля
flake8 kafka_to_adb/

# Проверка типов
mypy kafka_to_adb/
```

## Отладка

### 1. Логирование
```python
# Настройка логирования для тестов
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Отладчик
```python
# Использование pdb
import pdb; pdb.set_trace()
```

### 3. Визуализация
```python
# Генерация отчетов
pytest --html=report.html tests/
``` 