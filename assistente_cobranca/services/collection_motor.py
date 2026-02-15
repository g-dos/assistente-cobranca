from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from assistente_cobranca.models.collection_case import CollectionCase
from assistente_cobranca.models.contact_attempt import ContactAttempt


def _milestone(vencimento: dt.date, days: int) -> dt.datetime:
    base = dt.datetime.combine(vencimento, dt.time(9, 0), tzinfo=dt.timezone.utc)
    return base + dt.timedelta(days=days)


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class CollectionMotor:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run_case(self, case: CollectionCase, now: dt.datetime | None = None) -> ContactAttempt | None:
        now = now or _now_utc()

        if case.status != "aberto":
            return None

        inv = case.invoice
        if not inv:
            return None

        days_overdue = max((now.date() - inv.vencimento).days, 0)

        attempted = {
            a.template_key for a in case.attempts if a.template_key and a.status in ("ok", "enviado", "feito")
        }

        # d+30 -> pre litigio (marca e para)
        if days_overdue >= 30 and case.stage != "pre_litigio":
            case.stage = "pre_litigio"
            case.next_action_at = None
            attempt = ContactAttempt(
                case_id=case.id,
                canal="sistema",
                template_key="pre_litigio",
                status="ok",
                sent_at=now,
            )
            self.db.add(attempt)
            return attempt

        # d+15 -> notificação (pdf mock)
        if days_overdue >= 15 and "notificacao_pdf" not in attempted:
            case.stage = "notificacao"
            case.next_action_at = _milestone(inv.vencimento, 30)
            attempt = ContactAttempt(
                case_id=case.id,
                canal="pdf",
                template_key="notificacao_pdf",
                status="ok",
                sent_at=now,
            )
            self.db.add(attempt)
            return attempt

        # d+7 -> e-mail 2 (mock)
        if days_overdue >= 7 and "email_n2" not in attempted:
            case.stage = "amigavel"
            case.next_action_at = _milestone(inv.vencimento, 15)
            attempt = ContactAttempt(
                case_id=case.id,
                canal="email",
                template_key="email_n2",
                status="ok",
                sent_at=now,
            )
            self.db.add(attempt)
            return attempt

        # d+1 -> e-mail 1 (mock)
        if days_overdue >= 1 and "email_n1" not in attempted:
            case.stage = "amigavel"
            case.next_action_at = _milestone(inv.vencimento, 7)
            attempt = ContactAttempt(
                case_id=case.id,
                canal="email",
                template_key="email_n1",
                status="ok",
                sent_at=now,
            )
            self.db.add(attempt)
            return attempt

        # nada pra fazer agora, agenda a próxima milestone que ainda faz sentido
        if case.next_action_at is None:
            case.next_action_at = _milestone(inv.vencimento, 1)
        return None

    def run_due_cases(self, now: dt.datetime | None = None) -> int:
        now = now or _now_utc()

        q = (
            select(CollectionCase)
            .where(CollectionCase.status == "aberto")
            .where(CollectionCase.next_action_at.is_not(None))
            .where(CollectionCase.next_action_at <= now)
        )
        cases = self.db.scalars(q).all()

        ran = 0
        for case in cases:
            attempt = self.run_case(case, now=now)
            if attempt:
                ran += 1
        return ran

