# assistente-cobranca

motor de cobrança b2b (extrajudicial) com:

- cadastro de devedores pj
- enriquecimento de dados via brasilapi (cnpj)
- cálculo de mora/multa
- geração de notificação extrajudicial em pdf
- régua simples de cobrança e trilha de auditoria

## como rodar (dev)

```bash
docker compose up --build
```

api em `http://localhost:8000` (docs em `/docs`).

