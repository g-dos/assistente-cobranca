from __future__ import annotations

import re
from dataclasses import dataclass

import httpx


def normalize_cnpj(value: str) -> str:
    return re.sub(r"\\D", "", value or "")


def is_valid_cnpj(value: str) -> bool:
    cnpj = normalize_cnpj(value)
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    def calc_digit(nums: list[int], weights: list[int]) -> int:
        s = sum(n * w for n, w in zip(nums, weights, strict=True))
        r = s % 11
        return 0 if r < 2 else 11 - r

    nums = [int(c) for c in cnpj]
    d1 = calc_digit(nums[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = calc_digit(nums[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return nums[12] == d1 and nums[13] == d2


@dataclass(frozen=True)
class BrasilApiClient:
    base_url: str = "https://brasilapi.com.br/api"
    timeout_s: float = 10.0

    async def fetch_cnpj(self, cnpj: str) -> dict:
        cnpj_norm = normalize_cnpj(cnpj)
        if not is_valid_cnpj(cnpj_norm):
            raise ValueError("cnpj invalido")

        url = f"{self.base_url}/cnpj/v1/{cnpj_norm}"
        async with httpx.AsyncClient(timeout=self.timeout_s) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

