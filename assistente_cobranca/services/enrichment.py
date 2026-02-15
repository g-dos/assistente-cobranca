from __future__ import annotations

import datetime as dt

from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.services.brasilapi import BrasilApiClient


class EnrichmentService:
    def __init__(self, client: BrasilApiClient | None = None) -> None:
        self.client = client or BrasilApiClient()

    async def enrich_debtor_from_cnpj(self, debtor: Debtor) -> Debtor:
        data = await self.client.fetch_cnpj(debtor.cnpj)

        debtor.razao_social = data.get("razao_social") or data.get("razao_social", None)
        debtor.nome_fantasia = data.get("nome_fantasia")
        debtor.situacao_cadastral = data.get("descricao_situacao_cadastral")

        debtor.email = data.get("email")
        tel = data.get("ddd_telefone_1") or data.get("ddd_telefone_2")
        debtor.telefone = tel

        debtor.logradouro = data.get("logradouro")
        debtor.numero = data.get("numero")
        debtor.complemento = data.get("complemento")
        debtor.bairro = data.get("bairro")
        debtor.municipio = data.get("municipio")
        debtor.uf = data.get("uf")
        debtor.cep = data.get("cep")

        debtor.enriched_at = dt.datetime.now(dt.timezone.utc)
        return debtor

