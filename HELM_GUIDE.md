# 🚢 Helm Configuration Guide

## 📋 Содержание
- [Базовые конфигурации](#базовые-конфигурации)
- [Продвинутые конфигурации](#продвинутые-конфигурации)
- [Микросервисная архитектура](#микросервисная-архитектура)
- [Высоконагруженные приложения](#высоконагруженные-приложения)

## 🎯 Введение
В этом руководстве собраны примеры конфигураций Helm для различных сценариев использования. Каждый пример содержит подробные комментарии и рекомендации по настройке.

## 🔰 Базовые конфигурации

### 📝 Простой пример values.yaml
Базовая конфигурация для типичного веб-приложения.

```yaml
# 🐳 Настройки образа контейнера
image:
  # Имя образа в registry
  repository: nginx
  # Тег версии образа
  tag: "1.21.0"
  # Политика загрузки образа (Always, IfNotPresent, Never)
  pullPolicy: IfNotPresent

# 🔄 Настройки реплик
replicaCount: 3  # Количество экземпляров пода

# 💻 Настройки ресурсов контейнера
resources:
  # Минимальные требуемые ресурсы
  requests:
    cpu: 100m      # 0.1 ядра CPU
    memory: 128Mi  # 128 МБ памяти
  # Максимальные лимиты ресурсов
  limits:
    cpu: 200m      # 0.2 ядра CPU
    memory: 256Mi  # 256 МБ памяти

# 🌐 Конфигурация сервиса
service:
  # Тип сервиса (ClusterIP, NodePort, LoadBalancer)
  type: ClusterIP
  # Порт сервиса
  port: 80
  # Целевой порт контейнера
  targetPort: 8080

# ⚖️ Настройки автомасштабирования
autoscaling:
  # Включение HPA
  enabled: true
  # Минимальное количество реплик
  minReplicas: 2
  # Максимальное количество реплик
  maxReplicas: 10
  # Целевая утилизация CPU
  targetCPUUtilizationPercentage: 80
```

## 🚀 Продвинутые конфигурации

### 📊 Пример с Ingress и хранилищем
Расширенная конфигурация с настройками Ingress, хранилища и мониторинга.

```yaml
# 📱 Настройки приложения
app:
  # Имя приложения, используется в labels
  name: myapp
  # Окружение (dev, staging, prod)
  environment: prod
  # Версия приложения
  version: "2.1.0"

# 🌍 Настройки Ingress
ingress:
  # Включение Ingress
  enabled: true
  # Класс Ingress контроллера
  className: nginx
  # Аннотации для Ingress
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  # Настройки хостов
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
          pathType: Prefix
  # Настройки TLS
  tls:
    - secretName: myapp-tls
      hosts:
        - myapp.example.com

# 💾 Настройки постоянного хранилища
persistence:
  # Включение PVC
  enabled: true
  # Класс хранилища
  storageClass: standard
  # Размер хранилища
  size: 10Gi
  # Режим доступа
  accessMode: ReadWriteOnce

# 🔒 Настройки безопасности
security:
  # Включение ServiceAccount
  serviceAccount:
    create: true
    annotations: {}
  # Настройки Pod Security Context
  podSecurityContext:
    fsGroup: 2000
  # Security Context контейнера
  securityContext:
    capabilities:
      drop:
        - ALL
    runAsNonRoot: true
    runAsUser: 1000

# 📊 Настройки мониторинга
monitoring:
  # Prometheus метрики
  metrics:
    enabled: true
    # Аннотации для scraping метрик
    serviceMonitor:
      enabled: true
      interval: 15s
  # Настройки логирования
  logging:
    enabled: true
    # Формат логов (json, text)
    format: json
```

## 🏗️ Микросервисная архитектура

### 🔄 Пример конфигурации микросервисов
Комплексная конфигурация для микросервисной архитектуры.

```yaml
# 🌍 Глобальные настройки
global:
  # Docker registry настройки
  registry:
    url: registry.example.com
    secret: registry-credentials
  # Общие метки
  labels:
    team: backend
    project: microservices
  # Сетевые настройки
  network:
    domain: cluster.local
    apiHost: api.example.com

# 🖥️ Frontend сервис
frontend:
  enabled: true
  image:
    repository: frontend
    tag: "v1.2.0"
  replicaCount: 2
  ingress:
    enabled: true
    host: www.example.com

# ⚙️ Backend API
backend:
  enabled: true
  image:
    repository: backend
    tag: "v1.1.0"
  replicaCount: 3
  database:
    url: postgresql://db:5432/myapp
    secretName: db-credentials

# 🗄️ База данных
database:
  enabled: true
  image:
    repository: postgres
    tag: "13-alpine"
  persistence:
    enabled: true
    size: 20Gi
  backup:
    enabled: true
    schedule: "0 2 * * *"
    retention: 7d

# 📊 Мониторинг
monitoring:
  prometheus:
    enabled: true
    scrapeInterval: 30s
  grafana:
    enabled: true
    adminPassword: "admin-password"
    dashboards:
      enabled: true
      label: grafana_dashboard
```

## 🚀 Высоконагруженные приложения

### ⚡ Пример конфигурации для high-load
Оптимизированная конфигурация для высоконагруженных приложений.

```yaml
# 🔧 Настройки производительности
performance:
  # JVM настройки
  jvm:
    heapSize: 4Gi
    gcType: G1GC
    extraOpts:
      - "-XX:+UseCompressedOops"
      - "-XX:+UseStringDeduplication"

  # Системные ресурсы
  resources:
    requests:
      cpu: 2000m
      memory: 4Gi
    limits:
      cpu: 4000m
      memory: 8Gi

  # Сетевая оптимизация
  network:
    tcp:
      backlog: 4096
      keepalive: true
      maxConnections: 10000
    loadBalancer:
      algorithm: "least_conn"
      sessionAffinity: true
      timeout: 30s

# 🔄 Отказоустойчивость
highAvailability:
  # Pod Disruption Budget
  pdb:
    enabled: true
    minAvailable: 75%
  
  # Анти-аффинити настройки
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - topologyKey: "kubernetes.io/hostname"
          labelSelector:
            matchLabels:
              app: high-load-app

  # Проверки работоспособности
  probes:
    liveness:
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    readiness:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 3
      successThreshold: 2

# 📈 Масштабирование
autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
  metrics:
    cpu:
      enabled: true
      targetAverageUtilization: 70
    memory:
      enabled: true
      targetAverageUtilization: 80
    custom:
      enabled: true
      metric:
        name: requests_per_second
        target: 1000
```

## 📚 Дополнительные ресурсы

### 🔗 Полезные ссылки
- [Официальная документация Helm](https://helm.sh/docs/)
- [Best Practices Guide](https://helm.sh/docs/chart_best_practices/)
- [Chart Development Tips](https://helm.sh/docs/howto/charts_tips_and_tricks/)

### 🛠️ Инструменты
- [Helm CLI](https://helm.sh/docs/intro/install/)
- [Helm Hub](https://hub.helm.sh/)
- [Chart Testing](https://github.com/helm/chart-testing)

### ⚠️ Важные замечания
1. Всегда проверяйте values.yaml на безопасность
2. Используйте версионирование для чартов
3. Следите за обновлениями зависимостей
4. Тестируйте конфигурации перед production

## 🤝 Содействие

Если у вас есть предложения по улучшению этого руководства:
1. Создайте Issue
2. Предложите Pull Request
3. Поделитесь своим опытом

## 📝 Лицензия

MIT License - свободно используйте для своих проектов.

---

🌟 Надеемся, это руководство поможет вам в работе с Helm! 
