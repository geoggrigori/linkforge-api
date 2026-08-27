<!-- ══════════════════════════ TITLE ══════════════════════════ -->
<div align="center">
  <img src="docs/title-banner.svg" width="100%" alt="LinkForge"/>
</div>

<br/>

<!-- ══════════════════════ IDIOMAS / LANGUAGES ══════════════════════ -->
<div align="center">
<a href="README.md"><img src="https://img.shields.io/badge/Português-555555?style=for-the-badge" alt="Português"/></a>
<a href="README.en.md"><img src="https://img.shields.io/badge/English-1987F0?style=for-the-badge" alt="English"/></a>
<a href="README.es.md"><img src="https://img.shields.io/badge/Español-555555?style=for-the-badge" alt="Español"/></a>
</div>

<br/>

<h1 align="center">LinkForge ⚡🔗</h1>
<p align="center"><em>A production-style URL shortener & analytics API — not a toy CRUD</em></p>
<p align="center"><strong>JWT auth → rate limiting → TTL/LRU cache → redirect → async analytics</strong></p>

<div align="center">
<a href="https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml"><img src="https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
<br/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="fastapi"/>
<img src="https://img.shields.io/badge/SQLModel_%2F_SQLAlchemy-D71F00?style=flat-square" alt="sqlmodel"/>
<img src="https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white" alt="jwt"/>
<img src="https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white" alt="pytest"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="docker"/>
</div>

<div align="center">
<a href="#about"><img src="https://img.shields.io/badge/▸_ABOUT-1987F0?style=for-the-badge" alt="about"/></a>
<a href="#api"><img src="https://img.shields.io/badge/▸_API-000000?style=for-the-badge" alt="api"/></a>
<a href="#architecture"><img src="https://img.shields.io/badge/▸_ARCHITECTURE-1987F0?style=for-the-badge" alt="architecture"/></a>
<a href="#tech-stack"><img src="https://img.shields.io/badge/▸_TECH_STACK-000000?style=for-the-badge" alt="tech"/></a>
<a href="#usage"><img src="https://img.shields.io/badge/▸_USAGE-1987F0?style=for-the-badge" alt="usage"/></a>
</div>

<br/>

> 💡 **Doesn't hide the algorithms.** The rate limiter (token bucket) and cache (TTL/LRU) are hand-built to show the engineering behind them, not hidden behind a library.

<div align="center">
  <img src="docs/screenshot.png" width="100%" alt="LinkForge API — interactive OpenAPI docs"/>
</div>

## About

**LinkForge** is a **production-style URL shortener & analytics API** built with FastAPI. Not a toy CRUD — it's designed to show the engineering that separates a hobby endpoint from a real service: authentication, rate limiting, caching, background processing, tests, containerization, and CI.

**Highlights:**
- **JWT authentication** — register/login, passwords hashed with PBKDF2-HMAC-SHA256 (per-user salt, constant-time verification). No plaintext, ever.
- **Token-bucket rate limiting** — custom ASGI middleware, per-client-IP, with `Retry-After`. No Redis needed for a single instance.
- **TTL + LRU redirect cache** — hot `code → URL` lookups skip the database; thread-safe, bounded, with automatic expiry.
- **Async click analytics** — redirects record clicks in a background task, off the response path.
- **Ownership & authorization** — users only see and manage their own links.
- **Auto-generated OpenAPI docs** — interactive Swagger UI at `/docs`, ReDoc at `/redoc`.
- **Fully tested** — 16 pytest tests covering auth, validation, redirects, analytics, and authorization.
- **Containerized + CI** — Dockerfile (non-root, healthcheck), `docker-compose`, GitHub Actions running the suite on every push.

## API

| Method | Endpoint | Auth | Description |
|---|---|:---:|---|
| `POST` | `/auth/register` | — | Create an account |
| `POST` | `/auth/login` | — | Get a JWT access token |
| `POST` | `/links` | ✅ | Create a short link (random or custom code) |
| `GET` | `/links` | ✅ | List your links with click counts |
| `GET` | `/links/{code}/stats` | ✅ | Analytics for a link |
| `DELETE` | `/links/{code}` | ✅ | Delete a link |
| `GET` | `/{code}` | — | Redirect to the target URL (302) + record click |
| `GET` | `/health` | — | Liveness probe |

Full, interactive docs at **`/docs`** once running.

## Architecture

<div align="center">
  <img src="docs/architecture.svg" width="100%" alt="Architecture"/>
</div>

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (+ Starlette middleware) |
| Data | SQLModel / SQLAlchemy, SQLite (Postgres-ready via `DATABASE_URL`) |
| Auth | PyJWT + standard-library PBKDF2 |
| Testing | pytest + httpx (`TestClient`) |
| Ops | Docker, docker-compose, GitHub Actions |

## Usage

**Local:**
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env   # optional

uvicorn app.main:app --reload
```
Open **http://localhost:8000/docs** and try it out.

**Docker:**
```bash
docker compose up --build
```

**Tests:**
```bash
pytest -q
```
The suite spins the app against a throwaway SQLite database and exercises the full request lifecycle (auth → create → redirect → analytics → authorization).

## License

[MIT](LICENSE).

<div align="center">
  <img src="https://file.loading.io/color/feature/thumb/Blues-8.png?" width="100%" height="10px" alt="divider"/>
</div>

<p align="center"><sub>Built by <strong><a href="https://github.com/geoggrigori">Grigori</a></strong> · 2026</sub></p>
