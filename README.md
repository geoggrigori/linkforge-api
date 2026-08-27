<!-- ══════════════════════════ TÍTULO ══════════════════════════ -->
<div align="center">
  <img src="docs/title-banner.svg" width="100%" alt="LinkForge"/>
</div>

<br/>

<!-- ══════════════════════ IDIOMAS / LANGUAGES ══════════════════════ -->
<div align="center">
<a href="README.md"><img src="https://img.shields.io/badge/Português-1987F0?style=for-the-badge" alt="Português"/></a>
<a href="README.en.md"><img src="https://img.shields.io/badge/English-555555?style=for-the-badge" alt="English"/></a>
<a href="README.es.md"><img src="https://img.shields.io/badge/Español-555555?style=for-the-badge" alt="Español"/></a>
</div>

<br/>

<h1 align="center">LinkForge ⚡🔗</h1>
<p align="center"><em>Encurtador de URL & API de analytics com pegada de produção — não é um CRUD de brinquedo</em></p>
<p align="center"><strong>JWT auth → rate limiting → cache TTL/LRU → redirect → analytics assíncrono</strong></p>

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
<a href="#sobre"><img src="https://img.shields.io/badge/▸_SOBRE-1987F0?style=for-the-badge" alt="sobre"/></a>
<a href="#api"><img src="https://img.shields.io/badge/▸_API-000000?style=for-the-badge" alt="api"/></a>
<a href="#arquitetura"><img src="https://img.shields.io/badge/▸_ARQUITETURA-1987F0?style=for-the-badge" alt="arquitetura"/></a>
<a href="#tecnologias"><img src="https://img.shields.io/badge/▸_TECNOLOGIAS-000000?style=for-the-badge" alt="tech"/></a>
<a href="#uso"><img src="https://img.shields.io/badge/▸_USO-1987F0?style=for-the-badge" alt="uso"/></a>
</div>

<br/>

> 💡 **Não esconde os algoritmos.** Rate limiter (token bucket) e cache (TTL/LRU) são implementados do zero para mostrar a engenharia por trás, não escondida atrás de uma lib.

<div align="center">
  <img src="docs/screenshot.png" width="100%" alt="LinkForge API — documentação OpenAPI interativa"/>
</div>

## Sobre

**LinkForge** é um **encurtador de URL & API de analytics com pegada de produção**, construído com FastAPI. Não é um CRUD de brinquedo — foi desenhado para mostrar a engenharia que separa um endpoint de hobby de um serviço de verdade: autenticação, rate limiting, cache, processamento em background, testes, containerização e CI.

**Destaques:**
- **JWT** — registro/login, senhas com PBKDF2-HMAC-SHA256 (salt por usuário, verificação em tempo constante). Nunca texto puro.
- **Rate limiting (token bucket)** — middleware ASGI próprio, por IP, com `Retry-After`. Sem precisar de Redis pra uma instância só.
- **Cache TTL + LRU** — lookups quentes `code → URL` pulam o banco; thread-safe, limitado, com expiração automática.
- **Analytics assíncrono** — cliques são registrados em background task, fora do caminho de resposta. Endpoint de stats agrega totais, cliques-por-dia e top referrers.
- **Ownership** — cada usuário só vê e gerencia seus próprios links.
- **Docs OpenAPI automáticas** — Swagger UI interativo em `/docs`, ReDoc em `/redoc`.
- **Totalmente testado** — 16 testes pytest cobrindo auth, validação, redirects, analytics e autorização.
- **Containerizado + CI** — Dockerfile (non-root, healthcheck), `docker-compose`, GitHub Actions rodando a suíte a cada push.

## API

| Método | Endpoint | Auth | Descrição |
|---|---|:---:|---|
| `POST` | `/auth/register` | — | Cria uma conta |
| `POST` | `/auth/login` | — | Retorna um token JWT |
| `POST` | `/links` | ✅ | Cria um link curto (código aleatório ou customizado) |
| `GET` | `/links` | ✅ | Lista seus links com contagem de cliques |
| `GET` | `/links/{code}/stats` | ✅ | Analytics de um link |
| `DELETE` | `/links/{code}` | ✅ | Remove um link |
| `GET` | `/{code}` | — | Redireciona para a URL alvo (302) + registra o clique |
| `GET` | `/health` | — | Liveness probe |

Docs completas e interativas em **`/docs`** com o app rodando.

## Arquitetura

<div align="center">
  <img src="docs/architecture.svg" width="100%" alt="Arquitetura"/>
</div>

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Framework | FastAPI (+ middleware Starlette) |
| Dados | SQLModel / SQLAlchemy, SQLite (pronto pra Postgres via `DATABASE_URL`) |
| Auth | PyJWT + PBKDF2 da stdlib |
| Testes | pytest + httpx (`TestClient`) |
| Ops | Docker, docker-compose, GitHub Actions |

## Uso

**Local:**
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env   # opcional

uvicorn app.main:app --reload
```
Abra **http://localhost:8000/docs** e teste.

**Docker:**
```bash
docker compose up --build
```

**Testes:**
```bash
pytest -q
```
A suíte sobe o app contra um SQLite descartável e exercita o ciclo completo (auth → criação → redirect → analytics → autorização).

## Licença

[MIT](LICENSE).

<div align="center">
  <img src="https://file.loading.io/color/feature/thumb/Blues-8.png?" width="100%" height="10px" alt="divider"/>
</div>

<p align="center"><sub>Desenvolvido por <strong><a href="https://github.com/geoggrigori">Grigori</a></strong> · 2026</sub></p>
