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

# Учетные данные KubeSphere (опционально)
export KUBESPHERE_ADMIN="admin"
export KUBESPHERE_PASSWORD="your_password"
```

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
