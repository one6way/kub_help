# 🎮 Kubernetes Commands Reference Guide

## 📋 Содержание
- [Управление узлами](#управление-узлами)
- [Сетевая диагностика](#сетевая-диагностика)
- [Логирование](#логирование)
- [Управление ресурсами](#управление-ресурсами)
- [Управление секретами](#управление-секретами)
- [Управление конфигурацией](#управление-конфигурацией)
- [RBAC](#rbac)
- [Продвинутая отладка](#продвинутая-отладка)
- [StatefulSet/DaemonSet](#statefulsetdaemonset)
- [Мониторинг](#мониторинг)
- [Ingress](#ingress)
- [Хранилище](#хранилище)

## 🖥️ Управление узлами

### 📊 Информация о узлах
```bash
# Просмотр всех узлов кластера
kubectl get nodes

# Подробная информация о узле
kubectl describe node <node-name>

# Получение метрик узла
kubectl top node

# Маркировка узла
kubectl label node <node-name> key=value

# Drain узла для обслуживания
kubectl drain <node-name> --ignore-daemonsets
```

### 🔄 Управление подами на узлах
```bash
# Получение всех подов на конкретном узле
kubectl get pods --field-selector spec.nodeName=<node-name>

# Cordoning узла (предотвращение размещения новых подов)
kubectl cordon <node-name>

# Uncordoning узла
kubectl uncordon <node-name>
```

## 🌐 Сетевая диагностика

### 🔍 Проверка сетевой связности
```bash
# DNS тестирование
kubectl run test-dns --image=busybox:1.28 --rm -it -- nslookup kubernetes.default

# Проверка сетевых политик
kubectl get networkpolicies --all-namespaces

# Просмотр сервисов
kubectl get services --all-namespaces
```

### 🔌 Отладка сетевых проблем
```bash
# Проверка endpoints
kubectl get endpoints <service-name>

# Проверка DNS
kubectl exec -it <pod-name> -- nslookup <service-name>

# Просмотр логов kube-proxy
kubectl logs -n kube-system -l k8s-app=kube-proxy
```

## 📝 Логирование

### 📊 Просмотр логов
```bash
# Получение логов пода
kubectl logs <pod-name>

# Логи с предыдущего запуска
kubectl logs <pod-name> --previous

# Логи конкретного контейнера в поде
kubectl logs <pod-name> -c <container-name>

# Следование за логами в реальном времени
kubectl logs -f <pod-name>
```

### 🔍 Расширенное логирование
```bash
# Логи с временными метками
kubectl logs <pod-name> --timestamps=true

# Логи за последние N часов
kubectl logs --since=3h <pod-name>

# Логи с метками
kubectl logs -l app=nginx
```

## 💾 Управление ресурсами

### 📊 Квоты и лимиты
```bash
# Просмотр ResourceQuotas
kubectl get resourcequotas

# Просмотр LimitRanges
kubectl get limitranges

# Создание ResourceQuota
kubectl create quota my-quota --hard=cpu=1,memory=1G,pods=2

# Описание квоты
kubectl describe resourcequota my-quota
```

### 🔄 Масштабирование
```bash
# Масштабирование deployment
kubectl scale deployment <name> --replicas=3

# Автомасштабирование
kubectl autoscale deployment <name> --min=2 --max=5 --cpu-percent=80

# Просмотр HPA
kubectl get hpa
```

## 🔐 Управление секретами

### 🔑 Работа с секретами
```bash
# Создание секрета
kubectl create secret generic my-secret --from-literal=key1=supersecret

# Просмотр секретов
kubectl get secrets

# Декодирование секрета
kubectl get secret my-secret -o jsonpath='{.data.key1}' | base64 --decode

# Обновление секрета
kubectl create secret generic my-secret --from-literal=key1=newsecret --dry-run=client -o yaml | kubectl apply -f -
```

## ⚙️ Управление конфигурацией

### 📝 ConfigMaps
```bash
# Создание ConfigMap
kubectl create configmap my-config --from-file=config.txt

# Просмотр ConfigMaps
kubectl get configmaps

# Редактирование ConfigMap
kubectl edit configmap my-config

# Просмотр данных ConfigMap
kubectl get configmap my-config -o yaml
```

### 🔄 Применение изменений
```bash
# Применение конфигурации
kubectl apply -f config.yaml

# Откат изменений
kubectl rollout undo deployment/my-app

# История изменений
kubectl rollout history deployment/my-app
```

## 🔒 RBAC

### 👥 Управление ролями
```bash
# Создание роли
kubectl create role pod-reader --verb=get,list,watch --resource=pods

# Создание привязки роли
kubectl create rolebinding pod-reader-binding --role=pod-reader --user=jane

# Просмотр ролей
kubectl get roles

# Просмотр привязок ролей
kubectl get rolebindings
```

### 🌍 ClusterRoles
```bash
# Создание ClusterRole
kubectl create clusterrole pod-reader --verb=get,list,watch --resource=pods

# Создание ClusterRoleBinding
kubectl create clusterrolebinding pod-reader-binding --clusterrole=pod-reader --user=jane

# Просмотр ClusterRoles
kubectl get clusterroles

# Просмотр ClusterRoleBindings
kubectl get clusterrolebindings
```

## 🔍 Продвинутая отладка

### 🐛 Отладка подов
```bash
# Запуск отладочного пода
kubectl run debug-pod --image=busybox --rm -it -- sh

# Копирование файлов из/в под
kubectl cp <pod-name>:/path/to/file ./local-file

# Просмотр событий
kubectl get events --sort-by=.metadata.creationTimestamp

# Описание пода
kubectl describe pod <pod-name>
```

### 🔬 Диагностика кластера
```bash
# Проверка компонентов кластера
kubectl get componentstatuses

# Проверка API endpoints
kubectl get --raw /api/v1/namespaces

# Проверка метрик
kubectl top pods --all-namespaces
```

## 📊 StatefulSet/DaemonSet

### 📈 StatefulSet операции
```bash
# Создание StatefulSet
kubectl create -f statefulset.yaml

# Масштабирование StatefulSet
kubectl scale statefulset <name> --replicas=5

# Обновление StatefulSet
kubectl rollout status statefulset/<name>

# Удаление StatefulSet (сохранение подов)
kubectl delete statefulset <name> --cascade=false
```

### 🔄 DaemonSet операции
```bash
# Создание DaemonSet
kubectl create -f daemonset.yaml

# Обновление DaemonSet
kubectl rollout status daemonset/<name>

# Просмотр DaemonSets
kubectl get daemonsets

# История изменений DaemonSet
kubectl rollout history daemonset/<name>
```

## 📈 Мониторинг

### 📊 Метрики
```bash
# Метрики подов
kubectl top pod

# Метрики узлов
kubectl top node

# Метрики по namespace
kubectl top pod --namespace=kube-system

# Сортировка по использованию CPU
kubectl top pod --sort-by=cpu
```

### 🔍 Prometheus запросы
```bash
# Получение метрик Prometheus
kubectl get --raw /metrics

# Проверка целей Prometheus
kubectl get servicemonitors --all-namespaces

# Проверка правил алертинга
kubectl get prometheusrules --all-namespaces
```

## 🌐 Ingress

### 🛣️ Управление Ingress
```bash
# Создание Ingress
kubectl create -f ingress.yaml

# Просмотр Ingress
kubectl get ingress

# Описание Ingress
kubectl describe ingress <name>

# Обновление Ingress
kubectl apply -f ingress.yaml
```

### 🔒 TLS настройка
```bash
# Создание TLS секрета
kubectl create secret tls tls-secret --key=path/to/key.key --cert=path/to/cert.crt

# Привязка TLS к Ingress
kubectl patch ingress <name> -p '{"spec":{"tls":[{"secretName":"tls-secret"}]}}'
```

## 💾 Хранилище

### 📁 PersistentVolumes
```bash
# Создание PV
kubectl create -f pv.yaml

# Просмотр PV
kubectl get pv

# Просмотр PVC
kubectl get pvc

# Описание PV
kubectl describe pv <pv-name>
```

### 🗄️ StorageClasses
```bash
# Создание StorageClass
kubectl create -f storageclass.yaml

# Просмотр StorageClasses
kubectl get storageclasses

# Установка класса по умолчанию
kubectl patch storageclass <name> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
```

## 📚 Дополнительные ресурсы

### 🔗 Полезные ссылки
- [Официальная документация Kubernetes](https://kubernetes.io/docs/)
- [Kubernetes Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

### 🛠️ Инструменты
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [kubectx/kubens](https://github.com/ahmetb/kubectx)
- [k9s](https://k9scli.io/)

## 🤝 Содействие
Если у вас есть предложения по улучшению этого руководства:
1. Создайте Issue
2. Предложите Pull Request
3. Поделитесь своим опытом

## 📝 Лицензия
MIT License - свободно используйте для ваших проектов.

---

🌟 Надеемся, это руководство поможет вам в работе с Kubernetes!
