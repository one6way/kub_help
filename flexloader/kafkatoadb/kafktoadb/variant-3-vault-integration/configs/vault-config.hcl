storage "raft" {
  path = "/vault/data"
  node_id = "node1"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1
}

api_addr = "http://0.0.0.0:8200"
cluster_addr = "https://0.0.0.0:8201"
ui = true

# Включение движка секретов KV v2
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Включение PKI для выдачи сертификатов
path "pki*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

# Настройка политики для Spark-приложений
path "secret/data/kafka-certs" {
  capabilities = ["read"]
}

# Настройка политики для автоматической ротации сертификатов
path "secret/data/kafka-certs" {
  capabilities = ["create", "read", "update", "delete"]
  min_wrapping_ttl = "1h"
  max_wrapping_ttl = "24h"
}

# Настройка лимитов для производительности
max_lease_ttl = "768h"
default_lease_ttl = "768h" 