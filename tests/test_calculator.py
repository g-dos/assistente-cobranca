import datetime as dt

from assistente_cobranca.services.calculator import updated_value


def test_updated_value_no_delay():
    v = updated_value(
        principal=1000.0,
        vencimento=dt.date(2026, 2, 10),
        ref_date=dt.date(2026, 2, 10),
        multa_pct=2.0,
        juros_mensal_pct=1.0,
    )
    assert v.dias_em_atraso == 0
    assert v.total == 1000.0


def test_updated_value_with_delay():
    v = updated_value(
        principal=1000.0,
        vencimento=dt.date(2026, 2, 1),
        ref_date=dt.date(2026, 3, 2),  # 29 dias
        multa_pct=2.0,
        juros_mensal_pct=1.0,
    )
    assert v.dias_em_atraso == 29
    assert v.multa == 20.0
    assert v.juros == round(1000.0 * 0.01 * (29 / 30), 2)
    assert v.total == round(1000.0 + v.multa + v.juros, 2)

