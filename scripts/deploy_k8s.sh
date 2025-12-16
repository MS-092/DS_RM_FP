#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting GitForge Kubernetes Deployment..."

# Check if minikube is running
if ! minikube status | grep -q "Running"; then
    echo "❌ Minikube is not running. Please start it with 'minikube start'"
    exit 1
fi

echo "📦 Setting up Docker environment..."
eval $(minikube docker-env)

echo "🏗️ Building Backend Image..."
docker build -t gitforge-backend:latest "$PROJECT_ROOT/backend"

echo "🏗️ Building Frontend Image..."
docker build -t gitforge-frontend:latest "$PROJECT_ROOT/frontend"

echo "☸️ Applying Kubernetes Manifests..."
kubectl apply -f "$PROJECT_ROOT/infra/k8s/00-namespace.yaml"
kubectl apply -f "$PROJECT_ROOT/infra/k8s/01-cockroachdb.yaml"

echo "⏳ Waiting for CockroachDB to initialize..."
kubectl wait --for=condition=ready pod -l app=cockroachdb -n gitforge --timeout=120s || echo "⚠️  CockroachDB pods not ready yet, proceeding..."

# Initialize DB Job
# We apply the job now that pods are running (or trying to)
# Note: The job might fail if pods aren't up, but restartPolicy is OnFailure

# Re-applying ensures Job is picked up if I uncommented or split it, 
# (Wait, I put Job in same file. It's fine).

kubectl apply -f "$PROJECT_ROOT/infra/k8s/02-gitea.yaml"
kubectl apply -f "$PROJECT_ROOT/infra/k8s/03-backend.yaml"
kubectl apply -f "$PROJECT_ROOT/infra/k8s/04-frontend.yaml"
kubectl apply -f "$PROJECT_ROOT/infra/k8s/05-ingress.yaml"

echo "🔍 Waiting for Deployments to Rollout..."
kubectl rollout status statefulset/cockroachdb -n gitforge
kubectl rollout status statefulset/gitea -n gitforge
kubectl rollout status deployment/backend -n gitforge
kubectl rollout status deployment/frontend -n gitforge

echo "🎉 Deployment Complete!"
echo "Access the application via 'minikube service frontend -n gitforge' or configure ingress."
echo "If using Ingress addon: 'minikube tunnel'"
echo "Dashboard URL: http://localhost (via tunnel) or check 'minikube ip'"
