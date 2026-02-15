from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class UpdatedValue:
    principal: float
    dias_em_atraso: int
    multa: float
    juros: float
    total: float


def updated_value(
    *,
    principal: float,
    vencimento: dt.date,
    ref_date: dt.date,
    multa_pct: float,
    juros_mensal_pct: float,
) -> UpdatedValue:
    dias = max((ref_date - vencimento).days, 0)

    if dias <= 0:
        return UpdatedValue(
            principal=float(principal),
            dias_em_atraso=0,
            multa=0.0,
            juros=0.0,
            total=float(principal),
        )

    multa = float(principal) * (float(multa_pct) / 100.0)
    juros = float(principal) * (float(juros_mensal_pct) / 100.0) * (dias / 30.0)
    total = float(principal) + multa + juros

    # arredonda por segurança
    multa = round(multa, 2)
    juros = round(juros, 2)
    total = round(total, 2)

    return UpdatedValue(
        principal=float(principal),
        dias_em_atraso=dias,
        multa=multa,
        juros=juros,
        total=total,
    )

