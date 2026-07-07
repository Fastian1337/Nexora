# Clean Architecture in Nexora

## Overview

Nexora follows **Clean Architecture** principles to ensure the codebase is maintainable, testable, and adaptable to change.

## Layer Responsibilities

### 1. Domain Layer (`app/core/`)

The innermost layer. Contains business rules and entities that are independent of any framework, database, or external service.

**Contents:**
- `exceptions.py` — Domain-specific exception hierarchy
- `constants.py` — Business constants
- `interfaces/repository.py` — Abstract repository contracts

**Rules:**
- ✅ Pure Python — no framework imports
- ✅ Defines interfaces (ports) that outer layers implement
- ❌ Never imports from `models/`, `db/`, `api/`, or `middleware/`

### 2. Application Layer (`app/services/`)

Contains use cases that orchestrate business logic by coordinating between domain objects and infrastructure.

**Contents:**
- Business logic and use case implementations
- Service classes that inject repositories

**Rules:**
- ✅ Depends on Domain layer interfaces
- ✅ Uses repository interfaces (not concrete implementations)
- ❌ Never accesses the database directly
- ❌ Never knows about HTTP requests or responses

### 3. Infrastructure Layer (`app/models/`, `app/repositories/`, `app/db/`)

Implements the interfaces defined by the Domain layer using specific technologies.

**Contents:**
- `models/` — SQLAlchemy ORM models
- `repositories/` — Concrete repository implementations
- `db/` — Database and Redis connection management

**Rules:**
- ✅ Implements Domain layer interfaces
- ✅ Contains all technology-specific code
- ❌ Business logic belongs in services, not here

### 4. Presentation Layer (`app/api/`, `app/middleware/`)

Handles HTTP requests and responses. Converts between external formats and internal domain objects.

**Contents:**
- `api/` — FastAPI routers and endpoints
- `middleware/` — HTTP middleware (CORS, logging, error handling)
- `schemas/` — Pydantic request/response models

**Rules:**
- ✅ Thin layer — delegates to services
- ✅ Handles serialization/deserialization
- ❌ No business logic in endpoints

## Dependency Flow

```
Presentation → Application → Domain ← Infrastructure
     │              │           ▲            │
     │              │           │            │
     │              └───────────┘            │
     │                                       │
     └──────── depends on ──────────────────┘
                                    implements
```

**Key Principle:** Dependencies flow inward. The Domain layer never depends on outer layers. Infrastructure implements Domain interfaces (Dependency Inversion).

## Example: How a Request Flows

```
1. HTTP Request → FastAPI Endpoint (Presentation)
2. Endpoint injects Service via Depends() (DI)
3. Service calls Repository method (Application)
4. Repository executes SQL query (Infrastructure)
5. Result flows back: Repository → Service → Endpoint → HTTP Response
```

## Why This Matters

| Benefit | How |
|---|---|
| **Testability** | Services can be tested with mock repositories |
| **Flexibility** | Swap PostgreSQL for MongoDB by changing only repositories |
| **Maintainability** | Changes in one layer don't cascade to others |
| **Clarity** | Each file has a clear, single responsibility |
