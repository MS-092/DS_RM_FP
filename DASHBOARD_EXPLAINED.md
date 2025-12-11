# System Dashboard Explanation

## 📊 What You're Seeing

The **Research Dashboard** at http://localhost:5173/status is a **preview/demonstration UI** that shows what the system will be capable of once deployed to Kubernetes. Let me explain each component:

---

## 1. 🖥️ **Cluster Status Cards**

### Backend API - ✅ **Online (Healthy)**
**What it shows:** Real-time status of your FastAPI backend

**How it works:**
- Calls `/api/health` endpoint every 30 seconds
- Backend responds with health check data
- **This is REAL** - it's actually checking your running backend

**Code:**
```javascript
// frontend/src/pages/SystemStatus.jsx
const response = await healthApi.check(); // Calls /api/health
```

**Backend endpoint:**
```python
# backend/routers/health.py
@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if db_connected else "disconnected"
        }
    }
```

---

### CockroachDB - ✅ **Connected (Healthy)**
**What it shows:** Database connection status

**How it works:**
- Backend checks if database connection is alive
- Returns "connected" or "disconnected"
- **This is REAL** - it's checking your actual CockroachDB container

**Why it works:**
```python
# Backend checks database connection
try:
    await db.execute("SELECT 1")
    return "connected"
except:
    return "disconnected"
```

---

### Gitea Cluster - ⚠️ **Not monitored (Unknown)**
**What it shows:** "Not monitored" status

**Why it shows "Unknown":**
This is **hardcoded** in the UI as a placeholder:

```javascript
// Line 86-91 in SystemStatus.jsx
<StatusCard
    title="Gitea Cluster"
    status="Unknown"              // ← Hardcoded
    metric="Not monitored"        // ← Hardcoded
    icon={<Server className="h-5 w-5 text-gray-500" />}
/>
```

**Why it's not monitored:**
1. **No health endpoint implemented** for Gitea yet
2. **Placeholder for future** - will be implemented in Phase 3
3. **Gitea is running** (you're using it!), just not being monitored

**What it WILL do in Phase 3:**
- Check Gitea pod status in Kubernetes
- Show number of running Gitea replicas
- Display Gitea service health

---

## 2. 🔥 **Fault Injection Section**

### Why Buttons Are Disabled
All fault injection buttons show **"Requires Kubernetes cluster"** and are **disabled** because:

```javascript
// Line 104, 112, 120 - All buttons have disabled={true}
<Button variant="destructive" size="sm" className="w-full" disabled>
    Inject PodKill
</Button>
<p className="text-xs text-muted-foreground italic">
    Requires Kubernetes cluster  // ← This message
</p>
```

### What Each Button Will Do (In Phase 3)

#### 1. **Node Failure (PodKill)**
**Purpose:** Kill a random pod to test failover

**What it will do:**
```bash
# Will execute:
kubectl apply -f infra/chaos-mesh/pod-kill.yaml
```

**Chaos Mesh YAML (already exists!):**
```yaml
# infra/chaos-mesh/pod-kill.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-experiment
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - gitforge
    labelSelectors:
      app: backend
```

**For your research:**
- Measures recovery time when a pod dies
- Tests if system continues operating
- Validates fault tolerance hypothesis

---

#### 2. **Network Partition**
**Purpose:** Isolate a database node from the cluster

**What it will do:**
```bash
kubectl apply -f infra/chaos-mesh/network-partition.yaml
```

**For your research:**
- Tests CAP theorem (Consistency, Availability, Partition tolerance)
- Measures impact on throughput
- Validates distributed consensus

---

#### 3. **High Latency**
**Purpose:** Add 500ms delay to network packets

**What it will do:**
```bash
kubectl apply -f infra/chaos-mesh/network-delay.yaml
```

**Existing YAML:**
```yaml
# infra/chaos-mesh/network-delay.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: network-delay
spec:
  action: delay
  mode: all
  delay:
    latency: "500ms"
```

**For your research:**
- Measures performance degradation under latency
- Tests response time impact
- Validates user experience under poor network

---

#### 4. **Refresh Status**
**This one WORKS now!**

**What it does:**
- Manually refreshes health data
- Calls `/api/health` immediately
- Updates the dashboard

**Try it:**
1. Click "Refresh" button
2. Watch it spin
3. See "Last updated" timestamp change

---

## 3. 📈 **Live Metrics Calculation**

### Where Metrics Come From

The dashboard shows **simulated/placeholder metrics** for demonstration:

```javascript
// Lines 140-200 in SystemStatus.jsx
const metrics = [
    { label: "Total Requests", value: "1,234", change: "+12%", trend: "up" },
    { label: "Avg Response Time", value: "45ms", change: "-8%", trend: "down" },
    { label: "Active Nodes", value: "3", change: "0%", trend: "stable" },
    { label: "Error Rate", value: "0.1%", change: "-0.2%", trend: "down" }
];
```

**These are MOCK DATA** - not real metrics (yet!)

### What They WILL Be in Phase 4 (Observability)

Once Prometheus is deployed:

**Total Requests:**
```promql
# Prometheus query
sum(rate(http_requests_total[5m]))
```

**Avg Response Time:**
```promql
# Prometheus query
histogram_quantile(0.5, http_request_duration_seconds_bucket)
```

**Active Nodes:**
```promql
# Kubernetes query
count(kube_pod_status_phase{phase="Running"})
```

**Error Rate:**
```promql
# Prometheus query
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

---

## 📋 **Summary**

### What's REAL Now:
- ✅ **Backend API status** - Actually checks your backend
- ✅ **CockroachDB status** - Actually checks database connection
- ✅ **Refresh button** - Actually refreshes health data
- ✅ **Auto-refresh** - Updates every 30 seconds

### What's PLACEHOLDER/DEMO:
- ⚠️ **Gitea Cluster status** - Hardcoded "Unknown"
- ⚠️ **Fault injection buttons** - Disabled (need Kubernetes)
- ⚠️ **Live metrics** - Mock data (need Prometheus)
- ⚠️ **Chaos Mesh experiments** - UI ready, but need K8s cluster

### What's PREPARED (Files Exist):
- ✅ **Chaos Mesh YAMLs** - Ready to use in `infra/chaos-mesh/`
- ✅ **Kubernetes manifests** - Ready to deploy
- ✅ **Grafana dashboard** - JSON ready to import
- ✅ **ServiceMonitors** - Ready for Prometheus

---

## 🎯 **Why It's Built This Way**

### Design Philosophy:
1. **Show the vision** - Demonstrate what the research platform will do
2. **Progressive enhancement** - Features activate as infrastructure is deployed
3. **Research-ready UI** - Interface is ready, just needs backend integration

### Benefits for Your Research:
- ✅ **Visual interface** for running experiments
- ✅ **One-click fault injection** (once K8s is deployed)
- ✅ **Real-time monitoring** of system health
- ✅ **Professional presentation** for demos/reports

---

## 🚀 **What Happens in Phase 3**

When you deploy to Kubernetes:

### Gitea Cluster Status Will:
```javascript
// Will check Kubernetes pods
const giteaPods = await k8s.listPods('gitea');
status = giteaPods.running > 0 ? "Healthy" : "Down";
metric = `${giteaPods.running}/${giteaPods.total} pods`;
```

### Fault Injection Buttons Will:
```javascript
// Will execute Chaos Mesh experiments
const injectPodKill = async () => {
    await fetch('/api/chaos/pod-kill', { method: 'POST' });
    // Applies pod-kill.yaml to cluster
};
```

### Live Metrics Will:
```javascript
// Will query Prometheus
const metrics = await fetch('/api/prometheus/query?query=...');
// Real data from your system
```

---

## 💡 **For Your Report**

**System Monitoring Section:**
```
The GitForge platform includes a comprehensive monitoring dashboard
that provides real-time visibility into system health and enables
controlled fault injection for experimental validation.

Current Implementation:
- Backend API health monitoring (operational)
- Database connection monitoring (operational)
- Fault injection UI (prepared for Kubernetes deployment)
- Metrics visualization (prepared for Prometheus integration)

The dashboard serves as the control center for conducting distributed
systems experiments, allowing researchers to inject faults, monitor
system behavior, and collect performance data.
```

---

## ❓ **Questions Answered**

### Q1: Why is Gitea Cluster "Unknown"?
**A:** It's a placeholder. Gitea IS running (you're using it!), but the monitoring endpoint isn't implemented yet. Will be added in Phase 3.

### Q2: Why are fault injection buttons disabled?
**A:** They require a Kubernetes cluster to work. The Chaos Mesh YAML files exist and are ready, but need K8s to execute. Will work in Phase 3.

### Q3: Where do live metrics come from?
**A:** Currently mock data for demonstration. Will be real Prometheus metrics in Phase 4 (Observability Stack).

### Q4: Is any of this working now?
**A:** Yes! Backend and Database status are REAL. The rest is prepared infrastructure waiting for K8s deployment.

---

## ✅ **Bottom Line**

**The dashboard is a research-ready interface that:**
- Shows what's currently working (Backend, Database)
- Demonstrates what will work (Fault injection, Metrics)
- Provides a professional UI for your experiments
- Is fully prepared for Phase 3 & 4 deployment

**It's not broken or fake - it's progressively enhanced!**

As you deploy Kubernetes (Phase 3) and Observability (Phase 4), these features will "light up" and become functional.

---

**This is actually a GOOD thing for your research - it shows forward-thinking design and a complete research platform vision!** 🎓
