from __future__ import annotations

import datetime as dt
import uuid

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from assistente_cobranca.core.db import get_db
from assistente_cobranca.models.collection_case import CollectionCase
from assistente_cobranca.models.contact_attempt import ContactAttempt
from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice
from assistente_cobranca.services.collection_motor import CollectionMotor
from assistente_cobranca.services.enrichment import EnrichmentService


templates = Jinja2Templates(directory="assistente_cobranca/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    debtors = db.scalars(select(Debtor).order_by(Debtor.created_at.desc()).limit(20)).all()
    invoices = db.scalars(select(Invoice).order_by(Invoice.created_at.desc()).limit(20)).all()
    cases = db.scalars(select(CollectionCase).order_by(CollectionCase.created_at.desc()).limit(20)).all()

    # aging simples
    now = dt.date.today()
    buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "90+": 0}
    for inv in invoices:
        d = max((now - inv.vencimento).days, 0)
        if d <= 30:
            buckets["0-30"] += 1
        elif d <= 60:
            buckets["31-60"] += 1
        elif d <= 90:
            buckets["61-90"] += 1
        else:
            buckets["90+"] += 1

    return templates.TemplateResponse(
        request,
        "home.html",
        {"debtors": debtors, "invoices": invoices, "cases": cases, "buckets": buckets},
    )


@router.post("/debtors")
async def web_create_debtor(
    cnpj: str = Form(...),
    enrich: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    exists = db.scalar(select(Debtor).where(Debtor.cnpj == cnpj))
    if exists:
        return RedirectResponse(url="/", status_code=303)

    debtor = Debtor(cnpj=cnpj)
    db.add(debtor)
    db.commit()
    db.refresh(debtor)

    if enrich:
        try:
            await EnrichmentService().enrich_debtor_from_cnpj(debtor)
            db.add(debtor)
            db.commit()
        except Exception:
            pass

    return RedirectResponse(url="/", status_code=303)


@router.post("/invoices")
def web_create_invoice(
    debtor_id: uuid.UUID = Form(...),
    numero: str = Form(...),
    vencimento: dt.date = Form(...),
    principal: float = Form(...),
    multa_pct: float = Form(default=2.0),
    juros_mensal_pct: float = Form(default=1.0),
    descricao: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    debtor = db.get(Debtor, debtor_id)
    if not debtor:
        raise HTTPException(status_code=404, detail="devedor nao encontrado")

    inv = Invoice(
        debtor_id=debtor_id,
        numero=numero,
        descricao=descricao,
        vencimento=vencimento,
        principal=principal,
        multa_pct=multa_pct,
        juros_mensal_pct=juros_mensal_pct,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    case = CollectionCase(
        invoice_id=inv.id,
        stage="amigavel",
        status="aberto",
        next_action_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1),
    )
    db.add(case)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@router.get("/cases/{case_id}", response_class=HTMLResponse)
def web_case_detail(case_id: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    case = db.get(CollectionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="caso nao encontrado")

    inv = case.invoice
    debtor = inv.debtor if inv else None
    attempts = db.scalars(
        select(ContactAttempt).where(ContactAttempt.case_id == case_id).order_by(ContactAttempt.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        request,
        "case_detail.html",
        {"case": case, "invoice": inv, "debtor": debtor, "attempts": attempts},
    )


@router.post("/cases/{case_id}/run")
def web_run_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(CollectionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="caso nao encontrado")

    motor = CollectionMotor(db)
    motor.run_case(case)
    db.add(case)
    db.commit()
    return RedirectResponse(url=f"/cases/{case_id}", status_code=303)


@router.post("/cases/run-due")
def web_run_due(db: Session = Depends(get_db)):
    ran = CollectionMotor(db).run_due_cases()
    db.commit()
    return RedirectResponse(url=f"/?ran={ran}", status_code=303)

