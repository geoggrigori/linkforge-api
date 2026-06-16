"""Pydantic request/response schemas (the public API contract)."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# --- Auth ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Links ---
class LinkCreate(BaseModel):
    target_url: HttpUrl
    # Optional custom code; otherwise one is generated.
    code: str | None = Field(default=None, min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")


class LinkPublic(BaseModel):
    id: int
    code: str
    target_url: str
    short_url: str
    created_at: datetime
    active: bool
    clicks: int = 0


class DailyClicks(BaseModel):
    date: str
    count: int


class LinkStats(BaseModel):
    code: str
    target_url: str
    total_clicks: int
    clicks_by_day: list[DailyClicks]
    top_referers: list[dict]
