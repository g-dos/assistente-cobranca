from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    debtor_id: uuid.UUID
    numero: str = Field(min_length=1, max_length=80)
    descricao: str | None = Field(default=None, max_length=255)

    vencimento: dt.date
    principal: float = Field(gt=0)

    multa_pct: float = Field(default=0, ge=0)
    juros_mensal_pct: float = Field(default=0, ge=0)


class InvoiceRead(BaseModel):
    id: uuid.UUID
    debtor_id: uuid.UUID

    numero: str
    descricao: str | None = None
    vencimento: dt.date
    principal: float

    multa_pct: float
    juros_mensal_pct: float
    status: str

    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = {"from_attributes": True}


class InvoiceUpdatedValue(BaseModel):
    invoice_id: uuid.UUID
    ref_date: dt.date

    principal: float
    dias_em_atraso: int
    multa: float
    juros: float
    total: float

