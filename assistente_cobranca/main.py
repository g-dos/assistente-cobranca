from fastapi import FastAPI

from assistente_cobranca.core.db import check_db


app = FastAPI(title="assistente-cobranca", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True, "db": check_db()}

