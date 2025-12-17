# GitForge Architecture

## System Overview

GitForge is a distributed version control platform designed to eliminate single points of failure by separating Git operations from metadata storage. The system consists of multiple independent components that work together to provide a resilient, fault-tolerant Git hosting solution.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                               │
└────────────┬────────────────────────────────────┬───────────┘
             │                                     │
             │ HTTP/HTTPS                          │ Git HTTP
             ▼                                     ▼
┌────────────────────────┐              ┌──────────────────────┐
│   Frontend (React)     │              │   Git Proxy          │
│   - UI Components      │              │   (FastAPI)          │
│   - State Management   │◄─────────────┤   - Route Git ops    │
│   - API Client         │   REST API   │   - Forward to Gitea │
└────────────┬───────────┘              └──────────┬───────────┘
             │                                     │
             │ REST API                            │
             ▼                                     ▼
┌────────────────────────┐              ┌──────────────────────┐
│   Backend API          │              │   Gitea Cluster      │
│   (FastAPI)            │              │   (StatefulSet)      │
│   - Issue Tracker      │              │   - Git Operations   │
│   - Comments API       │              │   - Repository Store │
│   - Health Checks      │              │   - User Management  │
└────────────┬───────────┘              └──────────────────────┘
             │
             │ SQL
             ▼
┌────────────────────────┐
│   CockroachDB          │
│   (StatefulSet)        │
│   - Distributed SQL    │
│   - Replication        │
│   - Fault Tolerance    │
└────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Observability Layer                      │
├────────────────┬──────────────────┬─────────────────────────┤
│  Prometheus    │    Grafana       │    Chaos Mesh           │
│  (Metrics)     │  (Visualization) │  (Fault Injection)      │
└────────────────┴──────────────────┴─────────────────────────┘
```

## Components

### 1. Frontend (React + Vite)

**Purpose**: User interface for interacting with the system

**Technology Stack**:
- React 19
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)
- React Router (navigation)

**Key Features**:
- Repository browser
- Issue tracker UI
- System status dashboard
- Real-time updates
- Responsive design

**Deployment**:
- Development: Vite dev server (port 5173)
- Production: Nginx serving static files

**Scalability**:
- Stateless (can scale horizontally)
- CDN-ready for global distribution
- Client-side caching

### 2. Backend API (FastAPI)

**Purpose**: Business logic and API gateway

**Technology Stack**:
- Python 3.13
- FastAPI (web framework)
- SQLAlchemy (ORM)
- Uvicorn (ASGI server)
- Pydantic (validation)

**Key Features**:
- RESTful API
- Async/await support
- Automatic OpenAPI docs
- Input validation
- Health check endpoints

**API Endpoints**:
- `/api/issues` - Issue management
- `/api/comments` - Comment management
- `/api/health` - Health checks
- `/git/*` - Git proxy
- `/metrics` - Prometheus metrics

**Deployment**:
- Development: Uvicorn (port 8000)
- Production: Multiple replicas behind load balancer

**Scalability**:
- Stateless (can scale horizontally)
- Connection pooling to database
- Async I/O for high concurrency

### 3. CockroachDB

**Purpose**: Distributed SQL database for metadata storage

**Technology Stack**:
- CockroachDB v23.1.10
- PostgreSQL-compatible
- Raft consensus protocol

**Key Features**:
- Distributed transactions
- Automatic replication
- Fault tolerance
- Horizontal scalability
- Strong consistency

**Data Model**:
```sql
-- Issues table
CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'open',
    repository VARCHAR,
    created_by VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    issue_id INTEGER REFERENCES issues(id),
    user VARCHAR,
    body TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

**Deployment**:
- Development: Single node (port 26257)
- Production: 3+ node cluster (StatefulSet)

**Scalability**:
- Horizontal scaling by adding nodes
- Automatic data rebalancing
- Read replicas for read-heavy workloads

### 4. Gitea

**Purpose**: Git repository hosting and operations

**Technology Stack**:
- Gitea v1.21.0
- Go-based Git service
- Git HTTP protocol

**Key Features**:
- Git repository management
- User authentication
- Web UI for repositories
- Git HTTP smart protocol

**Deployment**:
- Development: Single container (port 3000)
- Production: 3+ replicas (StatefulSet)

**Scalability**:
- Horizontal scaling with shared storage
- Load balancing for Git operations

## Data Flow

### Issue Creation Flow

```
1. User fills form in Frontend
   ↓
2. Frontend sends POST /api/issues
   ↓
3. Backend validates request
   ↓
4. Backend inserts into CockroachDB
   ↓
5. CockroachDB replicates to other nodes
   ↓
6. Backend returns created issue
   ↓
7. Frontend updates UI
```

### Git Clone Flow

```
1. User runs: git clone http://gitforge.com/git/user/repo.git
   ↓
2. Request hits Backend /git/* endpoint
   ↓
3. Backend proxies to Gitea
   ↓
4. Gitea serves repository data
   ↓
5. Backend streams response to user
```

### Health Check Flow

```
1. Kubernetes liveness probe hits /api/health/live
   ↓
2. Backend checks its own health
   ↓
3. Returns 200 OK if healthy
   ↓
4. Kubernetes keeps pod running

(Separate flow for readiness probe)
```

## Fault Tolerance Architecture

GitForge implements a dual-layer fault tolerance architecture:
1.  **Infrastructure Layer**: Kubernetes-native mechanisms (for production reliability).
2.  **Application Research Layer**: Explicit algorithms implemented in Python (for empirical study).

### 1. Infrastructure Layer (Production)

This layer ensures the base platform remains operational.

*   **Database (CockroachDB)**: Uses Raft consensus. Configured with `replicas: 3`. Tolerates 1 node failure without data loss (RF=3).
*   **Git Storage (Gitea)**: Uses `StatefulSet` with Persistent Volume Claims (PVC). Data survives pod restarts.
*   **API Gateway (Backend)**: Stateless. Kubernetes `Deployment` ensures `replicas: 1+` are always running.

### 2. Application Research Layer (Experimental)

This layer is the core of the research project (`backend/fault_tolerance/`). It implements the "Strategy Pattern" to dynamically switch recovery mechanisms at runtime.

#### Class Structure
*   **`FaultToleranceManager`**: Singleton coordinator. Handles strategy switching and metrics collection.
*   **`BaseFaultToleranceStrategy` (Interface)**: Defines `store()`, `retrieve()`, `recover()`.
*   **Strategies**:
    *   **Baseline (`BaselineStrategy`)**:
        *   *Mechanism*: In-memory dictionary.
        *   *Failure*: `dict.clear()`.
        *   *Recovery*: Re-initialization (empty).
    *   **Checkpointing (`CheckpointingStrategy`)**:
        *   *Mechanism*: Asynchronous background thread writes to disk (JSON/Pickle).
        *   *Recovery*: Load latest valid snapshot + replay Write-Ahead-Log (WAL).
    *   **Replication (`ReplicationStrategy`)**:
        *   *Mechanism*: Active in-memory replication to virtual "nodes" (Python objects).
        *   *Recovery*: Failover to healthy virtual replica.
    *   **Hybrid (`HybridStrategy`)**:
        *   *Mechanism*: Combined replication (for speed) and checkpointing (for catastrophe).

#### Data Flow (Research Mode)

```
1. Client POST /api/fault-tolerance/store
   ↓
2. Manager delegates to Active Strategy (e.g., Replication)
   ↓
3. Strategy writes to Virtual Node A AND Virtual Node B
   ↓
4. Acknowledge Write (200 OK)
   ↓
[External Trigger: Chaos Mesh Kills Pod]
   ↓
5. System Restarts
   ↓
6. Manager initializes
   ↓
7. Client POST /api/fault-tolerance/recover
   ↓
8. Strategy executes specific recovery logic (e.g., Load from Disk)
```

**Recovery Time Objective (RTO)** is measured from step 7 start to finish.

## Security

### Network Security

```
┌─────────────────────────────────────┐
│         Internet                     │
└──────────────┬──────────────────────┘
               │
               │ HTTPS (TLS 1.3)
               ▼
┌──────────────────────────────────────┐
│      Ingress Controller              │
│      - TLS termination               │
│      - Rate limiting                 │
│      - WAF rules                     │
└──────────────┬───────────────────────┘
               │
               │ HTTP (internal)
               ▼
┌──────────────────────────────────────┐
│      Service Mesh (optional)         │
│      - mTLS                          │
│      - Service-to-service auth       │
└──────────────┬───────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
   ┌─────────┐   ┌─────────┐
   │ Backend │   │Frontend │
   └─────────┘   └─────────┘
```

### Data Security

- **Encryption at rest**: CockroachDB encryption
- **Encryption in transit**: TLS for all connections
- **Secrets management**: Kubernetes secrets
- **Network policies**: Restrict pod-to-pod communication

### Authentication & Authorization (Implemented)

The system checks permissions against Gitea's API but manages session state independently via stateless JWTs.

1.  **The "Proxy" Pattern (Security)**:
    *   **Principle**: GitForge never stores user passwords.
    *   **Mechanism**: On login, credentials are exchanged with Gitea for an Access Token. This token is encrypted and embedded in the GitForge JWT.
    *   **Benefit**: Minimizes attack surface. If GitForge DB is leaked, no credentials are compromised.

2.  **Consistency Strategy**:
    *   **Question**: "How do we ensure that if Gitea is down, GitForge handles the error gracefully?"
    *   **Answer**: Circuit Breaker pattern. If Gitea API returns 503, GitForge degrades functionality (e.g., Read-Only mode for metadata) but keeps the Issue Tracker (CockroachDB) online.
    *   **Sync**: Updates are always performed via Gitea REST API (`PUT /api/v1/...`), ensuring hooks and internal consistency are maintained by the source of truth.

3.  **Privilege Separation (RBAC)**:
    *   **Policy**:
        *   **Private Repos**: Strict Ownership. Only the repo owner can Read/Write.
        *   **Public Repos**: World Readable. Only Owner can Write/Delete.
    *   **Implementation**: Logic resides in `backend/dependencies.py` layer, enforcing checks *before* proxying requests.

4.  **Webhooks (Reverse Sync)**:
    *   *Optional Design*: To ensure Gitea -> GitForge consistency (e.g., user pushes code via CLI), a Webhook Listener (`POST /api/webhooks`) consumes Gitea push events to update GitForge's metadata cache if needed.

### Tech Stack
*   **Backend**: Python (FastAPI) for high-performance async I/O.
*   **Auth**: PyJWT for stateless session management.
*   **Integration**: `httpx` for async non-blocking calls to Gitea.

## Observability

### Metrics (Prometheus)

**Backend Metrics**:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `http_requests_in_flight` - Concurrent requests
- `database_connections` - DB connection pool

**Database Metrics**:
- `sql_query_count` - Query count
- `sql_query_latency` - Query latency
- `replication_lag` - Replication delay
- `node_status` - Node health

**System Metrics**:
- CPU usage
- Memory usage
- Disk I/O
- Network traffic

### Logging

**Log Levels**:
- ERROR: Critical errors requiring attention
- WARNING: Potential issues
- INFO: General information
- DEBUG: Detailed debugging information

**Log Aggregation**:
- Loki for log collection
- Grafana for log visualization
- Structured logging (JSON format)

### Tracing

*Note: Not yet implemented*

Future implementation:
- OpenTelemetry for distributed tracing
- Jaeger for trace visualization
- Request correlation IDs

## Performance

### Caching Strategy

```
┌─────────┐
│ Browser │ ← Static assets (1 year)
└────┬────┘
     │
     ▼
┌─────────┐
│   CDN   │ ← Frontend files (1 day)
└────┬────┘
     │
     ▼
┌─────────┐
│ Backend │ ← API responses (no cache)
└────┬────┘
     │
     ▼
┌─────────┐
│Database │ ← Query results (connection pool)
└─────────┘
```

### Database Optimization

- **Indexes**: On frequently queried columns
- **Connection pooling**: Reuse database connections
- **Query optimization**: Use EXPLAIN to analyze queries
- **Batch operations**: Group multiple operations

### API Optimization

- **Async I/O**: Non-blocking operations
- **Response compression**: Gzip for large responses
- **Pagination**: Limit result sets
- **Field selection**: Return only requested fields

## Scalability

### Horizontal Scaling

**Backend**:
```bash
# Scale to 5 replicas
kubectl scale deployment backend --replicas=5
```

**Frontend**:
```bash
# Scale to 3 replicas
kubectl scale deployment frontend --replicas=3
```

**Database**:
```bash
# Add node to cluster
kubectl scale statefulset cockroachdb --replicas=5
```

### Vertical Scaling

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Disaster Recovery

### Backup Strategy

**Database Backups**:
- Full backup: Daily at 2 AM
- Incremental backup: Every 6 hours
- Retention: 30 days
- Storage: S3-compatible object storage

**Repository Backups**:
- Git repositories: Replicated to backup storage
- Frequency: Continuous replication
- Retention: Indefinite

### Recovery Procedures

**Database Recovery**:
```bash
# Restore from backup
cockroach sql --insecure -e "RESTORE DATABASE defaultdb FROM 'backup-location';"
```

**Application Recovery**:
```bash
# Rollback deployment
kubectl rollout undo deployment/backend

# Restore from specific revision
kubectl rollout undo deployment/backend --to-revision=2
```

## Development Workflow

```
┌──────────────┐
│  Developer   │
└──────┬───────┘
       │
       │ git push
       ▼
┌──────────────┐
│   GitHub     │
└──────┬───────┘
       │
       │ webhook
       ▼
┌──────────────┐
│  CI Pipeline │
│  - Lint      │
│  - Test      │
│  - Build     │
└──────┬───────┘
       │
       │ success
       ▼
┌──────────────┐
│  Container   │
│  Registry    │
└──────┬───────┘
       │
       │ deploy
       ▼
┌──────────────┐
│  Kubernetes  │
│  Cluster     │
└──────────────┘
```

## Future Enhancements

1. **Authentication & Authorization**
   - User management
   - Role-based access control
   - OAuth2 integration

2. **Advanced Features**
   - Pull requests
   - Code review
   - CI/CD integration
   - Webhooks

3. **Performance**
   - Redis caching layer
   - Read replicas
   - GraphQL API

4. **Observability**
   - Distributed tracing
   - Advanced alerting
   - SLA monitoring

5. **Multi-tenancy**
   - Organization support
   - Resource quotas
   - Billing integration

## Conclusion

GitForge's architecture is designed for:
- **Resilience**: No single point of failure
- **Scalability**: Horizontal scaling of all components
- **Observability**: Comprehensive monitoring and logging
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Modular design for future enhancements

The distributed nature of the system ensures high availability and fault tolerance, making it suitable for both production use and distributed systems research.
