#!/usr/bin/env python3
"""Placa a medida: la caida del volumen de juego por tramos de la temporada.
No entra en build_metric porque no es una metrica con ranking de 36, es una serie
propia partida en cuatro bloques."""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from colon_kit import _base_canvas, F, MONO_M, MONO_R, BEBAS, LABEL, MICRO, SPLIT_X, W, H

GOLD, GRAY, WHITE, STEEL, RED = '#FFC533', '#A9B4BE', '#FFFFFF', '#8C99A8', '#C8102E'
FUENTE = 'Fuente: FootyStats · Promiedos'


def build(fecha, filas, outpath):
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    draw.text((46, 196), 'CUÁNTO REMATA', font=F(MONO_M, 42), fill=GOLD,
              stroke_width=2, stroke_fill=GOLD)
    draw.text((46, 246), 'POR TRAMO', font=F(MONO_M, 42), fill=GOLD,
              stroke_width=2, stroke_fill=GOLD)
    draw.text((46, 304), 'REMATES Y xG POR PARTIDO,', font=F(MONO_M, LABEL), fill=GRAY)
    draw.text((46, 338), 'POR ETAPAS DE LA TEMPORADA', font=F(MONO_M, LABEL), fill=GRAY)

    w = draw.textbbox((0, 0), 'xG', font=F(MONO_M, LABEL))[2]
    draw.text((LIM - w, 384), 'xG', font=F(MONO_M, LABEL), fill=GOLD)
    draw.line([(46, 416), (LIM, 416)], fill='#242424', width=2)

    y = 434
    mx = max(f[1] for f in filas)
    for rot, rem, xg, destacar in filas:
        col = RED if destacar else STEEL
        fl = F(MONO_M, 28)
        draw.text((46, y + 16), rot, font=fl, fill=WHITE if destacar else GRAY)
        t = f'{rem:.1f}'
        fn = F(BEBAS, 66 if destacar else 58)
        draw.text((250, y - 2), t, font=fn, fill=WHITE if destacar else STEEL)
        bx0, bw = 370, LIM - 370 - 110
        draw.rounded_rectangle([bx0, y + 22, bx0 + bw, y + 36], 7, fill='#242424')
        draw.rounded_rectangle([bx0, y + 22, bx0 + int(bw * rem / mx), y + 36], 7, fill=col)
        tx = f'{xg:.2f}'
        fx = F(BEBAS, 46)
        wx = draw.textbbox((0, 0), tx, font=fx)[2]
        draw.text((LIM - wx, y + 6), tx, font=fx, fill=GOLD if destacar else GRAY)
        y += 76

    y += 6
    draw.line([(46, y), (LIM, y)], fill=GOLD, width=2)
    y += 26
    for ln in ['EL AÑO ENTERO EN CINCO ETAPAS. ARRANCÓ',
               'FLOJO, CRECIÓ, SE DERRUMBÓ EN SEPTIEMBRE',
               'Y TERMINA JUGANDO MEJOR QUE NUNCA.']:
        draw.text((46, y), ln, font=F(MONO_M, 26), fill=GRAY)
        y += 34
    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')

    px = SPLIT_X + 40
    cx = SPLIT_X + (W - SPLIT_X) // 2
    draw.text((px, 220), 'EN EL TRAMO', font=F(MONO_M, LABEL), fill=GOLD)
    draw.text((px, 252), 'FINAL', font=F(MONO_M, LABEL), fill=GOLD)
    fn = F(BEBAS, 160)
    t = '17'
    bb = draw.textbbox((0, 0), t, font=fn)
    draw.text((cx - bb[2] // 2 - bb[0], 296), t, font=fn, fill=GOLD)
    yy = 296 + bb[3] + 18
    for ln in ['REMATES POR', 'PARTIDO']:
        draw.text((px, yy), ln, font=F(MONO_M, 24), fill=GOLD)
        yy += 34
    draw.line([(px, yy + 16), (W - 40, yy + 16)], fill=GOLD, width=2)
    yy += 50
    for ln in ['CASI EL DOBLE', 'QUE EN CUALQUIER', 'OTRO TRAMO DE', 'LA TEMPORADA']:
        draw.text((px, yy), ln, font=F(MONO_M, 23), fill=GOLD)
        yy += 32
    draw.text((px, H - 58), f'F{fecha} · 35 PJ', font=F(MONO_R, 20), fill=GOLD)
    img.save(outpath, 'JPEG', quality=92)
    return outpath


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, default=31)
    ap.add_argument('--outdir', default=os.getcwd())
    a = ap.parse_args()
    FILAS = [('FECHAS 1-10', 10.00, 1.27, False), ('FECHAS 11-20', 11.10, 1.49, False),
             ('FECHAS 21-26', 11.00, 1.51, False), ('FECHAS 27-31', 7.20, 1.11, True)]
    p = build(a.fecha, FILAS, os.path.join(a.outdir, f'f{a.fecha}_tramos.jpg'))
    import numpy as np
    arr = np.array(Image.open(p).convert('RGB'))
    mk = (arr[:, :, 0] > 90) & (arr[:, :, 1] > 90) & (arr[:, :, 2] > 90)
    xs = np.where(mk[:, :735].any(axis=0))[0]; ys = np.where(mk[:, :735].any(axis=1))[0]
    print(f'ok tramos · x max {xs.max()} (div 740) · y max {ys.max()} (alto 1080)')
