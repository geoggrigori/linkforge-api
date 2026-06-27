# LinkForge ⚡🔗

[English](README.md) · **Português** · [Español](README.es.md)

Uma **API de encurtamento de URLs e analytics em estilo de produção** construída com FastAPI. Não é um CRUD de brinquedo — foi projetada para mostrar a engenharia que separa um endpoint de hobby de um serviço real: autenticação, rate limiting, cache, processamento em segundo plano, testes, containerização e CI.

> Crie links curtos, redirecione com buscas em cache sub-milissegundo e acompanhe o analytics de cliques — tudo protegido por autenticação JWT.

[![CI](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml/badge.svg)](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml)

---

![LinkForge API — interactive OpenAPI docs](docs/screenshot.png)

## ✨ Recursos

- **Autenticação JWT** — registro/login, senhas com hash via PBKDF2-HMAC-SHA256 (salt por usuário, verificação em tempo constante). Nunca em texto puro.
- **Rate limiting por token bucket** — middleware ASGI customizado, por IP de cliente, com `Retry-After`. Sem necessidade de Redis para uma única instância.
- **Cache de redirecionamento TTL + LRU** — buscas quentes de `code → URL` pulam o banco de dados; thread-safe, limitado e com expiração automática.
- **Analytics de cliques assíncrono** — os redirecionamentos registram cliques em uma tarefa em segundo plano, fora do caminho da resposta. O endpoint de estatísticas agrega totais, cliques por dia e principais referenciadores.
- **Propriedade e autorização** — usuários só visualizam e gerenciam seus próprios links.
- **Documentação OpenAPI gerada automaticamente** — Swagger UI interativo em `/docs`, ReDoc em `/redoc`.
- **Totalmente testado** — 16 testes pytest cobrindo autenticação, validação, redirecionamentos, analytics e autorização.
- **Containerizado + CI** — Dockerfile amigável a multi-stage (non-root, healthcheck), `docker-compose` e GitHub Actions executando a suíte a cada push.

## 🧩 Visão geral da API

| Method | Endpoint | Auth | Descrição |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | — | Cria uma conta |
| `POST` | `/auth/login` | — | Obtém um token de acesso JWT |
| `POST` | `/links` | ✅ | Cria um link curto (código aleatório ou customizado) |
| `GET`  | `/links` | ✅ | Lista seus links com contagem de cliques |
| `GET`  | `/links/{code}/stats` | ✅ | Analytics de um link |
| `DELETE` | `/links/{code}` | ✅ | Exclui um link |
| `GET`  | `/{code}` | — | Redireciona para a URL de destino (302) + registra o clique |
| `GET`  | `/health` | — | Sonda de liveness |

Documentação completa e interativa em **`/docs`** quando em execução.

## 🏗️ Arquitetura

![Architecture](docs/architecture.svg)

## 🚀 Primeiros passos

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

Abra **http://localhost:8000/docs** e experimente.

### Docker

```bash
docker compose up --build
```

## 🧪 Testes

```bash
pytest -q
```

A suíte sobe a aplicação contra um banco de dados SQLite descartável e exercita todo o ciclo de vida da requisição (autenticação → criação → redirecionamento → analytics → autorização).

## 🛠️ Stack de tecnologia

- **Framework:** FastAPI (+ middleware do Starlette)
- **Dados:** SQLModel / SQLAlchemy, SQLite (pronto para Postgres via `DATABASE_URL`)
- **Autenticação:** PyJWT + PBKDF2 da biblioteca padrão
- **Testes:** pytest + httpx (`TestClient`)
- **Ops:** Docker, docker-compose, GitHub Actions

## 📝 Notas de design

- **Por que PBKDF2 da stdlib?** Evita uma dependência nativa de criptografia mantendo a segurança (200k iterações, salt por senha). Substituível por argon2/bcrypt se desejado.
- **Por que um rate limiter e cache customizados?** Para demonstrar os algoritmos subjacentes (token bucket, TTL/LRU) em vez de escondê-los atrás de uma biblioteca. Em uma implantação multi-instância, você os apoiaria com Redis.
- **Caminho de escala:** aponte `DATABASE_URL` para o Postgres, mova o cache/rate-limiter para o Redis, e a aplicação escala horizontalmente sem alterações de código nos routers.

---

Construído como projeto de portfólio para demonstrar profundidade em engenharia de backend: autenticação, middleware, cache, trabalho assíncrono, testes e deploy.

## Licença

Distribuído sob a [Licença MIT](LICENSE).
