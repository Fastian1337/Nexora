# Folder Structure

## Complete Project Layout

```
nexora/
│
├── backend/                            # FastAPI Backend Application
│   ├── app/                            # Application source code
│   │   ├── __init__.py
│   │   ├── main.py                     # App factory + lifespan + middleware registration
│   │   │
│   │   ├── config/                     # Configuration management
│   │   │   ├── settings.py             # Pydantic Settings (env var loading)
│   │   │   └── logging.py             # Structured logging (structlog)
│   │   │
│   │   ├── core/                       # Domain layer (no infrastructure deps)
│   │   │   ├── exceptions.py           # Domain exception hierarchy
│   │   │   ├── constants.py            # App-wide constants
│   │   │   └── interfaces/             # Abstract interfaces (ports)
│   │   │       └── repository.py       # CRUD contract for all repositories
│   │   │
│   │   ├── models/                     # SQLAlchemy ORM models
│   │   │   └── base.py                 # BaseModel (UUID, org_id, timestamps, audit)
│   │   │
│   │   ├── schemas/                    # Pydantic V2 request/response schemas
│   │   │   ├── base.py                 # ApiResponse envelope, pagination
│   │   │   └── health.py              # Health check response models
│   │   │
│   │   ├── repositories/              # Data access implementations (adapters)
│   │   │   └── base.py                 # Generic SQLAlchemy CRUD repository
│   │   │
│   │   ├── services/                   # Business logic / use cases
│   │   │   └── base.py                 # Base service with repository injection
│   │   │
│   │   ├── api/                        # API presentation layer
│   │   │   ├── deps.py                 # FastAPI dependency injection
│   │   │   └── v1/                     # Version 1 endpoints
│   │   │       ├── router.py           # v1 router aggregator
│   │   │       └── endpoints/
│   │   │           └── health.py       # Health check endpoints
│   │   │
│   │   ├── db/                         # Database infrastructure
│   │   │   ├── session.py              # Async engine + session factory
│   │   │   └── redis.py               # Redis connection manager
│   │   │
│   │   ├── middleware/                 # HTTP middleware
│   │   │   ├── correlation_id.py       # Request correlation ID
│   │   │   ├── request_logging.py      # Structured request/response logging
│   │   │   └── error_handler.py        # Global exception handling
│   │   │
│   │   └── utils/                      # Shared utility functions
│   │       └── datetime.py             # UTC datetime helpers
│   │
│   ├── alembic/                        # Database migrations
│   │   ├── env.py                      # Async Alembic environment
│   │   ├── script.py.mako              # Migration file template
│   │   └── versions/                   # Migration files
│   │
│   ├── tests/                          # Backend tests
│   │   ├── conftest.py                 # Shared test fixtures
│   │   ├── unit/                       # Unit tests (no I/O)
│   │   └── integration/               # Integration tests (DB/Redis)
│   │
│   ├── requirements/                   # Python dependencies
│   │   ├── base.txt                    # Core production dependencies
│   │   ├── dev.txt                     # Dev + testing dependencies
│   │   └── prod.txt                    # Production-only (gunicorn)
│   │
│   ├── pyproject.toml                  # Python project config (pytest, ruff, mypy)
│   ├── alembic.ini                     # Alembic configuration
│   ├── Dockerfile                      # Production multi-stage build
│   ├── Dockerfile.dev                  # Development with hot-reload
│   ├── .env.example                    # Environment variable template
│   └── .dockerignore
│
├── frontend/                           # Next.js Frontend Application
│   ├── src/
│   │   ├── app/                        # Next.js App Router
│   │   │   ├── layout.tsx              # Root layout
│   │   │   ├── page.tsx                # Landing page
│   │   │   ├── globals.css             # Global styles + Tailwind
│   │   │   └── providers.tsx           # Client providers (theme)
│   │   │
│   │   ├── components/                 # Reusable React components
│   │   │   ├── ui/                     # Base UI primitives
│   │   │   └── layout/                # Layout components
│   │   │
│   │   ├── lib/                        # Utility libraries
│   │   │   ├── api/
│   │   │   │   └── client.ts           # Type-safe API client
│   │   │   └── utils/
│   │   │       └── cn.ts              # classnames utility
│   │   │
│   │   ├── hooks/                      # Custom React hooks
│   │   ├── types/                      # Global TypeScript types
│   │   │   └── index.ts
│   │   ├── config/                     # Frontend configuration
│   │   │   └── site.ts                # Site metadata
│   │   └── styles/                     # Additional style modules
│   │
│   ├── public/                         # Static assets
│   ├── next.config.ts                  # Next.js configuration
│   ├── tailwind.config.ts              # TailwindCSS configuration
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── .eslintrc.json                  # ESLint configuration
│   ├── .prettierrc                     # Prettier configuration
│   ├── Dockerfile                      # Production build
│   ├── Dockerfile.dev                  # Development with hot-reload
│   └── .env.example
│
├── docker/                             # Container orchestration
│   ├── docker-compose.yml              # Development environment
│   ├── docker-compose.prod.yml         # Production environment
│   ├── nginx/
│   │   └── nginx.conf                  # Reverse proxy configuration
│   └── postgres/
│       └── init.sql                    # Database initialization (extensions)
│
├── docs/                               # Documentation
│   ├── architecture/
│   │   ├── overview.md                 # System architecture
│   │   ├── folder-structure.md         # This file
│   │   └── clean-architecture.md       # Clean architecture guide
│   └── setup/
│       └── installation.md             # Installation guide
│
├── scripts/                            # Automation scripts
│   ├── setup.ps1                       # Initial project setup
│   ├── start-dev.ps1                   # Start development environment
│   └── start-prod.ps1                  # Start production environment
│
├── infrastructure/                     # Future IaC (Terraform, K8s)
│
├── tests/                              # Cross-cutting E2E tests
│   └── e2e/
│
├── .gitignore
├── .editorconfig
├── README.md
└── LICENSE
```

## Module Pattern

Each future module (auth, organizations, knowledge base, etc.) follows this pattern:

```
app/
├── models/
│   └── user.py              # SQLAlchemy model
├── schemas/
│   └── user.py              # Pydantic schemas
├── repositories/
│   └── user.py              # Data access
├── services/
│   └── user.py              # Business logic
└── api/v1/endpoints/
    └── users.py             # API endpoints
```
