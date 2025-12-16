#!/bin/bash
set -e

# Wraps the Python experiment controller
# Ensure you are connected to the K8s cluster (minikube)

echo "🧪 Starting Automated Experiments..."
echo "Target: Minikube Cluster"

# Install requirements if needed
# pip install -r ../backend/requirements.txt (Assume user has env)

# Run the controller
python3 scripts/experiment_controller.py
