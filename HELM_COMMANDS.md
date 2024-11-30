# 🎯 Helm Commands Reference Guide

## 📋 Содержание
- [Управление репозиториями](#управление-репозиториями)
- [Операции с чартами](#операции-с-чартами)
- [Управление релизами](#управление-релизами)
- [Тестирование и отладка](#тестирование-и-отладка)
- [Управление плагинами](#управление-плагинами)
- [Продвинутые команды](#продвинутые-команды)
- [Управление зависимостями](#управление-зависимостями)
- [OCI Registry](#oci-registry)
- [Проверка безопасности](#проверка-безопасности)

## 📦 Управление репозиториями

### 🔄 Базовые операции с репозиториями
```bash
# Добавление репозитория
helm repo add bitnami https://charts.bitnami.com/bitnami

# Обновление репозиториев
helm repo update

# Список репозиториев
helm repo list

# Поиск чартов
helm search repo nginx

# Удаление репозитория
helm repo remove bitnami
```

### 🔍 Поиск и информация
```bash
# Поиск с описанием
helm search repo wordpress -l

# Поиск конкретной версии
helm search repo nginx --version 1.0.0

# Поиск в Artifact Hub
helm search hub wordpress
```

## 📊 Операции с чартами

### 🛠️ Создание и упаковка
```bash
# Создание нового чарта
helm create mychart

# Упаковка чарта
helm package mychart

# Проверка чарта
helm lint mychart

# Просмотр шаблонов
helm template mychart
```

### 📥 Установка и обновление
```bash
# Установка чарта
helm install myrelease mychart

# Установка с values файлом
helm install -f values.yaml myrelease mychart

# Установка с переопределением значений
helm install --set key=value myrelease mychart

# Обновление релиза
helm upgrade myrelease mychart
```

## 🔄 Управление релизами

### 📋 Информация о релизах
```bash
# Список релизов
helm list

# История релиза
helm history myrelease

# Статус релиза
helm status myrelease

# Получение values релиза
helm get values myrelease
```

### 🔧 Управление релизами
```bash
# Откат релиза
helm rollback myrelease 1

# Удаление релиза
helm uninstall myrelease

# Сохранение истории при удалении
helm uninstall --keep-history myrelease
```

## 🔍 Тестирование и отладка

### 🐛 Отладка чартов
```bash
# Проверка синтаксиса
helm lint mychart

# Просмотр сгенерированных манифестов
helm template mychart

# Тестирование установки
helm install --dry-run --debug myrelease mychart

# Проверка values
helm show values mychart
```

### 🧪 Тестирование релизов
```bash
# Запуск тестов
helm test myrelease

# Просмотр тестовых логов
helm test myrelease --logs

# Тестирование с таймаутом
helm test myrelease --timeout 5m
```

## 🔌 Управление плагинами

### 🛠️ Операции с плагинами
```bash
# Установка плагина
helm plugin install https://github.com/user/helm-plugin

# Список плагинов
helm plugin list

# Обновление плагина
helm plugin update plugin-name

# Удаление плагина
helm plugin uninstall plugin-name
```

## 🚀 Продвинутые команды

### 🔧 Продвинутая установка
```bash
# Установка с несколькими values файлами
helm install -f values1.yaml -f values2.yaml myrelease mychart

# Установка с wait
helm install --wait --timeout 5m myrelease mychart

# Установка с hooks
helm install --no-hooks myrelease mychart

# Установка с конкретной версией
helm install --version 1.2.3 myrelease mychart
```

### 📊 Продвинутое управление
```bash
# Получение всех ресурсов релиза
helm get all myrelease

# Получение манифестов
helm get manifest myrelease

# Получение notes
helm get notes myrelease

# Проверка обновления
helm upgrade --dry-run --debug myrelease mychart
```

## 📦 Управление зависимостями

### 🔄 Операции с зависимостями
```bash
# Обновление зависимостей
helm dependency update mychart

# Список зависимостей
helm dependency list mychart

# Сборка зависимостей
helm dependency build mychart

# Проверка зависимостей
helm dependency update --verify mychart
```

## 🏗️ OCI Registry

### 📤 Работа с OCI
```bash
# Логин в registry
helm registry login registry.example.com

# Загрузка чарта
helm push mychart-0.1.0.tgz oci://registry.example.com/charts

# Загрузка из registry
helm pull oci://registry.example.com/charts/mychart --version 0.1.0

# Выход из registry
helm registry logout registry.example.com
```

## 🔒 Проверка безопасности

### 🛡️ Безопасность чартов
```bash
# Проверка подписи
helm verify mychart-0.1.0.tgz

# Подписание чарта
helm package --sign mychart

# Проверка провенанса
helm verify --provenance mychart-0.1.0.tgz
```

## 📚 Дополнительные ресурсы

### 🔗 Полезные ссылки
- [Официальная документация Helm](https://helm.sh/docs/)
- [Helm Hub](https://hub.helm.sh/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

### 🛠️ Инструменты
- [Helm CLI](https://helm.sh/docs/intro/install/)
- [Helm Dashboard](https://github.com/komodorio/helm-dashboard)
- [Helmfile](https://github.com/roboll/helmfile)

## 🤝 Содействие
Если у вас есть предложения по улучшению этого руководства:
1. Создайте Issue
2. Предложите Pull Request
3. Поделитесь своим опытом

## 📝 Лицензия
MIT License - свободно используйте для ваших проектов.

---

🌟 Надеемся, это руководство поможет вам в работе с Helm!
