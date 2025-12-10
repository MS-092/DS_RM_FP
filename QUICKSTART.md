# Quick Start Guide - GitForge with Improvements

## Prerequisites
- Docker Desktop running
- Python 3.13+ with venv
- Node.js 18+

## Step 1: Start Infrastructure

```bash
# From project root
docker compose up -d
```

This starts:
- CockroachDB on port 26257 (dashboard on 8080)
- Gitea on port 3000

## Step 2: Start Backend

```bash
cd backend
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

Backend will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

## Step 3: Start Frontend

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Start the dev server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Step 4: Test the Application

### Create a Test Issue via API

```bash
curl -X POST "http://localhost:8000/api/issues" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Issue",
    "description": "This is a test issue",
    "repository": "test-repo",
    "created_by": "test-user"
  }'
```

### View Issues in Frontend

1. Open `http://localhost:5173`
2. Click on "Issues" in the navigation
3. You should see your test issue
4. Click on the issue to view details
5. Try adding a comment

### Check System Health

1. Navigate to "System Status" in the navigation
2. You should see:
   - Backend API: Healthy
   - CockroachDB: Connected
   - Live metrics

## Troubleshooting

### Backend won't start
- Ensure Docker is running
- Check if CockroachDB is accessible: `docker ps`
- Verify dependencies: `pip list | grep sqlalchemy`

### Frontend shows errors
- Check if backend is running on port 8000
- Open browser console for error details
- Verify `.env` file exists in frontend directory

### CORS errors
- Ensure backend CORS middleware includes `http://localhost:5173`
- Check browser console for specific CORS error

### Database connection fails
- Verify CockroachDB is running: `docker ps | grep cockroach`
- Check connection string in `backend/database.py`
- Ensure `sqlalchemy-cockroachdb` is installed

## Available API Endpoints

### Issues
- `GET /api/issues` - List all issues
- `GET /api/issues/{id}` - Get issue by ID
- `POST /api/issues` - Create new issue
- `DELETE /api/issues/{id}` - Delete issue

### Comments
- `GET /api/comments/issue/{issue_id}` - Get comments for an issue
- `POST /api/comments` - Create a comment
- `DELETE /api/comments/{id}` - Delete a comment

### Health
- `GET /api/health` - System health status
- `GET /api/health/ready` - Readiness check
- `GET /api/health/live` - Liveness check

## Next Steps

1. Explore the API documentation at `http://localhost:8000/docs`
2. Create more issues and test the comment functionality
3. Monitor system health in the dashboard
4. Review `IMPROVEMENTS.md` for details on what was added
