#!/bin/bash
set -e

# Wraps the Python experiment controller
# Ensure you are connected to the K8s cluster (minikube)

echo "🧪 Starting Automated Experiments..."
echo "Target: Minikube Cluster"

# Install requirements if needed
# pip install -r ../backend/requirements.txt (Assume user has env)

# Check if Backend is accessible
if ! curl -s "http://localhost:8000/api/health" > /dev/null; then
    echo "❌ Error: Backend not accessible at http://localhost:8000"
    echo "⚠️  Please run: kubectl port-forward svc/backend 8000:8000 -n gitforge"
    exit 1
fi

# Run the controller
python3 scripts/experiment_controller.py

