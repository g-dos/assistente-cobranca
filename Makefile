.PHONY: up down build logs test seed motor

up:
\tdocker compose up --build

down:
\tdocker compose down -v

build:
\tdocker compose build

logs:
\tdocker compose logs -f api

test:
\tdocker compose run --rm api sh -lc "pip install -r requirements-dev.txt && pytest -q"

seed:
\tdocker compose run --rm api python -m assistente_cobranca.seed

motor:
\tdocker compose run --rm api python -m assistente_cobranca.motor

