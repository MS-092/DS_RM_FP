# Testing Guide - Phases 1 & 2

This guide will help you test the Gitea Integration (Phase 1) and Load Testing Scripts (Phase 2).

## Prerequisites

Before testing, ensure you have:
- ✅ Docker Desktop running
- ✅ Docker Compose services started
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed

## Step 1: Start All Services

### 1.1 Start Docker Services

```bash
# From project root
docker compose up -d

# Verify services are running
docker ps

# You should see:
# - ds_rm_fp-cockroachdb-1
# - ds_rm_fp-gitea-1
```

### 1.2 Create a Test Repository in Gitea

1. Open Gitea: http://localhost:3000
2. If first time:
   - Click "Register" (top right)
   - Create an account (e.g., username: `testuser`, password: `testpass123`)
   - Complete registration
3. Create a test repository:
   - Click "+" (top right) → "New Repository"
   - Repository name: `test-repo`
   - Description: "Test repository for GitForge"
   - Initialize with README: ✅ Check this
   - Click "Create Repository"
4. Add some files (optional):
   - Click "New File"
   - Create `hello.txt` with content "Hello GitForge!"
   - Commit the file

### 1.3 Start Backend

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate

# Install any missing dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 1.4 Start Frontend

```bash
# Terminal 2: Frontend
cd frontend

# Install dependencies if needed
npm install

# Start dev server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

## Step 2: Test Phase 1 - Gitea Integration

### Test 2.1: Repository List

1. Open browser: http://localhost:5173
2. Click "Repositories" in the navigation
3. **Expected**: You should see your test repository listed
4. **Verify**:
   - Repository name is displayed
   - Description is shown
   - Stats (stars, forks, issues) are visible
   - Search box works

**Screenshot what you see!**

### Test 2.2: Repository Details

1. Click on your test repository
2. **Expected**: Repository detail page opens
3. **Verify**:
   - Repository name and description
   - Clone URLs (HTTPS and SSH)
   - File browser showing files
   - Stats (stars, forks, issues, branch)

**Try copying the clone URL!**

### Test 2.3: File Browsing

1. On repository detail page, you should see files
2. Click on a file (e.g., `README.md` or `hello.txt`)
3. **Expected**: File content is displayed
4. **Verify**:
   - File name is shown
   - File size is displayed
   - Content is readable
   - "Back to files" button works

**Try navigating between files!**

### Test 2.4: API Endpoints

Test the API directly:

```bash
# List repositories
curl http://localhost:8000/api/repositories

# Get specific repository (replace with your username/repo)
curl http://localhost:8000/api/repositories/testuser/test-repo

# Browse repository contents
curl http://localhost:8000/api/repositories/testuser/test-repo/contents/

# Get file content
curl http://localhost:8000/api/repositories/testuser/test-repo/file/README.md
```

**Expected**: JSON responses with repository data

### Test 2.5: Error Handling

1. Try accessing a non-existent repository:
   - Visit: http://localhost:5173/repos/fake/repo
2. **Expected**: Error message displayed
3. Stop Gitea: `docker stop ds_rm_fp-gitea-1`
4. Refresh repository list
5. **Expected**: Error message about Gitea being unavailable
6. Restart Gitea: `docker start ds_rm_fp-gitea-1`

## Step 3: Test Phase 2 - Load Testing Scripts

### Test 3.1: Issue Creation Load Test

```bash
# From project root
# Small test first
python scripts/load_test_issues.py -n 10 -c 2

# Expected output:
# Starting load test: 10 issues, 2 concurrent requests
# Creating issues 1 to 2...
# Creating issues 3 to 4...
# ...
# LOAD TEST RESULTS
# Total Issues:        10
# Successful:          10 (100.0%)
# Throughput:          X.XX issues/sec
```

**What to check:**
- ✅ All issues created successfully (100%)
- ✅ Throughput > 10 issues/sec
- ✅ Average response time < 500ms
- ✅ JSON results file created

**Verify in UI:**
1. Go to http://localhost:5173/issues
2. You should see the 10 new test issues

### Test 3.2: Larger Load Test

```bash
# More aggressive test
python scripts/load_test_issues.py -n 100 -c 10

# Expected:
# Successful: 100 (100.0%)
# Throughput: >50 issues/sec
```

**What to check:**
- ✅ Success rate > 95%
- ✅ No errors in backend logs
- ✅ Database still responsive

### Test 3.3: Repository Clone Load Test

**First, get your repository clone URL from Gitea:**
1. Go to http://localhost:3000
2. Open your test repository
3. Copy the HTTPS clone URL (e.g., `http://localhost:3000/testuser/test-repo.git`)

```bash
# Test cloning (replace with your URL)
python scripts/load_test_clone.py http://localhost:3000/testuser/test-repo.git -n 5 -c 2

# Expected output:
# Starting clone test: 5 clones, 2 concurrent
# Cloning batch 1 to 2...
# ...
# CLONE TEST RESULTS
# Total Clones:        5
# Successful:          5 (100.0%)
# Average clone time:  X.XXs
```

**What to check:**
- ✅ All clones successful (100%)
- ✅ Average clone time < 10s
- ✅ Temporary directory cleaned up

### Test 3.4: Locust Load Test

**Install Locust first:**
```bash
pip install locust
```

**Run Locust:**
```bash
# Start Locust with web UI
locust -f scripts/locustfile.py --host=http://localhost:8000
```

**Test with Web UI:**
1. Open http://localhost:8089
2. Enter:
   - Number of users: `10`
   - Spawn rate: `2`
3. Click "Start swarming"
4. **Watch the charts:**
   - Total requests per second
   - Response times
   - Number of users
   - Failures

**Let it run for 1-2 minutes, then:**
- Click "Stop"
- Review statistics
- Check "Charts" tab

**What to check:**
- ✅ Requests per second > 10
- ✅ Median response time < 200ms
- ✅ Failure rate < 1%

### Test 3.5: Headless Load Test

```bash
# Run without web UI
locust -f scripts/locustfile.py --host=http://localhost:8000 --headless -u 20 -r 5 -t 60s

# This will:
# - Simulate 20 users
# - Spawn 5 users per second
# - Run for 60 seconds
```

**Expected output:**
```
Type     Name              # reqs      # fails  |     Avg     Min     Max  Median  |   req/s failures/s
--------|------------------|-------|-------------|-------|-------|-------|--------|---------|-----------
GET      /api/health           50     0(0.00%)  |      10       5      50      10  |    0.83        0.00
GET      /api/issues          100     0(0.00%)  |      25      10     100      20  |    1.67        0.00
...
```

## Step 4: Verify Everything Works

### Checklist

**Phase 1 - Gitea Integration:**
- [ ] Repositories list shows real data from Gitea
- [ ] Repository details page works
- [ ] File browser navigates directories
- [ ] File content viewer displays files
- [ ] Clone URLs are correct
- [ ] Search functionality works
- [ ] Error handling works (when Gitea is down)

**Phase 2 - Load Testing:**
- [ ] Issue creation script works
- [ ] Clone script works
- [ ] Locust web UI works
- [ ] Headless mode works
- [ ] Results files are created
- [ ] Statistics are accurate

## Troubleshooting

### Problem: "Failed to fetch repositories from Gitea"

**Solution:**
```bash
# Check Gitea is running
docker ps | grep gitea

# Check Gitea is accessible
curl http://localhost:3000

# Restart Gitea if needed
docker restart ds_rm_fp-gitea-1
```

### Problem: "Repository not found"

**Solution:**
- Make sure you created a repository in Gitea
- Check the repository is public (not private)
- Verify the URL format: `/repos/username/reponame`

### Problem: Load test scripts fail

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check Python dependencies
pip install httpx asyncio

# For clone test, verify git is installed
git --version
```

### Problem: Locust won't start

**Solution:**
```bash
# Install locust
pip install locust

# Verify installation
locust --version

# Check the locustfile
python -m py_compile scripts/locustfile.py
```

## Expected Performance Benchmarks

### Good Performance:
- **Issue Creation**: >50 issues/sec
- **API Response**: <200ms average
- **Clone Time**: <5s for small repos
- **Success Rate**: >99%

### Acceptable Performance:
- **Issue Creation**: >20 issues/sec
- **API Response**: <500ms average
- **Clone Time**: <10s for small repos
- **Success Rate**: >95%

### Poor Performance (investigate):
- Issue creation <10 issues/sec
- API response >1000ms
- Clone time >20s
- Success rate <90%

## Next Steps

After successful testing:

1. **Document your results:**
   - Take screenshots
   - Note performance numbers
   - Save test output

2. **Ready for Phase 3:**
   - Kubernetes/Minikube deployment
   - Ingress configuration
   - Service mesh setup

3. **Report any issues:**
   - Note what didn't work
   - Share error messages
   - Describe unexpected behavior

## Success Criteria

✅ **Phase 1 is successful if:**
- You can see real repositories from Gitea
- You can browse files and directories
- You can view file contents
- Clone URLs are displayed correctly

✅ **Phase 2 is successful if:**
- Load test scripts run without errors
- Performance meets acceptable benchmarks
- Results files are generated
- Locust web UI works

---

**Once you've tested everything, let me know the results and we'll proceed to Phase 3!**
