# Руководство по работе с Kubernetes

## Оглавление
1. [Введение в Kubernetes](#введение-в-kubernetes)
2. [Архитектура](#архитектура)
3. [Основные концепции](#основные-концепции)
4. [Лучшие практики](#лучшие-практики)
5. [Безопасность](#безопасность)
6. [Мониторинг и логирование](#мониторинг-и-логирование)
7. [Решение проблем](#решение-проблем)
8. [Продвинутые концепции](#продвинутые-концепции)
9. [Сетевые концепции](#сетевые-концепции)
10. [Хранилище](#хранилище)
11. [Безопасность](#безопасность-1)
12. [Мониторинг и логирование](#мониторинг-и-логирование-1)
13. [Оптимизация производительности](#оптимизация-производительности)
14. [Управление конфигурацией](#управление-конфигурацией)
15. [Продвинутая отладка](#продвинутая-отладка)
16. [Продвинутые паттерны развертывания](#продвинутые-паттерны-развертывания)

## Введение в Kubernetes

### Что такое Kubernetes?
Kubernetes (K8s) - это открытая платформа для автоматизации развертывания, масштабирования и управления контейнеризированными приложениями.

### Основные преимущества:
- Автоматическое масштабирование
- Самовосстановление
- Балансировка нагрузки
- Управление конфигурацией
- Автоматическое развертывание
- Управление хранилищем

## Архитектура

### Control Plane (Master Node)
1. **API Server**: 
   - Центральный компонент управления
   - Обрабатывает все API запросы
   - Валидирует и конфигурирует данные

2. **etcd**:
   - Распределенное хранилище
   - Хранит состояние кластера
   - Обеспечивает консистентность данных

3. **Scheduler**:
   - Распределяет поды по узлам
   - Учитывает ресурсы и ограничения
   - Принимает решения о размещении

4. **Controller Manager**:
   - Управляет контроллерами
   - Следит за состоянием кластера
   - Обеспечивает желаемое состояние

### Worker Nodes
1. **Kubelet**:
   - Управляет подами на узле
   - Обеспечивает работу контейнеров
   - Отчитывается о состоянии

2. **Container Runtime**:
   - Docker/containerd/CRI-O
   - Запускает контейнеры
   - Управляет контейнерами

3. **Kube-proxy**:
   - Сетевой прокси
   - Управляет сетевыми правилами
   - Обеспечивает сетевую связность

## Основные концепции

### Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
```

- Минимальная единица развертывания
- Может содержать один или несколько контейнеров
- Имеет общее сетевое пространство
- Временный (ephemeral) объект

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```

- Управляет ReplicaSet
- Обеспечивает декларативные обновления
- Поддерживает rollback
- Масштабирование

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

- Обеспечивает доступ к подам
- Балансировка нагрузки
- Типы: ClusterIP, NodePort, LoadBalancer

### ConfigMap и Secret
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "mongodb://localhost:27017"
  api_key: "development-key"
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  username: dXNlcm5hbWU=  # base64 encoded
  password: cGFzc3dvcmQ=  # base64 encoded
```

## Лучшие практики

### 1. Управление ресурсами
```yaml
spec:
  containers:
  - name: app
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### 2. Проверки работоспособности
```yaml
spec:
  containers:
  - name: app
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
```

### 3. Использование меток и селекторов
```yaml
metadata:
  labels:
    app: myapp
    environment: production
    version: v1.0.0
```

### 4. Стратегии обновления
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## Безопасность

### 1. RBAC (Role-Based Access Control)
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

### 2. Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 3. Pod Security Context
```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
```

## Мониторинг и логирование

### 1. Prometheus + Grafana
- Метрики кластера
- Метрики приложений
- Алертинг

### 2. EFK Stack
- Elasticsearch
- Fluentd/Fluent Bit
- Kibana

### 3. Важные метрики
- CPU/Memory utilization
- Pod status/health
- Network traffic
- Latency
- Error rates

## Решение проблем

### 1. Проблемы с подами
- Проверка логов
- Описание пода
- Проверка событий

### 2. Проблемы с узлами
- Проверка состояния узла
- Проверка ресурсов
- Проверка системных логов

### 3. Проблемы с сетью
- Проверка DNS
- Проверка сервисов
- Проверка сетевых политик

### 4. Проблемы с хранилищем
- Проверка PV/PVC
- Проверка StorageClass
- Проверка прав доступа

## Продвинутые концепции

### StatefulSet
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

### DaemonSet
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-elasticsearch
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: quay.io/fluentd_elasticsearch/fluentd:v2.5.2
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

### CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: hello
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: hello
            image: busybox
            args:
            - /bin/sh
            - -c
            - date; echo Hello from Kubernetes
          restartPolicy: OnFailure
```

## Сетевые концепции

### Ingress с множественными правилами
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multiple-hosts
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: foo.example.com
    http:
      paths:
      - path: /foo
        pathType: Prefix
        backend:
          service:
            name: foo-service
            port:
              number: 80
  - host: bar.example.com
    http:
      paths:
      - path: /bar
        pathType: Prefix
        backend:
          service:
            name: bar-service
            port:
              number: 80
```

### Network Policy с множественными правилами
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multi-client-server-netpol
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          project: myproject
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 5978
```

## Хранилище

### Persistent Volume с различными провайдерами
```yaml
# AWS EBS
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ebs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  awsElasticBlockStore:
    volumeID: vol-xxxxx
    fsType: ext4

---
# NFS
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: nfs-server.example.com
    path: "/path/to/share"

---
# Azure Disk
apiVersion: v1
kind: PersistentVolume
metadata:
  name: azure-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  azureDisk:
    diskName: myAKSDisk
    diskURI: /subscriptions/.../resourceGroups/.../providers/Microsoft.Compute/disks/myAKSDisk
```

### Storage Class с различными параметрами
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  iopsPerGB: "10"
  encrypted: "true"
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

## Безопасность

### Pod Security Policy
```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  seLinux:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAsNonRoot
  fsGroup:
    rule: RunAsAny
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
```

### Service Account с ограниченными правами
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: restricted-sa
  namespace: default

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: restricted-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## Мониторинг и логирование

### Prometheus ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
  labels:
    team: frontend
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: web
    interval: 15s
```

### Grafana Dashboard ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard
data:
  dashboard.json: |
    {
      "annotations": {
        "list": []
      },
      "editable": true,
      "fiscalYearStartMonth": 0,
      "graphTooltip": 0,
      "links": [],
      "liveNow": false,
      "panels": [],
      "refresh": "",
      "schemaVersion": 38,
      "style": "dark",
      "tags": [],
      "templating": {
        "list": []
      },
      "time": {
        "from": "now-6h",
        "to": "now"
      },
      "timepicker": {},
      "timezone": "",
      "title": "Kubernetes Cluster Monitoring",
      "version": 0,
      "weekStart": ""
    }
```

## Оптимизация производительности

### HorizontalPodAutoscaler с пользовательскими метриками
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  - type: Pods
    pods:
      metric:
        name: packets-per-second
      target:
        type: AverageValue
        averageValue: 1k
  - type: Object
    object:
      metric:
        name: requests-per-second
      describedObject:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: main-route
      target:
        type: Value
        value: 10k
```

### VerticalPodAutoscaler
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        memory: "100Mi"
        cpu: "100m"
      maxAllowed:
        memory: "3Gi"
        cpu: "3"
      controlledResources: ["cpu", "memory"]
```

## Управление конфигурацией

### ConfigMap с множественными источниками
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: game-config
data:
  # Файл свойств
  game.properties: |
    enemy.types=aliens,monsters
    player.maximum-lives=5
  
  # JSON конфигурация
  game-config.json: |
    {
      "enemies": {
        "aliens": {"hp": 150, "damage": 10},
        "monsters": {"hp": 200, "damage": 15}
      },
      "powerups": {
        "health": {"restore": 50},
        "ammo": {"count": 5}
      }
    }
  
  # Переменные окружения
  ui-env: |
    THEME=dark
    LANGUAGE=en
    DEBUG=false
```

### Secret с различными типами
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: multi-type-secret
type: Opaque
stringData:
  # Базовая аутентификация
  .htpasswd: |
    admin:$apr1$7YEth1Ki$VxnMFfnKLQVXpIzxvArYr0
  
  # SSL сертификат
  tls.crt: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
  tls.key: |
    -----BEGIN PRIVATE KEY-----
    ...
    -----END PRIVATE KEY-----
  
  # OAuth конфигурация
  oauth.json: |
    {
      "clientId": "xxx",
      "clientSecret": "xxx",
      "redirectUri": "https://app.example.com/callback"
    }
```

## Продвинутая отладка

### Debugging Pod
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: debugging-pod
spec:
  containers:
  - name: debug
    image: nicolaka/netshoot
    command:
      - sleep
      - "3600"
    securityContext:
      capabilities:
        add: ["NET_ADMIN", "SYS_ADMIN"]
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
```

## Продвинутые паттерны развертывания

### Blue-Green Deployment
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  labels:
    app: my-app
spec:
  selector:
    app: my-app
    version: v1  # Переключается между v1 и v2
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: v1
  template:
    metadata:
      labels:
        app: my-app
        version: v1
    spec:
      containers:
      - name: my-app
        image: my-app:v1

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: v2
  template:
    metadata:
      labels:
        app: my-app
        version: v2
    spec:
      containers:
      - name: my-app
        image: my-app:v2
```

### Canary Deployment с Istio
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-app-vsvc
spec:
  hosts:
  - my-app
  http:
  - route:
    - destination:
        host: my-app
        subset: v1
      weight: 90
    - destination:
        host: my-app
        subset: v2
      weight: 10

---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: my-app-destrule
spec:
  host: my-app
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
