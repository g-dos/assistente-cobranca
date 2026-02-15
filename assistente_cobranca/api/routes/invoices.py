from __future__ import annotations

import uuid

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from assistente_cobranca.core.db import get_db
from assistente_cobranca.models.collection_case import CollectionCase
from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice
from assistente_cobranca.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdatedValue
from assistente_cobranca.services.calculator import updated_value
from assistente_cobranca.services.pdf_notification import generate_notification_pdf


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    debtor = db.get(Debtor, payload.debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")

    # cria o título e já abre um caso de cobrança (bem simples por enquanto)
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

    # primeira ação: d+1 do vencimento
    next_action_at = dt.datetime.combine(inv.vencimento, dt.time(9, 0), tzinfo=dt.timezone.utc) + dt.timedelta(
        days=1
    )
    case = CollectionCase(invoice_id=inv.id, next_action_at=next_action_at)
    db.add(case)
    db.commit()
    return inv


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(invoice_id: uuid.UUID, db: Session = Depends(get_db)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="titulo nao encontrado")
    return inv


@router.get("/{invoice_id}/updated-value", response_model=InvoiceUpdatedValue)
def get_updated_value(
    invoice_id: uuid.UUID,
    ref_date: dt.date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="titulo nao encontrado")

    ref = ref_date or dt.date.today()
    calc = updated_value(
        principal=float(inv.principal),
        vencimento=inv.vencimento,
        ref_date=ref,
        multa_pct=float(inv.multa_pct),
        juros_mensal_pct=float(inv.juros_mensal_pct),
    )

    return InvoiceUpdatedValue(
        invoice_id=inv.id,
        ref_date=ref,
        principal=calc.principal,
        dias_em_atraso=calc.dias_em_atraso,
        multa=calc.multa,
        juros=calc.juros,
        total=calc.total,
    )


@router.post("/{invoice_id}/notification")
def generate_notification(invoice_id: uuid.UUID, db: Session = Depends(get_db)):
    inv = db.get(Invoice, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="titulo nao encontrado")

    debtor = db.get(Debtor, inv.debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")

    pdf = generate_notification_pdf(debtor=debtor, invoice=inv)
    return Response(content=pdf, media_type="application/pdf")

