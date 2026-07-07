# System Architecture Overview

## Nexora AI Employee Platform

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│              (Browser, WhatsApp, Phone, API)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │     Nginx       │
                    │  Reverse Proxy  │
                    └───┬─────────┬───┘
                        │         │
              ┌─────────▼──┐  ┌──▼─────────┐
              │  Next.js   │  │  FastAPI    │
              │  Frontend  │  │  Backend    │
              │  (SSR/CSR) │  │  (API)      │
              └────────────┘  └──┬──────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Application Layer     │
                    │   (Services / Use Cases) │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────▼──────────────────┐
              │           AI Brain                   │
              │  ┌──────────┐  ┌──────────────────┐ │
              │  │ LangGraph│  │  Knowledge Base   │ │
              │  │(Reasoning│  │  (pgvector)       │ │
              │  │ +Decisions│  │                   │ │
              │  └─────┬────┘  └──────────────────┘ │
              │        │                             │
              │  ┌─────▼────────────┐               │
              │  │  Tool Manager    │               │
              │  │  (Action Router) │               │
              │  └──┬──┬──┬──┬──┬──┘               │
              └─────┼──┼──┼──┼──┼───────────────────┘
                    │  │  │  │  │
         ┌──────────┘  │  │  │  └──────────┐
         ▼             ▼  ▼  ▼             ▼
    ┌────────┐  ┌────┐ │  │ ┌─────┐  ┌────────┐
    │AI Gate-│  │n8n │ │  │ │Voice│  │External│
    │way     │  │    │ │  │ │Gate-│  │APIs    │
    │(LLMs)  │  │    │ │  │ │way  │  │(CRM,   │
    └────────┘  └────┘ │  │ └─────┘  │Calendar)│
                       │  │          └────────┘
                 ┌─────▼──▼─────┐
                 │  PostgreSQL  │
                 │  + Redis     │
                 └──────────────┘
```

### Architecture Style: Modular Monolith

The platform is designed as a **Modular Monolith** — a single deployable unit with clearly separated internal modules. Each module:

- Has its own models, schemas, repositories, services, and endpoints
- Communicates with other modules through well-defined interfaces
- Can be extracted to a microservice when scaling demands it

### Key Design Decisions

| Decision | Rationale |
|---|---|
| **Modular Monolith** | Faster development velocity while maintaining clear boundaries. Microservices add operational complexity that isn't justified at Phase 1. |
| **FastAPI** | High-performance async Python framework. Native OpenAPI docs. Strong typing with Pydantic. |
| **SQLAlchemy 2 (async)** | Mature ORM with async support. Type-safe query building. Alembic for migrations. |
| **LangGraph for AI** | Graph-based agent orchestration. Supports complex reasoning flows, memory, and tool use. |
| **n8n for workflows** | Visual workflow builder for non-technical automation. Execution only — no reasoning. |
| **pgvector** | Native PostgreSQL vector embeddings for knowledge base RAG. No external vector DB needed. |
| **Multi-tenant with org_id** | Simple, effective tenant isolation at the data layer. Every query is scoped. |

### AI Flow

```
Customer Message
       │
       ▼
   FastAPI (Authentication + Organization Validation)
       │
       ▼
   LangGraph (Reasoning Engine)
       │
       ├── Knowledge Base Retrieval (pgvector)
       ├── Conversation Memory (PostgreSQL)
       ├── Context Assembly
       │
       ▼
   Decision (What action to take?)
       │
       ▼
   Tool Manager (Route to correct tool)
       │
       ├── AI Gateway → LLM Response
       ├── n8n → Workflow Execution
       ├── Voice Gateway → STT/TTS
       ├── Database → CRUD Operations
       ├── CRM → Customer Data
       ├── Calendar → Appointments
       ├── Email → Notifications
       └── WhatsApp → Messaging
```

### Multi-Tenancy

Every organization operates in complete isolation:

1. **Data Isolation**: Every database table includes `organization_id`
2. **Query Scoping**: Every repository query filters by `organization_id`
3. **API Validation**: Every request validates the user's organization
4. **No Cross-Tenant Access**: Authorization checks prevent data leakage

### Security Layers

1. **Transport**: HTTPS via Nginx
2. **Authentication**: JWT tokens
3. **Authorization**: Role-Based Access Control (RBAC)
4. **Rate Limiting**: Nginx + application-level
5. **Input Validation**: Pydantic V2 schema validation
6. **Data Isolation**: Organization-scoped queries
7. **Audit Trail**: All mutations logged
8. **Secret Management**: Environment variables (never hardcoded)
