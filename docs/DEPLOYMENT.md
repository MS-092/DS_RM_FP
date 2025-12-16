# GitForge Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Production Considerations](#production-considerations)
5. [Monitoring and Observability](#monitoring-and-observability)

## Local Development

### Quick Start

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

#### Backend (.env or environment)
```bash
DATABASE_URL=cockroachdb+psycopg://root@localhost:26257/defaultdb
GITEA_URL=http://localhost:3000
LOG_LEVEL=INFO
```

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Docker Deployment

### Building Docker Images

#### Backend Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Frontend nginx.conf

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (optional)
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
services:
  cockroachdb:
    image: cockroachdb/cockroach:v23.1.10
    command: start --insecure
    ports:
      - "26257:26257"
      - "8080:8080"
    volumes:
      - cockroach-data:/cockroach/cockroach-data
    networks:
      - gitforge-network
    restart: unless-stopped

  gitea:
    image: gitea/gitea:1.21.0
    environment:
      - USER_UID=1000
      - USER_GID=1000
    ports:
      - "3000:3000"
      - "2222:22"
    volumes:
      - gitea-data:/data
    networks:
      - gitforge-network
    restart: unless-stopped
    depends_on:
      - cockroachdb

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=cockroachdb+psycopg://root@cockroachdb:26257/defaultdb
      - GITEA_URL=http://gitea:3000
    ports:
      - "8000:8000"
    networks:
      - gitforge-network
    restart: unless-stopped
    depends_on:
      - cockroachdb
      - gitea

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    networks:
      - gitforge-network
    restart: unless-stopped
    depends_on:
      - backend

volumes:
  cockroach-data:
  gitea-data:

networks:
  gitforge-network:
    driver: bridge
```

### Building and Running

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Stop services
docker compose -f docker-compose.prod.yml down
```

## Kubernetes Deployment

### Quick Start (Automated Script)

The easiest way to deploy to Minikube is using the provided script:

```bash
# 1. Start Minikube (if not running)
minikube start --cpus=4 --memory=8192

# 2. Run the deployment script
./scripts/deploy_k8s.sh
```

This script will:
1. Build backend and frontend Docker images inside Minikube.
2. Apply all Kubernetes manifests from `infra/k8s/`.
3. Wait for all services to become ready.

### Manual Deployment Steps

If you prefer to deploy manually or debug specific components:

#### 1. Namespace Setup

```bash
kubectl apply -f infra/k8s/00-namespace.yaml
kubectl config set-context --current --namespace=gitforge
```

#### 2. Deploy CockroachDB

```bash
kubectl apply -f infra/k8s/01-cockroachdb.yaml
# Wait for pods
kubectl wait --for=condition=ready pod -l app=cockroachdb -n gitforge --timeout=120s
```

#### 3. Deploy Gitea

```bash
kubectl apply -f infra/k8s/02-gitea.yaml
```

#### 4. Build & Deploy Backend

```bash
# Set docker env to minikube
eval $(minikube docker-env)

# Build image
docker build -t gitforge-backend:latest backend/

# Deploy
kubectl apply -f infra/k8s/03-backend.yaml
```

#### 5. Build & Deploy Frontend

```bash
# Build image
docker build -t gitforge-frontend:latest frontend/

# Deploy
kubectl apply -f infra/k8s/04-frontend.yaml
```

#### 6. Configure Ingress

```bash
# Enable ingress addon
minikube addons enable ingress

# Apply ingress
kubectl apply -f infra/k8s/05-ingress.yaml

# Start tunnel (in a separate terminal) for load balancer IP
minikube tunnel
```

### Chaos Mesh Deployment

Install Chaos Mesh to enable fault injection experiments:

```bash
curl -sSL https://mirrors.chaos-mesh.org/v2.6.0/install.sh | bash
```

Apply chaos experiments when ready:

```bash
# Pod kill experiment
kubectl apply -f infra/chaos-mesh/pod-kill-experiment.yaml
```

### Verify Deployment

```bash
# Check all pods
kubectl get pods -n gitforge

# Check services
kubectl get svc -n gitforge

# View logs
kubectl logs -f deployment/backend -n gitforge
```


## Production Considerations

### Security

#### 1. Enable TLS/HTTPS

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

#### 2. Secure CockroachDB

Use secure mode with certificates:

```bash
# Generate certificates
cockroach cert create-ca --certs-dir=certs --ca-key=my-safe-directory/ca.key
cockroach cert create-node localhost cockroachdb --certs-dir=certs --ca-key=my-safe-directory/ca.key
cockroach cert create-client root --certs-dir=certs --ca-key=my-safe-directory/ca.key

# Create Kubernetes secrets
kubectl create secret generic cockroachdb-certs --from-file=certs
```

#### 3. Network Policies

Create `infra/kubernetes/network-policy.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: gitforge
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: cockroachdb
    ports:
    - protocol: TCP
      port: 26257
```

### High Availability

#### 1. Pod Disruption Budgets

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
  namespace: gitforge
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: backend
```

#### 2. Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: gitforge
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
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Backup and Recovery

#### CockroachDB Backups

```bash
# Create backup
kubectl exec -it cockroachdb-0 -- ./cockroach sql --insecure -e "BACKUP DATABASE defaultdb TO 'nodelocal://1/backup';"

# Restore backup
kubectl exec -it cockroachdb-0 -- ./cockroach sql --insecure -e "RESTORE DATABASE defaultdb FROM 'nodelocal://1/backup';"
```

#### Automated Backups with CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cockroachdb-backup
  namespace: gitforge
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: cockroachdb/cockroach:v23.1.10
            command:
            - /bin/sh
            - -c
            - |
              ./cockroach sql --insecure --host=cockroachdb -e "BACKUP DATABASE defaultdb TO 'nodelocal://1/backup-$(date +%Y%m%d)';"
          restartPolicy: OnFailure
```

## Monitoring and Observability

### Prometheus Setup

Install Prometheus Operator:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

### ServiceMonitor for Backend

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-metrics
  namespace: gitforge
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

### Grafana Dashboards

Import the dashboard from `infra/grafana/dashboard.json`:

1. Access Grafana (usually port-forwarded)
2. Go to Dashboards → Import
3. Upload `infra/grafana/dashboard.json`

### Logging with Loki

```bash
helm install loki grafana/loki-stack -n monitoring
```

### Alerting Rules

Create `infra/monitoring/alerts.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: gitforge-alerts
  namespace: gitforge
spec:
  groups:
  - name: gitforge
    interval: 30s
    rules:
    - alert: BackendDown
      expr: up{job="backend"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Backend is down"
        description: "Backend has been down for more than 1 minute"
    
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High error rate detected"
        description: "Error rate is above 5% for 5 minutes"
```

### Health Checks

The backend provides health check endpoints:

- `/api/health` - Overall health
- `/api/health/ready` - Readiness probe
- `/api/health/live` - Liveness probe

Configure in Kubernetes:

```yaml
livenessProbe:
  httpGet:
    path: /api/health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  
readinessProbe:
  httpGet:
    path: /api/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Scaling Guide

### Vertical Scaling

Increase resources for pods:

```bash
kubectl set resources deployment backend -n gitforge \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

### Horizontal Scaling

Manual scaling:

```bash
kubectl scale deployment backend -n gitforge --replicas=5
```

Auto-scaling (HPA already configured above).

### Database Scaling

Add more CockroachDB nodes:

```bash
kubectl scale statefulset cockroachdb -n gitforge --replicas=5
```

## Troubleshooting Production

### Pod Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n gitforge

# Check logs
kubectl logs <pod-name> -n gitforge

# Check events
kubectl get events -n gitforge --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Test connection from backend pod
kubectl exec -it deployment/backend -n gitforge -- curl http://cockroachdb:26257

# Check CockroachDB status
kubectl exec -it cockroachdb-0 -n gitforge -- ./cockroach node status --insecure
```

### Performance Issues

```bash
# Check resource usage
kubectl top pods -n gitforge
kubectl top nodes

# View metrics
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Visit http://localhost:9090
```

## Rollback Procedures

### Deployment Rollback

```bash
# View rollout history
kubectl rollout history deployment/backend -n gitforge

# Rollback to previous version
kubectl rollout undo deployment/backend -n gitforge

# Rollback to specific revision
kubectl rollout undo deployment/backend -n gitforge --to-revision=2
```

### Database Rollback

```bash
# Restore from backup
kubectl exec -it cockroachdb-0 -n gitforge -- ./cockroach sql --insecure -e "RESTORE DATABASE defaultdb FROM 'nodelocal://1/backup-20251209';"
```

## Maintenance Windows

### Planned Maintenance

1. Scale down to minimum replicas
2. Perform maintenance
3. Scale back up
4. Verify health

```bash
# Scale down
kubectl scale deployment backend -n gitforge --replicas=1

# Perform maintenance
# ...

# Scale back up
kubectl scale deployment backend -n gitforge --replicas=3

# Verify
kubectl get pods -n gitforge
kubectl rollout status deployment/backend -n gitforge
```

## Cost Optimization

### Resource Requests/Limits

Set appropriate values based on actual usage:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Cluster Autoscaling

Enable cluster autoscaler for cloud providers:

```bash
# GKE example
gcloud container clusters update gitforge-cluster \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10
```

### Spot/Preemptible Instances

Use for non-critical workloads to reduce costs.

## Conclusion

This deployment guide covers local development through production Kubernetes deployment. For specific cloud providers (AWS, GCP, Azure), refer to their respective documentation for managed Kubernetes services.

For questions or issues, refer to the troubleshooting section or create an issue in the repository.
