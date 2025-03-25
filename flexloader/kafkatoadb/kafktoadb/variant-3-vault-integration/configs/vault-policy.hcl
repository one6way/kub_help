# Политика для доступа Spark-приложения к секретам Kafka в Vault

# Разрешаем чтение секретов для Kafka-сертификатов
path "secret/data/kafka-certs" {
  capabilities = ["read"]
}

# Разрешаем проверку существования секрета
path "secret/metadata/kafka-certs" {
  capabilities = ["read"]
}

# Запрещаем запись и обновление секретов
path "secret/data/kafka-certs" {
  capabilities = ["deny"]
  denied_parameters = {
    "*" = []
  }
}

# Доступ к информации о собственном токене (используется Vault Agent)
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Позволяем обновлять собственный токен (используется Vault Agent)
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Позволяем отзывать собственный токен (хорошая практика безопасности)
path "auth/token/revoke-self" {
  capabilities = ["update"]
} 