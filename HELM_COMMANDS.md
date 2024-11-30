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

---

## 📝 Лицензия
MIT License - свободно используйте для ваших проектов.

---

🌟 Надеемся, это руководство поможет вам в работе с Helm!
