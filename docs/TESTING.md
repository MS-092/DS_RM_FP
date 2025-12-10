# GitForge Testing Guide

## Overview

This guide covers testing strategies for the GitForge distributed system, including unit tests, integration tests, and chaos engineering experiments.

## Backend Testing

### Setup

Install test dependencies:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_issues.py

# Run specific test
pytest tests/test_issues.py::test_create_issue

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test Structure

```
backend/tests/
├── __init__.py
├── test_api.py          # Basic API tests
├── test_issues.py       # Issues endpoint tests
└── test_comments.py     # Comments endpoint tests
```

### Writing Tests

#### Basic Test Example

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_example():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
```

#### Test with Database

```python
@pytest.fixture
async def test_db():
    """Create test database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_with_db(client, test_db):
    # Your test here
    pass
```

### Coverage Reports

After running tests with coverage:

```bash
# View HTML report
open htmlcov/index.html

# View terminal report
pytest --cov=. --cov-report=term-missing
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install
```

### Running Tests

```bash
# Run tests (when implemented)
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch

# Run linter
npm run lint

# Fix linting issues
npm run lint:fix
```

### Test Structure (To be implemented)

```
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── Button.test.jsx
│   │   └── Input.test.jsx
│   ├── pages/
│   │   ├── IssueList.test.jsx
│   │   └── IssueDetail.test.jsx
│   └── lib/
│       └── api.test.js
```

### Example Component Test (Vitest + React Testing Library)

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '../components/ui/button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
});
```

## Integration Testing

### API Integration Tests

Test the full request/response cycle:

```python
@pytest.mark.asyncio
async def test_full_issue_lifecycle(client, test_db):
    # Create issue
    create_response = await client.post("/api/issues", json={
        "title": "Test Issue",
        "description": "Test",
        "repository": "test-repo",
        "created_by": "user"
    })
    assert create_response.status_code == 200
    issue_id = create_response.json()["id"]
    
    # Get issue
    get_response = await client.get(f"/api/issues/{issue_id}")
    assert get_response.status_code == 200
    
    # Add comment
    comment_response = await client.post("/api/comments", json={
        "issue_id": issue_id,
        "user": "commenter",
        "body": "Great issue!"
    })
    assert comment_response.status_code == 201
    
    # Get comments
    comments_response = await client.get(f"/api/comments/issue/{issue_id}")
    assert len(comments_response.json()) == 1
    
    # Delete issue
    delete_response = await client.delete(f"/api/issues/{issue_id}")
    assert delete_response.status_code == 200
```

### End-to-End Testing

Use tools like Playwright or Cypress for E2E tests:

```javascript
// Example with Playwright
import { test, expect } from '@playwright/test';

test('create and view issue', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:5173');
  
  // Go to issues page
  await page.click('text=Issues');
  
  // Should see issues list
  await expect(page.locator('h1')).toContainText('Global Issue Tracker');
  
  // Click on an issue
  await page.click('text=Test Issue');
  
  // Should see issue details
  await expect(page.locator('h1')).toContainText('Test Issue');
});
```

## Load Testing

### Using Locust

Create `backend/locustfile.py`:

```python
from locust import HttpUser, task, between

class GitForgeUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def list_issues(self):
        self.client.get("/api/issues")
    
    @task(2)
    def get_issue(self):
        self.client.get("/api/issues/1")
    
    @task(1)
    def health_check(self):
        self.client.get("/api/health")
```

Run load test:

```bash
locust -f backend/locustfile.py --host=http://localhost:8000
```

### Using Apache Bench

```bash
# Test issues endpoint
ab -n 1000 -c 10 http://localhost:8000/api/issues

# Test health endpoint
ab -n 10000 -c 100 http://localhost:8000/api/health
```

## Chaos Engineering

### Prerequisites

- Kubernetes cluster
- Chaos Mesh installed

### Running Chaos Experiments

#### Pod Kill Experiment

```bash
# Apply pod kill experiment
kubectl apply -f infra/chaos-mesh/pod-kill.yaml

# Watch the chaos
kubectl get podchaos -n gitforge -w

# View affected pods
kubectl get pods -n gitforge -w

# Check logs
kubectl logs -f deployment/backend -n gitforge
```

#### Network Delay Experiment

```bash
# Apply network delay
kubectl apply -f infra/chaos-mesh/network-delay.yaml

# Monitor latency
kubectl exec -it deployment/backend -n gitforge -- curl -w "@curl-format.txt" http://cockroachdb:26257

# Check metrics
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit http://localhost:9090
```

### Measuring Recovery Time

Create a monitoring script:

```bash
#!/bin/bash
# monitor-recovery.sh

START_TIME=$(date +%s)

# Wait for pod to be killed
kubectl wait --for=delete pod -l app=backend -n gitforge --timeout=60s

# Wait for pod to be ready again
kubectl wait --for=condition=ready pod -l app=backend -n gitforge --timeout=120s

END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))

echo "Recovery time: ${RECOVERY_TIME} seconds"
```

### Chaos Mesh Dashboard

Access the Chaos Mesh dashboard:

```bash
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
```

Visit http://localhost:2333

## Performance Testing

### Database Performance

Test CockroachDB performance:

```bash
# Connect to CockroachDB
kubectl exec -it cockroachdb-0 -n gitforge -- ./cockroach sql --insecure

# Run performance test
CREATE TABLE test (id INT PRIMARY KEY, data STRING);
INSERT INTO test SELECT generate_series(1, 10000), md5(random()::text);
SELECT count(*) FROM test;
```

### API Performance Benchmarks

Create `backend/benchmark.py`:

```python
import asyncio
import time
from httpx import AsyncClient

async def benchmark_endpoint(url, num_requests=1000):
    async with AsyncClient() as client:
        start = time.time()
        
        tasks = [client.get(url) for _ in range(num_requests)]
        responses = await asyncio.gather(*tasks)
        
        end = time.time()
        duration = end - start
        
        success = sum(1 for r in responses if r.status_code == 200)
        
        print(f"URL: {url}")
        print(f"Requests: {num_requests}")
        print(f"Duration: {duration:.2f}s")
        print(f"RPS: {num_requests/duration:.2f}")
        print(f"Success rate: {success/num_requests*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(benchmark_endpoint("http://localhost:8000/api/health"))
```

## Continuous Integration

Tests run automatically on:
- Every push to main/develop
- Every pull request

See `.github/workflows/ci-cd.yml` for CI configuration.

### Local CI Simulation

Run the same tests that CI runs:

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=xml

# Frontend linting
cd frontend
npm run lint

# Frontend build
npm run build
```

## Test Data Management

### Fixtures

Create reusable test data:

```python
# conftest.py
import pytest

@pytest.fixture
def sample_issue():
    return {
        "title": "Sample Issue",
        "description": "Sample description",
        "repository": "test-repo",
        "created_by": "test-user"
    }

@pytest.fixture
def sample_comment():
    return {
        "user": "commenter",
        "body": "Sample comment"
    }
```

### Database Seeding

Create seed data for testing:

```python
# seed.py
async def seed_database():
    async with AsyncSessionLocal() as session:
        # Create test issues
        for i in range(10):
            issue = Issue(
                title=f"Test Issue {i}",
                description=f"Description {i}",
                repository="test-repo",
                created_by="seeder"
            )
            session.add(issue)
        
        await session.commit()
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Use Fixtures**: Reuse common setup code
3. **Mock External Services**: Don't rely on external APIs
4. **Test Edge Cases**: Not just happy paths
5. **Keep Tests Fast**: Use in-memory databases when possible
6. **Meaningful Assertions**: Test behavior, not implementation
7. **Clean Up**: Always clean up test data
8. **Document Tests**: Add docstrings explaining what you're testing

## Troubleshooting Tests

### Tests Fail Locally

```bash
# Clear pytest cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database connection
docker ps | grep cockroach
```

### Tests Pass Locally but Fail in CI

- Check environment variables
- Verify service dependencies
- Check for timing issues (add waits)
- Review CI logs carefully

### Slow Tests

```bash
# Find slowest tests
pytest --durations=10

# Run tests in parallel
pytest -n auto
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Chaos Mesh Documentation](https://chaos-mesh.org/docs/)
- [Vitest Documentation](https://vitest.dev/)

## Next Steps

1. Add more test coverage
2. Implement E2E tests
3. Set up performance benchmarks
4. Create chaos engineering playbooks
5. Automate test reporting
