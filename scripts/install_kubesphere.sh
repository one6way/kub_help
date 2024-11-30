#!/bin/bash

# Download KubeSphere installer
wget https://github.com/kubesphere/ks-installer/releases/download/v3.3.0/kubesphere-installer.yaml
wget https://github.com/kubesphere/ks-installer/releases/download/v3.3.0/cluster-configuration.yaml

# Install KubeSphere
kubectl apply -f kubesphere-installer.yaml
kubectl apply -f cluster-configuration.yaml

# Wait for KubeSphere to be ready
echo "Waiting for KubeSphere to be ready..."
kubectl -n kubesphere-system wait --for=condition=complete job/ks-installer --timeout=1800s

# Get KubeSphere console URL and credentials
echo "KubeSphere installation completed!"
echo "Console URL: http://$(kubectl get svc/ks-console -n kubesphere-system -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):30880"
echo "Default account: admin"
echo "Default password: P@88w0rd"
