# Installation Guide

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker Desktop | 24+ | Container orchestration |
| Python | 3.12+ | Backend development |
| Node.js | 20+ | Frontend development |
| Git | Latest | Version control |

## Option 1: Docker (Recommended)

The fastest way to get the entire platform running.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Fastian1337/Nexora.git
cd Nexora
```

### Step 2: Configure Environment

```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Edit `backend/.env` and set:
- `DATABASE_PASSWORD` — A secure database password
- `SECRET_KEY` — A random 64-character string
- `REDIS_PASSWORD` — A secure Redis password (optional for dev)

### Step 3: Start Services

```bash
docker compose -f docker/docker-compose.yml up -d
```

This starts:
- **PostgreSQL** (port 5432) with pgvector extension
- **Redis** (port 6379) for caching
- **FastAPI Backend** (port 8000) with hot-reload
- **Next.js Frontend** (port 3000) with hot-reload
- **Nginx** (port 8080) reverse proxy
- **n8n** (port 5678) workflow engine

### Step 4: Verify

```bash
# Check all services are running
docker compose -f docker/docker-compose.yml ps

# Test backend health
curl http://localhost:8000/api/v1/health

# Test readiness
curl http://localhost:8000/api/v1/health/ready
```

### Step 5: Run Database Migrations

```bash
docker compose -f docker/docker-compose.yml exec backend alembic upgrade head
```

---

## Option 2: Local Development

For development without Docker (requires local PostgreSQL and Redis).

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt

# Copy environment config
cp .env.example .env
# Edit .env with your local DB/Redis credentials

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment config
cp .env.example .env

# Start development server
npm run dev
```

---

## Verify Installation

| Service | URL | Expected |
|---|---|---|
| Backend Health | http://localhost:8000/api/v1/health | `{"status": "healthy"}` |
| Backend Readiness | http://localhost:8000/api/v1/health/ready | `{"status": "ready"}` |
| API Documentation | http://localhost:8000/api/docs | Swagger UI |
| Frontend | http://localhost:3000 | Nexora landing page |
| n8n | http://localhost:5678 | n8n login page |

---

## Troubleshooting

### Port Already in Use

```bash
# Find and kill the process using the port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Failed

Ensure PostgreSQL is running and the credentials in `.env` match your setup.

### Docker Build Fails

```bash
# Clean rebuild
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml build --no-cache
docker compose -f docker/docker-compose.yml up -d
```
