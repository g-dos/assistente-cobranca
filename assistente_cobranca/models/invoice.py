from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from assistente_cobranca.models.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debtor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("debtors.id", ondelete="CASCADE"), index=True
    )

    numero: Mapped[str] = mapped_column(String(80))
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)

    vencimento: Mapped[dt.date] = mapped_column(Date)
    principal: Mapped[float] = mapped_column(Numeric(12, 2))

    multa_pct: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    juros_mensal_pct: Mapped[float] = mapped_column(Numeric(6, 4), default=0)

    status: Mapped[str] = mapped_column(String(30), default="aberta")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    debtor = relationship("Debtor", back_populates="invoices")
    case = relationship("CollectionCase", back_populates="invoice", uselist=False)

