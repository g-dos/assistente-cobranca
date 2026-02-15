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

## fluxo rápido (demo)

suba o banco e rode um seed:

```bash
cp .env.example .env
make up
```

em outro terminal:

```bash
make seed
```

interface web:

- `http://localhost:8000/`

motor (executa ações vencidas):

```bash
make motor
```

## endpoints principais

- `post /api/v1/debtors` cria devedor pj
- `post /api/v1/debtors/{id}/enrich` enriquece via brasilapi
- `post /api/v1/invoices` cria título
- `get /api/v1/invoices/{id}/updated-value` calcula valor atualizado
- `post /api/v1/invoices/{id}/notification` gera pdf
- `get /api/v1/cases` lista casos
- `post /api/v1/cases/{id}/run` roda próxima ação
- `post /api/v1/cases/run-due` roda vencidos

