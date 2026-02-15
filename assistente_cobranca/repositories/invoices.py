from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from assistente_cobranca.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, invoice_id: uuid.UUID) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

