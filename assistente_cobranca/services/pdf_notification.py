from __future__ import annotations

import datetime as dt
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from assistente_cobranca.models.debtor import Debtor
from assistente_cobranca.models.invoice import Invoice
from assistente_cobranca.services.calculator import updated_value


def _fmt_money(value: float) -> str:
    # pt-br simples
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"r$ {s}"


def generate_notification_pdf(*, debtor: Debtor, invoice: Invoice, ref_date: dt.date | None = None) -> bytes:
    ref_date = ref_date or dt.date.today()

    calc = updated_value(
        principal=float(invoice.principal),
        vencimento=invoice.vencimento,
        ref_date=ref_date,
        multa_pct=float(invoice.multa_pct),
        juros_mensal_pct=float(invoice.juros_mensal_pct),
    )

    buff = BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    w, h = A4

    # fonte padrão já serve, mas deixa registrado (se quiser trocar depois)
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
        c.setFont("DejaVuSans", 12)
    except Exception:
        c.setFont("Helvetica", 12)

    x = 20 * mm
    y = h - 25 * mm

    c.setFont(c._fontname, 14)
    c.drawString(x, y, "notificação extrajudicial de cobrança")
    y -= 10 * mm

    c.setFont(c._fontname, 11)
    c.drawString(x, y, f"data: {ref_date.strftime('%d/%m/%Y')}")
    y -= 10 * mm

    # destinatário
    c.setFont(c._fontname, 12)
    c.drawString(x, y, "destinatário:")
    y -= 6 * mm
    c.setFont(c._fontname, 11)
    c.drawString(x, y, f"{debtor.razao_social or '(razao social nao informada)'}")
    y -= 5 * mm
    c.drawString(x, y, f"cnpj: {debtor.cnpj}")
    y -= 5 * mm
    addr = " - ".join(
        [p for p in [debtor.logradouro, debtor.numero, debtor.bairro, debtor.municipio, debtor.uf, debtor.cep] if p]
    )
    if addr:
        c.drawString(x, y, f"endereço: {addr}")
        y -= 10 * mm
    else:
        y -= 5 * mm

    # dados do título
    c.setFont(c._fontname, 12)
    c.drawString(x, y, "dados do título:")
    y -= 6 * mm
    c.setFont(c._fontname, 11)
    c.drawString(x, y, f"número: {invoice.numero}")
    y -= 5 * mm
    c.drawString(x, y, f"vencimento: {invoice.vencimento.strftime('%d/%m/%Y')}")
    y -= 5 * mm
    if invoice.descricao:
        c.drawString(x, y, f"descrição: {invoice.descricao}")
        y -= 5 * mm
    y -= 2 * mm

    # valores
    c.drawString(x, y, f"principal: {_fmt_money(calc.principal)}")
    y -= 5 * mm
    c.drawString(x, y, f"multa: {_fmt_money(calc.multa)} ({float(invoice.multa_pct):g}%)")
    y -= 5 * mm
    c.drawString(x, y, f"juros: {_fmt_money(calc.juros)} ({float(invoice.juros_mensal_pct):g}% a.m.)")
    y -= 5 * mm
    c.setFont(c._fontname, 12)
    c.drawString(x, y, f"total atualizado: {_fmt_money(calc.total)}")
    y -= 12 * mm

    c.setFont(c._fontname, 11)
    texto = (
        "solicitamos a regularização do débito no prazo de 5 (cinco) dias úteis, "
        "contados do recebimento desta notificação, sob pena de adoção das medidas cabíveis."
    )
    c.drawString(x, y, texto)
    y -= 20 * mm

    c.drawString(x, y, "atenciosamente,")
    y -= 15 * mm
    c.drawString(x, y, "assistente-cobranca (demo)")

    c.showPage()
    c.save()
    return buff.getvalue()

