from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    ForeignKey,
    JSON,
    String,
    Integer,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    type_annotation_map = {
        dict: JSON
    }



class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    hashed_password: Mapped[Optional[str]] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_oauth_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    resumes: Mapped[List["Resume"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    oauth_details: Mapped[List["OAuthDetail"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )



class OAuthDetail(Base):
    __tablename__ = "oauth_details"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )  # google, github, etc.

    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column()

    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    scopes: Mapped[Optional[str]] = mapped_column(String(255))

    user: Mapped["User"] = relationship(
        back_populates="oauth_details"
    )



class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    minio_object_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="processing",
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    owner: Mapped["User"] = relationship(
        back_populates="resumes"
    )

    analyses: Mapped[List["Analysis"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan"
    )



class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.id"),
        index=True,
        nullable=False
    )

    match_score: Mapped[int] = mapped_column(nullable=False)

    raw_ai_output: Mapped[dict] = mapped_column(nullable=False)

    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="analyses"
    )