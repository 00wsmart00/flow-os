from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    from app.models.bom import BomItem


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Material(BaseModel):
    __tablename__ = "material"
    __table_args__ = (Index("material_code", "code", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(48))
    name: Mapped[str] = mapped_column(String(120))
    unit: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(), default=utc_now, onupdate=utc_now
    )

    bom_items: Mapped[list[BomItem]] = relationship(back_populates="material")
