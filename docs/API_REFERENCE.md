# GitForge API Reference

## Base URL

```
http://localhost:8000
```

For production, replace with your actual domain.

## Authentication

*Note: Authentication is not yet implemented. All endpoints are currently public.*

## Response Format

All API responses follow this general structure:

### Success Response
```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Endpoints

### Root

#### GET /

Welcome endpoint.

**Response**
```json
{
  "message": "Welcome to GitForge Distributed System"
}
```

---

### Health Check

#### GET /api/health

Get system health status.

**Response**
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

**Status Values**
- `healthy` - All systems operational
- `degraded` - Some systems experiencing issues
- `error` - Critical systems down

#### GET /api/health/ready

Kubernetes readiness probe.

**Response**
```json
{
  "ready": true
}
```

#### GET /api/health/live

Kubernetes liveness probe.

**Response**
```json
{
  "alive": true
}
```

---

### Issues

#### GET /api/issues

List all issues.

**Response**
```json
[
  {
    "id": 1,
    "title": "Bug in login page",
    "description": "Login button not working",
    "status": "open",
    "repository": "frontend-app",
    "created_by": "john-doe",
    "created_at": "2025-12-09T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Add dark mode",
    "description": "Implement dark mode theme",
    "status": "closed",
    "repository": "frontend-app",
    "created_by": "jane-smith",
    "created_at": "2025-12-08T15:30:00Z"
  }
]
```

#### GET /api/issues/{id}

Get a specific issue by ID.

**Parameters**
- `id` (path, integer, required) - Issue ID

**Response**
```json
{
  "id": 1,
  "title": "Bug in login page",
  "description": "Login button not working on mobile devices",
  "status": "open",
  "repository": "frontend-app",
  "created_by": "john-doe",
  "created_at": "2025-12-09T10:00:00Z"
}
```

**Error Responses**
- `404 Not Found` - Issue doesn't exist

#### POST /api/issues

Create a new issue.

**Request Body**
```json
{
  "title": "Bug in login page",
  "description": "Login button not working",
  "repository": "frontend-app",
  "created_by": "john-doe"
}
```

**Fields**
- `title` (string, required) - Issue title
- `description` (string, optional) - Detailed description
- `repository` (string, required) - Repository name
- `created_by` (string, optional, default: "anonymous") - Creator username

**Response** (201 Created)
```json
{
  "id": 1,
  "title": "Bug in login page",
  "description": "Login button not working",
  "status": "open",
  "repository": "frontend-app",
  "created_by": "john-doe",
  "created_at": "2025-12-09T10:00:00Z"
}
```

**Error Responses**
- `422 Unprocessable Entity` - Invalid request data

#### DELETE /api/issues/{id}

Delete an issue.

**Parameters**
- `id` (path, integer, required) - Issue ID

**Response**
```json
{
  "status": "deleted"
}
```

**Error Responses**
- `404 Not Found` - Issue doesn't exist

---

### Comments

#### GET /api/comments/issue/{issue_id}

Get all comments for a specific issue.

**Parameters**
- `issue_id` (path, integer, required) - Issue ID

**Response**
```json
[
  {
    "id": 1,
    "issue_id": 1,
    "user": "alice",
    "body": "I'm experiencing the same issue",
    "created_at": "2025-12-09T11:00:00Z"
  },
  {
    "id": 2,
    "issue_id": 1,
    "user": "bob",
    "body": "This is fixed in the latest version",
    "created_at": "2025-12-09T12:00:00Z"
  }
]
```

**Notes**
- Returns empty array if no comments exist
- Comments are ordered by creation time (oldest first)

#### POST /api/comments

Create a new comment on an issue.

**Request Body**
```json
{
  "issue_id": 1,
  "user": "alice",
  "body": "I'm experiencing the same issue"
}
```

**Fields**
- `issue_id` (integer, required) - ID of the issue to comment on
- `user` (string, required) - Username of commenter
- `body` (string, required) - Comment text

**Response** (201 Created)
```json
{
  "id": 1,
  "issue_id": 1,
  "user": "alice",
  "body": "I'm experiencing the same issue",
  "created_at": "2025-12-09T11:00:00Z"
}
```

**Error Responses**
- `422 Unprocessable Entity` - Invalid request data

#### DELETE /api/comments/{id}

Delete a comment.

**Parameters**
- `id` (path, integer, required) - Comment ID

**Response**
```json
{
  "status": "deleted",
  "id": 1
}
```

**Error Responses**
- `404 Not Found` - Comment doesn't exist

---

### Git Proxy

#### GET /git/{path}
#### POST /git/{path}

Proxy Git operations to Gitea.

**Parameters**
- `path` (path, string, required) - Git path (e.g., `username/repo.git/info/refs`)

**Example**
```bash
# Clone repository
git clone http://localhost:8000/git/username/repo.git

# Push changes
git push http://localhost:8000/git/username/repo.git
```

**Notes**
- Forwards all Git HTTP operations to Gitea
- Supports both GET and POST methods
- Streams responses for large operations

---

### Metrics

#### GET /metrics

Prometheus metrics endpoint.

**Response** (text/plain)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/issues"} 42
http_requests_total{method="POST",endpoint="/api/issues"} 5

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 35
http_request_duration_seconds_bucket{le="0.5"} 40
http_request_duration_seconds_sum 12.5
http_request_duration_seconds_count 42
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI where you can:
- Browse all endpoints
- See request/response schemas
- Test API calls directly
- Download OpenAPI specification

Alternative documentation at `http://localhost:8000/redoc`

---

## Code Examples

### Python

```python
import requests

# List issues
response = requests.get("http://localhost:8000/api/issues")
issues = response.json()

# Create issue
new_issue = {
    "title": "New feature request",
    "description": "Add export functionality",
    "repository": "backend-api",
    "created_by": "developer"
}
response = requests.post("http://localhost:8000/api/issues", json=new_issue)
issue = response.json()

# Add comment
comment = {
    "issue_id": issue["id"],
    "user": "reviewer",
    "body": "Great idea!"
}
response = requests.post("http://localhost:8000/api/comments", json=comment)
```

### JavaScript

```javascript
// Using fetch
async function getIssues() {
  const response = await fetch('http://localhost:8000/api/issues');
  const issues = await response.json();
  return issues;
}

async function createIssue(issueData) {
  const response = await fetch('http://localhost:8000/api/issues', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(issueData),
  });
  return await response.json();
}

// Using axios
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// List issues
const issues = await api.get('/api/issues');

// Create issue
const newIssue = await api.post('/api/issues', {
  title: 'Bug report',
  description: 'Found a bug',
  repository: 'frontend',
  created_by: 'user1',
});
```

### cURL

```bash
# List issues
curl http://localhost:8000/api/issues

# Get specific issue
curl http://localhost:8000/api/issues/1

# Create issue
curl -X POST http://localhost:8000/api/issues \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New issue",
    "description": "Issue description",
    "repository": "my-repo",
    "created_by": "user1"
  }'

# Add comment
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -d '{
    "issue_id": 1,
    "user": "commenter",
    "body": "Comment text"
  }'

# Delete issue
curl -X DELETE http://localhost:8000/api/issues/1

# Health check
curl http://localhost:8000/api/health
```

---

## Rate Limiting

*Note: Rate limiting is not yet implemented.*

Future implementation will include:
- 100 requests per minute per IP
- 1000 requests per hour per IP
- Custom limits for authenticated users

---

## Pagination

*Note: Pagination is not yet implemented.*

Future implementation will support:
```
GET /api/issues?page=1&per_page=20
```

---

## Filtering and Sorting

*Note: Advanced filtering is not yet implemented.*

Future implementation will support:
```
GET /api/issues?status=open&repository=frontend&sort=created_at&order=desc
```

---

## Webhooks

*Note: Webhooks are not yet implemented.*

Future implementation will allow subscribing to events:
- Issue created
- Issue updated
- Issue closed
- Comment added

---

## Versioning

Current API version: `v1`

The API is currently unversioned. Future versions will use URL versioning:
```
http://localhost:8000/api/v1/issues
http://localhost:8000/api/v2/issues
```

---

## Error Handling

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Not Found Errors

```json
{
  "detail": "Issue not found"
}
```

### Server Errors

```json
{
  "detail": "Internal server error"
}
```

---

## CORS

CORS is enabled for:
- `http://localhost:5173` (Frontend dev server)
- `http://localhost:3000` (Gitea)

All methods and headers are allowed.

---

## Best Practices

1. **Always check status codes** - Don't assume 200 OK
2. **Handle errors gracefully** - Display user-friendly messages
3. **Use appropriate HTTP methods** - GET for reading, POST for creating, DELETE for deleting
4. **Include Content-Type header** - Always use `application/json`
5. **Validate input** - Check data before sending to API
6. **Cache when appropriate** - Cache GET requests to reduce load
7. **Use health checks** - Monitor API availability

---

## Support

For issues or questions:
- Check the [User Guide](./USER_GUIDE.md)
- Review [Troubleshooting](./USER_GUIDE.md#troubleshooting)
- Create an issue in the repository
- Check server logs for detailed error messages

---

## Changelog

### v1.0.0 (Current)
- Initial API release
- Issues CRUD operations
- Comments CRUD operations
- Health check endpoints
- Git proxy functionality
- Prometheus metrics
