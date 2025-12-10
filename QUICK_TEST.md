# Quick Test Commands - Phases 1 & 2

## 🚀 Quick Start (3 Terminals)

### Terminal 1: Docker
```bash
docker compose up -d
docker ps  # Verify running
```

### Terminal 2: Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

## 🧪 Quick Tests

### Test Gitea Integration
```bash
# Visit in browser:
http://localhost:5173/repos

# Or test API:
curl http://localhost:8000/api/repositories
```

### Test Load Scripts
```bash
# Quick issue test (10 issues)
python scripts/load_test_issues.py -n 10 -c 2

# Quick clone test (replace URL)
python scripts/load_test_clone.py http://localhost:3000/USER/REPO.git -n 3 -c 1

# Locust (install first: pip install locust)
locust -f scripts/locustfile.py --host=http://localhost:8000
# Then visit: http://localhost:8089
```

## 📋 Checklist

### Before Testing:
- [ ] Docker Desktop running
- [ ] `docker compose up -d` executed
- [ ] Created test repo in Gitea (http://localhost:3000)
- [ ] Backend running (port 8000)
- [ ] Frontend running (port 5173)

### Phase 1 Tests:
- [ ] Can see repositories at http://localhost:5173/repos
- [ ] Can click and view repository details
- [ ] Can browse files in repository
- [ ] Can view file contents
- [ ] Clone URLs displayed correctly

### Phase 2 Tests:
- [ ] Issue load test runs successfully
- [ ] Clone load test works
- [ ] Locust web UI accessible
- [ ] All tests show >95% success rate

## 🎯 Success Indicators

✅ **Gitea Integration Working:**
- Repositories list shows real data
- File browser navigates correctly
- No "mock data" visible

✅ **Load Testing Working:**
- Scripts complete without errors
- JSON result files created
- Performance metrics displayed

## 📞 Need Help?

See detailed guide: `TESTING_PHASES_1_2.md`

## ⏭️ After Testing

Report results and we'll proceed to Phase 3 (Kubernetes deployment)!
