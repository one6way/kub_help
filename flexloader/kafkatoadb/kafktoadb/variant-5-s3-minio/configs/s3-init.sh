#!/bin/bash
# Скрипт для инициализации S3/MinIO и загрузки Kafka-сертификатов

set -e

# Переменные окружения
S3_ENDPOINT=${S3_ENDPOINT:-"http://localhost:9000"}
S3_ACCESS_KEY=${S3_ACCESS_KEY:-"minioadmin"}
S3_SECRET_KEY=${S3_SECRET_KEY:-"minioadmin"}
S3_BUCKET=${S3_BUCKET:-"kafka-certs"}
AWS_REGION=${AWS_REGION:-"us-east-1"}

# Пути к сертификатам
KEYSTORE_PATH=${KEYSTORE_PATH:-"../../certs/keystore.jks"}
TRUSTSTORE_PATH=${TRUSTSTORE_PATH:-"../../certs/truststore.jks"}

# Проверка наличия необходимых утилит
for cmd in aws mc; do
  if ! command -v $cmd &> /dev/null; then
    echo "Предупреждение: утилита $cmd не найдена"
    if [ "$cmd" = "mc" ]; then
      USE_MC=false
    elif [ "$cmd" = "aws" ]; then
      USE_AWS=false
    fi
  else
    if [ "$cmd" = "mc" ]; then
      USE_MC=true
    elif [ "$cmd" = "aws" ]; then
      USE_AWS=true
    fi
  fi
done

if [ "$USE_MC" = false ] && [ "$USE_AWS" = false ]; then
  echo "Ошибка: необходима хотя бы одна из утилит - mc (MinIO Client) или aws (AWS CLI)"
  exit 1
fi

# Проверка существования файлов сертификатов
if [ ! -f "$KEYSTORE_PATH" ] || [ ! -f "$TRUSTSTORE_PATH" ]; then
  echo "Внимание: файлы сертификатов не найдены"
  echo "Создаем демонстрационные файлы для примера..."
  
  # Создаем пустые файлы для примера
  echo "sample_keystore_content" > sample_keystore.jks
  echo "sample_truststore_content" > sample_truststore.jks
  
  KEYSTORE_PATH="sample_keystore.jks"
  TRUSTSTORE_PATH="sample_truststore.jks"
fi

echo "Инициализация хранилища S3/MinIO для Kafka-сертификатов..."

if [ -n "$S3_ENDPOINT" ] && [ "$USE_MC" = true ]; then
  # Используем MinIO Client если указан эндпоинт и доступен mc
  echo "Используем MinIO Client для подключения к $S3_ENDPOINT"
  
  # Настройка подключения к MinIO
  mc alias set minio "$S3_ENDPOINT" "$S3_ACCESS_KEY" "$S3_SECRET_KEY"
  
  # Проверка и создание бакета если не существует
  if ! mc ls minio | grep -q "$S3_BUCKET"; then
    echo "Создание бакета $S3_BUCKET..."
    mc mb "minio/$S3_BUCKET"
  else
    echo "Бакет $S3_BUCKET уже существует"
  fi
  
  # Загрузка сертификатов в бакет
  echo "Загрузка сертификатов в бакет $S3_BUCKET..."
  mc cp "$KEYSTORE_PATH" "minio/$S3_BUCKET/certs/keystore.jks"
  mc cp "$TRUSTSTORE_PATH" "minio/$S3_BUCKET/certs/truststore.jks"
  
  # Проверка загрузки
  echo "Проверка загрузки файлов..."
  mc ls "minio/$S3_BUCKET/certs/"
  
elif [ "$USE_AWS" = true ]; then
  # Используем AWS CLI если доступен aws
  echo "Используем AWS CLI для подключения к S3"
  
  # Настройка AWS CLI
  if [ -n "$S3_ENDPOINT" ]; then
    # Для MinIO или другого S3-совместимого хранилища
    AWS_ARGS="--endpoint-url $S3_ENDPOINT"
  else
    # Для AWS S3
    AWS_ARGS="--region $AWS_REGION"
  fi
  
  # Экспорт учетных данных для AWS CLI
  export AWS_ACCESS_KEY_ID="$S3_ACCESS_KEY"
  export AWS_SECRET_ACCESS_KEY="$S3_SECRET_KEY"
  
  # Проверка и создание бакета если не существует
  if ! aws $AWS_ARGS s3 ls "s3://$S3_BUCKET" 2>/dev/null; then
    echo "Создание бакета $S3_BUCKET..."
    aws $AWS_ARGS s3 mb "s3://$S3_BUCKET"
  else
    echo "Бакет $S3_BUCKET уже существует"
  fi
  
  # Загрузка сертификатов в бакет
  echo "Загрузка сертификатов в бакет $S3_BUCKET..."
  aws $AWS_ARGS s3 cp "$KEYSTORE_PATH" "s3://$S3_BUCKET/certs/keystore.jks"
  aws $AWS_ARGS s3 cp "$TRUSTSTORE_PATH" "s3://$S3_BUCKET/certs/truststore.jks"
  
  # Проверка загрузки
  echo "Проверка загрузки файлов..."
  aws $AWS_ARGS s3 ls "s3://$S3_BUCKET/certs/"
fi

echo "Инициализация S3/MinIO завершена успешно!"

# Удаление временных файлов если они были созданы
if [ -f "sample_keystore.jks" ]; then
  rm sample_keystore.jks
  rm sample_truststore.jks
fi 