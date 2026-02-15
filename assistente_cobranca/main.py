from fastapi import FastAPI


app = FastAPI(title="assistente-cobranca")


@app.get("/health")
def health():
    return {"ok": True}

