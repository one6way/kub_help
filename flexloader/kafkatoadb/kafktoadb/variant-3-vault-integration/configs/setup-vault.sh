#!/bin/bash
# Скрипт для настройки HashiCorp Vault для хранения и доступа к Kafka-сертификатам

set -e

# Переменные для настройки
VAULT_ADDR=${VAULT_ADDR:-"http://localhost:8200"}
VAULT_TOKEN=${VAULT_TOKEN:-"root"}
K8S_HOST=${K8S_HOST:-"https://kubernetes.default.svc"}
NAMESPACE=${NAMESPACE:-"spark-namespace"}
SERVICE_ACCOUNT=${SERVICE_ACCOUNT:-"spark-vault-auth"}
POLICY_NAME=${POLICY_NAME:-"spark-kafka-policy"}
ROLE_NAME=${ROLE_NAME:-"spark-app"}
SECRET_PATH=${SECRET_PATH:-"secret/kafka-certs"}

# Проверка наличия необходимых утилит
for cmd in curl jq base64; do
  if ! command -v $cmd &> /dev/null; then
    echo "Ошибка: требуется утилита $cmd"
    exit 1
  fi
done

# Установка переменных окружения Vault
export VAULT_ADDR=$VAULT_ADDR
export VAULT_TOKEN=$VAULT_TOKEN

echo "Настраиваем Vault для Spark-приложения с Kafka-сертификатами..."

# 1. Создание политики
echo "1. Создание политики $POLICY_NAME..."
if [ -f "vault-policy.hcl" ]; then
  vault policy write $POLICY_NAME vault-policy.hcl
else
  echo "Ошибка: файл политики vault-policy.hcl не найден"
  exit 1
fi

# 2. Включение Kubernetes аутентификации если еще не включена
echo "2. Настройка Kubernetes аутентификации..."
vault auth list | grep -q kubernetes || vault auth enable kubernetes

# 3. Настройка конфигурации Kubernetes аутентификации
echo "3. Конфигурация Kubernetes аутентификации..."
# Получаем токен и CA-сертификат из service account в Kubernetes
# В реальном сценарии вам потребуется извлечь эти данные из вашего кластера
# Здесь для примера используются фиктивные данные
SA_JWT_TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9..."
SA_CA_CRT=$(cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt | base64 | tr -d '\n')

vault write auth/kubernetes/config \
    token_reviewer_jwt="$SA_JWT_TOKEN" \
    kubernetes_host="$K8S_HOST" \
    kubernetes_ca_cert="$SA_CA_CRT"

# 4. Создание роли для Spark-приложения
echo "4. Создание роли $ROLE_NAME..."
vault write auth/kubernetes/role/$ROLE_NAME \
    bound_service_account_names=$SERVICE_ACCOUNT \
    bound_service_account_namespaces=$NAMESPACE \
    policies=$POLICY_NAME \
    ttl=1h

# 5. Создание секрета с Kafka-сертификатами
echo "5. Создание секрета с Kafka-сертификатами..."

# Проверка наличия файлов сертификатов
KEYSTORE_FILE="../../certs/keystore.jks"
TRUSTSTORE_FILE="../../certs/truststore.jks"

if [ ! -f "$KEYSTORE_FILE" ] || [ ! -f "$TRUSTSTORE_FILE" ]; then
  echo "Ошибка: файлы сертификатов не найдены"
  echo "Создаем демонстрационные файлы для примера..."
  
  # Создаем пустой файл для примера
  echo "sample_data" > sample_keystore.jks
  echo "sample_data" > sample_truststore.jks
  
  KEYSTORE_FILE="sample_keystore.jks"
  TRUSTSTORE_FILE="sample_truststore.jks"
fi

# Кодируем сертификаты в base64
KEYSTORE_CONTENT=$(base64 -w0 $KEYSTORE_FILE)
TRUSTSTORE_CONTENT=$(base64 -w0 $TRUSTSTORE_FILE)

# Создаем секрет в Vault
vault kv put secret/kafka-certs \
    keystore_content="$KEYSTORE_CONTENT" \
    truststore_content="$TRUSTSTORE_CONTENT" \
    keystore_password="keystore_password" \
    truststore_password="truststore_password"

echo "Настройка Vault завершена успешно!"
echo "Путь к сертификатам: $SECRET_PATH"
echo "Роль для Kubernetes: $ROLE_NAME"
echo "Политика: $POLICY_NAME"

# Чистим демо-файлы, если они были созданы
if [ -f "sample_keystore.jks" ]; then
  rm sample_keystore.jks
  rm sample_truststore.jks
fi 