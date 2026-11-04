import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=35,35

build_portada(fecha=F, pj=PJ, pts=57, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'QUEDA UNA SOLA FECHA',
    'CINCO PARTIDOS SIN PERDER',
    'EL MEJOR TRAMO DE TODO EL AÑO',
    'LA DEFENSA, EN SU MEJOR NIVEL',
    'Y OCHO GOLES DE VENTAJA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.34, jugador_goles='15', jugador_pj='32', jugador_min='2721',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.38','12g'),
    ('FAGUNDEZ', 'Morón',           '8.98','15g'),
    ('GORDILLO', 'Gimnasia y Tiro', '8.14','13g'),
    ('LAGO',     'Colón',           '7.34','15g'),
    ('PINO',     'Godoy Cruz',      '6.89','18g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F36: Colon LOCAL recibe a Defensores de Belgrano -> colon_es_local=True
build_proximo_rival(fecha_rival=36, rival_nombre='Defensores', rival_ciudad='Santa Fe',
  rival_local_pj='17', rival_local_wdl='4-6-7', rival_local_xg='1.19', rival_local_xga='1.37',
  colon_visit_pj='16', colon_visit_wdl='10-4-2', colon_visit_xg='1.57', colon_visit_xga='1.01',
  rival_tag='ZA', rival_pts='39', diferencia_txt='COLÓN +18',
  goleador_rival='E. GONZÁLEZ · 8g', goleador_colon='I. LAGO · 15g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='DOM 01/11 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('ok')
