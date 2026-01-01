# 🧪 Research Experiment Runbook
**Project**: Distributed GitForge with Fault Tolerance
**Objective**: Empirically compare Checkpointing, Replication, and Hybrid strategies.

---

## 🏗️ Phase 1: Setup & Validation

Before gathering data, ensure the test environment is standardized to minimize noise.

1.  **Environment Check**:
    *   Laptop plugged in (power adapter).
    *   Close unnecessary background apps (Chrome tabs, etc).
    *   Verify Kubernetes Tunnels:
        ```bash
        # Terminal 1
        minikube tunnel
        # Terminal 2
        kubectl port-forward svc/backend 8000:8000 -n gitforge
        ```

2.  **Sanity Check**:
    *   Go to `http://localhost/status`.
    *   Verify "CockroachDB" is **Green**.
    *   Click "Run Experiment" with default settings.
    *   **Pass Criteria**: You see a result (e.g., "Last Run: 0.23s").

---

## 📊 Phase 2: Automated Data Collection (N=200)

This phase generates the raw dataset for your research paper/report.

**Hypothesis**:
*   *Replication* will have the fastest RTO (Receiver Time Objective) but slower Write latency.
*   *Checkpointing* will have slower RTO but faster Write latency.
*   *Hybrid* will offer a balanced trade-off.

**Procedure**:
1.  Run the automated suite:
    ```bash
    cd /Users/matthewstaniswinata/Documents/GitHub/DS_RM_FP
    python3 scripts/run_ft_experiments.py
    ```
    *Note: The script now accounts for simulated network latency (100ms-400ms) to ensure realistic results.*

2.  **Wait**: The script takes approx **5-10 minutes** to run 200 experiments.
    *   *Do not interact with the system during this time.*

3.  **Output**:
    *   Look for a file named `experiment_results_YYYYMMDD_HHMM.csv`.
    *   This CSV contains `recovery_time_seconds`, `store_time_seconds`, `strategy`, etc.

---

## 💥 Phase 3: Fault Injection (Chaos Mode)

This phase tests the system's resilience against "Cascading Failures" and "Network Partitions".

**Goal**: Prove that the system detects failures and self-recovers.

1.  **Scenario A: The "Pod Death" (Fail-Stop)**
    *   **Dashboard**: Set Control Panel to **Replication (Factor 3)**.
    *   **Action**: Click **Inject Fault: PodKill**.
    *   **Observation**:
        1.  UI Badge turns **RED** (Degraded).
        2.  Logs show `🔥 Replica node-1 FAILED`.
        3.  Operations *continue* (because 2/3 nodes are healthy).
    *   **Recovery**: Click **Recover**. Badge turns **GREEN**.

2.  **Scenario B: The "Network Split" (Partition)**
    *   **Dashboard**: Set Control Panel to **Checkpointing**.
    *   **Action**: Click **Inject Fault: Partition**.
    *   **Observation**:
        1.  UI Badge turns **RED**.
        2.  Write operations fail (simulated).
    *   **Recovery**: Click **Recover**. System reloads last checkpoint from disk.

---

## 📈 Phase 4: Analysis & Reporting

Use the CSV from Phase 2 to generate your charts.

**Key Metrics to Graph**:
1.  **Recovery Time (RTO) Comparison**:
    *   Bar Chart: Average `recovery_time_seconds` per Strategy.
    *   *Expectation*: Replication (~0.1s) < Hybrid (~0.2s) < Checkpointing (~0.5s).

2.  **Write Latency Comparison**:
    *   Bar Chart: Average `store_time_seconds`.
    *   *Expectation*: Checkpointing (Fast) < Replication (Slow - wait for quorum).

3.  **Reliability**:
    *   Table: `data_recovery_rate_percent`.
    *   *Expectation*: All should be near 100%, except "Baseline" (0%).

---

## 🆘 Troubleshooting

*   **Script hangs/timeouts**: The simulated latency might be higher than the client timeout.
    *   Fix: Edit `scripts/run_ft_experiments.py` and increase `timeout=10`.
*   **"Connection Refused"**: Check your `kubectl port-forward`.
