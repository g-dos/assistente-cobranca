from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from assistente_cobranca.core.db import get_db
from assistente_cobranca.schemas.debtor import DebtorCreate, DebtorRead
from assistente_cobranca.repositories.debtors import DebtorRepository
from assistente_cobranca.services.enrichment import EnrichmentService


router = APIRouter(prefix="/debtors", tags=["debtors"])


@router.post("", response_model=DebtorRead, status_code=status.HTTP_201_CREATED)
def create_debtor(payload: DebtorCreate, db: Session = Depends(get_db)):
    repo = DebtorRepository(db)
    exists = repo.get_by_cnpj(payload.cnpj)
    if exists:
        raise HTTPException(status_code=409, detail="cnpj ja cadastrado")

    debtor = repo.create(cnpj=payload.cnpj)
    return debtor


@router.get("/{debtor_id}", response_model=DebtorRead)
def get_debtor(debtor_id: uuid.UUID, db: Session = Depends(get_db)):
    debtor = DebtorRepository(db).get(debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")
    return debtor


@router.post("/{debtor_id}/enrich", response_model=DebtorRead)
async def enrich_debtor(debtor_id: uuid.UUID, db: Session = Depends(get_db)):
    debtor = DebtorRepository(db).get(debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")

    svc = EnrichmentService()
    try:
        await svc.enrich_debtor_from_cnpj(debtor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception:
        raise HTTPException(status_code=502, detail="falha ao consultar cnpj")

    db.add(debtor)
    db.commit()
    db.refresh(debtor)
    return debtor

