from __future__ import annotations

import datetime as dt

from sqlalchemy import select

from assistente_cobranca.core.db import SessionLocal, init_db
from assistente_cobranca.models.collection_case import CollectionCase
from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice


def main() -> None:
    init_db()

    db = SessionLocal()
    try:
        # cnpj público usado como exemplo na documentação da brasilapi
        cnpj = "19131243000197"

        debtor = db.scalar(select(Debtor).where(Debtor.cnpj == cnpj))
        if not debtor:
            debtor = Debtor(cnpj=cnpj)
            db.add(debtor)
            db.commit()
            db.refresh(debtor)

        inv = Invoice(
            debtor_id=debtor.id,
            numero="fat-0001",
            descricao="serviço mensal (demo)",
            vencimento=dt.date.today() - dt.timedelta(days=18),
            principal=1500.00,
            multa_pct=2.0,
            juros_mensal_pct=1.0,
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)

        case = CollectionCase(
            invoice_id=inv.id,
            stage="amigavel",
            status="aberto",
            next_action_at=dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1),
        )
        db.add(case)
        db.commit()

        print("seed ok")
        print(f"debtor_id={debtor.id}")
        print(f"invoice_id={inv.id}")
        print(f"case_id={case.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

