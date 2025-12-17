#!/bin/bash

# Exit on error
set -e

echo "🔄 Rebuilding Backend in Minikube Environment..."

# 1. Point Docker to Minikube
eval $(minikube docker-env)

# 2. Rebuild the image
echo "🏗️  Building gitforge-backend image..."
docker build -t gitforge-backend:latest -f backend/Dockerfile backend/

# 3. Restart the pod to pick up the new image
echo "♻️  Restarting backend pod..."
kubectl rollout restart deployment/backend -n gitforge

# 4. Wait for it to be ready
echo "⏳ Waiting for rollout..."
kubectl rollout status deployment/backend -n gitforge

echo "✅ Backend updated successfully! 'rafael' should now be in the repository list."
