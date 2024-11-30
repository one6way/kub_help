#!/bin/bash

# Set variables
SERVER="95.163.229.168"
USER="root"
PASSWORD="0TzqdpsLz1olIto7"

# Install sshpass if not installed
brew install sshpass

# Copy scripts to remote server
sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no -r ./scripts/* $USER@$SERVER:/root/

# Execute scripts on remote server
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $USER@$SERVER 'bash -s' << 'EOF'
cd /root
chmod +x *.sh
./init_server.sh
./install_kubernetes.sh
./install_kubesphere.sh
EOF
