# GitForge Load Testing Scripts

This directory contains scripts for load testing the GitForge distributed system.

## Available Scripts

### 1. Issue Creation Load Test (`load_test_issues.py`)

Tests the API's ability to handle concurrent issue creation.

**Usage:**
```bash
# Create 100 issues with 10 concurrent requests
python scripts/load_test_issues.py -n 100 -c 10

# Create 500 issues with 20 concurrent requests
python scripts/load_test_issues.py -n 500 -c 20

# Use custom API URL
python scripts/load_test_issues.py -n 100 --api-url http://your-api:8000
```

**Options:**
- `-n, --num-issues`: Number of issues to create (default: 100)
- `-c, --concurrent`: Number of concurrent requests (default: 10)
- `--api-url`: API base URL (default: http://localhost:8000)

**Output:**
- Console summary with statistics
- JSON file with detailed results

### 2. Repository Clone Load Test (`load_test_clone.py`)

Tests Git clone performance under load.

**Usage:**
```bash
# Clone a repository 10 times with 3 concurrent clones
python scripts/load_test_clone.py http://localhost:3000/user/repo.git -n 10 -c 3

# More aggressive test
python scripts/load_test_clone.py http://localhost:3000/user/repo.git -n 50 -c 5
```

**Options:**
- `repo_url`: Repository URL to clone (required)
- `-n, --num-clones`: Number of times to clone (default: 10)
- `-c, --concurrent`: Number of concurrent clones (default: 3)

**Requirements:**
- Git must be installed

**Output:**
- Console summary with clone times and data transfer
- JSON file with detailed results

### 3. Locust Load Test (`locustfile.py`)

Comprehensive load testing with realistic user behavior.

**Usage:**
```bash
# Install locust first
pip install locust

# Run with web UI
locust -f scripts/locustfile.py --host=http://localhost:8000

# Run headless (no web UI)
locust -f scripts/locustfile.py --host=http://localhost:8000 --headless -u 10 -r 2 -t 60s
```

**Options:**
- `-u, --users`: Number of concurrent users
- `-r, --spawn-rate`: User spawn rate (users per second)
- `-t, --run-time`: Test duration (e.g., 60s, 5m, 1h)

**Features:**
- Simulates realistic user behavior
- Multiple user types (regular users and admins)
- Weighted task distribution
- Real-time statistics via web UI (http://localhost:8089)

## Test Scenarios

### Scenario 1: API Performance Test
```bash
# Test issue creation performance
python scripts/load_test_issues.py -n 1000 -c 50

# Expected: >100 issues/sec on local machine
```

### Scenario 2: Git Operations Test
```bash
# First, create a test repository in Gitea
# Then test clone performance
python scripts/load_test_clone.py http://localhost:3000/testuser/testrepo.git -n 20 -c 4

# Expected: <5s per clone for small repos
```

### Scenario 3: Mixed Workload Test
```bash
# Simulate 50 users for 5 minutes
locust -f scripts/locustfile.py --host=http://localhost:8000 --headless -u 50 -r 5 -t 5m

# Expected: <200ms average response time
```

### Scenario 4: Stress Test
```bash
# Push the system to its limits
locust -f scripts/locustfile.py --host=http://localhost:8000 --headless -u 200 -r 10 -t 10m

# Monitor: CPU, memory, database connections
```

## Interpreting Results

### Good Performance Indicators:
- **Issue Creation**: >100 issues/sec
- **API Response Time**: <200ms average
- **Clone Time**: <5s for small repos
- **Success Rate**: >99%

### Warning Signs:
- Response times >500ms
- Success rate <95%
- Increasing error rates over time
- Database connection errors

## Tips for Effective Load Testing

1. **Start Small**: Begin with low load and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and database metrics
3. **Test Incrementally**: Test one component at a time
4. **Use Realistic Data**: Match production patterns
5. **Run Multiple Times**: Results should be consistent
6. **Document Baselines**: Record performance baselines for comparison

## Troubleshooting

### "Connection refused" errors
- Ensure backend is running: `uvicorn main:app --reload`
- Check API URL is correct
- Verify ports are not blocked

### "Too many open files" errors
- Increase system limits: `ulimit -n 10000`
- Reduce concurrent requests

### Slow performance
- Check database connection pool size
- Monitor database query performance
- Verify network latency
- Check for resource constraints

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/performance-test.yml
- name: Run Performance Tests
  run: |
    python scripts/load_test_issues.py -n 100 -c 10
    # Fail if throughput < 50 issues/sec
```

## Advanced Usage

### Custom Test Scenarios

Create your own test script:

```python
import asyncio
import httpx

async def custom_test():
    async with httpx.AsyncClient() as client:
        # Your custom test logic
        pass

asyncio.run(custom_test())
```

### Distributed Load Testing

Run Locust in distributed mode:

```bash
# Master
locust -f scripts/locustfile.py --master --host=http://localhost:8000

# Workers (on different machines)
locust -f scripts/locustfile.py --worker --master-host=<master-ip>
```

## See Also

- [Testing Guide](../docs/TESTING.md) - Complete testing documentation
- [API Reference](../docs/API_REFERENCE.md) - API endpoint details
- [Deployment Guide](../docs/DEPLOYMENT.md) - Production deployment
