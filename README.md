# Merkato Directory

Merkato Directory is a searchable directory of businesses located inside Merkato buildings. The database is the source of truth for every public filter and directory result.

```text
Building 1 ── N Floor 1 ── N Business N ── N Category
```

The physical path is `Business.floor_id -> Floor.building_id`. Building is never stored independently on a business. Classification uses the composite-key `business_categories` join table. Public building, floor, category, and business data comes from the API; React does not own a duplicate directory dataset.

## Architecture overview

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React + Vite
- Schema changes: Alembic migrations
- Infrastructure: Docker Compose for local PostgreSQL and services
- Security: role-based permissions, JWT/session auth, audit logging

## Project structure

- `backend/` — API service and domain logic
- `frontend/` — public and admin web app
- `docs/` — product and operational design notes
- `docker-compose.yml` — local services
- `.env.example` — environment template

## Phase plan

1. Foundation: relational models, auth, config, health endpoints
2. Admin management: buildings, floors, businesses, categories
3. Public directory: search, URL-backed building/floor/category filters
4. Quality control: report handling, verification, audit history
5. Production hardening: images, backups, caching, security, observability

## Important design rule

The system models one physical location per business: each business belongs to one floor, and the floor determines its building. A business can belong to many categories through `business_categories`. Buildings, floors, businesses, and categories are archived rather than destructively deleted.

## Quick start

### Local PostgreSQL

```bash
Copy-Item .env.example .env
# Edit .env: set unique SECRET_KEY, JWT_SECRET, POSTGRES_PASSWORD, and matching DATABASE_URL.
docker compose up --build
```

Compose binds PostgreSQL to host port `55432` so it does not take over an existing service on `5432` or `5433`. The backend waits for PostgreSQL, applies Alembic migrations at startup, and reports database connectivity from `GET /health`.

The public app runs at `http://localhost:5173`; the API runs at `http://localhost:8000`.

### Optional demo data

```bash
cd backend
python seed_data.py
```

The demo administrator is `admin@merkato.local` with the local seed password `admin123`. Change it after first sign-in; never use demo credentials in production.

### Migrations

```bash
cd backend
python -m alembic revision --autogenerate -m "describe schema change"
python -m alembic upgrade head
```

Do not use `Base.metadata.create_all()` as a production schema migration mechanism. Migrations fail safely if legacy business locations cannot be represented by exactly one consistent floor.
