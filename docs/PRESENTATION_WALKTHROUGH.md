# 🎓 GitForge Presentation Script (Step-by-Step)

This is your strictly defined script for the presentation. Follow it exactly.

---

## 🛑 Phase 0: Emergency Preparation (DO THIS NOW)
**Goal:** Ensure your latest code changes are running and the cluster is healthy.

1.  **Check Cluster Status**:
    ```bash
    minikube status
    # If "Stopped" or "Misconfigured":
    minikube update-context
    minikube start
    ```

2.  **Force Update Application** (Only if you suspect code is stale):
    ```bash
    ./scripts/update_backend.sh
    ./scripts/update_frontend.sh
    ```

---

## ⚡ Phase 1: Pre-Demo Setup (5 Mins Before)
**Goal:** Open the necessary network tunnels. **You must restart these if Minikube restarts.**

**Terminal 1: The Tunnel (Root Access)**
```bash
sudo minikube tunnel
# Enter password. Keep this running.
```

**Terminal 2: Backend Access** (Required for API calls)
```bash
kubectl port-forward svc/backend 8000:8000 -n gitforge
# Keep running.
```

**Terminal 3: Gitea Access** (Required for Repositories)
```bash
kubectl port-forward svc/gitea-service 3000:3000 -n gitforge
# Keep running.
```

**Terminal 4: Frontend Access** (Your View)
```bash
minikube service frontend -n gitforge
# Creates a direct tunnel to the web interface. Click the URL it generates.
```

---

## 🎬 Phase 2: The Live Presentation (The Script)

### Step 1: Introduction & Architecture
*"Good morning. I am presenting GitForge, a Distributed Repository Management System designed for high fault tolerance."*

*(Show the Architecture Diagram if you have one, or just the code)*

*"Unlike standard GitHub or Gitea, we have **decoupled** the components. Our React Frontend, FastAPI Backend, and CockroachDB Storage run as independent microservices."*

### Step 2: System Demo (The "Wow" Factor)

**1. Landing Page**
*   **Action**: Open the Frontend URL from Terminal 4.
*   **Say**: "This is the research platform dashboard. It monitors the health of our distributed nodes."
*   **Action**: Click on **"System Status"**. Show the green health cards.

**2. Repository Management**
*   **Action**: Click **"Repositories"**.
*   **Observation**: You should see repos for `matthew`, `AdrielMS`, and `rafael` (if you ran the backend update).
*   **Say**: "Here we aggregate repositories from our distributed Gitea cluster."

**3. The 'Resilient' Issue Tracker**
*   **Action**: Click **"Issues"** -> **"New Issue"**.
*   **Action**: Fill in the form:
    *   **Title**: "Demonstrating Persistence"
    *   **Description**: "Data surviving node failure."
    *   **Click**: "Create Issue".
*   **Observation**: You will be redirected to the issue list, showing your new issue.
*   **Say**: "Notice that this Issue Tracker is **independent** of the code repositories. Standard Gitea couples them. We store Issues in CockroachDB. This means even if the Gitea service crashes, our project management data remains 100% available. This is a deliberate architectural choice for resilience."

---

### Step 3: Research Experiment (The "Science")

*"Now, let's test the fault tolerance strategies we engineered."*

**1. Visual Demonstration**
*   **Action**: Open a new terminal (Terminal 5).
*   **Command**:
    ```bash
    python3 scripts/demo_ft_strategies.py
    ```
*   **Narrative**: "I will simulate real-time failures.
    *   **Baseline**: Watch user_1... 💥 LOST. Zero recovery.
    *   **Replication**: Watch... 💥 RECOVERED instantly (0.00s). We use 3 active replicas.
    *   **Checkpointing**: Watch... 💥 RECOVERED. It takes longer due to disk I/O, but it survives memory crashes."

**2. Batch Experiment (Optional deeply technical proof)**
*   **Command**:
    ```bash
    python3 scripts/run_ft_experiments.py
    ```
*   **Say**: "For our paper, we automated 200 chaos engineering runs. We found that Replication offers the best RTO (Recovery Time), while Checkpointing provides cost-effective Durability (RPO)."

---

## 🏁 Conclusion
*"GitForge demonstrates that by decoupling storage from logic and implementing hybrid fault tolerance strategies, we can achieve 99.9% availability even on unreliable hardware."*
