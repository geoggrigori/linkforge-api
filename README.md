# LinkForge ⚡🔗

**English** · [Português](README.pt.md) · [Español](README.es.md)

A **production-style URL shortener & analytics API** built with FastAPI. Not a toy CRUD — it's designed to show the engineering that separates a hobby endpoint from a real service: authentication, rate limiting, caching, background processing, tests, containerization, and CI.

> Create short links, redirect with cached sub-millisecond lookups, and track click analytics — all behind JWT auth.

[![CI](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml/badge.svg)](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml)

---

![LinkForge API — interactive OpenAPI docs](docs/screenshot.png)

## ✨ Features

- **JWT authentication** — register/login, passwords hashed with PBKDF2-HMAC-SHA256 (per-user salt, constant-time verification). No plaintext, ever.
- **Token-bucket rate limiting** — custom ASGI middleware, per-client-IP, with `Retry-After`. No Redis needed for a single instance.
- **TTL + LRU redirect cache** — hot `code → URL` lookups skip the database; thread-safe, bounded, with automatic expiry.
- **Async click analytics** — redirects record clicks in a background task, off the response path. Stats endpoint aggregates totals, clicks-by-day, and top referrers.
- **Ownership & authorization** — users only see and manage their own links.
- **Auto-generated OpenAPI docs** — interactive Swagger UI at `/docs`, ReDoc at `/redoc`.
- **Fully tested** — 16 pytest tests covering auth, validation, redirects, analytics, and authorization.
- **Containerized + CI** — multi-stage-friendly Dockerfile (non-root, healthcheck), `docker-compose`, GitHub Actions running the suite on every push.

## 🧩 API overview

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | — | Create an account |
| `POST` | `/auth/login` | — | Get a JWT access token |
| `POST` | `/links` | ✅ | Create a short link (random or custom code) |
| `GET`  | `/links` | ✅ | List your links with click counts |
| `GET`  | `/links/{code}/stats` | ✅ | Analytics for a link |
| `DELETE` | `/links/{code}` | ✅ | Delete a link |
| `GET`  | `/{code}` | — | Redirect to the target URL (302) + record click |
| `GET`  | `/health` | — | Liveness probe |

Full, interactive docs at **`/docs`** once running.

## 🏗️ Architecture

![Architecture](docs/architecture.svg)

## 🚀 Getting started

### Local

```bash
# 1. Create a virtual environment and install deps
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. (optional) copy env defaults
cp .env.example .env

# 3. Run
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** and try it out.

### Docker

```bash
docker compose up --build
```

## 🧪 Tests

```bash
pytest -q
```

The suite spins the app against a throwaway SQLite database and exercises the full request lifecycle (auth → create → redirect → analytics → authorization).

## 🛠️ Tech stack

- **Framework:** FastAPI (+ Starlette middleware)
- **Data:** SQLModel / SQLAlchemy, SQLite (Postgres-ready via `DATABASE_URL`)
- **Auth:** PyJWT + standard-library PBKDF2
- **Testing:** pytest + httpx (`TestClient`)
- **Ops:** Docker, docker-compose, GitHub Actions

## 📝 Design notes

- **Why PBKDF2 from the stdlib?** Avoids a native crypto dependency while staying secure (200k iterations, per-password salt). Swappable for argon2/bcrypt if desired.
- **Why a custom rate limiter & cache?** To demonstrate the underlying algorithms (token bucket, TTL/LRU) rather than hide them behind a library. In a multi-instance deployment you'd back these with Redis.
- **Scaling path:** point `DATABASE_URL` at Postgres, move the cache/rate-limiter to Redis, and the app scales horizontally with no code changes to the routers.

---

Built as a portfolio project to demonstrate backend engineering depth: auth, middleware, caching, async work, testing, and deployment.
