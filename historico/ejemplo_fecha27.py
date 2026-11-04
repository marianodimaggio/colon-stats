import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=27,27

build_portada(fecha=F, pj=PJ, pts=45, posicion_zona='3°', zona='A',
  en_este_hilo=[
    'SE CORTÓ LA RACHA EN CÓRDOBA',
    'GENERAMOS MÁS Y PERDIMOS',
    'UN SOLO REMATE AL ARCO',
    'LOS DE ATRÁS SE ACERCARON',
    'Y AHORA VIENE MORÓN',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #5 del torneo: entra inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.22, jugador_goles='11', jugador_pj='26', jugador_min='2216',
  puesto_liga='5', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.35','11g'),
    ('FAGUNDEZ', 'Morón',           '8.89','13g'),
    ('GORDILLO', 'Gimnasia y Tiro', '8.24','12g'),
    ('SILBA',    'Dep. Madryn',     '7.69','11g'),
    ('LAGO',     'Colón',           '7.22','11g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F28: Colon LOCAL recibe a Moron -> colon_es_local=True.
# Con localia invertida se pasan los numeros del rival COMO VISITANTE y los de Colon COMO LOCAL.
build_proximo_rival(fecha_rival=28, rival_nombre='Morón', rival_ciudad='Santa Fe',
  rival_local_pj='13', rival_local_wdl='3-4-6', rival_local_xg='1.28', rival_local_xga='1.38',
  colon_visit_pj='13', colon_visit_wdl='8-4-1', colon_visit_xg='1.52', colon_visit_xga='0.98',
  rival_tag='ZA', rival_pts='49', diferencia_txt='MORÓN +4',
  goleador_rival='F. FAGUNDEZ · 13g', goleador_colon='I. LAGO · 11g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 05/09 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('ok')
