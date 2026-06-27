# LinkForge ⚡🔗

[English](README.md) · [Português](README.pt.md) · **Español**

Una **API de acortamiento de URLs y analítica de estilo producción** construida con FastAPI. No es un CRUD de juguete: está diseñada para mostrar la ingeniería que separa un endpoint de aficionado de un servicio real: autenticación, rate limiting, caché, procesamiento en segundo plano, pruebas, contenedorización y CI.

> Crea enlaces cortos, redirige con búsquedas en caché de sub-milisegundo y registra la analítica de clics, todo detrás de autenticación JWT.

[![CI](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml/badge.svg)](https://github.com/geoggrigori/linkforge-api/actions/workflows/ci.yml)

---

![LinkForge API — interactive OpenAPI docs](docs/screenshot.png)

## ✨ Características

- **Autenticación JWT** — registro/inicio de sesión, contraseñas con hash mediante PBKDF2-HMAC-SHA256 (salt por usuario, verificación en tiempo constante). Nunca en texto plano.
- **Rate limiting con token bucket** — middleware ASGI personalizado, por IP de cliente, con `Retry-After`. Sin necesidad de Redis para una sola instancia.
- **Caché de redirección TTL + LRU** — las búsquedas frecuentes de `code → URL` omiten la base de datos; thread-safe, acotado y con expiración automática.
- **Analítica de clics asíncrona** — las redirecciones registran clics en una tarea en segundo plano, fuera de la ruta de la respuesta. El endpoint de estadísticas agrega totales, clics por día y principales referentes.
- **Propiedad y autorización** — los usuarios solo ven y gestionan sus propios enlaces.
- **Documentación OpenAPI generada automáticamente** — Swagger UI interactivo en `/docs`, ReDoc en `/redoc`.
- **Totalmente probado** — 16 pruebas pytest que cubren autenticación, validación, redirecciones, analítica y autorización.
- **Contenedorizado + CI** — Dockerfile compatible con multi-stage (non-root, healthcheck), `docker-compose` y GitHub Actions ejecutando la suite en cada push.

## 🧩 Resumen de la API

| Method | Endpoint | Auth | Descripción |
|--------|----------|:----:|-------------|
| `POST` | `/auth/register` | — | Crea una cuenta |
| `POST` | `/auth/login` | — | Obtiene un token de acceso JWT |
| `POST` | `/links` | ✅ | Crea un enlace corto (código aleatorio o personalizado) |
| `GET`  | `/links` | ✅ | Lista tus enlaces con el conteo de clics |
| `GET`  | `/links/{code}/stats` | ✅ | Analítica de un enlace |
| `DELETE` | `/links/{code}` | ✅ | Elimina un enlace |
| `GET`  | `/{code}` | — | Redirige a la URL de destino (302) + registra el clic |
| `GET`  | `/health` | — | Sonda de liveness |

Documentación completa e interactiva en **`/docs`** una vez en ejecución.

## 🏗️ Arquitectura

![Architecture](docs/architecture.svg)

## 🚀 Primeros pasos

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

Abre **http://localhost:8000/docs** y pruébalo.

### Docker

```bash
docker compose up --build
```

## 🧪 Pruebas

```bash
pytest -q
```

La suite levanta la aplicación contra una base de datos SQLite desechable y ejercita todo el ciclo de vida de la petición (autenticación → creación → redirección → analítica → autorización).

## 🛠️ Stack tecnológico

- **Framework:** FastAPI (+ middleware de Starlette)
- **Datos:** SQLModel / SQLAlchemy, SQLite (listo para Postgres vía `DATABASE_URL`)
- **Autenticación:** PyJWT + PBKDF2 de la biblioteca estándar
- **Pruebas:** pytest + httpx (`TestClient`)
- **Ops:** Docker, docker-compose, GitHub Actions

## 📝 Notas de diseño

- **¿Por qué PBKDF2 de la stdlib?** Evita una dependencia nativa de criptografía manteniendo la seguridad (200k iteraciones, salt por contraseña). Reemplazable por argon2/bcrypt si se desea.
- **¿Por qué un rate limiter y una caché personalizados?** Para demostrar los algoritmos subyacentes (token bucket, TTL/LRU) en lugar de ocultarlos tras una biblioteca. En un despliegue multi-instancia los respaldarías con Redis.
- **Ruta de escalado:** apunta `DATABASE_URL` a Postgres, mueve la caché/rate-limiter a Redis, y la aplicación escala horizontalmente sin cambios de código en los routers.

---

Construido como proyecto de portafolio para demostrar profundidad en ingeniería de backend: autenticación, middleware, caché, trabajo asíncrono, pruebas y despliegue.

## Licencia

Distribuido bajo la [Licencia MIT](LICENSE).
