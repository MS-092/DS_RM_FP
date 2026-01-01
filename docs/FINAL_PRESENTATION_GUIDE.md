# 🎓 GITFORGE: THE FINAL RUNBOOK

Follow this guide EXACTLY to start, verify, and present your Distributed Systems project.

---

## 🛑 PART 1: SYSTEM RESET (DO THIS NOW)
**Goal:** Ensure a clean slate with the latest code (Visual Demo, Issue Tracker Fixes).

1.  **Close ALL** existing terminal windows.
2.  **Open a NEW Terminal**.
3.  **Run the Full Reset Script**:
    ```bash
    # Go to project folder
    cd /Users/matthewstaniswinata/Documents/GitHub/DS_RM_FP
    
    # Run the nuclear option (Rebuilds everything properly)
    chmod +x scripts/full_system_reset.sh
    ./scripts/full_system_reset.sh
    ```
    *(Wait ~2-3 minutes until it says "✅ SYSTEM READY!")*

---

## ⚡ PART 2: NETWORK TUNNELS (THE "CONN-GROUPS")
**Goal:** Open the 4 required gateways. Open **4 Separate Terminal Tabs**.

**Terminal 1: THE ROOT TUNNEL**
```bash
sudo minikube tunnel
# Enter password. Minimize this window but KEEP OPEN.
```

**Terminal 2: BACKEND BRIDGE**
```bash
kubectl port-forward svc/backend 8000:8000 -n gitforge
```

**Terminal 3: GITEA BRIDGE**
```bash
kubectl port-forward svc/gitea-service 3000:3000 -n gitforge
```

**Terminal 4: FRONTEND BRIDGE (YOUR VIEW)**
```bash
minikube service frontend -n gitforge
# This will output a URL (e.g., http://127.0.0.1:56789). CLICK IT.
# OR, if sudo tunnel worked perfect, just go to http://localhost
```

---

## 🎬 PART 3: THE LIVE PRESENTATION SCRIPT

### 1. The Opening Hook (Architecture)
*   **Show**: The `http://localhost` Dashboard.
*   **Say**: "This is GitForge. Unlike Gitea, we **decoupled** the Frontend, Backend, and Database into distributed microservices."
*   **Demo**: Click **System Status**. Show the Green Health Cards.

### 2. The "Decoupled" Feature (Issues)
*   **Action**: Go to **System Reliability Log** (formerly Issues).
*   **Action**: Click **New Issue**.
*   **Type**:
    *   Title: "Testing Persistence"
    *   Desc: "Data survives node failure."
*   **Say**: "Note that this Incident Log is stored in **CockroachDB**, separate from the git repositories. Even if the Git Service fails, this log remains online."

### 3. The "Visual" Demo (The Terminal Show)
*   **Action**: Open **Terminal 5** (New Window).
*   **Command**:
    ```bash
    python3 scripts/demo_ft_strategies.py
    ```
*   **Say**: "I will now simulate a catastrophe."
*   **Watch**:
    *   **Baseline**: "Fails instantly. 0% Data."
    *   **Replication**: "Connecting to Replica B... ✅ Syncing... Success."
    *   **Checkpointing**: "Reading Disk WAL... ██████ 100%... Success."

### 4. Run Research Experiments:
    *   **Demonstration**: Use the **System Status Dashboard** to show live metrics and fault injection (Visual Mode).
    *   **Data Collection**: For the printed report, follow the steps in `docs/RESEARCH_RUNBOOK.md` to run the automated Python suite and generate CSVs.
    *   **Fault Injection**: Use the dashboard buttons to simulate 'PodKill' or 'Partition'.

### 5. The "Integration" (The Payoff)
*   **Action**: Go back to your **System Reliability Log** in the Browser.
*   **Refresh**: The page.
*   **Show**: The automated incidents ("node_failure_detected") are now listed!
*   **Say**: "Our automated chaos testing script actually injected these incidents into the live dashboard via the API. The system is fully integrated."

---

## 🚑 TROUBLESHOOTING CHEAT SHEET

1.  **"Connection Refused"**:
    *   Did Minikube crash? Run `minikube start` then `sudo minikube tunnel`.
2.  **"Failed to create issue"**:
    *   Did you run the Reset Script? It fixes the proxy.
    *   Are Terminals 1 & 2 running?
3.  **"Gitea 500 Error"**:
    *   Gitea might need setup. Go to `http://localhost:3000` to fix the install/user.
