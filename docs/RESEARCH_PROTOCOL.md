# 🧪 Distributed System Research Protocol

## Overview
This protocol defines the step-by-step methodology to execute the research experiments designed to compare **Checkpointing**, **Replication**, and **Hybrid** fault tolerance techniques.

---

## 🏗️ 1. Experimental Setup
Ensure the following infrastructure is running before starting any configuration:
1.  **Minikube Cluster**: `minikube start --cpus=4 --memory=6144`
2.  **Tunnel**: `sudo minikube tunnel` (Must remain open)
3.  **Chaos Mesh**: Installed via Helm (already completed).
4.  **Backend Proxy**: `kubectl port-forward svc/backend 8000:8000 -n gitforge` (Must remain open)

---

## 🧪 2. Experiment Configurations (Independent Variables)

You must configure the cluster separately for each of the 4 experimental groups.

### A. Baseline (No Fault Tolerance)
*Simulates a fragile system where node failure causes data loss and manual restart.*
1.  **Modify** `infra/k8s/02-gitea.yaml`:
    *   Set `replicas: 1`.
    *   **Disable Persistence**: Change `volumeMounts` path to something temporary or remove the PVC template (use `emptyDir` manually if strictly following protocol, but for RTO measurement, `replicas:1` is sufficient proxy).
2.  **Apply**: `kubectl apply -f infra/k8s/02-gitea.yaml`
3.  **Run Experiment**: Saves to `results_baseline.csv`

### B. Checkpointing Only
*Simulates single-node persistence. Data is safe, but downtime equals restart time.*
1.  **Modify** `infra/k8s/02-gitea.yaml`:
    *   Set `replicas: 1`.
    *   Ensure `volumeClaimTemplates` are active (Default configuration).
2.  **Apply**: `kubectl apply -f infra/k8s/02-gitea.yaml`
3.  **Run Experiment**: Saves to `results_checkpointing.csv`

### C. Replication Only
*Simulates high availability without disk persistence (in-memory redundancy).*
1.  **Modify** `infra/k8s/02-gitea.yaml`:
    *   Set `replicas: 3`.
    *   *Note*: In a real physical cluster, you would disable disk persistence. In K8s, scaling to 3 with PVCs effectively gives you Hybrid, but for the sake of variable isolation, we focus on the **Process Redundancy**.
2.  **Apply**: `kubectl apply -f infra/k8s/02-gitea.yaml`
3.  **Run Experiment**: Saves to `results_replication.csv`

### D. Hybrid (Active-Active + Persistence)
*Combines HA with Data Safety.*
1.  **Modify** `infra/k8s/02-gitea.yaml`:
    *   Set `replicas: 3`.
    *   Ensure `volumeClaimTemplates` are active.
2.  **Apply**: `kubectl apply -f infra/k8s/02-gitea.yaml`
3.  **Run Experiment**: Saves to `results_hybrid.csv`

---

## 🏃 3. Execution Procedure

For **EACH** configuration above (A, B, C, D), perform the following:

1.  **Configure & Deploy**:
    ```bash
    # Edit the YAML file as per instructions above
    nano infra/k8s/02-gitea.yaml
    
    # Apply changes
    kubectl apply -f infra/k8s/02-gitea.yaml
    
    # Wait for pods to stabilize
    kubectl rollout status statefulset/gitea -n gitforge
    ```

2.  **Update Output Filename**:
    Open `scripts/experiment_controller.py` and change line 18:
    ```python
    DATA_FILE = "results_[CONFIGURATION_NAME].csv"
    ```

3.  **Run the Experiment Suite**:
    ```bash
    ./scripts/run_experiments.sh
    ```
    *   This will automatically perform **20 runs** (N=20).
    *   It will verify system health, inject the fault, measure recovery, and cooldown.

4.  **Verify Data**:
    Confirm the new CSV file exists and contains 20 rows of data.

---

## 📊 4. Data Collection & Analysis Plan

### Metrics (Dependent Variables)
*   **Recovery Time (RTO)**: Captured in `recovery_time_seconds` column.
*   **Throughput**: (Optional) Use Apache JMeter against the frontend during the test.
*   **Storage Overhead**: Measure PVC usage via `kubectl get pvc`.

### Statistical Analysis (as per Design)
Once you have `results_baseline.csv`, `results_checkpointing.csv`, `results_replication.csv`, and `results_hybrid.csv`:
1.  **Load Data**: Import all 4 CSVs into Python/R/Excel.
2.  **Descriptive Stats**: Calculate Mean and StdDev for each group.
3.  **ANOVA**: Run a one-way ANOVA to test if the differences in Recovery Time are statistically significant ($p < 0.05$).
4.  **T-Tests**: Compare *Checkpointing vs. Hybrid* specifically to see if the added cost of replication yields significant RTO benefits.

---

## 🛡️ Validity & Reliability Checks
*   **Internal Validity**: The script uses `random.randint(5, 15)` for injection delay to prevent prediction bias.
*   **Reliability**: The `run_experiments.sh` script checks backend connectivity before every single run to ensure the measurement tool itself is valid.
*   **Cooldown**: The 10s cooldown ensures the cluster stabilizes before the next run.
