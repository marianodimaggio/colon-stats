import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=32,32

build_portada(fecha=F, pj=PJ, pts=52, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'EL MEJOR PARTIDO DEL AÑO',
    '20 REMATES Y UN SOLO GOL',
    'VOLVIÓ EL VOLUMEN DE JUEGO',
    'PERO SE FUE LA PUNTERÍA FINA',
    'QUEDAN CUATRO FECHAS',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.48, jugador_goles='13', jugador_pj='29', jugador_min='2451',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.35','12g'),
    ('FAGUNDEZ', 'Morón',           '9.22','15g'),
    ('GORDILLO', 'Gimnasia y Tiro', '7.69','13g'),
    ('LAGO',     'Colón',           '7.48','13g'),
    ('SILBA',    'Dep. Madryn',     '7.13','13g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F33: Colon VISITANTE a Mitre -> colon_es_local default False
build_proximo_rival(fecha_rival=33, rival_nombre='CA Mitre', rival_ciudad='Santiago del Estero',
  rival_local_pj='16', rival_local_wdl='5-6-5', rival_local_xg='1.35', rival_local_xga='1.15',
  colon_visit_pj='16', colon_visit_wdl='4-6-6', colon_visit_xg='1.16', colon_visit_xga='1.33',
  rival_tag='ZA', rival_pts='35', diferencia_txt='COLÓN +17',
  goleador_rival='M. MACHADO · 12g', goleador_colon='I. LAGO · 13g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='DOM 11/10')
print('ok')
