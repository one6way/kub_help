#!/bin/bash
set -e

# Проверяем, переданы ли пароли через переменные окружения
if [ -z "${KEYSTORE_PASSWORD}" ]; then
  echo "Ошибка: переменная KEYSTORE_PASSWORD не определена"
  exit 1
fi

if [ -z "${TRUSTSTORE_PASSWORD}" ]; then
  echo "Ошибка: переменная TRUSTSTORE_PASSWORD не определена"
  exit 1
fi

# Добавляем параметры для Spark
export SPARK_SUBMIT_OPTS="\
-Dspark.kafka.ssl.keystore.location=${SPARK_KAFKA_SSL_KEYSTORE_LOCATION} \
-Dspark.kafka.ssl.truststore.location=${SPARK_KAFKA_SSL_TRUSTSTORE_LOCATION} \
-Dspark.kafka.ssl.keystore.password=${KEYSTORE_PASSWORD} \
-Dspark.kafka.ssl.truststore.password=${TRUSTSTORE_PASSWORD} \
${SPARK_SUBMIT_OPTS}"

# Логи
echo "Spark настроен для использования SSL с Kafka"
echo "Keystore: ${SPARK_KAFKA_SSL_KEYSTORE_LOCATION}"
echo "Truststore: ${SPARK_KAFKA_SSL_TRUSTSTORE_LOCATION}"

# Выполняем оригинальную точку входа из образа Spark
exec /opt/entrypoint.sh "$@" 