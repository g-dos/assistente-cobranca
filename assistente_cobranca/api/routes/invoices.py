from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from assistente_cobranca.core.db import get_db
from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice
from assistente_cobranca.schemas.invoice import InvoiceCreate, InvoiceRead


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    debtor = db.get(Debtor, payload.debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")

    inv = Invoice(
        debtor_id=payload.debtor_id,
        numero=payload.numero,
        descricao=payload.descricao,
        vencimento=payload.vencimento,
        principal=payload.principal,
        multa_pct=payload.multa_pct,
        juros_mensal_pct=payload.juros_mensal_pct,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: uuid.UUID, db: Session = Depends(get_db)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="titulo nao encontrado")
    return inv

