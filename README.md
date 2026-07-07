# Nexora Platform

**AI Employee Platform — Enterprise-grade SaaS for business automation**

Built by **Nexora Technologies**

---

## Mission

Build AI Employees that automate businesses — customer support, voice calls, appointments, marketing, sales, and internal operations.

## Architecture

- **Architecture Style:** Modular Monolith (microservices-ready)
- **Backend:** FastAPI (Python 3.12) with SQLAlchemy 2, Alembic
- **Frontend:** Next.js with TypeScript, TailwindCSS
- **Database:** PostgreSQL 16 with pgvector, Redis 7
- **AI Engine:** LangGraph + LangChain
- **Workflow:** n8n (self-hosted, execution-only)
- **Deployment:** Docker, Nginx

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v24+)
- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- [Git](https://git-scm.com/)

### Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/Fastian1337/Nexora.git
cd Nexora

# 2. Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Start all services via Docker
docker compose -f docker/docker-compose.yml up -d

# 4. Access the application
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API Docs:  http://localhost:8000/api/docs
# n8n:       http://localhost:5678
# Nginx:     http://localhost:8080
```

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements/dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Project Structure

```
nexora/
├── backend/          # FastAPI application
├── frontend/         # Next.js application
├── docker/           # Docker Compose, Nginx, Postgres
├── docs/             # Architecture & setup documentation
├── scripts/          # Automation scripts
├── infrastructure/   # Future IaC configurations
└── tests/            # End-to-end tests
```

See [docs/architecture/folder-structure.md](docs/architecture/folder-structure.md) for detailed structure.

## Documentation

- [Architecture Overview](docs/architecture/overview.md)
- [Clean Architecture](docs/architecture/clean-architecture.md)
- [Folder Structure](docs/architecture/folder-structure.md)
- [Installation Guide](docs/setup/installation.md)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript, TailwindCSS |
| Backend | FastAPI, Python 3.12, Pydantic V2 |
| Database | PostgreSQL 16, pgvector, Redis 7 |
| ORM | SQLAlchemy 2 (async) |
| Migrations | Alembic |
| AI | LangGraph, LangChain |
| Voice | Faster Whisper (STT), Piper/Kokoro (TTS) |
| Workflow | n8n (self-hosted) |
| Deployment | Docker, Nginx, Gunicorn |

## License

Proprietary — Nexora Technologies
