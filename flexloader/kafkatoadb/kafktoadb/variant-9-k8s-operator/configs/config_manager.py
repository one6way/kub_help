import os
import yaml
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
import threading
from datetime import datetime

@dataclass
class ConfigValue:
    value: Any
    source: str
    last_updated: datetime
    is_sensitive: bool = False

class ConfigManager:
    def __init__(self, config_path: str):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.config_path = config_path
        self.config: Dict[str, ConfigValue] = {}
        self._lock = threading.Lock()
        self._load_config()

    def _setup_logging(self):
        """Настройка логирования"""
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"Конфигурационный файл не найден: {self.config_path}")
                return

            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                elif self.config_path.endswith('.json'):
                    config_data = json.load(f)
                else:
                    self.logger.error(f"Неподдерживаемый формат конфигурационного файла: {self.config_path}")
                    return

            with self._lock:
                for key, value in config_data.items():
                    self.config[key] = ConfigValue(
                        value=value,
                        source=self.config_path,
                        last_updated=datetime.now(),
                        is_sensitive=self._is_sensitive_key(key)
                    )

            self.logger.info(f"Конфигурация загружена из {self.config_path}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки конфигурации: {str(e)}")

    def _is_sensitive_key(self, key: str) -> bool:
        """Проверка, является ли ключ конфигурации чувствительным"""
        sensitive_keywords = ['password', 'secret', 'key', 'token', 'credential']
        return any(keyword in key.lower() for keyword in sensitive_keywords)

    def get(self, key: str, default: Any = None) -> Any:
        """Получение значения конфигурации"""
        try:
            with self._lock:
                config_value = self.config.get(key)
                if config_value:
                    return config_value.value
                return default
        except Exception as e:
            self.logger.error(f"Ошибка получения значения конфигурации {key}: {str(e)}")
            return default

    def set(self, key: str, value: Any, source: str = "runtime"):
        """Установка значения конфигурации"""
        try:
            with self._lock:
                self.config[key] = ConfigValue(
                    value=value,
                    source=source,
                    last_updated=datetime.now(),
                    is_sensitive=self._is_sensitive_key(key)
                )
                self.logger.info(f"Значение конфигурации {key} обновлено")
        except Exception as e:
            self.logger.error(f"Ошибка установки значения конфигурации {key}: {str(e)}")

    def get_all(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Получение всех значений конфигурации"""
        try:
            with self._lock:
                return {
                    key: config_value.value
                    for key, config_value in self.config.items()
                    if include_sensitive or not config_value.is_sensitive
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения всех значений конфигурации: {str(e)}")
            return {}

    def get_config_info(self) -> Dict[str, Dict[str, Any]]:
        """Получение информации о конфигурации"""
        try:
            with self._lock:
                return {
                    key: {
                        "value": "***" if config_value.is_sensitive else config_value.value,
                        "source": config_value.source,
                        "last_updated": config_value.last_updated.isoformat(),
                        "is_sensitive": config_value.is_sensitive
                    }
                    for key, config_value in self.config.items()
                }
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о конфигурации: {str(e)}")
            return {}

    def reload(self):
        """Перезагрузка конфигурации из файла"""
        self._load_config()

    def save(self):
        """Сохранение конфигурации в файл"""
        try:
            config_data = self.get_all(include_sensitive=True)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    yaml.dump(config_data, f, default_flow_style=False)
                elif self.config_path.endswith('.json'):
                    json.dump(config_data, f, indent=4)
                else:
                    self.logger.error(f"Неподдерживаемый формат конфигурационного файла: {self.config_path}")
                    return

            self.logger.info(f"Конфигурация сохранена в {self.config_path}")
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {str(e)}")

    def validate(self) -> bool:
        """Проверка валидности конфигурации"""
        try:
            required_keys = self.get('required_keys', [])
            for key in required_keys:
                if key not in self.config:
                    self.logger.error(f"Отсутствует обязательный ключ конфигурации: {key}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации конфигурации: {str(e)}")
            return False

    def get_sensitive_keys(self) -> list:
        """Получение списка чувствительных ключей конфигурации"""
        try:
            with self._lock:
                return [
                    key for key, config_value in self.config.items()
                    if config_value.is_sensitive
                ]
        except Exception as e:
            self.logger.error(f"Ошибка получения списка чувствительных ключей: {str(e)}")
            return [] 