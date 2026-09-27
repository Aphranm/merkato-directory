# Merkato Directory

A mobile-first business directory with a public storefront and an admin dashboard. The directory is managed dynamically via the backend and database, with no hard-coded buildings, categories, rooms, or business records.

## Features

- Public storefront and search experience
- Admin authentication and protected dashboard
- Dynamic building → category → room → business hierarchy
- Image upload, validation, and storage via local filesystem (ready for object storage)
- Built with FastAPI and React + Vite
- PostgreSQL-ready with SQLite fallback for local development
- Seed data for testing the full directory workflow

## Stack

- Backend: Python, FastAPI, SQLAlchemy, PostgreSQL/SQLite
- Frontend: React, Vite, React Router
- Auth: JWT-based admin sessions
- Image handling: file upload and static asset serving

## Repository layout

- `backend/` – API, models, database, auth, seed data
- `frontend/` – mobile-first React client/admin app
- `README.md` – setup and usage notes

## Quick start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev -- --host 0.0.0.0
```

Open the app in the browser. The default frontend URL is typically `http://localhost:5173` and the API is `http://localhost:8000`.

## Default admin login

- Username: `admin`
- Password: `admin123`

## Environment variables

Use the examples provided in:

- `backend/.env.example`
- `frontend/.env.example`

## API notes

The backend exposes routes such as:

- `/api/buildings`
- `/api/buildings/{id}/categories`
- `/api/categories/{id}/rooms`
- `/api/rooms/{id}/business`
- `/api/businesses/{id}`
- `/api/search`
- `/api/auth/login`

## Seed data

The backend seeds sample data on first startup, including a building, categories, rooms, and businesses for testing the directory flow.

## Production considerations

This project is architecture-ready for production scaling.

- PostgreSQL is the preferred production database.
- Media is stored as file paths/URLs rather than binary blobs in the database.
- Images can be moved to S3 or another object store later without changing the app model.
- The admin dashboard and public client are deliberately separated.

## Admin workflow to test

1. Log in as admin
2. Add a building
3. Upload a building image
4. Add a category
5. Add a room
6. Add a business
7. Upload a business image
8. Save and confirm the public site shows the directory entry
9. Search for the new business from the public site

## License

MIT
