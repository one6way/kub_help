# 🚢 Kubernetes & KubeSphere Deployment Guide

## 📋 Содержание
- [Введение](#введение)
- [Документация](#документация)
- [Начало работы](#начало-работы)
- [Структура проекта](#структура-проекта)
- [Дополнительные ресурсы](#дополнительные-ресурсы)
- [Автоматизированная установка](#автоматизированная-установка)

## 🎯 Введение
Добро пожаловать в руководство по развертыванию Kubernetes и KubeSphere! Этот репозиторий содержит подробную документацию и примеры для эффективной работы с Kubernetes и Helm.

## 📚 Документация

### 🔷 Kubernetes
- [**Kubernetes Commands Guide**](./KUBERNETES_COMMANDS.md)
  - Подробное руководство по командам Kubernetes
  - Примеры использования и лучшие практики
  - Решения типичных проблем

### 🔶 Helm
- [**Helm Commands Guide**](./HELM_COMMANDS.md)
  - Полный справочник по командам Helm
  - Управление чартами и релизами
  - Работа с репозиториями

### 📊 Конфигурации
- [**Helm Configuration Guide**](./HELM_GUIDE.md)
  - Примеры values.yaml для разных сценариев
  - Шаблоны конфигураций
  - Лучшие практики

## 🚀 Начало работы

### 📋 Предварительные требования
1. Установленный Kubernetes кластер
2. Helm 3.x
3. kubectl CLI
4. KubeSphere (опционально)

### ⚡ Быстрый старт
```bash
# Клонирование репозитория
git clone https://github.com/yourusername/k8s-kubesphere-deployment.git
cd k8s-kubesphere-deployment

# Проверка доступа к кластеру
kubectl cluster-info

# Проверка версии Helm
helm version
```

## 🚀 Быстрый старт

### 📋 Предварительные требования

- Linux/Unix-совместимая операционная система
- Docker 20.10.x или выше
- Минимум 2 CPU и 4GB RAM для узла
- Доступ к интернету для загрузки образов
- Sudo/root права для установки компонентов

### 🛠 Варианты установки

1. **Автоматическая установка на удаленный сервер**
   ```bash
   # 1. Установите переменные окружения
   export SERVER_IP="your_server_ip"
   export SERVER_USER="your_username"
   export SERVER_PASSWORD="your_password"
   
   # 2. Запустите скрипт развертывания
   ./scripts/deploy.sh
   ```

2. **Установка на локальный кластер**
   ```bash
   # 1. Инициализация сервера
   ./scripts/init_server.sh
   
   # 2. Установка Kubernetes
   ./scripts/install_kubernetes.sh
   
   # 3. Установка KubeSphere
   ./scripts/install_kubesphere.sh
   ```

3. **Установка дополнительных компонентов**
   ```bash
   # Установка Grafana
   ./install-grafana.sh
   
   # Установка KubeSphere с кастомными настройками
   export KUBESPHERE_ADMIN="custom_admin"
   export KUBESPHERE_PASSWORD="custom_password"
   ./install-kubesphere.sh
   ```

### 🔍 Проверка установки

1. **Проверка Kubernetes:**
   ```bash
   kubectl get nodes
   kubectl get pods --all-namespaces
   ```

2. **Проверка KubeSphere:**
   ```bash
   kubectl get pods -n kubesphere-system
   kubectl get svc/ks-console -n kubesphere-system
   ```

3. **Проверка Grafana:**
   ```bash
   kubectl get pods -n monitoring
   kubectl get svc/grafana -n monitoring
   ```

### ⚠️ Возможные проблемы

1. **Ошибка подключения к серверу**
   - Проверьте доступность сервера: `ping $SERVER_IP`
   - Проверьте SSH доступ: `ssh $SERVER_USER@$SERVER_IP`
   - Убедитесь, что порты 22, 6443, 30880, 30881 открыты

2. **Ошибки установки Kubernetes**
   - Проверьте системные требования
   - Убедитесь, что swap отключен: `free -h`
   - Проверьте логи: `journalctl -xeu kubelet`

3. **Проблемы с KubeSphere**
   - Проверьте статус установки: `kubectl logs -n kubesphere-system $(kubectl get pod -n kubesphere-system -l app=ks-install -o jsonpath='{.items[0].metadata.name}') -f`
   - Убедитесь, что все зависимости установлены

### 🔄 Обновление компонентов

1. **Обновление Kubernetes:**
   ```bash
   apt update
   apt-get install -y kubelet kubeadm kubectl
   kubeadm upgrade plan
   kubeadm upgrade apply
   ```

2. **Обновление KubeSphere:**
   ```bash
   kubectl apply -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/kubesphere-installer.yaml
   kubectl apply -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/cluster-configuration.yaml
   ```

3. **Обновление Grafana:**
   ```bash
   helm repo update
   helm upgrade grafana grafana/grafana -n monitoring
   ```

### 🧹 Очистка

Если вам нужно удалить установленные компоненты:

```bash
# Удаление Grafana
helm uninstall grafana -n monitoring
kubectl delete namespace monitoring

# Удаление KubeSphere
kubectl delete -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/kubesphere-installer.yaml
kubectl delete -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/cluster-configuration.yaml

# Удаление Kubernetes
kubeadm reset
apt-get purge -y kubeadm kubectl kubelet kubernetes-cni
apt-get autoremove -y
rm -rf ~/.kube
```

## 📁 Структура проекта
```
k8s-kubesphere-deployment/
├── README.md                  # Основная документация
├── KUBERNETES_COMMANDS.md     # Руководство по командам Kubernetes
├── HELM_COMMANDS.md          # Руководство по командам Helm
├── HELM_GUIDE.md            # Руководство по конфигурации Helm
└── examples/                # Примеры конфигураций
    ├── basic/              # Базовые примеры
    ├── advanced/          # Продвинутые конфигурации
    └── production/       # Примеры для production
```

## 🚀 Автоматизированная установка

В репозитории есть набор скриптов для автоматической установки Kubernetes и KubeSphere:

### 📁 Структура скриптов

- `scripts/deploy.sh` - Основной скрипт развертывания
- `scripts/init_server.sh` - Инициализация сервера (установка Docker и базовых компонентов)
- `scripts/install_kubernetes.sh` - Установка и настройка Kubernetes
- `scripts/install_kubesphere.sh` - Установка KubeSphere

### 🔐 Переменные окружения

Для работы скриптов необходимо установить следующие переменные окружения:

```bash
# Данные для подключения к серверу
export SERVER_IP="your_server_ip"
export SERVER_USER="your_username"
export SERVER_PASSWORD="your_password"

# Учетные данные KubeSphere
export KUBESPHERE_IP="your_node_ip"           # IP-адрес узла для доступа к консоли
export KUBESPHERE_PORT="30880"                # Порт консоли (по умолчанию: 30880)
export KUBESPHERE_ADMIN="admin"               # Имя администратора (по умолчанию: admin)
export KUBESPHERE_PASSWORD="your_password"    # Пароль администратора

# Настройки Grafana
export GRAFANA_NODE_PORT="30881"              # Порт для доступа к Grafana (по умолчанию: 30881)
export GRAFANA_ADMIN_PASSWORD="your_password"  # Пароль администратора Grafana
export PROMETHEUS_URL="http://prometheus-operated.kubesphere-monitoring-system.svc:9090"  # URL Prometheus
```

> **Примечание**: Все переменные имеют значения по умолчанию. Установка переменных необходима только если вы хотите использовать другие значения.

### 📥 Использование

1. Клонируйте репозиторий:
```bash
git clone https://github.com/one6way/kub_help.git
cd kub_help
```

2. Установите переменные окружения (см. выше)

3. Запустите скрипт развертывания:
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 🔧 Дополнительные ресурсы

### 🔗 Полезные ссылки
- [Официальная документация Kubernetes](https://kubernetes.io/docs/)
- [Официальная документация Helm](https://helm.sh/docs/)
- [KubeSphere Documentation](https://kubesphere.io/docs/)

### 📚 Рекомендуемая литература
- Kubernetes: Up and Running
- Helm: The Kubernetes Package Manager
- Cloud Native DevOps with Kubernetes

### 🛠️ Инструменты
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [KubeSphere](https://kubesphere.io/docs/quick-start/all-in-one-on-linux/)

## 🤝 Содействие
Мы приветствуем ваш вклад в развитие проекта! Вот как вы можете помочь:
1. Fork репозитория
2. Создайте ветку для ваших изменений
3. Отправьте Pull Request

## 📝 Лицензия
MIT License - используйте код свободно для ваших проектов.

## 📮 Контакты
- GitHub Issues: Создайте issue в этом репозитории

---

🌟 Надеемся, эта документация поможет вам в работе с Kubernetes и Helm!
