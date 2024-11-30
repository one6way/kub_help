#!/bin/bash

# Exit on any error
set -e

echo "Starting KubeSphere installation..."

# Remove any existing KubeSphere installations
kubectl delete --ignore-not-found=true -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/kubesphere-installer.yaml
kubectl delete --ignore-not-found=true -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/cluster-configuration.yaml

# Remove any existing webhook configurations that might conflict
kubectl delete validatingwebhookconfigurations.admissionregistration.k8s.io --ignore-not-found=true kubesphere-validating-webhook-configuration

# Wait for resources to be fully deleted
echo "Waiting for resources to be cleaned up..."
sleep 10

# Apply KubeSphere installer
echo "Applying KubeSphere installer..."
kubectl apply -f https://github.com/kubesphere/ks-installer/releases/download/v3.4.1/kubesphere-installer.yaml
kubectl apply -f cluster-config.yaml

# Wait for the installation to complete
echo "Waiting for KubeSphere to be ready..."
kubectl -n kubesphere-system wait --for=condition=complete job/ks-installer --timeout=1200s

echo "KubeSphere installation completed!"
echo "You can access the console at: http://${KUBESPHERE_IP:-<your-node-ip>}:${KUBESPHERE_PORT:-30880}"
echo "Default credentials:"
echo "Username: ${KUBESPHERE_ADMIN:-admin}"
echo "Password: ${KUBESPHERE_PASSWORD:-P@88w0rd}"
