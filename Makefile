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
\tpython3 -m pip install -r requirements.txt -r requirements-dev.txt
\tpytest -q

seed:
\tpython3 -m assistente_cobranca.seed

motor:
\tpython3 -m assistente_cobranca.motor

