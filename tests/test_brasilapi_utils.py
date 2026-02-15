from assistente_cobranca.services.brasilapi import is_valid_cnpj, normalize_cnpj


def test_normalize_cnpj():
    assert normalize_cnpj("19.131.243/0001-97") == "19131243000197"


def test_is_valid_cnpj():
    assert is_valid_cnpj("19131243000197") is True
    assert is_valid_cnpj("00.000.000/0000-00") is False
    assert is_valid_cnpj("123") is False

