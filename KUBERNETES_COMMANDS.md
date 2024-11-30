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
- [Продвинутые техники](#продвинутые-техники)
- [Производительность и диагностика](#производительность-и-диагностика)
- [Безопасность](#безопасность)
- [CI/CD и автоматизация](#cicd-и-автоматизация)
- [Управление хранилищем](#управление-хранилищем)
- [Service Mesh](#service-mesh)
- [Работа с контейнерами](#работа-с-контейнерами)
- [Поиск и устранение неисправностей](#поиск-и-устранение-неисправностей)
- [Мониторинг производительности](#мониторинг-производительности)
- [Безопасность кластера](#безопасность-кластера)
- [Управление состоянием](#управление-состоянием)
- [Оптимизация производительности](#оптимизация-производительности)
- [Тестирование и качество](#тестирование-и-качество)
- [Расширенное управление](#расширенное-управление)
- [Анализ и отчетность](#анализ-и-отчетность)

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

## 🎯 Продвинутые техники

### 🔍 Отладка подов
```bash
# Запуск временного пода для отладки
kubectl run debug-pod --image=busybox --rm -it -- sh

# Копирование файлов из/в под
kubectl cp <pod-name>:/path/to/file /local/path
kubectl cp /local/path <pod-name>:/path/in/pod

# Проброс портов
kubectl port-forward <pod-name> 8080:80

# Получение спецификации запущенного пода
kubectl get pod <pod-name> -o yaml > pod-spec.yaml
```

### 🔧 Управление контекстами
```bash
# Просмотр всех контекстов
kubectl config get-contexts

# Переключение контекста
kubectl config use-context <context-name>

# Установка namespace для контекста
kubectl config set-context --current --namespace=<namespace>

# Просмотр текущего контекста
kubectl config current-context
```

### 🛠️ Работа с манифестами
```bash
# Валидация манифеста
kubectl apply --validate=true --dry-run=client -f manifest.yaml

# Просмотр различий перед применением
kubectl diff -f manifest.yaml

# Применение манифеста с записью причины изменения
kubectl apply -f manifest.yaml --record

# Создание манифеста из запущенного ресурса
kubectl get deployment <name> -o yaml > deployment.yaml
```

## 📊 Производительность и диагностика

### 🔍 Метрики и мониторинг
```bash
# Метрики подов
kubectl top pods --all-namespaces --sort-by=cpu
kubectl top pods --all-namespaces --sort-by=memory

# Метрики узлов с сортировкой
kubectl top nodes --sort-by=cpu
kubectl top nodes --sort-by=memory

# Просмотр использования ресурсов в реальном времени
kubectl top pods --watch

# Подробная информация о потреблении ресурсов
kubectl describe pod <pod-name> | grep -A 5 "Resources"
```

### 🔧 Диагностика кластера
```bash
# Проверка состояния компонентов кластера
kubectl get componentstatuses

# Проверка состояния API сервера
kubectl get --raw /healthz
kubectl get --raw /readyz
kubectl get --raw /livez

# Проверка метрик API сервера
kubectl get --raw /metrics

# Диагностика DNS
kubectl run dnsutils --image=tutum/dnsutils --command -- sleep infinity
kubectl exec -it dnsutils -- dig kubernetes.default.svc.cluster.local
```

### 📈 Аудит и события
```bash
# Просмотр событий с сортировкой по времени
kubectl get events --sort-by='.metadata.creationTimestamp'

# События определенного пода
kubectl get events --field-selector involvedObject.name=<pod-name>

# События с фильтрацией по типу
kubectl get events --field-selector type=Warning

# Экспорт событий в файл
kubectl get events -A -o yaml > cluster-events.yaml
```

## 🔒 Безопасность

### 🛡️ Pod Security Policies
```bash
# Просмотр Pod Security Policies
kubectl get psp

# Создание PSP
kubectl create psp restricted --dry-run=client -o yaml > psp.yaml

# Проверка применения PSP
kubectl auth can-i use podsecuritypolicy/restricted

# Привязка PSP к сервисному аккаунту
kubectl create rolebinding psp:sa:restricted --role=psp:restricted --serviceaccount=<namespace>:<serviceaccount>
```

### 🔐 Управление сертификатами
```bash
# Просмотр сертификатов
kubectl get csr

# Одобрение сертификата
kubectl certificate approve <csr-name>

# Отклонение сертификата
kubectl certificate deny <csr-name>

# Создание нового сертификата
kubectl create csr <name> --from-file=<name>.csr
```

### 🔑 Secrets Management
```bash
# Создание TLS секрета
kubectl create secret tls my-tls --cert=path/to/cert --key=path/to/key

# Создание docker-registry секрета
kubectl create secret docker-registry regcred \
  --docker-server=<registry-server> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email>

# Создание секрета из файлов
kubectl create secret generic my-secret \
  --from-file=ssh-privatekey=~/.ssh/id_rsa \
  --from-file=ssh-publickey=~/.ssh/id_rsa.pub

# Обновление секрета
kubectl create secret generic my-secret \
  --from-file=./username.txt \
  --from-file=./password.txt \
  --dry-run=client -o yaml | kubectl apply -f -
```

## 🔄 CI/CD и автоматизация

### 📦 Работа с образами
```bash
# Обновление образа
kubectl set image deployment/<name> container=new-image:tag

# Проверка истории обновлений
kubectl rollout history deployment/<name>

# Откат к предыдущей версии
kubectl rollout undo deployment/<name>

# Откат к конкретной версии
kubectl rollout undo deployment/<name> --to-revision=2
```

### 🚀 Канареечные развертывания
```bash
# Создание канареечного деплоймента
kubectl create deployment canary --image=app:v2 --replicas=1

# Создание сервиса с селектором версии
kubectl create service clusterip canary --tcp=80:8080

# Обновление меток для маршрутизации
kubectl label pods -l app=myapp version=v1
kubectl label pods -l app=myapp version=v2

# Масштабирование канареечного деплоймента
kubectl scale deployment canary --replicas=3
```

### 📊 Мониторинг развертывания
```bash
# Просмотр статуса развертывания
kubectl rollout status deployment/<name>

# Пауза развертывания
kubectl rollout pause deployment/<name>

# Возобновление развертывания
kubectl rollout resume deployment/<name>

# Проверка доступности приложения
kubectl run -it --rm test-api --image=busybox -- wget -qO- http://my-service
```

## 🗄️ Управление хранилищем

### 💾 Persistent Volumes
```bash
# Создание PV
kubectl create -f pv.yaml

# Просмотр PV с сортировкой по размеру
kubectl get pv --sort-by=.spec.capacity.storage

# Просмотр PVC
kubectl get pvc --all-namespaces

# Удаление PV с сохранением данных
kubectl patch pv <pv-name> -p '{"metadata":{"finalizers":null}}'
```

### 📁 Storage Classes
```bash
# Просмотр storage classes
kubectl get storageclass

# Создание storage class
kubectl create -f storageclass.yaml

# Установка класса по умолчанию
kubectl patch storageclass <name> -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# Просмотр использования storage class
kubectl get pv -o custom-columns=NAME:.metadata.name,STORAGECLASS:.spec.storageClassName
```

## 🌐 Service Mesh

### 🔄 Istio
```bash
# Проверка инъекции sidecar
kubectl get namespace -L istio-injection

# Включение инъекции sidecar для namespace
kubectl label namespace <namespace> istio-injection=enabled

# Проверка Istio конфигурации
kubectl get virtualservices,destinationrules,gateways -A

# Просмотр метрик Istio
kubectl -n istio-system port-forward svc/prometheus 9090:9090
```

### 🔍 Service Discovery
```bash
# Просмотр endpoints
kubectl get endpoints

# Проверка DNS
kubectl run -it --rm debug --image=busybox -- nslookup kubernetes.default

# Просмотр сервисов с селекторами
kubectl get svc -o custom-columns=NAME:.metadata.name,SELECTOR:.spec.selector

# Проверка сервисных аккаунтов
kubectl get serviceaccounts
```

## 🐳 Работа с контейнерами

### 📊 Управление ресурсами контейнера
```bash
# Просмотр использования ресурсов
kubectl top pod <pod-name> --containers

# Изменение ресурсов контейнера
kubectl set resources deployment <name> -c=<container> --limits=cpu=200m,memory=512Mi

# Просмотр лимитов контейнера
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'

# Проверка QoS класса пода
kubectl get pod <pod-name> -o jsonpath='{.status.qosClass}'
```

### 🔍 Отладка контейнеров
```bash
# Запуск команды в контейнере
kubectl exec -it <pod-name> -c <container-name> -- /bin/sh

# Просмотр переменных окружения
kubectl exec <pod-name> -c <container-name> -- printenv

# Проверка файловой системы
kubectl exec <pod-name> -c <container-name> -- ls -la /

# Копирование файлов
kubectl cp <pod-name>:/path/file ./local/path -c <container-name>
```

## 🔍 Поиск и устранение неисправностей

### 📝 Сбор информации
```bash
# Создание дампа состояния кластера
kubectl cluster-info dump > cluster-dump.txt

# Проверка журналов системных компонентов
kubectl logs -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l component=kube-apiserver

# Проверка состояния узлов
kubectl describe nodes | grep -A 5 "Conditions"

# Поиск проблемных подов
kubectl get pods --all-namespaces -o wide | grep -v Running
```

### 🛠️ Инструменты отладки
```bash
# Запуск отладочного пода
kubectl run debug --image=nicolaka/netshoot -it --rm -- /bin/bash

# Проверка сетевой связности
kubectl run test-connectivity --image=busybox --rm -it -- wget -qO- http://service-name

# Проверка DNS
kubectl run test-dns --image=busybox --rm -it -- nslookup kubernetes.default

# Анализ сетевых политик
kubectl run test-netpol --image=busybox --rm -it -- nc -zv service-name 80
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

## 🌡️ Мониторинг производительности

### 📊 Prometheus и Grafana
```bash
# Установка Prometheus оператора
kubectl create namespace monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Проверка метрик Prometheus
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# Откройте http://localhost:9090 в браузере

# Доступ к Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Откройте http://localhost:3000 в браузере
```

### 📈 Метрики приложений
```bash
# Просмотр метрик HPA
kubectl get hpa -w

# Мониторинг использования ресурсов пода
kubectl top pod <pod-name> --containers

# Экспорт метрик в формате Prometheus
kubectl get --raw /metrics

# Просмотр метрик узла
kubectl top node --sort-by=cpu
```

## 🔐 Безопасность кластера

### 🛡️ Network Policies
```bash
# Создание базовой Network Policy
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF

# Проверка Network Policies
kubectl get networkpolicies --all-namespaces

# Анализ правил Network Policy
kubectl describe networkpolicy <policy-name>

# Удаление Network Policy
kubectl delete networkpolicy <policy-name>
```

### 🔒 RBAC расширенные настройки
```bash
# Создание сервисного аккаунта с ограниченными правами
kubectl create serviceaccount restricted-user
kubectl create role pod-reader --verb=get,list,watch --resource=pods
kubectl create rolebinding restricted-user-binding --role=pod-reader --serviceaccount=default:restricted-user

# Проверка прав
kubectl auth can-i --as=system:serviceaccount:default:restricted-user get pods
kubectl auth can-i --as=system:serviceaccount:default:restricted-user delete pods

# Аудит RBAC
kubectl get clusterroles,clusterrolebindings --all-namespaces -o wide
```

## 🔄 Управление состоянием

### 💾 Резервное копирование
```bash
# Резервное копирование всех ресурсов
kubectl get all --all-namespaces -o yaml > cluster-backup.yaml

# Резервное копирование секретов
kubectl get secrets --all-namespaces -o yaml > secrets-backup.yaml

# Резервное копирование ConfigMaps
kubectl get configmaps --all-namespaces -o yaml > configmaps-backup.yaml

# Резервное копирование PV и PVC
kubectl get pv,pvc --all-namespaces -o yaml > storage-backup.yaml
```

### 🔄 Миграция ресурсов
```bash
# Экспорт ресурсов из namespace
kubectl get all -n source-namespace -o yaml > namespace-export.yaml

# Изменение namespace в экспортированном файле
sed -i 's/source-namespace/target-namespace/g' namespace-export.yaml

# Применение ресурсов в новом namespace
kubectl apply -f namespace-export.yaml -n target-namespace
```

## 🎯 Оптимизация производительности

### 🚀 Оптимизация ресурсов
```bash
# Анализ использования ресурсов
kubectl describe nodes | grep -A 5 "Allocated resources"

# Поиск подов с высоким потреблением CPU
kubectl top pods --all-namespaces --sort-by=cpu | head -10

# Поиск подов с высоким потреблением памяти
kubectl top pods --all-namespaces --sort-by=memory | head -10

# Анализ QoS классов
kubectl get pods -o custom-columns=NAME:.metadata.name,QOS:.status.qosClass
```

### ⚡ Оптимизация сети
```bash
# Анализ сетевых эндпоинтов
kubectl get endpoints --all-namespaces

# Проверка DNS производительности
kubectl run dns-test --image=busybox:1.28 --rm -it -- sh -c 'time nslookup kubernetes.default.svc.cluster.local'

# Анализ сервисов и их эндпоинтов
kubectl get svc --all-namespaces -o custom-columns=NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,EXTERNAL-IP:.status.loadBalancer.ingress[0].ip
```

## 🔍 Тестирование и качество

### 🔍 Тестирование кластера
```bash
# Проверка компонентов кластера
kubectl get componentstatuses

# Тестирование DNS
kubectl run -it --rm --restart=Never dns-test --image=busybox:1.28 -- nslookup kubernetes.default

# Тестирование сетевой связности
kubectl run -it --rm --restart=Never net-test --image=busybox:1.28 -- wget -qO- http://kubernetes.default.svc.cluster.local

# Проверка API сервера
kubectl get --raw /healthz
```

### 📋 Проверка конфигурации
```bash
# Валидация YAML файлов
kubectl apply --validate=true --dry-run=client -f manifest.yaml

# Проверка синтаксиса манифестов
kubectl create --dry-run=client -f deployment.yaml -o yaml

# Анализ различий перед применением
kubectl diff -f manifest.yaml

# Проверка статуса развертывания
kubectl rollout status deployment/<deployment-name>
```

## 🎛️ Расширенное управление

### 🔧 Custom Resources
```bash
# Создание Custom Resource Definition
kubectl create -f custom-resource.yaml

# Просмотр Custom Resources
kubectl get crd

# Просмотр экземпляров Custom Resource
kubectl get <custom-resource-name>

# Описание Custom Resource
kubectl describe crd <crd-name>
```

### 🎮 Kubectl плагины
```bash
# Установка kubectl-krew (менеджер плагинов)
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

# Установка полезных плагинов
kubectl krew install ctx
kubectl krew install ns
kubectl krew install neat
kubectl krew install tree

# Использование плагинов
kubectl ctx  # переключение контекста
kubectl ns   # переключение namespace
```

## 📊 Анализ и отчетность

### 📈 Сбор метрик
```bash
# Экспорт метрик в JSON
kubectl top pods --all-namespaces -o json > pods-metrics.json

# Анализ использования ресурсов по namespace
kubectl describe resourcequota --all-namespaces

# Создание отчета по подам
kubectl get pods --all-namespaces -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName > pods-report.txt

# Анализ событий кластера
kubectl get events --sort-by='.metadata.creationTimestamp' > cluster-events.txt
```

### 📋 Аудит конфигурации
```bash
# Проверка конфигурации безопасности
kubectl auth can-i --list

# Анализ сетевых политик
kubectl get networkpolicies --all-namespaces -o yaml > network-policies.yaml

# Проверка конфигурации хранилища
kubectl get sc,pv,pvc --all-namespaces -o yaml > storage-config.yaml

# Экспорт конфигурации RBAC
kubectl get clusterroles,clusterrolebindings -o yaml > rbac-config.yaml
