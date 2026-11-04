import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=28,28

build_portada(fecha=F, pj=PJ, pts=45, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'SEGUNDA DERROTA SEGUIDA',
    'CAÍMOS DEL 3° AL 5° PUESTO',
    'PERDIMOS UN PARTIDO PAREJO',
    'LOS NÚMEROS NO SE MOVIERON',
    'PRÓXIMO: GODOY CRUZ AFUERA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.78, jugador_goles='11', jugador_pj='27', jugador_min='2306',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.62','11g'),
    ('FAGUNDEZ', 'Morón',           '9.35','13g'),
    ('GORDILLO', 'Gimnasia y Tiro', '7.91','13g'),
    ('LAGO',     'Colón',           '7.78','11g'),
    ('SILBA',    'Dep. Madryn',     '7.31','13g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F29: Colon VISITANTE a Godoy Cruz -> colon_es_local default False
build_proximo_rival(fecha_rival=29, rival_nombre='Godoy Cruz', rival_ciudad='Mendoza',
  rival_local_pj='14', rival_local_wdl='9-3-2', rival_local_xg='1.80', rival_local_xga='1.23',
  colon_visit_pj='14', colon_visit_wdl='4-5-5', colon_visit_xg='1.21', colon_visit_xga='1.29',
  rival_tag='ZA', rival_pts='46', diferencia_txt='G. CRUZ +1',
  goleador_rival='M. PINO · 11g', goleador_colon='I. LAGO · 11g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='DOM 13/09')
print('ok')
