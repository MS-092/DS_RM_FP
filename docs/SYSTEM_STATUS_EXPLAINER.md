# 📊 System Status Dashboard: Under the Hood

This document visualizes how the **Research Dashboard** (`SystemStatus.jsx`) functions and interacts with the distributed backend.

## 🔄 1. The Monitoring Loop (Live Metrics)

The dashboard maintains a real-time connection to the system state.

```mermaid
sequenceDiagram
    participant UI as React Dashboard
    participant API as Backend API
    participant FT as FaultToleranceManager
    participant K8s as Kubernetes/DB

    loop Every 5 Seconds
        UI->>API: GET /api/health
        API->>K8s: Check DB Connection
        K8s-->>API: { status: "connected" }
        
        UI->>API: GET /api/fault-tolerance/status
        API->>FT: get_manager().get_stats()
        FT-->>API: { strategy: "hybrid", last_recovery: 4.2s, healthy: true }
        
        API-->>UI: Update JSON
        UI-->>UI: Re-render Status Cards & Graphs
    end
```

### ✅ What You See
*   **"Healthy/Degraded" Badge**: Derived from `ft_status.is_healthy`.
*   **Recovery Timer**: Displays `ft_status.stats.last_recovery_time`.
*   **CockroachDB Status**: Derived from `health_data.components.database`.

---

## ⚙️ 2. Research Control Panel (Configuration)

This panel allows researchers to dynamically switch the fault tolerance algorithm at runtime.

```mermaid
graph LR
    User[User Selects "Replication"] -->|Click Run| UI[Frontend]
    UI -->|POST /run-experiment| API[Backend Router]
    API -->|1. Create Config| FT[FaultManager]
    FT -->|2. Instantiate Strategy| Strat[ReplicationStrategy]
    Strat -->|3. Simulate Ops| Nodes[Virtual Nodes]
    Nodes -->|4. Return Result| API
    API -->|5. JSON Result| UI
    UI -->|6. Show Badge| ResultBadge["Last Run: 1.2s"]
```

### ✅ How it Works
1.  **Select Strategy**: React state (`selectedStrategy`) updates.
2.  **Parameters**: Sliders update `checkpointInterval` state.
3.  **Run Experiment**: Sends a payload to `/run-experiment`.
4.  **Feedback**: The `experimentResult` state displays the measured Recovery Time immediately.

---

## 💥 3. Fault Injection (Chaos Mesh Integration)

Reliability testing requires breaking things.

```mermaid
sequenceDiagram
    actor User
    participant UI as Dashboard
    participant Chaos as Chaos Controller
    participant Cluster as Application Cluster

    User->>UI: Click "Inject PodKill"
    UI->>Chaos: POST /simulate-failure {type: "pod_kill"}
    
    rect rgb(255, 200, 200)
    Note over Chaos, Cluster: FAILURE SIMULATION
    Chaos->>Cluster: 1. Kill Gitea Service
    Chaos->>Cluster: 2. Mark Node as "Down"
    end
    
    UI->>UI: Refresh Data (Immediate)
    UI-->>User: Show "Degraded" State (Red)
    
    User->>UI: Click "Recover"
    UI->>Chaos: POST /recover
    Chaos->>Cluster: Restore Service / Failover
    UI-->>User: Show "Healthy" State (Green)
```

### ✅ Key Features
*   **Safety**: Triggers controlled logic in `backend/fault_tolerance/` which mimics infrastructure failure without actually destroying your laptop's Minikube cluster (unless mapped to real Chaos Mesh CRDs).
*   **Visual Feedback**: The "Availability" card turns **RED** instantly upon fault injection and **GREEN** after recovery.

---

## 4. Code Map

| Feature | Frontend Component | Backend Router | Python Logic |
| :--- | :--- | :--- | :--- |
| **Live Status** | `fetchSystemData()` | `GET /status` | `FaultToleranceManager.get_stats()` |
| **Experiment** | `handleRunExperiment` | `POST /run-experiment` | `manager.run_experiment()` |
| **Faults** | `handleInjectFault` | `POST /simulate-failure` | `strategy.simulate_failure()` |
