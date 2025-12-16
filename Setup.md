# 🛠️ Complete Setup & Research Guide for GitForge Distribution System Project

This guide provides a comprehensive, step-by-step walkthrough of the entire project lifecycle, from initial setup to running distributed system experiments.

---

## 📋 1. Prerequisites

Before starting, ensure you have the following tools installed on your machine (macOS recommended):

1.  **Docker Desktop**: [Install Docker](https://www.docker.com/products/docker-desktop/)
    *   Ensure it is running.
2.  **Minikube** (Local Kubernetes Cluster):
    ```bash
    brew install minikube
    ```
3.  **Kubectl** (Kubernetes CLI):
    ```bash
    brew install kubectl
    ```
4.  **Python 3.10+**:
    ```bash
    brew install python
    ```

---

## 🚀 2. Infrastructure Deployment

We use **Minikube** to simulate a distributed environment on your local machine.

### Step 2.1: Start the Cluster
Open your terminal and start Minikube with enough resources:
```bash
minikube start --cpus=4 --memory=6144
```

### Step 2.2: Deploy the System
We have an automated script that builds the Docker images and applies all Kubernetes manifests.
Run this from the project root:
```bash
./scripts/deploy_k8s.sh
```
*   **What this does**: Builds Frontend/Backend images, deploys CockroachDB (Database), Gitea (Git Server), and the App/API.
*   **Duration**: It may take 2-5 minutes for the first run.
*   **Success Check**: The script will finish with "🎉 Deployment Complete!".

### Step 2.3: Enable External Access
Kubernetes runs in an isolated network. To access the LoadBalancer service from your browser, you must run a **Tunnel**.
**Open a NEW terminal window** and run:
```bash
sudo minikube tunnel
```
*   **Note**: It may ask for your sudo password. **Keep this terminal window open** while you use the app.

---

## ⚙️ 3. One-Time Configuration (Critical)

Minikube is ephemeral. If you restart the cluster or delete it, you **must re-do this step**.

### Step 3.1: Access Gitea Internally
Since Gitea is an internal service, we port-forward it temporarily.
Open a terminal and run:
```bash
kubectl port-forward svc/gitea-service 3000:3000 -n gitforge
```
*(If this command fails, ensure no other process is using port 3000)*

### Step 3.2: Register the Research User
1.  Open your browser to: **[http://localhost:3000](http://localhost:3000)** (Use Incognito to ensure clean state).
2.  Click **Register** in the top right.
3.  Fill in the details exactly:
    *   **Username**: `matthew` (Case Sensitive!)
    *   **Email**: `matthew@example.com`
    *   **Password**: `password123`
4.  Click **Register Account**.

### Step 3.3: Create a Repository
1.  Once logged in as `matthew`, click the **+** icon (top right) -> **New Repository**.
2.  **Repository Name**: `test-repo`
3.  **Visibility**: Ensure it is **Public** (Uncheck "Make repository private").
4.  Click **Create Repository**.

### Step 3.4: Finish Configuration
You can now close the terminal process from **Step 3.1** (Ctrl+C). The internal Backend can now talk to Gitea automatically properly.

---

## 🖥️ 4. Using the System

The Distributed GitForge System is now live!

*   **Main Dashboard**: [http://localhost](http://localhost)
    *   **System Status**: Check if API/Database shows "Green".
    *   **Repositories**: You should see `test-repo` listed here.

---

## 🧪 5. Running Research Experiments

The core of this project is measuring **Recovery Time Objective (RTO)** during node failures.

### Step 5.1: Prepare the Experiment Runner
The automated experiment script needs direct access to the Backend API to poll its health.
Open a terminal and run:
```bash
kubectl port-forward svc/backend 8000:8000 -n gitforge
```
*(Keep this terminal open)*

### Step 5.2: Execute the Experiment Suite
In your **main terminal**, run the automation script:
```bash
./scripts/run_experiments.sh
```

**What happens next?**
1.  **Baseline**: The script checks system health.
2.  **Fault Injection**: It instructs Chaos Mesh to **Kill a Gitea Pod** (simulation of a node crash).
3.  **Measurement**: It polls the API every 0.5s to see when the system recovers.
4.  **Logging**: It saves the exact recovery time (in seconds) to a CSV file.
5.  **Repeat**: It runs this cycle 20 times for statistical significance.

---

## 📊 6. Analyzing Results

After the experiments finish, you will find a `.csv` file in the project folder (e.g., `experiment_results_checkpointing_30s.csv`).

**Key Metrics:**
*   **Injection Delay**: How long the system ran before the crash.
*   **Recovery Time**: The crucial metric.
    *   **< 10s**: High Availability (Success).
    *   **> 60s**: Slow recovery (Needs optimization).

---

## 🧹 7. Cleanup & Troubleshooting

### Cleanup
When you are done researching:
*   **Stop**: `minikube stop` (Saves state)
*   **Delete**: `minikube delete` (Fresh start)

### Troubleshooting
For a detailed log of issues and fixes, see **[docs/TROUBLESHOOTING_LOG.md](docs/TROUBLESHOOTING_LOG.md)**.

**Common Issues:**
*   **"Offline" Dashboard**: Restart `sudo minikube tunnel`.
*   **Empty Repositories**: Re-do Section 3 (Cluster might have reset).

