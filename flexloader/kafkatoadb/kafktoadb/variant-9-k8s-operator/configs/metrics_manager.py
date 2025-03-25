import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import threading
from collections import defaultdict

@dataclass
class MetricValue:
    value: float
    timestamp: datetime
    labels: Dict[str, str]

class MetricsManager:
    def __init__(self):
        self.metrics: Dict[str, Dict[str, MetricValue]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self._lock = threading.Lock()
        self._start_time = time.time()
        
    def _setup_logging(self):
        """Настройка логирования"""
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Запись метрики"""
        try:
            labels = labels or {}
            metric_value = MetricValue(
                value=value,
                timestamp=datetime.now(),
                labels=labels
            )
            
            with self._lock:
                self.metrics[name][str(labels)] = metric_value
                
            self.logger.debug(f"Записана метрика {name}: {value}")
        except Exception as e:
            self.logger.error(f"Ошибка записи метрики {name}: {str(e)}")

    def get_metric(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Получение значения метрики"""
        try:
            labels = labels or {}
            with self._lock:
                metric_value = self.metrics[name].get(str(labels))
                return metric_value.value if metric_value else None
        except Exception as e:
            self.logger.error(f"Ошибка получения метрики {name}: {str(e)}")
            return None

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех метрик"""
        try:
            with self._lock:
                return {
                    name: {
                        labels: {
                            "value": metric.value,
                            "timestamp": metric.timestamp.isoformat()
                        }
                        for labels, metric in metrics.items()
                    }
                    for name, metrics in self.metrics.items()
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения всех метрик: {str(e)}")
            return {}

    def record_latency(self, operation: str, duration: float):
        """Запись латентности операции"""
        self.record_metric(f"{operation}_latency", duration)

    def record_error(self, operation: str):
        """Запись ошибки операции"""
        self.record_metric(f"{operation}_errors", 1)

    def record_success(self, operation: str):
        """Запись успешной операции"""
        self.record_metric(f"{operation}_success", 1)

    def get_uptime(self) -> float:
        """Получение времени работы приложения"""
        return time.time() - self._start_time

    def record_memory_usage(self):
        """Запись использования памяти"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        self.record_metric("memory_usage", memory_info.rss / 1024 / 1024)  # в МБ

    def record_cpu_usage(self):
        """Запись использования CPU"""
        import psutil
        process = psutil.Process()
        self.record_metric("cpu_usage", process.cpu_percent())

    def start_monitoring(self, interval: int = 60):
        """Запуск мониторинга системных метрик"""
        def monitor():
            while True:
                try:
                    self.record_memory_usage()
                    self.record_cpu_usage()
                    self.logger.debug("Системные метрики обновлены")
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Ошибка мониторинга: {str(e)}")
                    time.sleep(60)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.logger.info("Мониторинг системных метрик запущен")

    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья приложения"""
        try:
            return {
                "uptime": self.get_uptime(),
                "memory_usage": self.get_metric("memory_usage"),
                "cpu_usage": self.get_metric("cpu_usage"),
                "metrics": self.get_all_metrics()
            }
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса здоровья: {str(e)}")
            return {} 