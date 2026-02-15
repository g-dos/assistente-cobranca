from fastapi import FastAPI

from assistente_cobranca.core.db import check_db, init_db


app = FastAPI(title="assistente-cobranca", version="0.1.0")


@app.on_event("startup")
def _startup():
    # só pra facilitar dev/local; depois a gente troca pra migrations (alembic)
    init_db()


@app.get("/health")
def health():
    return {"ok": True, "db": check_db()}

