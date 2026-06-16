"""LinkForge API — application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from . import __version__
from .cache import redirect_cache
from .database import engine, init_db
from .models import Click, Link
from .rate_limit import RateLimitMiddleware
from .routers import auth, links


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="LinkForge API",
    version=__version__,
    summary="A production-style URL shortener with analytics.",
    description=(
        "Create short links, redirect with sub-millisecond cached lookups, and "
        "track click analytics. Features JWT auth, token-bucket rate limiting, "
        "and a TTL/LRU redirect cache."
    ),
    lifespan=lifespan,
)

app.add_middleware(RateLimitMiddleware)
app.include_router(auth.router)
app.include_router(links.router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "version": __version__}


def _record_click(code: str, referer: str | None, user_agent: str | None) -> None:
    """Persist a click event. Runs in a background task, off the redirect path."""
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.code == code)).first()
        if link is None:
            return
        session.add(
            Click(link_id=link.id, referer=referer, user_agent=user_agent)
        )
        session.commit()


@app.get("/{code}", tags=["redirect"], summary="Redirect to the target URL")
def redirect(code: str, request: Request, background: BackgroundTasks):
    """Resolve a short code and redirect (302), recording the click async."""
    target = redirect_cache.get(code)

    if target is None:
        with Session(engine) as session:
            link = session.exec(select(Link).where(Link.code == code)).first()
            if link is None or not link.active:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, "Short link not found"
                )
            target = link.target_url
            redirect_cache.set(code, target)

    background.add_task(
        _record_click,
        code,
        request.headers.get("referer"),
        request.headers.get("user-agent"),
    )
    return RedirectResponse(url=target, status_code=302)
