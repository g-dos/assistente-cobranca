from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from assistente_cobranca.models.debtor import Debtor


class DebtorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, debtor_id: uuid.UUID) -> Debtor | None:
        return self.db.get(Debtor, debtor_id)

    def get_by_cnpj(self, cnpj: str) -> Debtor | None:
        return self.db.scalar(select(Debtor).where(Debtor.cnpj == cnpj))

    def create(self, *, cnpj: str) -> Debtor:
        debtor = Debtor(cnpj=cnpj)
        self.db.add(debtor)
        self.db.commit()
        self.db.refresh(debtor)
        return debtor

