#!/bin/bash

# Exit on error
set -e

echo "🔄 Rebuilding Frontend in Minikube Environment..."

# 1. Point Docker to Minikube
eval $(minikube docker-env)

# 2. Rebuild the image
echo "🏗️  Building gitforge-frontend image..."
docker build -t gitforge-frontend:latest -f frontend/Dockerfile frontend/

# 3. Restart the pod to pick up the new image
echo "♻️  Restarting frontend pod..."
kubectl rollout restart deployment/frontend -n gitforge

# 4. Wait for it to be ready
echo "⏳ Waiting for rollout..."
kubectl rollout status deployment/frontend -n gitforge

echo "Frontend updated"