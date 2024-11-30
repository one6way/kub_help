# Инструкция по настройке CI/CD для FlexLoader GUI в TeamCity

## Оглавление
1. [Общее описание процесса](#общее-описание-процесса)
2. [Предварительные требования](#предварительные-требования)
3. [Настройка TeamCity](#настройка-teamcity)
4. [Описание Build Steps](#описание-build-steps)
5. [Настройка параметров](#настройка-параметров)
6. [Helm чарты](#helm-чарты)
7. [Troubleshooting](#troubleshooting)

## Общее описание процесса

Процесс CI/CD для FlexLoader GUI состоит из двух основных компонентов (backend и frontend) и включает следующие этапы:
1. Продвижение Docker образов из тестового registry в продакшн
2. Развертывание приложения в Kubernetes с использованием Helm

```mermaid
graph LR
    A[Test Registry] --> B[Prod Registry]
    B --> C[Helm Deploy]
    C --> D[Kubernetes]
```

## Предварительные требования

1. Доступ к registry:
   - oneway-test.registrymy.ru (тестовый registry)
   - oneway-prod.myregistry.ru (продакшн registry)
   
2. Инструменты:
   - Docker
   - Helm (версия 3+)
   - kubectl
   - git

3. Доступы:
   - Учетные данные для обоих registry
   - Доступ к репозиторию с Helm чартами
   - kubeconfig для доступа к Kubernetes кластеру

## Настройка TeamCity

### 1. Создание нового проекта

1. Создайте новый проект в TeamCity
2. Название: FlexLoader GUI Deployment
3. Добавьте VCS root для репозитория с Helm чартами

### 2. Настройка Build Configuration

1. Создайте новую Build Configuration
2. Название: "Deploy to Production"
3. Добавьте параметры (см. раздел "Настройка параметров")

## Описание Build Steps

### Step 1: Promote Backend Image
```kotlin
runner {
    type = "command-line"
    name = "Promote Backend Image"
    
    param("script.content", """
        #!/bin/bash
        set -e
        
        SOURCE_REGISTRY="oneway-test.registrymy.ru"
        TARGET_REGISTRY="oneway-prod.myregistry.ru"
        IMAGE_NAME="flexloader-gui-backend"
        VERSION="%build.number%"
        
        echo "Logging into source registry..."
        docker login ${SOURCE_REGISTRY} -u %registry.user% -p %registry.password%
        
        echo "Logging into target registry..."
        docker login ${TARGET_REGISTRY} -u %registry.prod.user% -p %registry.prod.password%
        
        echo "Pulling image from source registry..."
        docker pull ${SOURCE_REGISTRY}/${IMAGE_NAME}:${VERSION}
        
        echo "Tagging image for production..."
        docker tag ${SOURCE_REGISTRY}/${IMAGE_NAME}:${VERSION} ${TARGET_REGISTRY}/${IMAGE_NAME}:${VERSION}
        
        echo "Pushing to production registry..."
        docker push ${TARGET_REGISTRY}/${IMAGE_NAME}:${VERSION}
    """.trimIndent())
}
```

### Step 2: Promote Frontend Image
```kotlin
runner {
    type = "command-line"
    name = "Promote Frontend Image"
    
    param("script.content", """
        #!/bin/bash
        set -e
        
        SOURCE_REGISTRY="oneway-test.registrymy.ru"
        TARGET_REGISTRY="oneway-prod.myregistry.ru"
        IMAGE_NAME="flexloader-gui-frontend"
        VERSION="%build.number%"
        
        echo "Pulling image from source registry..."
        docker pull ${SOURCE_REGISTRY}/${IMAGE_NAME}:${VERSION}
        
        echo "Tagging image for production..."
        docker tag ${SOURCE_REGISTRY}/${IMAGE_NAME}:${VERSION} ${TARGET_REGISTRY}/${IMAGE_NAME}:${VERSION}
        
        echo "Pushing to production registry..."
        docker push ${TARGET_REGISTRY}/${IMAGE_NAME}:${VERSION}
    """.trimIndent())
}
```

### Step 3: Clone Helm Charts
```kotlin
runner {
    type = "command-line"
    name = "Clone Helm Charts"
    
    param("script.content", """
        #!/bin/bash
        set -e
        
        echo "Cloning Helm charts repository..."
        git clone https://one6way.bitbucket.ru/flexloader-helm-charts.git
        cd flexloader-helm-charts
    """.trimIndent())
}
```

### Step 4: Deploy Backend
```kotlin
runner {
    type = "command-line"
    name = "Deploy Backend"
    
    param("script.content", """
        #!/bin/bash
        set -e
        
        echo "Deploying backend component..."
        helm upgrade --install flexloader-backend ./charts/backend \
            --namespace flexloader \
            --set image.repository=oneway-prod.myregistry.ru/flexloader-gui-backend \
            --set image.tag=%build.number% \
            --values ./values/backend-values.yaml
    """.trimIndent())
}
```

### Step 5: Deploy Frontend
```kotlin
runner {
    type = "command-line"
    name = "Deploy Frontend"
    
    param("script.content", """
        #!/bin/bash
        set -e
        
        echo "Deploying frontend component..."
        helm upgrade --install flexloader-frontend ./charts/frontend \
            --namespace flexloader \
            --set image.repository=oneway-prod.myregistry.ru/flexloader-gui-frontend \
            --set image.tag=%build.number% \
            --values ./values/frontend-values.yaml
    """.trimIndent())
}
```

## Настройка параметров

В TeamCity необходимо настроить следующие параметры:

1. Параметры для registry:
   ```
   registry.user - Username для тестового registry
   registry.password - Password для тестового registry
   registry.prod.user - Username для продакшн registry
   registry.prod.password - Password для продакшн registry
   ```

2. Параметры для Kubernetes:
   ```
   kubeconfig - Файл конфигурации для доступа к кластеру
   ```

## Helm чарты

### Структура Helm чартов
```
flexloader-helm-charts/
├── charts/
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   └── frontend/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── values/
    ├── backend-values.yaml
    └── frontend-values.yaml
```

### Пример backend-values.yaml
```yaml
image:
  repository: oneway-prod.myregistry.ru/flexloader-gui-backend
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8080

resources:
  limits:
    cpu: 1
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### Пример frontend-values.yaml
```yaml
image:
  repository: oneway-prod.myregistry.ru/flexloader-gui-frontend
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: flexloader.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Troubleshooting

### Общие проблемы и решения

1. Ошибка доступа к registry:
   - Проверьте корректность учетных данных
   - Убедитесь, что registry доступен
   - Проверьте права доступа к образам

2. Ошибки Helm:
   - Проверьте синтаксис values файлов
   - Убедитесь, что namespace существует
   - Проверьте права доступа к кластеру

3. Ошибки развертывания:
   - Проверьте логи подов
   - Убедитесь, что ресурсы кластера достаточны
   - Проверьте корректность конфигурации ingress

### Полезные команды для отладки

```bash
# Проверка статуса подов
kubectl get pods -n flexloader

# Просмотр логов
kubectl logs -n flexloader deployment/flexloader-backend
kubectl logs -n flexloader deployment/flexloader-frontend

# Проверка релизов Helm
helm list -n flexloader

# Проверка values релиза
helm get values flexloader-backend -n flexloader
```

## Рекомендации по безопасности

1. Регулярно обновляйте учетные данные registry
2. Используйте секреты Kubernetes для хранения чувствительных данных
3. Настройте Network Policies для ограничения сетевого доступа
4. Регулярно обновляйте версии Helm чартов и зависимостей
5. Используйте RBAC для ограничения прав доступа в Kubernetes
