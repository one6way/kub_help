#!/bin/bash

# Exit on any error
set -e

echo "Installing Grafana..."

# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Create monitoring namespace if it doesn't exist
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Install Grafana with custom values
cat << 'EOF' | helm upgrade --install grafana grafana/grafana -n monitoring -f -
adminPassword: "${GRAFANA_ADMIN_PASSWORD:-admin}"
service:
  type: NodePort
  nodePort: ${GRAFANA_NODE_PORT:-30881}
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: ${PROMETHEUS_URL:-http://prometheus-operated.kubesphere-monitoring-system.svc:9090}
      access: proxy
      isDefault: true
dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
    - name: 'default'
      orgId: 1
      folder: ''
      type: file
      disableDeletion: false
      editable: true
      options:
        path: /var/lib/grafana/dashboards
dashboards:
  default:
    kubernetes-cluster:
      gnetId: 315
      revision: 3
      datasource: Prometheus
    kubernetes-pods:
      gnetId: 6417
      revision: 1
      datasource: Prometheus
    node-exporter:
      gnetId: 1860
      revision: 27
      datasource: Prometheus
EOF

echo "Waiting for Grafana pod to be ready..."
kubectl rollout status deployment/grafana -n monitoring

echo "Grafana installation completed!"
echo "You can access Grafana at: http://<your-node-ip>:${GRAFANA_NODE_PORT:-30881}"
echo "Default credentials:"
echo "Username: admin"
echo "Password: ${GRAFANA_ADMIN_PASSWORD:-admin}"
