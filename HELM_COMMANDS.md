# 🎡 Helm Commands - Полное руководство

## 📑 Содержание
- [Основы Helm](#основы-helm)
- [Работа с репозиториями](#работа-с-репозиториями)
- [Управление чартами](#управление-чартами)
- [Установка и обновление](#установка-и-обновление)
- [Управление релизами](#управление-релизами)
- [Шаблоны и значения](#шаблоны-и-значения)
- [Тестирование и отладка](#тестирование-и-отладка)
- [Безопасность](#безопасность)
- [Продвинутые техники](#продвинутые-техники)
- [Интеграция и CI/CD](#интеграция-и-cicd)
- [Helm в облачных провайдерах](#helm-в-облачных-провайдерах)
- [GitOps и CI/CD интеграция](#gitops-и-cicd-интеграция)
- [Продвинутая отладка](#продвинутая-отладка)
- [Миграция между версиями](#миграция-между-версиями)
- [Разработка плагинов](#разработка-плагинов)
- [Продвинутая безопасность](#продвинутая-безопасность)
- [Мониторинг и метрики](#мониторинг-и-метрики)
- [Дополнительные ресурсы](#дополнительные-ресурсы)

## 🚀 Основы Helm

### 📦 Установка Helm
```bash
# Установка через Homebrew (macOS)
brew install helm

# Проверка версии
helm version

# Инициализация Helm (если требуется)
helm init
```

### 🔍 Поиск чартов
```bash
# Поиск чарта в репозиториях
helm search repo nginx

# Поиск в Artifact Hub
helm search hub wordpress

# Показать все версии чарта
helm search repo nginx --versions
```

## 📚 Работа с репозиториями

### 📋 Управление репозиториями
```bash
# Добавление репозитория
helm repo add bitnami https://charts.bitnami.com/bitnami

# Обновление репозиториев
helm repo update

# Список репозиториев
helm repo list

# Удаление репозитория
helm repo remove bitnami

# Показать информацию о репозитории
helm repo index
```

### 🔄 Создание локального репозитория
```bash
# Создание директории для репозитория
mkdir helm-repo && cd helm-repo

# Создание index.yaml
helm repo index .

# Обновление index.yaml с новыми чартами
helm repo index . --url https://example.com/charts
```

## 📦 Управление чартами

### 🛠️ Создание чарта
```bash
# Создание нового чарта
helm create mychart

# Структура чарта
mychart/
  Chart.yaml          # Метаданные чарта
  values.yaml         # Значения по умолчанию
  charts/             # Зависимые чарты
  templates/          # Шаблоны Kubernetes
  templates/NOTES.txt # Инструкции после установки
```

### 📝 Работа с чартами
```bash
# Проверка структуры чарта
helm lint mychart

# Упаковка чарта
helm package mychart

# Распаковка чарта
helm pull bitnami/wordpress --untar

# Показать документацию чарта
helm show readme bitnami/wordpress
helm show values bitnami/wordpress
```

## 🚀 Установка и обновление

### 📥 Установка чартов
```bash
# Установка чарта
helm install my-release bitnami/wordpress

# Установка с кастомными значениями
helm install my-release bitnami/wordpress -f values.yaml

# Установка с переопределением значений
helm install my-release bitnami/wordpress --set wordpressUsername=admin

# Установка с ожиданием готовности
helm install my-release bitnami/wordpress --wait
```

### 🔄 Обновление релизов
```bash
# Обновление релиза
helm upgrade my-release bitnami/wordpress

# Откат релиза
helm rollback my-release 1

# Обновление или установка
helm upgrade --install my-release bitnami/wordpress

# Показать историю релиза
helm history my-release
```

## 📊 Управление релизами

### 📋 Информация о релизах
```bash
# Список релизов
helm list

# Статус релиза
helm status my-release

# Получение манифестов релиза
helm get manifest my-release

# Получение значений релиза
helm get values my-release
```

### 🗑️ Удаление релизов
```bash
# Удаление релиза
helm uninstall my-release

# Удаление с сохранением истории
helm uninstall my-release --keep-history

# Удаление всех релизов
helm uninstall $(helm list -q)
```

## 📝 Шаблоны и значения

### 🎨 Работа с шаблонами
```bash
# Проверка шаблонов
helm template my-release bitnami/wordpress

# Отладка шаблонов
helm template my-release bitnami/wordpress --debug

# Проверка определенного шаблона
helm template my-release bitnami/wordpress -s templates/deployment.yaml
```

### ⚙️ Управление значениями
```bash
# Показать значения по умолчанию
helm show values bitnami/wordpress

# Проверка пользовательских значений
helm get values my-release

# Обновление с новыми значениями
helm upgrade my-release bitnami/wordpress --reuse-values --set service.type=NodePort
```

## 🔍 Тестирование и отладка

### 🧪 Тестирование чартов
```bash
# Запуск тестов
helm test my-release

# Проверка синтаксиса
helm lint mychart

# Проверка установки
helm install my-release bitnami/wordpress --dry-run
```

### 🐛 Отладка
```bash
# Отладка установки
helm install my-release bitnami/wordpress --debug --dry-run

# Отладка шаблонов
helm template mychart --debug

# Проверка манифестов
helm get manifest my-release
```

## 🔒 Безопасность

### 🔐 Управление секретами
```bash
# Создание секрета
helm secrets encrypt values.yaml

# Расшифровка секрета
helm secrets decrypt values.yaml

# Установка с секретами
helm secrets install my-release bitnami/wordpress -f secrets.yaml
```

### 📜 Управление сертификатами
```bash
# Создание сертификата
helm cert create

# Проверка сертификата
helm cert verify

# Обновление сертификата
helm cert renew
```

## 🎓 Продвинутые техники

### 🔄 Хуки жизненного цикла
```bash
# Создание pre-install хука
annotations:
  "helm.sh/hook": pre-install

# Создание post-install хука
annotations:
  "helm.sh/hook": post-install

# Управление весом хуков
annotations:
  "helm.sh/hook-weight": "5"
```

### 🎯 Зависимости
```bash
# Обновление зависимостей
helm dependency update mychart

# Построение зависимостей
helm dependency build mychart

# Список зависимостей
helm dependency list mychart
```

## 🔄 Интеграция и CI/CD

### 🚀 CI/CD интеграция
```bash
# Проверка в CI
helm lint mychart
helm template mychart
helm test my-release

# Автоматическая установка
helm upgrade --install my-release mychart --wait

# Проверка статуса
helm status my-release -o json
```

### 📦 Артефакты и репозитории
```bash
# Упаковка для CI
helm package mychart --version $(git describe --tags)

# Публикация в репозиторий
helm push mychart-0.1.0.tgz oci://registry.example.com/charts

# Загрузка из репозитория
helm pull oci://registry.example.com/charts/mychart --version 0.1.0
```

## 📚 Полезные плагины

### 🔌 Управление плагинами
```bash
# Установка плагина
helm plugin install https://github.com/helm/helm-2to3

# Список плагинов
helm plugin list

# Обновление плагина
helm plugin update 2to3

# Удаление плагина
helm plugin uninstall 2to3
```

### 🛠️ Популярные плагины
```bash
# Helm Secrets
helm plugin install https://github.com/jkroepke/helm-secrets

# Helm Diff
helm plugin install https://github.com/databus23/helm-diff

# Helm Monitor
helm plugin install https://github.com/ContainerSolutions/helm-monitor
```

## 🎯 Лучшие практики

### 📋 Организация чартов
```bash
# Структура репозитория
charts/
  ├── base/        # Базовые чарты
  ├── apps/        # Приложения
  └── infra/       # Инфраструктурные чарты

# Версионирование
Chart.yaml:
  version: 1.2.3   # Версия чарта
  appVersion: 2.0.0 # Версия приложения
```

### 🔍 Проверки и валидация
```bash
# Проверка перед коммитом
helm lint mychart
helm template mychart
kubectl apply --dry-run=client -f <(helm template mychart)

# Проверка значений
helm install --dry-run --debug mychart
```

## ☁️ Helm в облачных провайдерах

### 🌐 AWS EKS
```bash
# Настройка AWS CLI и kubectl
aws eks update-kubeconfig --name cluster-name --region region

# Установка AWS EKS чартов
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Установка AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=cluster-name

# Установка AWS EBS CSI Driver
helm install aws-ebs-csi-driver eks/aws-ebs-csi-driver \
  -n kube-system

# Установка AWS CloudWatch Agent
helm install cloudwatch eks/aws-cloudwatch-metrics \
  -n amazon-cloudwatch
```

### 🌊 Azure AKS
```bash
# Подключение к AKS
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

# Установка AGIC (Application Gateway Ingress Controller)
helm repo add application-gateway-kubernetes-ingress \
  https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/
helm install ingress-azure \
  -f helm-config.yaml \
  application-gateway-kubernetes-ingress/ingress-azure

# Установка Azure Monitor
helm install azure-monitor \
  --namespace monitoring \
  azure/azure-monitor-containers

# Установка Azure Service Operator
helm repo add azure-service-operator \
  https://raw.githubusercontent.com/Azure/azure-service-operator/master/charts
helm install aso azure-service-operator/azure-service-operator \
  --namespace azure-service-operator \
  --create-namespace
```

### 🌎 Google GKE
```bash
# Подключение к GKE
gcloud container clusters get-credentials cluster-name --region region

# Установка Google Cloud Monitoring
helm install prometheus-operator stable/prometheus-operator \
  --set prometheusOperator.createCustomResource=false

# Установка Cloud Storage CSI Driver
helm install csi-driver \
  https://raw.githubusercontent.com/kubernetes-sigs/gcp-compute-persistent-disk-csi-driver/master/deploy/helm/charts/gcp-compute-persistent-disk-csi-driver

# Установка GKE Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.service.loadBalancerIP=YOUR_STATIC_IP
```

## 🔄 GitOps и CI/CD интеграция

### 🚢 ArgoCD
```bash
# Установка ArgoCD
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace

# Конфигурация приложения в ArgoCD
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/my-org/my-app
    targetRevision: HEAD
    path: helm
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
EOF

# Синхронизация приложения
argocd app sync my-app

# Просмотр статуса синхронизации
argocd app get my-app
```

### ⚡ Flux CD
```bash
# Установка Flux
helm repo add fluxcd https://charts.fluxcd.io
helm install flux fluxcd/flux \
  --namespace flux \
  --set git.url=git@github.com:my-org/my-repo

# Установка Helm Operator
helm install helm-operator fluxcd/helm-operator \
  --namespace flux \
  --set git.ssh.secretName=flux-git-deploy

# Создание HelmRelease
cat <<EOF | kubectl apply -f -
apiVersion: helm.fluxcd.io/v1
kind: HelmRelease
metadata:
  name: my-release
  namespace: default
spec:
  chart:
    repository: https://charts.bitnami.com/bitnami
    name: wordpress
    version: 10.0.0
EOF

# Проверка статуса релиза
kubectl describe helmrelease my-release
```

## 🔍 Продвинутая отладка

### 🐛 Отладка шаблонов
```bash
# Отладка с подробным выводом
helm template mychart --debug --set key=value

# Проверка конкретного шаблона
helm template mychart --show-only templates/deployment.yaml

# Проверка встроенных объектов
helm template mychart --debug | grep "Release\|Chart\|Values"

# Валидация манифестов
helm template mychart | kubectl apply --dry-run=client -f -

# Проверка синтаксиса Go templates
helm lint mychart --strict
```

### 📊 Анализ производительности
```bash
# Время выполнения команд
time helm install myrelease mychart

# Профилирование памяти
helm --debug install myrelease mychart 2> helm-debug.log

# Анализ размера чарта
du -h mychart

# Проверка зависимостей
helm dep build mychart --debug
```

## 🔄 Миграция между версиями

### 🔀 Helm 2 to Helm 3
```bash
# Установка плагина 2to3
helm plugin install https://github.com/helm/helm-2to3

# Миграция конфигурации
helm 2to3 move config

# Миграция релизов
helm 2to3 convert RELEASE_NAME

# Очистка Helm 2 данных
helm 2to3 cleanup
```

### 📦 Обновление чартов
```bash
# Проверка совместимости
helm template old-chart --api-versions

# Миграция values
helm show values old-chart > values-old.yaml
helm show values new-chart > values-new.yaml
diff values-old.yaml values-new.yaml

# Тестовое обновление
helm upgrade --dry-run --debug myrelease new-chart
```

## 🔌 Разработка плагинов

### 🛠️ Создание плагина
```bash
# Структура плагина
mkdir -p helm-myplugin
cd helm-myplugin
cat <<EOF > plugin.yaml
name: "myplugin"
version: "0.1.0"
usage: "My custom plugin"
description: "This is my custom Helm plugin"
command: "$HELM_PLUGIN_DIR/myplugin.sh"
hooks:
  install: "cd $HELM_PLUGIN_DIR; scripts/install.sh"
EOF

# Создание скрипта плагина
cat <<EOF > myplugin.sh
#!/bin/bash
echo "Hello from my plugin!"
EOF
chmod +x myplugin.sh

# Установка плагина
helm plugin install ./helm-myplugin
```

### 🎮 Примеры плагинов
```bash
# Плагин для S3
helm plugin install https://github.com/hypnoglow/helm-s3.git
helm s3 init s3://my-bucket/charts

# Плагин для GCS
helm plugin install https://github.com/hayorov/helm-gcs.git
helm gcs init gs://my-bucket/charts

# Плагин для Azure
helm plugin install https://github.com/Azure/helm-azure-storage
helm azure init azure://my-container/charts
```

## 🔒 Продвинутая безопасность

### 🛡️ RBAC и PSP
```bash
# Создание ServiceAccount для Helm
kubectl create serviceaccount tiller
kubectl create clusterrolebinding tiller \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:tiller

# Установка с RBAC
helm install myrelease mychart \
  --set serviceAccount.create=true \
  --set serviceAccount.name=myapp

# Настройка Pod Security Policy
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: helm-psp
spec:
  privileged: false
  seLinux:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAsNonRoot
EOF
```

### 🔐 Шифрование секретов
```bash
# Установка plugin для секретов
helm plugin install https://github.com/jkroepke/helm-secrets

# Шифрование values
helm secrets enc secrets.yaml

# Установка с зашифрованными values
helm secrets install myrelease mychart -f secrets.yaml

# Просмотр расшифрованных values
helm secrets view secrets.yaml
```

## 📈 Мониторинг и метрики

### 📊 Prometheus и Grafana
```bash
# Установка стека мониторинга
helm repo add prometheus-community \
  https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Добавление аннотаций для сбора метрик
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "9090"

# Настройка алертов
helm upgrade prometheus prometheus-community/kube-prometheus-stack \
  --set alertmanager.config.global.slack_api_url=https://hooks.slack.com/services/XXX
```

### 📱 Визуализация
```bash
# Установка Grafana dashboards
helm install grafana grafana/grafana \
  --set dashboards.default=true

# Настройка Loki
helm install loki grafana/loki-stack \
  --set grafana.enabled=true

# Установка Jaeger
helm install jaeger jaegertracing/jaeger \
  --set provisionDataStore.cassandra=false
```

---

## 📚 Дополнительные ресурсы

### 📖 Документация
- [Helm Documentation](https://helm.sh/docs/)
- [Helm Hub](https://artifacthub.io/)
- [Helm GitHub](https://github.com/helm/helm)

### 🛠️ Инструменты
- [Helmfile](https://github.com/roboll/helmfile)
- [Helm Dashboard](https://github.com/komodorio/helm-dashboard)
- [Chart Testing](https://github.com/helm/chart-testing)

### 👥 Сообщество
- [Helm Slack](https://kubernetes.slack.com/messages/helm-users)
- [CNCF Slack](https://slack.cncf.io/)
- [Helm Twitter](https://twitter.com/helmpack)
