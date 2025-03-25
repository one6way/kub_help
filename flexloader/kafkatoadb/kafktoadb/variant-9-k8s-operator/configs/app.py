import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import signal
import sys

from .certificate_manager import CertificateManager
from .metrics_manager import MetricsManager
from .error_handler import ErrorHandler, ErrorSeverity
from .config_manager import ConfigManager

class Application:
    def __init__(self, config_path: str):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Инициализация компонентов
        self.config_manager = ConfigManager(config_path)
        self.certificate_manager = CertificateManager(
            self.config_manager.get('cert_path', '/etc/certs/kafka.cert'),
            self.config_manager.get('cert_refresh_interval', 3600)
        )
        self.metrics_manager = MetricsManager()
        self.error_handler = ErrorHandler(
            max_retries=self.config_manager.get('max_retries', 3),
            retry_delay=self.config_manager.get('retry_delay', 5)
        )
        
        # Флаги состояния
        self.is_running = False
        self._lock = threading.Lock()
        
        # Настройка обработчиков сигналов
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _setup_logging(self):
        """Настройка логирования"""
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _handle_shutdown(self, signum, frame):
        """Обработка сигналов завершения"""
        self.logger.info(f"Получен сигнал завершения: {signum}")
        self.stop()

    def start(self):
        """Запуск приложения"""
        try:
            with self._lock:
                if self.is_running:
                    self.logger.warning("Приложение уже запущено")
                    return

                # Проверка конфигурации
                if not self.config_manager.validate():
                    self.logger.error("Ошибка валидации конфигурации")
                    return

                # Загрузка сертификатов
                if not self.certificate_manager.load_certificate():
                    self.logger.error("Ошибка загрузки сертификатов")
                    return

                # Запуск мониторинга
                self.metrics_manager.start_monitoring(
                    interval=self.config_manager.get('metrics_interval', 60)
                )

                # Запуск мониторинга сертификатов
                self._start_certificate_monitoring()

                self.is_running = True
                self.logger.info("Приложение успешно запущено")

                # Основной цикл приложения
                self._main_loop()

        except Exception as e:
            self.error_handler.handle_error(e, ErrorSeverity.CRITICAL)
            self.stop()

    def stop(self):
        """Остановка приложения"""
        try:
            with self._lock:
                if not self.is_running:
                    return

                self.is_running = False
                self.logger.info("Остановка приложения...")

                # Здесь можно добавить логику корректного завершения
                # Например, закрытие соединений, сохранение состояния и т.д.

                self.logger.info("Приложение успешно остановлено")
        except Exception as e:
            self.error_handler.handle_error(e, ErrorSeverity.HIGH)
            sys.exit(1)

    def _start_certificate_monitoring(self):
        """Запуск мониторинга сертификатов в отдельном потоке"""
        def monitor():
            while self.is_running:
                try:
                    if not self.certificate_manager.check_certificate():
                        self.error_handler.handle_error(
                            Exception("Проблема с сертификатом"),
                            ErrorSeverity.HIGH
                        )
                    time.sleep(self.config_manager.get('cert_check_interval', 300))
                except Exception as e:
                    self.error_handler.handle_error(e, ErrorSeverity.MEDIUM)
                    time.sleep(60)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.logger.info("Мониторинг сертификатов запущен")

    def _main_loop(self):
        """Основной цикл приложения"""
        while self.is_running:
            try:
                # Здесь основная логика приложения
                # Например, обработка данных, взаимодействие с Kafka и ADB
                
                # Запись метрик
                self.metrics_manager.record_success("main_loop")
                
                # Проверка состояния
                self._check_health()
                
                time.sleep(self.config_manager.get('main_loop_interval', 1))
            except Exception as e:
                self.error_handler.handle_error(e, ErrorSeverity.HIGH)
                time.sleep(5)

    def _check_health(self):
        """Проверка состояния приложения"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "metrics": self.metrics_manager.get_health_status(),
                "certificates": self.certificate_manager.get_certificate_info(),
                "errors": self.error_handler.get_all_errors()
            }
            
            # Проверка критических метрик
            if self._check_critical_metrics(health_status):
                self.logger.info("Состояние приложения: здоровое")
            else:
                self.logger.warning("Обнаружены проблемы в состоянии приложения")
                
        except Exception as e:
            self.error_handler.handle_error(e, ErrorSeverity.MEDIUM)

    def _check_critical_metrics(self, health_status: Dict[str, Any]) -> bool:
        """Проверка критических метрик"""
        try:
            # Проверка использования памяти
            memory_usage = health_status["metrics"].get("memory_usage")
            if memory_usage and memory_usage > self.config_manager.get('memory_threshold', 90):
                self.logger.warning(f"Высокое использование памяти: {memory_usage}%")
                return False

            # Проверка использования CPU
            cpu_usage = health_status["metrics"].get("cpu_usage")
            if cpu_usage and cpu_usage > self.config_manager.get('cpu_threshold', 90):
                self.logger.warning(f"Высокое использование CPU: {cpu_usage}%")
                return False

            # Проверка ошибок
            errors = health_status["errors"]
            if any(not error["resolved"] for error in errors.values()):
                self.logger.warning("Есть неразрешенные ошибки")
                return False

            return True
        except Exception as e:
            self.error_handler.handle_error(e, ErrorSeverity.MEDIUM)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Получение статуса приложения"""
        try:
            return {
                "is_running": self.is_running,
                "start_time": self.metrics_manager._start_time,
                "uptime": self.metrics_manager.get_uptime(),
                "health": self.metrics_manager.get_health_status(),
                "certificates": self.certificate_manager.get_certificate_info(),
                "errors": self.error_handler.get_all_errors(),
                "config": self.config_manager.get_config_info()
            }
        except Exception as e:
            self.error_handler.handle_error(e, ErrorSeverity.LOW)
            return {} 