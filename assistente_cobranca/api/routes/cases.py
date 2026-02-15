from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from assistente_cobranca.core.db import get_db
from assistente_cobranca.models.collection_case import CollectionCase
from assistente_cobranca.models.contact_attempt import ContactAttempt
from assistente_cobranca.schemas.attempt import AttemptRead
from assistente_cobranca.schemas.case import CaseRead
from assistente_cobranca.services.collection_motor import CollectionMotor


router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseRead])
def list_cases(db: Session = Depends(get_db)):
    cases = db.scalars(select(CollectionCase).order_by(CollectionCase.created_at.desc())).all()
    return cases


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(CollectionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="caso nao encontrado")
    return case


@router.get("/{case_id}/attempts", response_model=list[AttemptRead])
def list_attempts(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(CollectionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="caso nao encontrado")
    attempts = db.scalars(
        select(ContactAttempt).where(ContactAttempt.case_id == case_id).order_by(ContactAttempt.created_at.desc())
    ).all()
    return attempts


@router.post("/{case_id}/run")
def run_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.get(CollectionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="caso nao encontrado")

    motor = CollectionMotor(db)
    attempt = motor.run_case(case)
    db.add(case)
    db.commit()

    return {
        "ok": True,
        "case_id": str(case.id),
        "ran": bool(attempt),
        "attempt_id": str(attempt.id) if attempt else None,
        "template_key": attempt.template_key if attempt else None,
    }


@router.post("/run-due")
def run_due(db: Session = Depends(get_db)):
    motor = CollectionMotor(db)
    ran = motor.run_due_cases()
    db.commit()
    return {"ok": True, "ran": ran}

