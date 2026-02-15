from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from assistente_cobranca.models.base import Base


class CollectionCase(Base):
    __tablename__ = "collection_cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("invoices.id", ondelete="CASCADE"), unique=True, index=True
    )

    stage: Mapped[str] = mapped_column(String(30), default="amigavel")
    status: Mapped[str] = mapped_column(String(30), default="aberto")
    next_action_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    invoice = relationship("Invoice", back_populates="case")
    attempts = relationship("ContactAttempt", back_populates="case")
    agreements = relationship("Agreement", back_populates="case")

