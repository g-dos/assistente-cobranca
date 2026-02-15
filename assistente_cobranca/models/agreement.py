from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from assistente_cobranca.models.base import Base


class Agreement(Base):
    __tablename__ = "agreements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("collection_cases.id", ondelete="CASCADE"), index=True
    )

    status: Mapped[str] = mapped_column(String(30), default="proposto")
    parcelas: Mapped[int] = mapped_column(default=1)

    valor_total: Mapped[float] = mapped_column(Numeric(12, 2))
    data_primeira_parcela: Mapped[dt.date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    case = relationship("CollectionCase", back_populates="agreements")

