import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=26,26

build_portada(fecha=F, pj=PJ, pts=45, posicion_zona='3°', zona='A',
  en_este_hilo=[
    'TRES VICTORIAS SEGUIDAS',
    'MORÓN USÓ SU PENDIENTE Y EMPATÓ',
    'EL xG NO SE MOVIÓ EN TRES FECHAS',
    'GANAMOS DEFINIENDO, NO JUGANDO',
    'PRÓXIMO: RACING EN CÓRDOBA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago quedo #4 del torneo: entra inline en el top 5.
# Goles por prensa = CSV + 1 (gol reasignado por FootyStats en julio, nunca corregido).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.33, jugador_goles='11', jugador_pj='25', jugador_min='2128',
  puesto_liga='4', total_jugadores='678',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '8.42','10g'),
    ('FAGUNDEZ', 'Morón',           '8.00','13g'),
    ('GORDILLO', 'Gimnasia y Tiro', '7.47','11g'),
    ('LAGO',     'Colón',           '7.33','11g'),
    ('PINO',     'Godoy Cruz',      '7.18','10g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

build_proximo_rival(fecha_rival=27, rival_nombre='Racing (Cba)', rival_ciudad='Córdoba',
  rival_local_pj='13', rival_local_wdl='7-4-2', rival_local_xg='1.35', rival_local_xga='0.87',
  colon_visit_pj='13', colon_visit_wdl='4-5-4', colon_visit_xg='1.21', colon_visit_xga='1.29',
  rival_tag='ZA', rival_pts='32', diferencia_txt='COLÓN +13',
  goleador_rival='P. CHAVARRÍA · 8g', goleador_colon='I. LAGO · 11g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='DOM 30/08')
print('ok')
