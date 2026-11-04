#!/usr/bin/env python3
"""
Ejemplo real y completo: la fecha 22 (Colón 0-1 Chaco For Ever).
Sirve de plantilla — copiar, cambiar los valores y correr.

Genera las 3 piezas que no salen del CSV: portada, xG individual y próximo rival.
Los 8 bloques de métrica los hace render.py.

    python3 ejemplo_fecha22.py --outdir /mnt/user-data/outputs
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival

ap = argparse.ArgumentParser()
ap.add_argument('--outdir', default=os.getcwd())
a = ap.parse_args()
o = lambda n: os.path.join(a.outdir, n)

FECHA, PJ = 22, 22

# ---------- PORTADA ----------
# Los items de "EN ESTE HILO" bajan el ángulo editorial sin editorializar en la placa.
# Máximo ~630px de ancho a 29px de DM Mono: unos 26 caracteres por línea.
build_portada(
    fecha=FECHA, pj=PJ, pts=35, posicion_zona='3°', zona='A',
    en_este_hilo=[
        'xG: EL PICO DE LA TEMPORADA',
        'CONVERSIÓN: EL COLCHÓN GASTADO',
        'xGA Y RENDIMIENTO DEFENSIVO',
        'LAGO, #1 EN xG DEL TORNEO',
        'PRÓXIMO RIVAL: ACASSUSO',
    ],
    outpath=o(f'colon_f{FECHA}_portada.jpg'), total_fechas=36)

# ---------- xG INDIVIDUAL ----------
# jugador_xg va como FLOAT. puesto_liga SIN '#' (el kit lo agrega).
# Los goles salen de prensa, no del CSV: FootyStats muestra 8 y la prensa confirmó 9.
build_top_jugadores(
    fecha=FECHA, pj=PJ, jugador_nombre='Ignacio Lago',
    jugador_xg=5.62, jugador_goles='9', jugador_pj='21', jugador_min='1772',
    puesto_liga='1', total_jugadores='577',
    top5_rows=[
        ('LAGO',      'Colón',            '5.62', '9g'),
        ('PINO',      'Godoy Cruz',       '5.54', '8g'),
        ('FUNEZ',     'San Martín (SJ)',  '5.27', '8g'),
        ('CHAVARRÍA', 'Racing (Cba)',     '5.27', '8g'),
        ('MACHADO',   'CA Mitre',         '5.26', '8g'),
    ],
    outpath=o(f'f{FECHA}_top_jugadores.jpg'))

# ---------- PRÓXIMO RIVAL ----------
# El kit asume Colón de visitante. Para un partido de local hay que ajustar
# la línea 'VISITANTE · {ciudad}' dentro de colon_kit.py.
build_proximo_rival(
    fecha_rival=23, rival_nombre='Acassuso', rival_ciudad='Beccar',
    rival_local_pj='9',  rival_local_wdl='4-1-4', rival_local_xg='1.21', rival_local_xga='1.48',
    colon_visit_pj='11', colon_visit_wdl='3-4-4', colon_visit_xg='1.25', colon_visit_xga='1.36',
    rival_tag='ZA', rival_pts='20', diferencia_txt='COLÓN +15',
    goleador_rival='R. REYNOSO · 5g', goleador_colon='I. LAGO · 9g',
    outpath=o(f'f{FECHA}_proximo_rival.jpg'),
    fecha_actual_pj_texto='SÁB 01/08 · LA QUEMA')

print('portada, xG individual y próximo rival ->', a.outdir)
