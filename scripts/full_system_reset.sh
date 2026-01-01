#!/bin/bash

# ==========================================
# 🛑 GITFORGE FULL SYSTEM RESET & SETUP 🛑
# ==========================================
set -e # Exit on error

echo "🚀 Starting Full System Initialization..."

# 1. Minikube Setup
echo "----------------------------------------"
echo "📦 Step 1: Preparing Minikube Cluster"
echo "----------------------------------------"
minikube status > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   Minikube not running. Starting..."
    minikube start --cpus=4 --memory=6144
else
    echo "   Minikube is running. Refreshing context..."
    minikube update-context
fi

# 2. Docker Environment
echo "----------------------------------------"
echo "🐳 Step 2: pointing Docker to Minikube"
echo "----------------------------------------"
eval $(minikube docker-env)
echo "   Docker environment set."

# 3. Build Images (Force Clean Build of Latest Code)
echo "----------------------------------------"
echo "🏗️  Step 3: Building Docker Images"
echo "----------------------------------------"
echo "   Building Backend..."
docker build -t gitforge-backend:latest -f backend/Dockerfile backend/
echo "   Building Frontend..."
docker build -t gitforge-frontend:latest -f frontend/Dockerfile frontend/

# 4. Deploy Kubernetes
echo "----------------------------------------"
echo "☸️  Step 4: Deploying to Kubernetes"
echo "----------------------------------------"
# Delete old pods to force restart with new images
echo "   Cleaning old pods..."
kubectl delete deployment backend frontend -n gitforge --ignore-not-found=true

# Run the standard deploy script
./scripts/deploy_k8s.sh

echo "----------------------------------------"
echo "✅ SYSTEM READY!"
echo "----------------------------------------"
echo "Now, open 3 NEW terminals and run these commands to access the system:"
echo ""
echo "👉 Terminal 1 (Tunnel):      sudo minikube tunnel"
echo "👉 Terminal 2 (Backend):     kubectl port-forward svc/backend 8000:8000 -n gitforge"
echo "👉 Terminal 3 (Gitea):       kubectl port-forward svc/gitea-service 3000:3000 -n gitforge"
echo ""
echo "🌍 Access Frontend at: http://localhost"
