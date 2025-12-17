# 📄 Product Requirements Document (PRD)
## Project: Distributed GitForge System (Research Edition)
**Version:** 1.0
**Status:** Approved for Research Experimentation

---

## 1. Executive Summary

### 1.1 Purpose & Vision
The **Distributed GitForge System** is developed as a comprehensive experimental platform for the empirical analysis of distributed system resilience. Its primary objective is to facilitate the quantitative evaluation of **Recovery Time Objective (RTO)** and **Data Integrity** across varying fault tolerance strategies within a microservices architecture.

Specifically, this research aims to:
1.  **Evaluate Strategy Efficacy**: Systematically compare the performance of **Checkpointing** (periodic state persistence), **Replication** (active process redundancy), and **Hybrid** (combined) methodologies under controlled failure conditions.
2.  **Quantify Trade-offs**: Measure the operational overhead versus recovery performance for each strategy.
3.  **Provide a Reproducible Testbed**: Establish a standardized, containerized environment using Kubernetes and Chaos Mesh to ensure experimental reproducibility and rigour.

### 1.2 Research Research Alignment
The application design explicitly supports the **Research Protocol** (see `docs/RESEARCH_PROTOCOL.md`) by:
*   **Decoupling State**: Separating the frontend (stateless) from the backend (stateful intermediaries) and the data store (CockroachDB/Gitea).
*   **Exposing Health Metrics**: Providing a dedicated `/api/health` endpoint that reflects the distributed state of the system, crucial for automated RTO measurement.
*   **Visualizing Faults**: Offering a real-time dashboard to monitor node status during Chaos Engineering experiments.

---

## 2. Product Architecture
The system is a Microservices-based Distributed Application running on Kubernetes.

*   **Frontend**: React (SPA) served via Nginx.
*   **Backend**: FastAPI (Python) acting as an API Gateway and orchestration layer.
*   **Git Service**: Gitea (StatefulSet) for repository management.
*   **Database**: CockroachDB (StatefulSet) for distributed metadata storage.
*   **Infrastructure**: Minikube with Chaos Mesh for fault injection.

---

## 3. User Interface & Feature Requirements

The application consists of **6 Core Pages**, each designed to function even during partial system degradation (demonstrating fault tolerance).

### 3.1 🏠 Landing Page
*   **File**: `src/pages/LandingPage.jsx`
*   **Purpose**: Initial entry point and system overview.
*   **Key Design Elements**:
    *   **Hero Section**: "Resilient Code Hosting for Distributed Research".
    *   **Feature Grid**: Highlights "High Availability", "Fault Tolerance", and "Chaos Engineering Ready".
    *   **Navigation**: Prominent calls to action for "View Repositories" and "Check System Status".
    *   **Tech Stack Display**: Visual confirmation of the underlying technologies (K8s, Docker, React, Python).

### 3.2 📉 System Status Dashboard (Research Core)
*   **File**: `src/pages/SystemStatus.jsx`
*   **Purpose**: The "Control Center" for the researcher. It provides real-time visibility into the health of the distributed nodes.
*   **Key Design Elements**:
    *   **Health Cards**: Three distinct cards for **Backend API**, **CockroachDB**, and **Gitea Cluster**.
        *   *Visuals*: Green (Healthy), Red (Offline), Yellow (Degraded).
        *   *Metrics*: Connection latency and uptime status.
    *   **Research Control Panel**:
        *   *Configuration Sliders*: Simulation of "Checkpoint Interval" (15s, 30s, etc.).
        *   *Replication Dropdown*: Visual indicator of current replication factor (2, 3, 5 Nodes).
        *   *Action Button*: "Trigger Experiment" (Manual hook for Chaos Mesh).
    *   **Status Logs**: A scrolling terminal-like log showing recent health check results.

### 3.3 📂 Repository List
*   **File**: `src/pages/RepositoryList.jsx`
*   **Purpose**: Displays the list of Git repositories hosted on the distributed system.
*   **Key Design Elements**:
    *   **Search Bar**: Real-time filtering of repositories.
    *   **Repo Cards**:
        *   Repository Name & Description.
        *   Stats (Stars, Forks, Issues).
        *   "Public/Private" Badges.
    *   **Fault Tolerance Behavior**: If the Gitea Read-Replica is active, this page should utilize caching to remain visible even if the primary write-node is down.

### 3.4 📄 Repository Detail
*   **File**: `src/pages/RepositoryDetail.jsx`
*   **Purpose**: Detailed view of a single repository's codebase and metadata.
*   **Key Design Elements**:
    *   **Header**: Repository Name, Owner, and Clone URL (`git clone ...`).
    *   **File Browser**: A tree-view or list structure allowing navigation of the source code.
    *   **Tabs Navigation**: "Code", "Issues", "Pull Requests", "Settings".
    *   **README Renderer**: Markdown rendering of the project's README file.
    *   **Branch Selector**: Functionality to switch between branches (main, develop).

### 3.5 🐛 Issue List
*   **File**: `src/pages/IssueList.jsx`
*   **Purpose**: Global tracker for bugs and features across the system.
*   **Key Design Elements**:
    *   **Filter Controls**: "All", "Open", "Closed".
    *   **Search Input**: Filter issues by title or content.
    *   **Issue List Items**:
        *   Status Icon (Green Circle for Open, Red Check for Closed).
        *   Issue Title (Clickable).
        *   Metadata: Created by [User] at [Time].
        *   Repository Tag: Shows which repo the issue belongs to.

### 3.6 💬 Issue Detail
*   **File**: `src/pages/IssueDetail.jsx`
*   **Purpose**: Deep dive into a specific problem report.
*   **Key Design Elements**:
    *   **Title & Header**: Large bold title with Open/Closed badge.
    *   **Description Box**: Full text of the issue.
    *   **Comment Thread**: List of comments/discussions chronologically.
    *   **Sidebar**:
        *   Assignees.
        *   Labels (Bug, Feature, Enchancement).
        *   Milestones.
    *   **New Comment Form**: Text area to post a reply.

---

## 4. Non-Functional Requirements (NFRs) for Research

### 4.1 Observability
The system must emit logs or metrics that enable the `experiment_controller.py` to:
*   Detect downtime with sub-second precision.
*   Differentiate between "Network Timeout" and "Internal Server Error (500)".

### 4.2 Scalability
The architecture must support dynamic scaling via Kubernetes:
*   `kubectl scale statefulset gitea --replicas=3` must work without code changes.

### 4.3 Data Persistence
*   **Baseline**: No persistence (pod kill = data loss).
*   **Checkpointing**: Persistent Volumes (PVC) retain `/data` across restarts.

---

## 5. Success Criteria for Evaluation
The product is deemed "Ready for Experimentation" when:
1.  **Baseline Test**: Killing a Gitea pod (Replica=1) results in downtime ~ container restart time (~10-30s).
2.  **Replication Test**: Killing a Gitea pod (Replica=3) results in **<1s downtime** (transparent failover).
3.  **Data Integrity**: Creating a repo, killing the pod, and refreshing the page results in the repository *still existing* (Persistence verification).
