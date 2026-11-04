#!/usr/bin/env python3
"""
Arma el PDF para compartir a partir de las placas y el JSON de tuits.
Una pagina por tarjeta: titulo, placa y el texto del tuit debajo.

    python3 pdf_reporte.py --fecha 35 --tuits tuits_f35.json \
        --imgdir /mnt/user-data/outputs --out colon_f35.pdf \
        --titulo "Colón · Fecha 35" --subtitulo "35 PJ · 57 pts · 5°"

Los emojis se sacan a proposito: las fuentes base de reportlab no los tienen y
saldrian como cuadrados negros.
"""
import json, os, re, argparse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak, KeepTogether)
from reportlab.pdfgen import canvas as rl_canvas

NEGRO, ROJO, DORADO, GRIS = colors.HexColor('#080808'), colors.HexColor('#C8102E'), \
                            colors.HexColor('#FFC533'), colors.HexColor('#A9B4BE')
EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]', flags=re.UNICODE)


def limpiar(t):
    """Saca emojis y deja el texto listo para las fuentes base de reportlab."""
    t = EMOJI.sub('', t)
    t = re.sub(r'[ \t]+\n', '\n', t)
    t = re.sub(r'\n{3,}', '\n\n', t)
    return t.strip()


def fondo(canv, doc):
    canv.saveState()
    canv.setFillColor(NEGRO)
    canv.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canv.setFillColor(ROJO)
    canv.rect(0, 0, A4[0], 6 * mm, fill=1, stroke=0)
    canv.setFillColor(GRIS)
    canv.setFont('Helvetica', 7)
    canv.drawString(18 * mm, 10 * mm, doc.pie)
    canv.drawRightString(A4[0] - 18 * mm, 10 * mm, f'{canv.getPageNumber()}')
    canv.restoreState()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, required=True)
    ap.add_argument('--tuits', required=True)
    ap.add_argument('--imgdir', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--titulo', default='')
    ap.add_argument('--subtitulo', default='')
    ap.add_argument('--pie', default='')
    a = ap.parse_args()

    secc = json.load(open(a.tuits, encoding='utf-8'))
    doc = SimpleDocTemplate(a.out, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm,
                            title=a.titulo, author='@MarianoDiMaggio')
    doc.pie = a.pie or a.titulo

    H1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=26, leading=30,
                        textColor=colors.white, spaceAfter=4)
    SUB = ParagraphStyle('SUB', fontName='Helvetica', fontSize=11, leading=15,
                         textColor=GRIS, spaceAfter=18)
    KICK = ParagraphStyle('KICK', fontName='Helvetica-Bold', fontSize=9, leading=12,
                          textColor=DORADO, spaceAfter=6)
    TIT = ParagraphStyle('TIT', fontName='Helvetica-Bold', fontSize=13, leading=16,
                         textColor=DORADO, spaceAfter=8)
    TXT = ParagraphStyle('TXT', fontName='Helvetica', fontSize=10.5, leading=15.5,
                         textColor=colors.HexColor('#E8E8E8'), alignment=TA_LEFT,
                         spaceAfter=7)

    st = []
    # portada del documento
    st.append(Spacer(1, 40 * mm))
    st.append(Paragraph('PRIMERA NACIONAL 2026 · ZONA A', KICK))
    st.append(Paragraph(a.titulo, H1))
    st.append(Paragraph(a.subtitulo, SUB))
    st.append(Paragraph(f'{len(secc)} placas con sus textos para publicar. '
                        'Fuente de los datos: FootyStats y Promiedos.', TXT))
    st.append(PageBreak())

    ancho = A4[0] - 36 * mm
    for i, s in enumerate(secc):
        ruta = os.path.join(a.imgdir, s['img'] + '.jpg')
        st.append(Paragraph(f"{i:02d} · {s['titulo']}", TIT))
        if os.path.exists(ruta):
            st.append(Image(ruta, width=ancho, height=ancho))   # las placas son 1:1
        st.append(Spacer(1, 7 * mm))
        for par in limpiar(s['tuit']).split('\n\n'):
            st.append(Paragraph(par.replace('\n', '<br/>'), TXT))
        if i < len(secc) - 1:
            st.append(PageBreak())

    doc.build(st, onFirstPage=fondo, onLaterPages=fondo)
    print(f'ok {a.out} ({os.path.getsize(a.out)/1048576:.2f} MB)')


if __name__ == '__main__':
    main()
