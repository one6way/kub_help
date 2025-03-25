import logging
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import threading
from dataclasses import dataclass
from enum import Enum

class ErrorSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ErrorInfo:
    timestamp: datetime
    error: Exception
    severity: ErrorSeverity
    context: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class ErrorHandler:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.errors: Dict[str, ErrorInfo] = {}
        self._lock = threading.Lock()
        self._error_handlers: Dict[ErrorSeverity, Callable] = {}
        self._setup_default_handlers()

    def _setup_logging(self):
        """Настройка логирования"""
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _setup_default_handlers(self):
        """Настройка обработчиков ошибок по умолчанию"""
        self._error_handlers = {
            ErrorSeverity.LOW: self._handle_low_severity,
            ErrorSeverity.MEDIUM: self._handle_medium_severity,
            ErrorSeverity.HIGH: self._handle_high_severity,
            ErrorSeverity.CRITICAL: self._handle_critical_severity
        }

    def _handle_low_severity(self, error_info: ErrorInfo):
        """Обработка ошибок низкой важности"""
        self.logger.warning(f"Ошибка низкой важности: {str(error_info.error)}")
        time.sleep(self.retry_delay)

    def _handle_medium_severity(self, error_info: ErrorInfo):
        """Обработка ошибок средней важности"""
        self.logger.error(f"Ошибка средней важности: {str(error_info.error)}")
        time.sleep(self.retry_delay * 2)

    def _handle_high_severity(self, error_info: ErrorInfo):
        """Обработка ошибок высокой важности"""
        self.logger.error(f"Ошибка высокой важности: {str(error_info.error)}")
        time.sleep(self.retry_delay * 3)

    def _handle_critical_severity(self, error_info: ErrorInfo):
        """Обработка критических ошибок"""
        self.logger.critical(f"Критическая ошибка: {str(error_info.error)}")
        # Здесь можно добавить логику уведомления администраторов
        time.sleep(self.retry_delay * 5)

    def register_error_handler(self, severity: ErrorSeverity, handler: Callable):
        """Регистрация пользовательского обработчика ошибок"""
        self._error_handlers[severity] = handler

    def handle_error(self, error: Exception, severity: ErrorSeverity, context: Optional[Dict[str, Any]] = None):
        """Обработка ошибки"""
        try:
            error_id = f"{error.__class__.__name__}_{int(time.time())}"
            context = context or {}
            
            error_info = ErrorInfo(
                timestamp=datetime.now(),
                error=error,
                severity=severity,
                context=context
            )
            
            with self._lock:
                self.errors[error_id] = error_info
            
            handler = self._error_handlers.get(severity)
            if handler:
                handler(error_info)
            
            self.logger.error(f"Ошибка обработана: {str(error)}")
            return error_id
        except Exception as e:
            self.logger.error(f"Ошибка при обработке ошибки: {str(e)}")
            return None

    def resolve_error(self, error_id: str):
        """Отметить ошибку как разрешенную"""
        try:
            with self._lock:
                if error_id in self.errors:
                    error_info = self.errors[error_id]
                    error_info.resolved = True
                    error_info.resolution_time = datetime.now()
                    self.logger.info(f"Ошибка {error_id} отмечена как разрешенная")
        except Exception as e:
            self.logger.error(f"Ошибка при разрешении ошибки: {str(e)}")

    def get_error_info(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации об ошибке"""
        try:
            with self._lock:
                error_info = self.errors.get(error_id)
                if error_info:
                    return {
                        "timestamp": error_info.timestamp.isoformat(),
                        "error": str(error_info.error),
                        "severity": error_info.severity.name,
                        "context": error_info.context,
                        "resolved": error_info.resolved,
                        "resolution_time": error_info.resolution_time.isoformat() if error_info.resolution_time else None
                    }
                return None
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации об ошибке: {str(e)}")
            return None

    def get_all_errors(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о всех ошибках"""
        try:
            with self._lock:
                return {
                    error_id: {
                        "timestamp": error_info.timestamp.isoformat(),
                        "error": str(error_info.error),
                        "severity": error_info.severity.name,
                        "context": error_info.context,
                        "resolved": error_info.resolved,
                        "resolution_time": error_info.resolution_time.isoformat() if error_info.resolution_time else None
                    }
                    for error_id, error_info in self.errors.items()
                }
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации об ошибках: {str(e)}")
            return {}

    def retry_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """Повторная попытка выполнения операции"""
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.handle_error(e, ErrorSeverity.HIGH, {"attempt": attempt + 1})
                    raise
                self.handle_error(e, ErrorSeverity.LOW, {"attempt": attempt + 1})
                time.sleep(self.retry_delay * (attempt + 1)) 