FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY assistente_cobranca ./assistente_cobranca

EXPOSE 8000

CMD ["uvicorn", "assistente_cobranca.main:app", "--host", "0.0.0.0", "--port", "8000"]

