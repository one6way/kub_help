import os
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import ssl
import hashlib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CertificateInfo:
    path: str
    expiration_date: datetime
    checksum: str
    last_updated: datetime

class CertificateManager:
    def __init__(self, cert_path: str, refresh_interval: int = 3600):
        self.cert_path = cert_path
        self.refresh_interval = refresh_interval
        self.cert_info: Optional[CertificateInfo] = None
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
    def _setup_logging(self):
        """Настройка логирования"""
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _calculate_checksum(self, file_path: str) -> str:
        """Вычисление контрольной суммы файла сертификата"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _validate_certificate(self, cert_path: str) -> bool:
        """Проверка валидности сертификата"""
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                ssl.PEM_cert_to_DER_cert(cert_data.decode())
            return True
        except Exception as e:
            self.logger.error(f"Ошибка валидации сертификата: {str(e)}")
            return False

    def _get_certificate_expiration(self, cert_path: str) -> datetime:
        """Получение даты истечения сертификата"""
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
                cert = ssl.PEM_cert_to_DER_cert(cert_data.decode())
                x509 = ssl.DER_cert_to_PEM_cert(cert)
                # Здесь должна быть логика извлечения даты истечения
                # Для демонстрации возвращаем текущую дату + 30 дней
                return datetime.now() + timedelta(days=30)
        except Exception as e:
            self.logger.error(f"Ошибка получения даты истечения сертификата: {str(e)}")
            return datetime.now() + timedelta(days=1)

    def load_certificate(self) -> bool:
        """Загрузка сертификата и обновление информации о нем"""
        try:
            if not os.path.exists(self.cert_path):
                self.logger.error(f"Сертификат не найден по пути: {self.cert_path}")
                return False

            if not self._validate_certificate(self.cert_path):
                return False

            checksum = self._calculate_checksum(self.cert_path)
            expiration_date = self._get_certificate_expiration(self.cert_path)
            
            self.cert_info = CertificateInfo(
                path=self.cert_path,
                expiration_date=expiration_date,
                checksum=checksum,
                last_updated=datetime.now()
            )
            
            self.logger.info(f"Сертификат успешно загружен. Истекает: {expiration_date}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка загрузки сертификата: {str(e)}")
            return False

    def check_certificate(self) -> bool:
        """Проверка состояния сертификата"""
        if not self.cert_info:
            return self.load_certificate()

        try:
            current_checksum = self._calculate_checksum(self.cert_path)
            if current_checksum != self.cert_info.checksum:
                self.logger.info("Обнаружено изменение сертификата")
                return self.load_certificate()

            if datetime.now() >= self.cert_info.expiration_date:
                self.logger.warning("Сертификат истек")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Ошибка проверки сертификата: {str(e)}")
            return False

    def get_certificate_info(self) -> Dict[str, Any]:
        """Получение информации о текущем сертификате"""
        if not self.cert_info:
            return {}
        
        return {
            "path": self.cert_info.path,
            "expiration_date": self.cert_info.expiration_date.isoformat(),
            "last_updated": self.cert_info.last_updated.isoformat(),
            "checksum": self.cert_info.checksum
        }

    def monitor_certificate(self):
        """Мониторинг состояния сертификата"""
        while True:
            try:
                if not self.check_certificate():
                    self.logger.warning("Проблема с сертификатом")
                    # Здесь можно добавить логику уведомления или автоматического обновления
                
                time.sleep(self.refresh_interval)
            except Exception as e:
                self.logger.error(f"Ошибка в мониторинге сертификата: {str(e)}")
                time.sleep(60)  # Пауза перед повторной попыткой 