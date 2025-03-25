# Развертывание приложения

## Обзор

Документация по развертыванию приложения Kafka to ADB описывает процесс установки, настройки и запуска приложения в различных окружениях.

## Требования

### Системные требования
- Python 3.8 или выше
- 2GB RAM минимум
- 1 CPU минимум
- 10GB свободного места на диске

### Зависимости
- Apache Kafka 2.8.0 или выше
- AnalyticDB (ADB) с поддержкой SSL
- SSL сертификаты
- Доступ к сети

## Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-org/kafka-to-adb.git
cd kafka-to-adb
```

### 2. Установка зависимостей
```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка пакетов
pip install -r requirements.txt
```

### 3. Настройка конфигурации
```bash
# Копирование примера конфигурации
cp configs/config.yaml.example configs/config.yaml

# Редактирование конфигурации
nano configs/config.yaml
```

### 4. Настройка сертификатов
```bash
# Создание директории для сертификатов
mkdir -p /etc/kafka-to-adb/certs

# Копирование сертификатов
cp /path/to/your/certs/* /etc/kafka-to-adb/certs/

# Установка прав доступа
chmod 600 /etc/kafka-to-adb/certs/*
```

## Развертывание в Kubernetes

### 1. Создание Docker образа
```dockerfile
# Dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### 2. Сборка и публикация образа
```bash
# Сборка образа
docker build -t kafka-to-adb:latest .

# Публикация в registry
docker tag kafka-to-adb:latest registry.example.com/kafka-to-adb:latest
docker push registry.example.com/kafka-to-adb:latest
```

### 3. Создание Kubernetes манифестов
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-to-adb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kafka-to-adb
  template:
    metadata:
      labels:
        app: kafka-to-adb
    spec:
      containers:
      - name: kafka-to-adb
        image: registry.example.com/kafka-to-adb:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: config
          mountPath: /app/configs
        - name: certs
          mountPath: /etc/kafka-to-adb/certs
      volumes:
      - name: config
        configMap:
          name: kafka-to-adb-config
      - name: certs
        secret:
          secretName: kafka-to-adb-certs
```

### 4. Создание ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-to-adb-config
data:
  config.yaml: |
    app_name: "kafka-to-adb"
    environment: "production"
    # ... остальные настройки ...
```

### 5. Создание Secret
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-to-adb-certs
type: Opaque
data:
  cert.pem: <base64-encoded-cert>
  key.pem: <base64-encoded-key>
```

### 6. Применение манифестов
```bash
kubectl apply -f deployment.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

## Мониторинг

### 1. Настройка Prometheus
```yaml
# prometheus.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kafka-to-adb
spec:
  selector:
    matchLabels:
      app: kafka-to-adb
  endpoints:
  - port: metrics
    interval: 30s
```

### 2. Настройка Grafana
```yaml
# grafana-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-to-adb-dashboard
data:
  dashboard.json: |
    {
      "dashboard": {
        "title": "Kafka to ADB Metrics",
        "panels": [
          {
            "title": "Memory Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "kafka_to_adb_memory_usage_bytes"
              }
            ]
          }
        ]
      }
    }
```

## Масштабирование

### 1. Горизонтальное масштабирование
```bash
# Увеличение количества реплик
kubectl scale deployment kafka-to-adb --replicas=3
```

### 2. Вертикальное масштабирование
```yaml
# Обновление ресурсов
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kafka-to-adb
spec:
  template:
    spec:
      containers:
      - name: kafka-to-adb
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
```

## Обновление

### 1. Обновление версии
```bash
# Обновление образа
kubectl set image deployment/kafka-to-adb kafka-to-adb=registry.example.com/kafka-to-adb:new-version
```

### 2. Откат изменений
```bash
# Откат к предыдущей версии
kubectl rollout undo deployment/kafka-to-adb
```

## Безопасность

### 1. Настройка RBAC
```yaml
# rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kafka-to-adb
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
```

### 2. Настройка Network Policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: kafka-to-adb
spec:
  podSelector:
    matchLabels:
      app: kafka-to-adb
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
```

## Рекомендации по развертыванию

### 1. Разработка
- Использовать локальное окружение
- Включать подробное логирование
- Отключать некоторые проверки

### 2. Тестирование
- Развертывать в тестовом окружении
- Проверять все компоненты
- Тестировать отказоустойчивость

### 3. Продакшн
- Использовать высокую доступность
- Настраивать мониторинг
- Регулярно обновлять

### 4. Обслуживание
- Планировать обновления
- Мониторить состояние
- Реагировать на проблемы 