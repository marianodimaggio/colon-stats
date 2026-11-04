#!/usr/bin/env python3
"""
Placas del hilo de varianza que dependen del MODELO DEL SIMULADOR, no de un Poisson
sobre xG. Existen porque la validacion del simulador mostro que en esta categoria el
xG no sirve para predecir: gano la variante que usa solo goles. Asi que el xG se usa
para DESCRIBIR (bloques 1 a 3) y el modelo para las PROBABILIDADES (bloques 4 a 6).

Numeros tomados del documento de metodo del simulador (fuerzas.json / modelo_dc.py).
Reglas de lenguaje del propio documento, respetadas en el copy:
  - "asciende en 13 de cada 100 simulaciones", nunca "tiene 13% de chances"
  - el numero va siempre con su metodo al lado
  - no comparar valores menores al 5% entre si

    python3 placas_modelo.py --fecha 28 --outdir /mnt/user-data/outputs
"""
import os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from colon_kit import _base_canvas, F, MONO_M, MONO_R, BEBAS, LABEL, MICRO, SPLIT_X, W, H

FUENTE = 'Fuente: simulador propio · modelo Dixon-Coles'
GOLD, GRAY, WHITE, STEEL = '#FFC533', '#A9B4BE', '#FFFFFF', '#8C99A8'


def _kicker(draw, l1, l2, sub1, sub2=None):
    draw.text((46, 196), l1, font=F(MONO_M, 42), fill=GOLD, stroke_width=2, stroke_fill=GOLD)
    y = 246
    if l2:
        draw.text((46, y), l2, font=F(MONO_M, 42), fill=GOLD, stroke_width=2, stroke_fill=GOLD)
        y += 58
    else:
        y += 8
    draw.text((46, y), sub1, font=F(MONO_M, LABEL), fill=GRAY)
    if sub2:
        draw.text((46, y + 34), sub2, font=F(MONO_M, LABEL), fill=GRAY)
    return y + (68 if sub2 else 34)


def _panel(draw, rotulos, num, detalle, nota=None):
    px = SPLIT_X + 40
    cx = SPLIT_X + (W - SPLIT_X) // 2
    y = 210
    for r in rotulos:
        draw.text((px, y), r, font=F(MONO_M, LABEL), fill=GOLD)
        y += 32
    fn = F(BEBAS, 168)
    bb = draw.textbbox((0, 0), num, font=fn)
    draw.text((cx - bb[2] // 2 - bb[0], y + 14), num, font=fn, fill=GOLD)
    yy = y + 14 + bb[3] + 16
    for ln in detalle:
        draw.text((px, yy), ln, font=F(MONO_M, 24), fill=GOLD)
        yy += 34
    if nota:
        draw.line([(px, yy + 16), (W - 40, yy + 16)], fill=GOLD, width=2)
        yy += 48
        for ln in nota:
            draw.text((px, yy), ln, font=F(MONO_M, 22), fill=GOLD)
            yy += 30


def placa_validacion(fecha, outpath):
    """Que tan bien predice el modelo. La fila incomoda va incluida a proposito."""
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    y = _kicker(draw, 'ASÍ DE', 'IMPREDECIBLE ES', 'QUÉ TAN BIEN SE PUEDE ANTICIPAR',
                'UN PARTIDO DE ESTA CATEGORÍA')
    CA = LIM
    draw.text((46, y + 26), 'ERROR AL PREDECIR', font=F(MONO_M, LABEL), fill=GOLD)
    w = draw.textbbox((0, 0), 'MÁS BAJO ES MEJOR', font=F(MONO_M, LABEL))[2]
    draw.text((CA - w, y + 26), 'MÁS BAJO ES MEJOR', font=F(MONO_M, LABEL), fill=GOLD)
    y += 66
    draw.line([(46, y), (LIM, y)], fill='#242424', width=2)
    y += 18
    FILAS = [('LAS CASAS DE APUESTAS', '1.0138', WHITE, 62),
             ('NO SABER NADA DE NADIE', '1.0244', STEEL, 56),
             ('NUESTRO MODELO', '1.0246', STEEL, 56)]
    for rot, val, col, fs in FILAS:
        fl = F(MONO_M, 28)
        bb = draw.textbbox((0, 0), rot, font=fl)
        draw.text((46, y + (60 - (bb[3] - bb[1])) // 2 - 4), rot, font=fl, fill=WHITE)
        fn = F(BEBAS, fs)
        wv = draw.textbbox((0, 0), val, font=fn)[2]
        draw.text((CA - wv, y - 2), val, font=fn, fill=col)
        y += 76
    y += 10
    draw.line([(46, y), (LIM, y)], fill=GOLD, width=2)
    y += 26
    for ln in ['"NO SABER NADA" ES APLICARLE A TODOS',
               'LOS PARTIDOS LA MISMA CUENTA: GANA EL',
               'LOCAL 47%, EMPATAN 32%, GANA EL',
               'VISITANTE 21%. SIN MIRAR QUIÉN JUEGA.']:
        draw.text((46, y), ln, font=F(MONO_M, LABEL), fill=GRAY)
        y += 34
    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')
    _panel(draw, ['MEDIDO SOBRE'], '267', ['PARTIDOS QUE EL', 'MODELO NO VIO'],
           ['NI LAS CASAS LE', 'GANAN POR MÁS', 'DE UN 1% A NO', 'SABER NADA'])
    draw.text((SPLIT_X + 40, H - 58), f'F{fecha} · VALIDACIÓN', font=F(MONO_R, 20), fill=GOLD)
    img.save(outpath, 'JPEG', quality=92)
    return outpath


def placa_localia(fecha, outpath):
    """Lo unico que si esta bien medido: la localia."""
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    y = _kicker(draw, 'LO QUE SÍ', 'ESTÁ MEDIDO', 'CÓMO TERMINAN LOS PARTIDOS',
                'DE LA PRIMERA NACIONAL 2026')
    y += 20
    FILAS = [('GANA EL LOCAL', 47, WHITE), ('EMPATAN', 32, GOLD), ('GANA EL VISITANTE', 21, STEEL)]
    for rot, pct, col in FILAS:
        t = f'{pct}%'
        fn = F(BEBAS, 92)
        bb = draw.textbbox((0, 0), t, font=fn)
        draw.text((46, y - bb[1]), t, font=fn, fill=WHITE)
        draw.text((250, y + 14), rot, font=F(MONO_M, 30), fill=GOLD)
        bx0, bw = 250, LIM - 250
        draw.rounded_rectangle([bx0, y + 58, bx0 + bw, y + 70], 6, fill='#242424')
        draw.rounded_rectangle([bx0, y + 58, bx0 + int(bw * pct / 100), y + 70], 6, fill=col)
        y += 122
    y += 8
    draw.line([(46, y), (LIM, y)], fill=GOLD, width=2)
    y += 26
    for ln in ['UN EQUIPO DE ESTA CATEGORÍA MULTIPLICA',
               'SUS GOLES POR 1,60 CUANDO JUEGA DE LOCAL.',
               'ESO ESTÁ ESTIMADO SOBRE CIENTOS DE',
               'PARTIDOS Y ES SÓLIDO.']:
        draw.text((46, y), ln, font=F(MONO_M, LABEL), fill=GRAY)
        y += 34
    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')
    _panel(draw, ['EL LOCAL', 'MULTIPLICA SUS'], '1,60', ['GOLES POR ESTE', 'NÚMERO'],
           ['ES LA VARIABLE', 'MÁS FUERTE DE', 'TODO EL MODELO'])
    draw.text((SPLIT_X + 40, H - 58), f'F{fecha} · TASAS DE LA LIGA', font=F(MONO_R, 20), fill=GOLD)
    img.save(outpath, 'JPEG', quality=92)
    return outpath


def placa_arriba(fecha, outpath):
    """Cuanto vale terminar arriba, que es la conclusion practica de todo el hilo."""
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    y = _kicker(draw, 'CUÁNTO VALE', 'TERMINAR ARRIBA', 'LO QUE SE JUEGA EN LAS OCHO',
                'FECHAS QUE QUEDAN')
    y += 16
    t = '77-82%'
    fn = F(BEBAS, 132)
    bb = draw.textbbox((0, 0), t, font=fn)
    draw.text((46, y - bb[1]), t, font=fn, fill=WHITE)
    fl = F(MONO_M, 28)
    for i, ln in enumerate(['GANA SU LLAVE EL MEJOR', 'UBICADO EN LA PRIMERA', 'FASE DEL REDUCIDO']):
        draw.text((46, y + bb[3] + 18 + i * 38), ln, font=fl, fill=GOLD)
    y = y + bb[3] + 152
    draw.line([(46, y), (LIM, y)], fill=GOLD, width=2)
    y += 26
    for ln in ['ES CASI EL MISMO NÚMERO EN LOS SIETE CRUCES.',
               'NO VIENE DE SER MEJOR EQUIPO: VIENE DE JUGAR',
               'DE LOCAL Y DE QUE LE ALCANZA EL EMPATE.']:
        draw.text((46, y), ln, font=F(MONO_M, 24), fill=GRAY)
        y += 32
    y += 10
    draw.text((46, y), 'EN 10.000 SIMULACIONES DEL TORNEO', font=F(MONO_M, LABEL), fill=GOLD)
    y += 40
    for rot, val, col in [('FERRO ASCIENDE', '46', WHITE), ('COLÓN ASCIENDE', '13', GOLD)]:
        fn = F(BEBAS, 62)
        bb2 = draw.textbbox((0, 0), val, font=fn)
        draw.text((46, y - bb2[1]), val, font=fn, fill=col)
        draw.text((140, y + 10), f'DE CADA 100 · {rot}', font=F(MONO_M, 25), fill=GRAY)
        y += 64
    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')
    _panel(draw, ['COLÓN ASCIENDE EN'], '13', ['DE CADA 100', 'SIMULACIONES'],
           ['VIENE SOBRE TODO', 'DE LOS PUNTOS Y', 'DE LAS FECHAS QUE', 'FALTAN'])
    draw.text((SPLIT_X + 40, H - 58), f'F{fecha} · MONTE CARLO', font=F(MONO_R, 20), fill=GOLD)
    img.save(outpath, 'JPEG', quality=92)
    return outpath


def placa_impredecible(fecha, outpath):
    """Version digerible: fusiona validacion y localia en una sola placa. En vez de
    mostrar el log-loss, muestra las tasas de la liga y dice que saber solo eso rinde
    igual que el modelo completo. Mismo hallazgo, sin metrica nueva para el lector."""
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    y = _kicker(draw, 'CÓMO TERMINAN', 'LOS PARTIDOS', 'LAS TRES TASAS DE LA CATEGORÍA',
                'EN LO QUE VA DE 2026')
    y += 26
    for rot, pct, col in [('GANA EL LOCAL', 47, WHITE), ('EMPATAN', 32, GOLD),
                          ('GANA EL VISITANTE', 21, STEEL)]:
        t = f'{pct}%'
        fn = F(BEBAS, 104)
        bb = draw.textbbox((0, 0), t, font=fn)
        draw.text((46, y - bb[1]), t, font=fn, fill=WHITE)
        draw.text((270, y + 18), rot, font=F(MONO_M, 32), fill=GOLD)
        bx0, bw = 270, LIM - 270
        draw.rounded_rectangle([bx0, y + 66, bx0 + bw, y + 80], 7, fill='#242424')
        draw.rounded_rectangle([bx0, y + 66, bx0 + int(bw * pct / 100), y + 80], 7, fill=col)
        y += 134
    y += 12
    draw.line([(46, y), (LIM, y)], fill=GOLD, width=2)
    y += 28
    for ln in ['APLICARLE ESTO A TODOS LOS PARTIDOS,',
               'SIN MIRAR QUIÉN JUEGA, ANTICIPA IGUAL',
               'DE BIEN QUE NUESTRO MODELO CON LA',
               'FUERZA DE LOS 36 EQUIPOS CARGADA.']:
        draw.text((46, y), ln, font=F(MONO_M, 27), fill=GRAY)
        y += 36
    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')
    _panel(draw, ['EL LOCAL', 'MULTIPLICA SUS'], '1,60', ['GOLES POR ESTE', 'NÚMERO'],
           ['ES LA VARIABLE', 'MÁS FUERTE DE', 'TODO EL MODELO'])
    draw.text((SPLIT_X + 40, H - 58), f'F{fecha} · TASAS DE LA LIGA', font=F(MONO_R, 20), fill=GOLD)
    img.save(outpath, 'JPEG', quality=92)
    return outpath


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, default=28)
    ap.add_argument('--outdir', default=os.getcwd())
    a = ap.parse_args()
    import numpy as np
    for fn, name in [(placa_impredecible, 'impredecible'), (placa_arriba, 'arriba'),
                     (placa_validacion, 'validacion'), (placa_localia, 'localia')]:
        p = fn(a.fecha, os.path.join(a.outdir, f'var_f{a.fecha}_{name}.jpg'))
        arr = np.array(Image.open(p).convert('RGB'))
        mk = (arr[:, :, 0] > 90) & (arr[:, :, 1] > 90) & (arr[:, :, 2] > 90)
        xs = np.where(mk[:, :735].any(axis=0))[0]
        ys = np.where(mk[:, :735].any(axis=1))[0]
        print(f'ok {name:11s} x max {xs.max()} (div 740) · y max {ys.max()} (alto 1080)')
