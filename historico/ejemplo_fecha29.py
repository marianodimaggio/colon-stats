import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=29,29

build_portada(fecha=F, pj=PJ, pts=45, posicion_zona='6°', zona='A',
  en_este_hilo=[
    'TERCERA DERROTA SEGUIDA',
    'CAÍMOS AL 6° PUESTO',
    'Y AHORA SÍ CAYERON LOS NÚMEROS',
    'UN GOL EN LAS ÚLTIMAS TRES',
    'PRÓXIMO: LOS ANDES EN CASA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.31, jugador_goles='11', jugador_pj='27', jugador_min='2306',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.66','11g'),
    ('FAGUNDEZ', 'Morón',           '8.82','14g'),
    ('GORDILLO', 'Gimnasia y Tiro', '8.10','13g'),
    ('LAGO',     'Colón',           '7.31','11g'),
    ('SILBA',    'Dep. Madryn',     '7.06','13g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F30: Colon LOCAL recibe a Los Andes -> colon_es_local=True
build_proximo_rival(fecha_rival=30, rival_nombre='Los Andes', rival_ciudad='Santa Fe',
  rival_local_pj='14', rival_local_wdl='4-5-5', rival_local_xg='1.34', rival_local_xga='1.63',
  colon_visit_pj='14', colon_visit_wdl='8-4-2', colon_visit_xg='1.50', colon_visit_xga='1.00',
  rival_tag='ZA', rival_pts='37', diferencia_txt='COLÓN +8',
  goleador_rival='M. ASENJO · 7g', goleador_colon='I. LAGO · 11g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='DOM 20/09 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('ok')
