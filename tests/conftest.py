"""Test configuration: spin the app against a throwaway database."""

import os
import tempfile

# Point the app at an isolated SQLite file and relax rate limiting BEFORE the
# app (and its cached settings) are imported.
_tmp_dir = tempfile.mkdtemp()
_db_path = os.path.join(_tmp_dir, "test.db").replace("\\", "/")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["RATE_LIMIT_REQUESTS"] = "100000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.cache import redirect_cache  # noqa: E402
from app.database import engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Click, Link, User  # noqa: E402

init_db()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
    # Reset state between tests for isolation.
    with Session(engine) as session:
        for model in (Click, Link, User):
            for row in session.exec(select(model)).all():
                session.delete(row)
        session.commit()
    redirect_cache.clear()


@pytest.fixture
def auth_headers(client):
    """Register a user and return Authorization headers with a valid token."""
    creds = {"email": "alice@example.com", "password": "supersecret123"}
    client.post("/auth/register", json=creds)
    token = client.post("/auth/login", json=creds).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
