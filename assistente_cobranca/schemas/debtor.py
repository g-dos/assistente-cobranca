from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel, Field


class DebtorCreate(BaseModel):
    cnpj: str = Field(min_length=14, max_length=20)


class DebtorRead(BaseModel):
    id: uuid.UUID
    cnpj: str

    razao_social: str | None = None
    nome_fantasia: str | None = None
    situacao_cadastral: str | None = None

    email: str | None = None
    telefone: str | None = None

    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    municipio: str | None = None
    uf: str | None = None
    cep: str | None = None

    enriched_at: dt.datetime | None = None
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = {"from_attributes": True}

