# GitForge: Distributed System Resilience Research Platform

GitForge is a specialized distributed system architecture designed to serve as a rigorous testbed for empirical fault tolerance research. Operating within a Kubernetes-orchestrated microservices environment, it provides a controlled setting to strictly evaluate and compare **Checkpointing**, **Replication**, and **Hybrid** recovery strategies.

Beyond its role as a functional Git hosting service (similar to GitHub/Gitea), its primary engineering purpose is to facilitate the quantitative analysis of **Recovery Time Objective (RTO)** and **Data Integrity** under induced chaotic failure conditions.

## 🚀 Recent Improvements

- ✅ **Full Backend-Frontend Integration**: Real API communication (no more mock data)
- ✅ **Comments System**: Create and view comments on issues
- ✅ **Health Monitoring**: Live system status dashboard
- ✅ **Better UX**: Loading states, error handling, and search functionality
- ✅ **CORS Support**: Proper cross-origin configuration
- ✅ **API Documentation**: Interactive Swagger docs at `/docs`

See [IMPROVEMENTS.md](./docs/IMPROVEMENTS.md) for detailed changes.

## 📁 Project Structure

- `frontend/`: React-based User Interface with Vite
- `backend/`: FastAPI Gateway and Distributed Logic
- `infra/`: Kubernetes manifests and Chaos Mesh configurations

## 🏃 Quick Start

See [QUICKSTART.md](./docs/QUICKSTART.md) for detailed instructions.

### TL;DR

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Start backend (in new terminal)
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 3. Start frontend (in new terminal)
cd frontend
npm install
npm run dev
```

Then visit:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Gitea**: http://localhost:3000
- **CockroachDB Dashboard**: http://localhost:8080

## 🎯 Features

### Frontend
- 📊 **Dashboard**: System health monitoring with live updates
- 📝 **Issue Tracker**: Create, view, and comment on issues
- 🔍 **Search & Filter**: Find issues quickly
- 🎨 **Modern UI**: Built with React, Tailwind CSS, and shadcn/ui
- ⚡ **Real-time Updates**: Auto-refresh system status

### Backend
- 🔌 **RESTful API**: FastAPI with automatic OpenAPI docs
- 💾 **Distributed Database**: CockroachDB for fault tolerance
- 🔄 **Git Proxy**: Forward Git operations to Gitea
- 📈 **Metrics**: Prometheus integration
- 🏥 **Health Checks**: Kubernetes-ready probes

### Infrastructure
- ☸️ **Kubernetes Ready**: StatefulSet manifests for Gitea and CockroachDB
- 🌪️ **Chaos Engineering**: Chaos Mesh experiments for fault injection
- 📊 **Monitoring**: Grafana dashboard configurations

## 🧪 Research Objectives

The platform is instrumented to conduct specific empirical studies:

1.  **Fault Tolerance efficacy**: Comparative analysis of Baseline, Checkpointing, Replication, and Hybrid strategies.
2.  **Recovery Performance**: Millisecond-precision measurement of Recovery Time Objective (RTO) following catastrophic pod failure.
3.  **Data Durability**: Quantitative assessment of data loss (RPO) during sudden termination events.
4.  **Overhead Analysis**: Evaluation of the operational cost (latency, resource usage) associated with each resilience strategy.

See [RESEARCH_PROTOCOL.md](./docs/RESEARCH_PROTOCOL.md) for the detailed experimental methodology.

## 📚 API Endpoints

### Issues
- `GET /api/issues` - List all issues
- `GET /api/issues/{id}` - Get specific issue
- `POST /api/issues` - Create new issue
- `DELETE /api/issues/{id}` - Delete issue

### Comments
- `GET /api/comments/issue/{issue_id}` - Get comments for issue
- `POST /api/comments` - Create comment
- `DELETE /api/comments/{id}` - Delete comment

### Health
- `GET /api/health` - System health check
- `GET /api/health/ready` - Readiness probe
- `GET /api/health/live` - Liveness probe

Full API documentation available at `http://localhost:8000/docs` when running.

## 🛠️ Technology Stack

**Frontend:**
- React 19 + Vite
- Tailwind CSS
- Axios for API calls
- React Router for navigation

**Backend:**
- FastAPI (Python)
- SQLAlchemy with async support
- CockroachDB (PostgreSQL-compatible)
- Prometheus client

**Infrastructure:**
- Docker & Docker Compose
- Kubernetes (for production)
- Chaos Mesh (for experiments)
- Grafana (for visualization)

## 📖 Documentation

### Quick Links
- **[User Guide](./docs/USER_GUIDE.md)** - Complete guide on using GitForge
- **[Quick Start](./docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[API Reference](./docs/API_REFERENCE.md)** - Complete API documentation
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Testing Guide](./docs/TESTING.md)** - Testing strategies and examples
- **[Architecture](./docs/ARCHITECTURE.md)** - System architecture and design
- **[Improvements Log](./docs/IMPROVEMENTS.md)** - Latest improvements and changes

### For Developers
- **[Testing Guide](./docs/TESTING.md)** - How to run and write tests
- **[API Reference](./docs/API_REFERENCE.md)** - API endpoints and examples
- **[Architecture](./docs/ARCHITECTURE.md)** - System design and components

### For Operators
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Deploy to production
- **[User Guide](./docs/USER_GUIDE.md)** - Troubleshooting section
- **[Architecture](./docs/ARCHITECTURE.md)** - Observability and monitoring

### For Researchers
- **[Architecture](./docs/ARCHITECTURE.md)** - Fault tolerance mechanisms
- **[Testing Guide](./docs/TESTING.md)** - Chaos engineering experiments
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Kubernetes and Chaos Mesh setup

## 🧪 Testing

The project includes comprehensive testing:

```bash
# Backend tests
cd backend
pytest --cov=. --cov-report=html

# Frontend tests (coming soon)
cd frontend
npm test
```

See [Testing Guide](./docs/TESTING.md) for details.

## 🚀 Deployment

### Local Development
See [QUICKSTART.md](./docs/QUICKSTART.md)

### Production Deployment
See [Deployment Guide](./docs/DEPLOYMENT.md) for:
- Docker deployment
- Kubernetes deployment
- Security configuration
- Monitoring setup
- Backup procedures

## 🤝 Contributing

This is a research project. Contributions are welcome! Areas for improvement:
- Authentication & authorization
- More comprehensive testing
- Additional Chaos Mesh experiments
- Performance optimizations

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

See [Testing Guide](./docs/TESTING.md) for testing requirements.

## Support

- **Documentation**: Check the [docs](./docs/) directory
- **Issues**: Create an issue in the repository
- **API Docs**: http://localhost:8000/docs (when running)

## License

- This project is for educational and research purposes.

## Project Status

- ✅ Core functionality complete
- ✅ Full documentation
- ✅ Testing infrastructure
- ✅ CI/CD pipeline
- ✅ Production-ready
- 🔄 Authentication (planned) / Currently navigated to Gitea authentication page
- 🔄 Advanced features (planned)
