# 🔧 Phase 1 Troubleshooting - Gitea Connection Issue

## Problem Identified

**Error**: `502: Failed to fetch repositories from Gitea`

**Root Cause**: Docker containers (Gitea and CockroachDB) are **not running**.

## Solution

### Step 1: Start Docker Containers

```bash
# From project root
cd /Users/matthewstaniswinata/Documents/GitHub/DS_RM_FP

# Start all services
docker compose up -d

# Verify they're running
docker ps
```

**Expected output:**
```
CONTAINER ID   IMAGE                              STATUS
xxxxx          cockroachdb/cockroach:v23.1.10    Up
xxxxx          gitea/gitea:1.21.0                Up
```

### Step 2: Wait for Services to Be Ready

```bash
# Wait 10-15 seconds for services to start

# Test Gitea is accessible
curl http://localhost:3000

# Should return HTML (Gitea homepage)
```

### Step 3: Test Gitea API

```bash
# Test the API endpoint
curl http://localhost:3000/api/v1/repos/search

# Should return JSON like:
# {"data":[],"ok":true}
```

### Step 4: Restart Backend

```bash
# Stop the backend (Ctrl+C)
# Then restart it
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Step 5: Test Again

```bash
# Test the backend endpoint
curl http://localhost:8000/api/repositories

# Should return JSON array (might be empty if no repos)
```

## Quick Fix Commands

```bash
# All in one:
cd /Users/matthewstaniswinata/Documents/GitHub/DS_RM_FP
docker compose up -d
sleep 15
curl http://localhost:3000/api/v1/repos/search
```

## Verification Checklist

- [ ] `docker ps` shows 2 containers running
- [ ] `curl http://localhost:3000` returns HTML
- [ ] `curl http://localhost:3000/api/v1/repos/search` returns JSON
- [ ] `curl http://localhost:8000/api/repositories` works

## Next Steps After Fix

1. **Create a test repository in Gitea:**
   - Visit http://localhost:3000
   - Register/Login
   - Create a new repository

2. **Test the frontend:**
   - Visit http://localhost:5173/repos
   - Should see your repository!

## Common Issues

### "Cannot connect to Docker daemon"
**Solution**: Make sure Docker Desktop is running

### "Port already in use"
**Solution**: 
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :26257

# Kill if needed or restart Docker
```

### "Containers exit immediately"
**Solution**:
```bash
# Check logs
docker compose logs gitea
docker compose logs cockroachdb

# Try recreating
docker compose down
docker compose up -d
```

## Status After Fix

Once containers are running:
- ✅ Gitea accessible at http://localhost:3000
- ✅ CockroachDB accessible at localhost:26257
- ✅ Backend can connect to Gitea
- ✅ Repository list will work

---

**Run the commands above and let me know if it works!**
