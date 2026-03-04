from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {
        dict: JSON
    }


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True,default=uuid4)
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True)
    hashed_password: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    resumes: Mapped[List["Resume"]] = relationship(back_populates="owner")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    minio_object_name: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(default="processing")

    file_size: Mapped[Optional[int]] = mapped_column()

    owner: Mapped["User"] = relationship(back_populates="resumes")
    analyses: Mapped[List["Analysis"]] = relationship(back_populates="resume")


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"))

    match_score: Mapped[int] = mapped_column()
    raw_ai_output: Mapped[dict] = mapped_column()

    prompt_tokens: Mapped[int] = mapped_column(default=0)

    resume: Mapped["Resume"] = relationship(back_populates="analyses")
