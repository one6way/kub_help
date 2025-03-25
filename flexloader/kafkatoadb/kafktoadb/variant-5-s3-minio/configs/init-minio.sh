#!/bin/bash
set -e

# Переменные окружения
MINIO_ENDPOINT="http://minio:9000"
MINIO_ACCESS_KEY="minio"
MINIO_SECRET_KEY="minio123"
BUCKET_NAME="kafka-certs-bucket"
KEYSTORE_PATH="./kafka.client.keystore.jks"
TRUSTSTORE_PATH="./kafka.client.truststore.jks"

echo "Настройка MinIO клиента для загрузки сертификатов..."

# Установка MinIO клиента
if ! command -v mc &> /dev/null; then
    echo "Установка MinIO клиента..."
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O mc
    chmod +x mc
fi

# Настройка подключения к MinIO
echo "Настройка подключения к MinIO серверу: ${MINIO_ENDPOINT}"
./mc alias set minio ${MINIO_ENDPOINT} ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

# Проверка существования бакета
if ./mc ls minio | grep -q ${BUCKET_NAME}; then
    echo "Бакет ${BUCKET_NAME} уже существует"
else
    echo "Создание бакета ${BUCKET_NAME}"
    ./mc mb minio/${BUCKET_NAME}
fi

# Настройка политик доступа
echo "Настройка политик доступа для бакета ${BUCKET_NAME}"
./mc policy set download minio/${BUCKET_NAME}

# Проверка наличия файлов сертификатов
if [ ! -f "${KEYSTORE_PATH}" ]; then
    echo "Ошибка: файл keystore не найден по пути ${KEYSTORE_PATH}"
    exit 1
fi

if [ ! -f "${TRUSTSTORE_PATH}" ]; then
    echo "Ошибка: файл truststore не найден по пути ${TRUSTSTORE_PATH}"
    exit 1
fi

# Загрузка сертификатов
echo "Загрузка сертификатов в бакет ${BUCKET_NAME}"
./mc cp ${KEYSTORE_PATH} minio/${BUCKET_NAME}/keystore.jks
./mc cp ${TRUSTSTORE_PATH} minio/${BUCKET_NAME}/truststore.jks

# Настройка тегов версионирования
echo "Настройка метаданных для сертификатов"
./mc tag set minio/${BUCKET_NAME}/keystore.jks "version=1.0"
./mc tag set minio/${BUCKET_NAME}/truststore.jks "version=1.0"

# Проверка загруженных файлов
echo "Проверка загруженных сертификатов:"
./mc ls minio/${BUCKET_NAME}

echo "Инициализация завершена успешно!" 