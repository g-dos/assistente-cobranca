import datetime as dt

from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice
from assistente_cobranca.services.pdf_notification import generate_notification_pdf


def test_generate_notification_pdf_bytes():
    d = Debtor(cnpj="19131243000197", razao_social="teste ltda")
    i = Invoice(
        debtor_id=d.id,
        numero="fat-1",
        descricao="demo",
        vencimento=dt.date.today() - dt.timedelta(days=10),
        principal=100.0,
        multa_pct=2.0,
        juros_mensal_pct=1.0,
    )
    b = generate_notification_pdf(debtor=d, invoice=i)
    assert isinstance(b, (bytes, bytearray))
    assert b[:4] == b"%PDF"

