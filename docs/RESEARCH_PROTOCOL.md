# 🧪 Distributed System Research Protocol

## Overview
This protocol defines the step-by-step methodology to execute the research experiments designed to compare **Checkpointing**, **Replication**, and **Hybrid** fault tolerance techniques.

The system now includes **dedicated source code implementations** of each technique, not just infrastructure-level configurations.

---

## 📁 Fault Tolerance Source Code

The fault tolerance techniques are implemented as dedicated Python modules:

```
backend/fault_tolerance/
├── __init__.py           # Module exports
├── base.py               # Abstract base class (Strategy Pattern)
├── baseline.py           # NO fault tolerance (control group)
├── checkpointing.py      # Periodic snapshots to disk
├── replication.py        # Active data replication across nodes
├── hybrid.py             # Combined checkpointing + replication
└── manager.py            # Runtime strategy selector
```

### Strategy Descriptions

| Strategy | File | Description | Recovery Mechanism |
|----------|------|-------------|-------------------|
| **Baseline** | `baseline.py` | No fault tolerance (control group) | None - data is permanently lost |
| **Checkpointing** | `checkpointing.py` | Periodic disk snapshots | Loads last checkpoint from disk |
| **Replication** | `replication.py` | Active multi-node redundancy | Failover to healthy replica nodes |
| **Hybrid** | `hybrid.py` | Checkpointing + Replication | Replica failover + checkpoint backup |

---

## 🛠️ Experimental Setup

### Prerequisites
1. **Backend Running**: Ensure the FastAPI backend is accessible
2. **API Access**: Either via Kubernetes port-forward or local development

### Starting the System

**Option A: Kubernetes (Minikube)**
```bash
# Start cluster
minikube start --cpus=4 --memory=6144

# Deploy application
./scripts/deploy_k8s.sh

# Start tunnel (new terminal)
sudo minikube tunnel

# Port-forward backend for API access
kubectl port-forward svc/backend 8000:8000 -n gitforge
```

**Option B: Local Development**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 🔬 Running Experiments

### Method 1: Using the REST API (Recommended)

The fault tolerance system is exposed via REST API at `http://localhost:8000/api/fault-tolerance/`.

#### Step 1: Check Available Strategies
```bash
curl http://localhost:8000/api/fault-tolerance/strategies
```

#### Step 2: Configure a Strategy
```bash
# Configure Baseline (Control Group)
curl -X POST http://localhost:8000/api/fault-tolerance/configure \
  -H "Content-Type: application/json" \
  -d '{"strategy": "baseline"}'

# Configure Checkpointing (30s interval)
curl -X POST http://localhost:8000/api/fault-tolerance/configure \
  -H "Content-Type: application/json" \
  -d '{"strategy": "checkpointing", "checkpoint_interval": 30}'

# Configure Replication (Factor 3)
curl -X POST http://localhost:8000/api/fault-tolerance/configure \
  -H "Content-Type: application/json" \
  -d '{"strategy": "replication", "replication_factor": 3}'

# Configure Hybrid
curl -X POST http://localhost:8000/api/fault-tolerance/configure \
  -H "Content-Type: application/json" \
  -d '{"strategy": "hybrid", "checkpoint_interval": 30, "replication_factor": 3}'
```

#### Step 3: Store Test Data
```bash
curl -X POST http://localhost:8000/api/fault-tolerance/store \
  -H "Content-Type: application/json" \
  -d '{"key": "test_key_1", "value": "test_value_1"}'
```

#### Step 4: Simulate Failure
```bash
curl -X POST http://localhost:8000/api/fault-tolerance/simulate-failure \
  -H "Content-Type: application/json" \
  -d '{"failure_type": "default"}'
```

#### Step 5: Measure Recovery
```bash
curl -X POST http://localhost:8000/api/fault-tolerance/recover
```

**Response:**
```json
{
  "success": true,
  "recovery_time_seconds": 0.0234,
  "is_healthy": true,
  "strategy": "checkpointing"
}
```

#### Step 6: Verify Data Integrity
```bash
curl http://localhost:8000/api/fault-tolerance/retrieve/test_key_1
```

---

### Method 2: Automated Experiment (Full Suite)

Run a complete experiment with a single API call:

```bash
curl -X POST http://localhost:8000/api/fault-tolerance/run-experiment \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "checkpointing",
    "data_items": 100,
    "checkpoint_interval": 30
  }'
```

**Response:**
```json
{
  "strategy": "checkpointing",
  "strategy_full_name": "Checkpointing (Interval: 30s)",
  "data_items": 100,
  "store_time_seconds": 0.0123,
  "recovery_time_seconds": 0.0456,
  "items_recovered": 100,
  "data_recovery_rate_percent": 100.0,
  "stats": {...}
}
```

---

### Method 3: Python Script (For N=20 Runs)

Create a Python script for batch experiments:

```python
#!/usr/bin/env python3
"""
Automated Experiment Runner for Fault Tolerance Research
Runs N experiments per strategy configuration
"""

import requests
import csv
import time
from datetime import datetime

API_BASE = "http://localhost:8000/api/fault-tolerance"
RUNS_PER_CONFIG = 20

# Research configurations based on design document
CONFIGURATIONS = [
    {"strategy": "baseline", "name": "Baseline"},
    {"strategy": "checkpointing", "checkpoint_interval": 15, "name": "Checkpoint_15s"},
    {"strategy": "checkpointing", "checkpoint_interval": 30, "name": "Checkpoint_30s"},
    {"strategy": "checkpointing", "checkpoint_interval": 60, "name": "Checkpoint_60s"},
    {"strategy": "replication", "replication_factor": 2, "name": "Replication_2"},
    {"strategy": "replication", "replication_factor": 3, "name": "Replication_3"},
    {"strategy": "replication", "replication_factor": 5, "name": "Replication_5"},
    {"strategy": "hybrid", "checkpoint_interval": 30, "replication_factor": 3, "name": "Hybrid"},
]

def run_experiment(config):
    """Run a single experiment with the given configuration."""
    response = requests.post(f"{API_BASE}/run-experiment", json={
        "strategy": config["strategy"],
        "data_items": 100,
        "checkpoint_interval": config.get("checkpoint_interval", 30),
        "replication_factor": config.get("replication_factor", 3)
    })
    return response.json()

def main():
    results = []
    
    for config in CONFIGURATIONS:
        print(f"\n--- Running {config['name']} ({RUNS_PER_CONFIG} runs) ---")
        
        for run in range(1, RUNS_PER_CONFIG + 1):
            print(f"  Run {run}/{RUNS_PER_CONFIG}...", end=" ")
            
            result = run_experiment(config)
            
            results.append({
                "config_name": config["name"],
                "strategy": config["strategy"],
                "run_id": run,
                "timestamp": datetime.now().isoformat(),
                "recovery_time_seconds": result["recovery_time_seconds"],
                "data_recovery_rate": result["data_recovery_rate_percent"],
                "items_recovered": result["items_recovered"]
            })
            
            print(f"Recovery: {result['recovery_time_seconds']:.4f}s")
            time.sleep(2)  # Cooldown between runs
    
    # Save to CSV
    filename = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✅ Results saved to {filename}")

if __name__ == "__main__":
    main()
```

Save as `scripts/run_ft_experiments.py` and run:
```bash
python3 scripts/run_ft_experiments.py
```

---

## 📊 Data Collection Matrix

For each configuration, collect the following metrics over N=20 runs:

| Metric | Description | Unit |
|--------|-------------|------|
| `recovery_time_seconds` | Time from failure to full restoration | seconds |
| `data_recovery_rate_percent` | Percentage of data recovered | % |
| `items_recovered` | Absolute count of recovered items | count |
| `store_time_seconds` | Time to write test data | seconds |

---

## 📈 Statistical Analysis Plan

### 1. Descriptive Statistics
For each configuration:
```python
import pandas as pd

df = pd.read_csv("experiment_results.csv")

# Group by configuration
summary = df.groupby("config_name")["recovery_time_seconds"].agg([
    'mean', 'std', 'min', 'max', 'count'
])
print(summary)
```

### 2. ANOVA Test
Compare recovery times across all strategies:
```python
from scipy import stats

baseline = df[df['strategy'] == 'baseline']['recovery_time_seconds']
checkpoint = df[df['strategy'] == 'checkpointing']['recovery_time_seconds']
replication = df[df['strategy'] == 'replication']['recovery_time_seconds']
hybrid = df[df['strategy'] == 'hybrid']['recovery_time_seconds']

f_stat, p_value = stats.f_oneway(baseline, checkpoint, replication, hybrid)
print(f"ANOVA: F={f_stat:.4f}, p={p_value:.6f}")
```

### 3. Post-Hoc Pairwise Comparisons
```python
from scipy.stats import ttest_ind

# Example: Baseline vs Hybrid
t_stat, p_value = ttest_ind(baseline, hybrid)
print(f"Baseline vs Hybrid: t={t_stat:.4f}, p={p_value:.6f}")
```

---

## ✅ Expected Results

Based on the implementation:

| Strategy | Expected Recovery Time | Expected Data Recovery |
|----------|----------------------|----------------------|
| Baseline | Manual/Infinite | 0% |
| Checkpointing (30s) | 0.01-0.1s | ~100% (since last checkpoint) |
| Replication (Factor 3) | 0.001-0.01s | 100% (instant failover) |
| Hybrid | 0.001-0.01s | 100% |

---

## 🔧 Troubleshooting

### API Not Responding
```bash
# Check if backend is running
curl http://localhost:8000/api/health

# If using Kubernetes, ensure port-forward is active
kubectl port-forward svc/backend 8000:8000 -n gitforge
```

### Strategy Not Switching
The manager is a singleton. Use `force_new=True` in API calls or restart the backend.

### Checkpoints Not Persisting
Check the checkpoint directory:
```bash
ls -la /tmp/gitforge_checkpoints/
```

---

## 📚 References

- `backend/fault_tolerance/base.py` - Strategy Pattern interface
- `backend/fault_tolerance/manager.py` - Runtime strategy selector
- `backend/routers/fault_tolerance.py` - REST API endpoints
- `docs/PRD.md` - Product Requirements Document
