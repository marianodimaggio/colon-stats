import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
import placa_tramos
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=36,36

build_portada(fecha=F, pj=PJ, pts=60, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'TERMINÓ EL TORNEO: 5° CON 60',
    'OCHO GOLES DE VENTAJA POR EMBOCAR',
    'SOLO 27 GOLES EN CONTRA',
    'EL MEJOR TRAMO FINAL DEL AÑO',
    'Y EN EL REDUCIDO: MIDLAND',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.61, jugador_goles='16', jugador_pj='33', jugador_min='2811',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.66','12g'),
    ('FAGUNDEZ', 'Morón',           '8.97','15g'),
    ('GORDILLO', 'Gimnasia y Tiro', '8.38','13g'),
    ('LAGO',     'Colón',           '7.61','16g'),
    ('SILBA',    'Dep. Madryn',     '7.31','16g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# REDUCIDO, primera fase: Colon LOCAL vs Midland, partido unico, con el empate a favor
build_proximo_rival(fecha_rival=1, rival_nombre='Midland', rival_ciudad='Santa Fe',
  rival_local_pj='18', rival_local_wdl='3-7-8', rival_local_xg='1.27', rival_local_xga='1.19',
  colon_visit_pj='16', colon_visit_wdl='10-4-2', colon_visit_xg='1.57', colon_visit_xga='1.01',
  rival_tag='ZB', rival_pts='55', diferencia_txt='COLÓN +5',
  goleador_rival='D. BULACIO · 8g', goleador_colon='I. LAGO · 16g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 14/11 · BRIGADIER LÓPEZ',
  colon_es_local=True,
  header_txt='REDUCIDO 2026 · PRIMERA FASE',
  pie_txt='SÁB 14/11 · BRIGADIER LÓPEZ')

FILAS=[('FECHAS 1-10',9.00,1.15,False),('FECHAS 11-20',11.10,1.49,False),
       ('FECHAS 21-26',11.00,1.51,False),('FECHAS 27-31',7.20,1.11,False),
       ('FECHAS 32-36',17.00,2.24,True)]
placa_tramos.build(36,FILAS,o(f'f{F}_tramos.jpg'))
print('ok')
