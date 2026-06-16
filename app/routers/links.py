"""Link management: create, list, stats, delete."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from sqlmodel import select

from ..cache import redirect_cache
from ..config import get_settings
from ..deps import CurrentUser, SessionDep
from ..models import Click, Link
from ..schemas import DailyClicks, LinkCreate, LinkPublic, LinkStats
from ..shortcode import generate_code

settings = get_settings()
router = APIRouter(prefix="/links", tags=["links"])

# Codes that would collide with API paths can't be used as custom codes.
RESERVED = {"auth", "links", "health", "docs", "redoc", "openapi.json"}


def _short_url(code: str) -> str:
    return f"{settings.base_url}/{code}"


def _to_public(link: Link, clicks: int) -> LinkPublic:
    return LinkPublic(
        id=link.id,
        code=link.code,
        target_url=link.target_url,
        short_url=_short_url(link.code),
        created_at=link.created_at,
        active=link.active,
        clicks=clicks,
    )


@router.post("", response_model=LinkPublic, status_code=status.HTTP_201_CREATED)
def create_link(
    payload: LinkCreate, user: CurrentUser, session: SessionDep
) -> LinkPublic:
    if payload.code:
        if payload.code.lower() in RESERVED:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "That code is reserved")
        if session.exec(select(Link).where(Link.code == payload.code)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "That code is already taken")
        code = payload.code
    else:
        # Retry until we hit an unused random code.
        code = generate_code()
        while session.exec(select(Link).where(Link.code == code)).first():
            code = generate_code()

    link = Link(code=code, target_url=str(payload.target_url), owner_id=user.id)
    session.add(link)
    session.commit()
    session.refresh(link)
    return _to_public(link, clicks=0)


@router.get("", response_model=list[LinkPublic])
def list_links(user: CurrentUser, session: SessionDep) -> list[LinkPublic]:
    # One query for links, one grouped query for click counts.
    links = session.exec(
        select(Link).where(Link.owner_id == user.id).order_by(Link.created_at.desc())
    ).all()
    counts = dict(
        session.exec(
            select(Click.link_id, func.count(Click.id)).group_by(Click.link_id)
        ).all()
    )
    return [_to_public(link, counts.get(link.id, 0)) for link in links]


def _owned_link(code: str, user_id: int, session: SessionDep) -> Link:
    link = session.exec(select(Link).where(Link.code == code)).first()
    if link is None or link.owner_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link not found")
    return link


@router.get("/{code}/stats", response_model=LinkStats)
def link_stats(code: str, user: CurrentUser, session: SessionDep) -> LinkStats:
    link = _owned_link(code, user.id, session)

    total = session.exec(
        select(func.count(Click.id)).where(Click.link_id == link.id)
    ).one()

    by_day = session.exec(
        select(func.date(Click.created_at), func.count(Click.id))
        .where(Click.link_id == link.id)
        .group_by(func.date(Click.created_at))
        .order_by(func.date(Click.created_at))
    ).all()

    referers = session.exec(
        select(Click.referer, func.count(Click.id))
        .where(Click.link_id == link.id)
        .group_by(Click.referer)
        .order_by(func.count(Click.id).desc())
        .limit(5)
    ).all()

    return LinkStats(
        code=link.code,
        target_url=link.target_url,
        total_clicks=total,
        clicks_by_day=[DailyClicks(date=str(d), count=c) for d, c in by_day],
        top_referers=[
            {"referer": r or "(direct)", "count": c} for r, c in referers
        ],
    )


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(code: str, user: CurrentUser, session: SessionDep) -> None:
    link = _owned_link(code, user.id, session)
    session.delete(link)
    session.commit()
    redirect_cache.invalidate(code)
