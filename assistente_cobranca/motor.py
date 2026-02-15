from __future__ import annotations

from assistente_cobranca.core.db import SessionLocal
from assistente_cobranca.services.collection_motor import CollectionMotor


def main() -> None:
    db = SessionLocal()
    try:
        motor = CollectionMotor(db)
        ran = motor.run_due_cases()
        db.commit()
        print(f"ok: {ran} acoes executadas")
    finally:
        db.close()


if __name__ == "__main__":
    main()

