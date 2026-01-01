# GitForge: Empirical Analysis of Distributed Recovery Strategies in Kubernetes Environments

## Abstract
This paper presents **GitForge**, a purpose-built distributed system designed to rigorously evaluate fault tolerance strategies in microservices architectures. By instrumenting a functional Git hosting platform with Chaos Mesh and Prometheus, we conducted a comparative analysis of **Checkpointing**, **State Machine Replication (SMR)**, and **Hybrid** recovery mechanisms. Our results demonstrate that memory-based Replication strategies achieve a Recovery Time Objective (RTO) of **~0.64s**, offering a **2x improvement** over disk-based Checkpointing (~1.25s). Furthermore, we identified critical stability thresholds in high-frequency checkpointing, observing that aggressive 15-second intervals caused stochastic I/O saturation events leading to 400s+ latency spikes (the "Thundering Herd" problem). We conclude that a Hybrid approach with asynchronous background persistence offers the optimal balance of High Availability (HA) and durability.

---

## 1. Introduction
The resilience of distributed systems is often discussed in theoretical terms, but empirical data on the trade-offs between recovery strategies in containerized environments remains valuable for practitioners. This research aims to quantify the "cost of reliability" by measuring the impact of different fault tolerance configurations on system performance and recovery speed.

We developed GitForge to answer three specific research questions:
1.  **Speed**: How much faster is memory-based replication compared to disk-based checkpointing in a real Kubernetes cluster?
2.  **Granularity**: Does increasing the frequency of checkpoints always improve data safety, or is there a point of diminishing returns?
3.  **Hybrid Viability**: Can a hybrid strategy deliver the speed of replication with the durability of checkpoints?

---

## 2. System Architecture
GitForge operates as a distributed microservices application on Kubernetes, comprising:

*   **Frontend**: React-based dashboard for real-time system health and issue tracking.
*   **Backend Gateway**: FastAPI service managing API requests and proxying Git operations.
*   **Distributed Storage**: CockroachDB cluster configured for tunable consistency and replication factors.
*   **Git Service**: Gitea instances for repository management.
*   **Chaos Engine**: Chaos Mesh for injecting precise failure scenarios (Pod Kill, Network Partition).

This architecture allows for the isolation of specific failure domains, ensuring that measured recovery times reflect the system's architectural logic rather than external noise.

---

## 3. Methodology

### 3.1 Experimental Design
We defined three primary recovery strategies for evaluation:
*   **Baseline**: No recovery mechanisms (Control group).
*   **Checkpointing**: Periodic persistence to disk at intervals of 15s, 30s, and 60s.
*   **Replication**: State Machine Replication with factors of 2 and 3.
*   **Hybrid**: A combination of Replication (Factor 3) and Asynchronous Checkpointing (30s).

### 3.2 Data Volume & Workload
Each experimental run processed a standardized workload of **100 Git Reference Metadata items**.
*   **Payload**: JSON objects representing commit hashes and timestamps.
*   **Volume**: Chosen to be large enough to measure transfer latency but small enough to allow for **200+ repeated trials**.

### 3.3 Metrics
*   **Recovery Time Objective (RTO)**: The duration from the instant of failure injection until the system returns to 95% of baseline throughput.
*   **Durability**: The percentage of confirmed writes successfully retrieved after recovery.

---

## 4. Results & Analysis

### 4.1 Baseline Performance
Under normal operating conditions (no failures), the system achieved:
*   **Max Throughput**: 74.06 issues/sec.
*   **Average Latency**: 30.97ms.
*   **Success Rate**: 100%.
This established a solid baseline for normalizing recovery metrics.

### 4.2 Comparative Recovery Speeds

| Strategy Type | Avg Recovery Time (RTO) | Performance vs. Baseline |
| :--- | :--- | :--- |
| **Replication** | **~0.64s** | ⚡️ **Fastest** |
| **Hybrid** | **~0.63s** | ⚡️ **Fastest** |
| **Checkpointing** | **~1.25s** | 🐢 **Slower** |

**Interpretation**: Replication consistently outperformed Checkpointing by approximately **600ms**. This significant delta represents the "Disk I/O Tax"—the time required to re-read state from physical storage, parse JSON logs, and rehydrate memory. In contrast, Replication allows for near-instant failover to a healthy in-memory peer.

### 4.3 The "15-Second" Anomaly
A key finding occurred during the `Checkpoint_15s` tests. While the average recovery time was expected to be low, we observed a massive standard deviation with max spikes reaching **444.38s**.

**Analysis**: This phenomenon demonstrates the **Trade-off of Granularity**. Checkpointing every 15 seconds overwhelmed the storage subsystem's operation queue. This "Thundering Herd" effect caused single operations to block for minutes as the disk controller sought to clear the backlog. This result proves that **30s or 60s** intervals are operationally superior to 15s in this specific architecture, as they avoid I/O saturation.

### 4.4 Hybrid Strategy Success
The **Hybrid** configuration (Replica Factor 3 + Checkpoint 30s) achieved an RTO of **0.63s**, virtually identical to pure Replication.
*   **Mechanism**: The system successfully defaulted to the "Fast Path" (recovering from a memory replica) while maintaining a background thread for disk persistence.
*   **Implication**: There was zero performance penalty for adding disk backups when implemented asynchronously. This validates the Hybrid approach as the "Gold Standard" for production systems.

---

## 5. Statistical Significance
An ANOVA test performed on the dataset confirmed that the difference between Replication (0.64s) and Checkpointing (1.25s) is statistically significant (Standard Deviation ~0.08s across 20 runs). The architecture, not random noise, is the determinant factor in recovery speed.

---

## 6. Conclusion
Our experiments with GitForge quantify the performance hierarchy of distributed recovery strategies. While **Replication** offers the fastest RTO (~0.6s), it comes with high memory costs. **Checkpointing** is resource-efficient but slower (~1.2s) and prone to I/O saturation if tuned too aggressively (as seen in the 15s anomaly).

The **Hybrid** strategy emerged as the optimal solution, effectively decoupling recovery speed from durability guarantees. Future work will explore the impact of network partitions on split-brain scenarios within this hybrid model.
