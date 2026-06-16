"""SQLModel database models."""

from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=utcnow)

    links: list["Link"] = Relationship(back_populates="owner")


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    target_url: str
    owner_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
    active: bool = Field(default=True)

    owner: User = Relationship(back_populates="links")
    clicks: list["Click"] = Relationship(
        back_populates="link",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Click(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    link_id: int = Field(foreign_key="link.id", index=True)
    created_at: datetime = Field(default_factory=utcnow, index=True)
    referer: str | None = None
    user_agent: str | None = None

    link: Link = Relationship(back_populates="clicks")
