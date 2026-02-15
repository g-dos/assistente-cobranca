from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy.orm import Session

from assistente_cobranca.models.collection_case import CollectionCase


class CaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, case_id: uuid.UUID) -> CollectionCase | None:
        return self.db.get(CollectionCase, case_id)

    def create_for_invoice(
        self,
        *,
        invoice_id: uuid.UUID,
        vencimento: dt.date,
        now: dt.datetime | None = None,
    ) -> CollectionCase:
        now = now or dt.datetime.now(dt.timezone.utc)
        next_action_at = dt.datetime.combine(vencimento, dt.time(9, 0), tzinfo=dt.timezone.utc) + dt.timedelta(days=1)
        if next_action_at < now:
            next_action_at = now

        case = CollectionCase(invoice_id=invoice_id, next_action_at=next_action_at)
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

