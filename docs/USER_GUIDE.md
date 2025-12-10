# GitForge User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Guide](#user-interface-guide)
4. [API Usage Guide](#api-usage-guide)
5. [Research Dashboard](#research-dashboard)
6. [Troubleshooting](#troubleshooting)

## Introduction

GitForge is a distributed version control platform that separates Git operations from metadata storage, providing fault tolerance and high availability. This guide will help you understand and use all features of the system.

### Key Concepts

- **Distributed Architecture**: Git operations are handled by Gitea while metadata (issues, comments) is stored in CockroachDB
- **Fault Tolerance**: System continues operating even when individual nodes fail
- **Research Platform**: Built-in chaos engineering tools for distributed systems research

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- Docker Desktop installed and running
- Python 3.13+ with pip
- Node.js 18+ with npm
- At least 4GB of free RAM
- Ports 3000, 5173, 8000, 8080, 26257 available

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd DS_RM_FP
```

#### 2. Start Infrastructure Services

```bash
# Start CockroachDB and Gitea
docker compose up -d

# Verify services are running
docker ps
```

You should see two containers:
- `ds_rm_fp-cockroachdb-1` (CockroachDB)
- `ds_rm_fp-gitea-1` (Gitea)

#### 3. Set Up Backend

```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload
```

The backend will start on `http://localhost:8000`

#### 4. Set Up Frontend

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start on `http://localhost:5173`

#### 5. Verify Installation

Open your browser and visit:
- Frontend: http://localhost:5173
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## User Interface Guide

### Navigation

The main navigation bar provides access to:
- **GitForge Logo** - Returns to home page
- **Repositories** - Browse Git repositories
- **Issues** - Global issue tracker
- **System Status** - Research dashboard
- **Login/Sign Up** - User authentication (coming soon)

### Home Page

The landing page displays:
- **System Status Indicators**: Real-time health of backend services
- **Feature Highlights**: Key capabilities of GitForge
- **Call-to-Action Buttons**: Quick access to repositories and issues

### Working with Issues

#### Viewing Issues

1. Click **Issues** in the navigation bar
2. You'll see a list of all issues across all repositories
3. Use the filter buttons to show:
   - **All** - All issues regardless of status
   - **Open** - Only open issues
   - **Closed** - Only closed issues
4. Use the search box to filter by title or repository name

#### Creating an Issue

Currently, issues can be created via the API:

```bash
curl -X POST "http://localhost:8000/api/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug: Login page not responsive",
    "description": "The login page does not work properly on mobile devices",
    "repository": "frontend-app",
    "created_by": "john-doe"
  }'
```

#### Viewing Issue Details

1. Click on any issue title in the issue list
2. The issue detail page shows:
   - **Title and Status**: Issue name and current state
   - **Description**: Detailed information about the issue
   - **Comments**: Discussion thread
   - **Metadata**: Repository, author, creation date

#### Adding Comments

1. Navigate to an issue detail page
2. Scroll to the comment section
3. Type your comment in the text area
4. Click **Add Comment**
5. Your comment will appear immediately

#### Understanding Issue Status

- 🟢 **Open**: Issue is active and needs attention
- ⚫ **Closed**: Issue has been resolved or closed

### Repository Browser

1. Click **Repositories** in the navigation
2. Browse available repositories
3. Use the search box to find specific repositories
4. Click on a repository to view:
   - File browser
   - README preview
   - Clone instructions (HTTPS/SSH)

### System Status Dashboard

The Research Dashboard provides:

#### Cluster Health

Real-time status of system components:
- **Backend API**: FastAPI service status
- **CockroachDB**: Database connection status
- **Gitea Cluster**: Git service status (when deployed in K8s)

Status indicators:
- 🟢 **Healthy**: Service operating normally
- 🟠 **Degraded**: Service experiencing issues
- 🔴 **Error**: Service unavailable
- ⚪ **Unknown**: Status cannot be determined

#### Live Metrics

- **Throughput**: Requests per second
- **Recovery Time**: Average time to recover from failures
- **Auto-refresh**: Updates every 30 seconds
- **Manual Refresh**: Click the refresh button for immediate update

#### Fault Injection (Chaos Engineering)

*Note: Requires Kubernetes deployment*

Available chaos experiments:
- **Node Failure**: Simulates pod crashes
- **Network Partition**: Isolates nodes from cluster
- **High Latency**: Adds network delays

## API Usage Guide

### Authentication

*Note: Authentication is not yet implemented. All endpoints are currently public.*

### Base URL

```
http://localhost:8000
```

### Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI where you can:
- Browse all available endpoints
- See request/response schemas
- Test API calls directly from the browser

### Common API Operations

#### List All Issues

```bash
curl http://localhost:8000/api/issues
```

Response:
```json
[
  {
    "id": 1,
    "title": "Example issue",
    "description": "Issue description",
    "status": "open",
    "repository": "my-repo",
    "created_by": "user1",
    "created_at": "2025-12-09T10:00:00Z"
  }
]
```

#### Get Specific Issue

```bash
curl http://localhost:8000/api/issues/1
```

#### Create New Issue

```bash
curl -X POST http://localhost:8000/api/issues \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New feature request",
    "description": "Add dark mode support",
    "repository": "frontend-app",
    "created_by": "alice"
  }'
```

#### Delete Issue

```bash
curl -X DELETE http://localhost:8000/api/issues/1
```

#### Get Comments for Issue

```bash
curl http://localhost:8000/api/comments/issue/1
```

#### Add Comment to Issue

```bash
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": 1,
    "user": "bob",
    "body": "I agree with this suggestion"
  }'
```

#### Check System Health

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-09T12:00:00Z",
  "services": {
    "database": "connected",
    "api": "running"
  }
}
```

### Error Handling

The API uses standard HTTP status codes:

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **404 Not Found**: Resource doesn't exist
- **422 Unprocessable Entity**: Invalid request data
- **500 Internal Server Error**: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Research Dashboard

### Purpose

The Research Dashboard is designed for distributed systems research, allowing you to:
- Monitor system health in real-time
- Inject faults to test resilience
- Measure recovery times
- Analyze system behavior under stress

### Using the Dashboard

#### Monitoring Health

1. Navigate to **System Status** in the navigation
2. View the cluster status cards showing:
   - Service name
   - Current status (Healthy/Degraded/Error)
   - Metric (e.g., "Connected", "Online")
3. Check the timestamp for last update
4. Click **Refresh** to manually update

#### Understanding Metrics

**Throughput (Req/sec)**
- Shows current request rate
- Higher is better
- Drops during failures

**Avg Recovery Time**
- Time taken to recover from failures
- Lower is better
- Measured over last 5 runs

#### Chaos Engineering (Kubernetes Only)

To use fault injection:

1. Deploy GitForge to Kubernetes cluster
2. Install Chaos Mesh
3. Apply chaos experiments from `infra/chaos-mesh/`
4. Monitor recovery in the dashboard

Available experiments:
- **PodKill**: Tests pod restart and failover
- **Network Delay**: Tests replication lag handling
- **Network Partition**: Tests split-brain scenarios

## Troubleshooting

### Backend Issues

#### "Cannot connect to database"

**Symptoms**: Backend fails to start with database connection error

**Solutions**:
1. Verify CockroachDB is running:
   ```bash
   docker ps | grep cockroach
   ```
2. Check CockroachDB logs:
   ```bash
   docker logs ds_rm_fp-cockroachdb-1
   ```
3. Restart CockroachDB:
   ```bash
   docker restart ds_rm_fp-cockroachdb-1
   ```

#### "Port 8000 already in use"

**Symptoms**: Backend won't start, says address already in use

**Solutions**:
1. Find process using port 8000:
   ```bash
   lsof -i :8000
   ```
2. Kill the process:
   ```bash
   kill -9 <PID>
   ```
3. Or use a different port:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

#### "Module not found" errors

**Symptoms**: Import errors when starting backend

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Verify Python version:
   ```bash
   python --version  # Should be 3.13+
   ```

### Frontend Issues

#### "Failed to load issues"

**Symptoms**: Frontend shows error message about loading issues

**Solutions**:
1. Verify backend is running on port 8000
2. Check browser console for CORS errors
3. Verify `.env` file exists in frontend directory
4. Test backend directly:
   ```bash
   curl http://localhost:8000/api/issues
   ```

#### "CORS policy" errors

**Symptoms**: Browser console shows CORS errors

**Solutions**:
1. Verify backend CORS configuration includes `http://localhost:5173`
2. Restart backend server
3. Clear browser cache

#### Blank page or "Cannot GET /"

**Symptoms**: Frontend shows blank page

**Solutions**:
1. Check if Vite dev server is running
2. Verify port 5173 is not in use
3. Check browser console for errors
4. Try clearing node_modules and reinstalling:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### Docker Issues

#### "Cannot connect to Docker daemon"

**Symptoms**: Docker commands fail

**Solutions**:
1. Ensure Docker Desktop is running
2. On macOS, check Docker Desktop in menu bar
3. Restart Docker Desktop
4. Verify Docker is accessible:
   ```bash
   docker ps
   ```

#### Containers won't start

**Symptoms**: `docker compose up` fails

**Solutions**:
1. Check Docker logs:
   ```bash
   docker compose logs
   ```
2. Remove old containers:
   ```bash
   docker compose down
   docker compose up -d
   ```
3. Check for port conflicts
4. Verify Docker has enough resources (4GB+ RAM)

### Performance Issues

#### Slow API responses

**Solutions**:
1. Check CockroachDB performance
2. Monitor system resources
3. Reduce number of concurrent requests
4. Check network latency

#### High memory usage

**Solutions**:
1. Restart Docker containers
2. Limit Docker memory in settings
3. Close unused applications
4. Check for memory leaks in logs

## Advanced Usage

### Custom Configuration

#### Backend Configuration

Edit `backend/database.py` to change database URL:
```python
DATABASE_URL = "cockroachdb+psycopg://user@host:port/database"
```

#### Frontend Configuration

Edit `frontend/.env`:
```
VITE_API_URL=http://your-backend-url:8000
```

### Running in Production

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment guide.

### Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## Getting Help

- **Documentation**: Check this guide and other docs in the repository
- **API Docs**: Visit http://localhost:8000/docs
- **Issues**: Create an issue in the repository
- **Logs**: Check backend console and browser console for errors

## Next Steps

- Explore the API documentation
- Create your first issue
- Try adding comments
- Monitor system health
- Read about Kubernetes deployment in DEPLOYMENT.md
