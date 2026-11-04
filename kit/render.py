#!/usr/bin/env python3
"""
Renderiza los 8 bloques de metrica leyendo bloques.json + datos.json.
Aplica autofit para que nada toque el panel rojo.

Uso:
  python3 render.py                       # usa datos.json de esta carpeta
  python3 render.py --datos otro.json --outdir /ruta/salida

La portada, el bloque de jugadores y el de proximo rival se arman aparte
porque llevan datos que no salen del CSV (angulo del hilo, ciudad del rival,
fecha y hora del partido). Ver ejemplos al final de este archivo.
"""
import json, os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from colon_kit import build_metric, F, MONO_M, MONO_R, BEBAS, LABEL, SPLIT_X

BASE = os.path.dirname(os.path.abspath(__file__))
probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))


def fmt(v, dec, signed, pct):
    return (f'{v:+.{dec}f}' if signed else f'{v:.{dec}f}') + ('%' if pct else '')


def autofit(labels, subs, val_txt, lstr, vstr, cfg):
    """Devuelve el par (label_size, val_size) mas grande que entra antes del panel rojo."""
    margen = cfg['margen_antes_del_panel_rojo']
    # El numero grande es el protagonista: se prueba primero el valor mas grande
    # y se achica el label antes que el numero.
    for vsz in cfg['val_sizes']:
        for lsz in cfg['label_sizes']:
            w  = [probe.textbbox((0,0), l, font=F(MONO_M, lsz))[2] for l in labels]
            w += [probe.textbbox((0,0), s, font=F(MONO_M, LABEL))[2] for s in subs]
            col2_x = 46 + max(w) + 40 + 30
            b2 = probe.textbbox((0,0), val_txt, font=F(BEBAS, vsz))
            need = max(probe.textbbox((0,0), lstr, font=F(BEBAS, 26))[2],
                       probe.textbbox((0,0), vstr, font=F(BEBAS, 26))[2],
                       probe.textbbox((0,0), 'VIS', font=F(MONO_R, 16))[2])
            if col2_x + b2[2] + 44 + need <= SPLIT_X - margen:
                return lsz, vsz
    return cfg['label_sizes'][-1], cfg['val_sizes'][-1]


def flecha(key, o, menor_es_mejor):
    """Verde si mejoro, gris si empeoro o quedo igual. El kit no tiene flecha roja."""
    dif = o['val'] - o['prev_val']
    mejoro = (dif < 0) if menor_es_mejor else (dif > 0)
    if not mejoro or o['rank'] > o['prev_rank']:
        return 'stable'
    return 'down_good' if menor_es_mejor else 'up'


def cola_delta(o):
    if o['rank'] == o['prev_rank']:
        return f"SE MANTIENE EN #{o['rank']}"
    return f"DE #{o['prev_rank']} A #{o['rank']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--datos', default=os.path.join(BASE, 'datos.json'))
    ap.add_argument('--outdir', default=os.getcwd())
    a = ap.parse_args()

    spec = json.load(open(os.path.join(BASE, '..', 'config', 'bloques.json'), encoding='utf-8'))
    D = json.load(open(a.datos, encoding='utf-8'))
    M, LV, META = D['mets'], D['lv'], D['meta']
    fecha, pj, vs = META['fecha'], META['pj'], META['vs']
    cfg = spec['autofit']
    hechos = []

    for b in spec['bloques']:
        k = b['key']; o = M[k]
        dec, sg, pct, asc = b['decimales'], b['signed'], b['is_pct'], b['menor_es_mejor']
        val   = round(o['val'], dec)
        worst = round(o['wmax'], dec) if asc else round(o['wmin'], dec)
        best  = round(o['wmin'], dec) if asc else round(o['wmax'], dec)
        avg   = round(o['avg'], dec)
        lo, vi = round(LV[k]['local'], dec), round(LV[k]['visit'], dec)
        val_txt = fmt(val, dec, sg, pct)
        lstr, vstr = fmt(lo, dec, sg, pct), fmt(vi, dec, sg, pct)
        lsz, vsz = autofit(b['label_lines'], b['sub_lines'], val_txt, lstr, vstr, cfg)

        top5 = [(n, fmt(round(v, dec), dec, sg, pct), pz, z) for n, v, pz, z in o['top5']]
        crow = None
        if o['colon_row']:
            n, v, pz, z = o['colon_row']
            crow = (n, fmt(round(v, dec), dec, sg, pct), pz, z)

        dif = o['val'] - o['prev_val']
        delta = (f'{dif:+.1f} pts vs F{vs}: {cola_delta(o)}' if pct
                 else f'{dif:+.2f} vs F{vs}: {cola_delta(o)}')
        unidad = b['unidad_panel']
        avgline = (fmt(avg, dec, sg, pct) if pct else f'{fmt(avg, dec, sg, pct)} {unidad}').strip()

        path = os.path.join(a.outdir, f'f{fecha}_{k}.jpg')
        build_metric(fecha=fecha, pj=pj, label_lines=b['label_lines'], label_font_size=lsz,
            sub_lines=b['sub_lines'], val_txt=val_txt, val_font_size=vsz,
            delta_txt=delta, arrow_dir=flecha(k, o, asc),
            worst=worst, avg=avg, best=best, val=val, signed=sg,
            local_val=lo, visit_val=vi, is_pct=pct,
            top5_rows=top5, colon_inline_idx=o['inline'], colon_row=crow,
            colon_rank=o['colon_rank'], outpath=path,
            puesto_txt=f"#{o['rank']}", avg_line_txt=avgline, top5_title=b['top5_title'])
        hechos.append(path)
        print(f"ok {k:8s} label={lsz} val={vsz}  {val_txt}  #{o['rank']}")

    # chequeo de desborde: nada de la fila principal debe pasar de x=740
    import numpy as np
    for p in hechos:
        arr = np.array(Image.open(p).convert('RGB'))[198:422]
        mask = (arr[:,:,0] > 150) & (arr[:,:,1] > 150) & (arr[:,:,2] > 150)
        xs = np.where(mask.any(axis=0))[0]; xs = xs[xs < 739]
        if len(xs) and xs.max() > 716:
            print(f"  [AVISO] {os.path.basename(p)}: texto hasta x={xs.max()}, muy cerca del panel rojo")
    print(f"\n{len(hechos)} bloques en {a.outdir}")


if __name__ == '__main__':
    main()

# --------------------------------------------------------------------------
# PIEZAS QUE NO SALEN DEL CSV (copiar y completar a mano cada fecha):
#
# from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
#
# build_portada(fecha=23, pj=23, pts=38, posicion_zona='3°', zona='A',
#     en_este_hilo=['...', '...'], outpath='portada.jpg', total_fechas=36)
#
# build_top_jugadores(fecha=23, pj=23, jugador_nombre='Ignacio Lago',
#     jugador_xg=5.62, jugador_goles='9', jugador_pj='21', jugador_min='1772',
#     puesto_liga='1', total_jugadores='577',
#     top5_rows=[('LAGO','Colón','5.62','9g'), ...], outpath='jugadores.jpg')
#     # OJO: jugador_xg va como float; puesto_liga sin '#' (el kit lo agrega);
#     # los goles de Lago se toman de prensa, no del CSV.
#
# build_proximo_rival(fecha_rival=24, rival_nombre='...', rival_ciudad='...',
#     rival_local_pj='9', rival_local_wdl='4-1-4', rival_local_xg='1.21', rival_local_xga='1.48',
#     colon_visit_pj='11', colon_visit_wdl='3-4-4', colon_visit_xg='1.25', colon_visit_xga='1.36',
#     rival_tag='ZA', rival_pts='20', diferencia_txt='COLÓN +15',
#     goleador_rival='...', goleador_colon='...', outpath='rival.jpg',
#     fecha_actual_pj_texto='SÁB 01/08 · ESTADIO')
# --------------------------------------------------------------------------
