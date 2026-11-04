import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=30,30

build_portada(fecha=F, pj=PJ, pts=48, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'SE CORTÓ LA RACHA CON UN 3-0',
    'SUBIMOS AL 5° PUESTO',
    'EL xG NO SE MOVIÓ NI UN DECIMAL',
    'GANAMOS DEFINIENDO, OTRA VEZ',
    'PRÓXIMO: ALL BOYS DE VISITANTE',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #4 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=7.93, jugador_goles='13', jugador_pj='28', jugador_min='2361',
  puesto_liga='4', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.53','11g'),
    ('GORDILLO', 'Gimnasia y Tiro', '8.49','13g'),
    ('FAGUNDEZ', 'Morón',           '8.02','14g'),
    ('LAGO',     'Colón',           '7.93','13g'),
    ('PINO',     'Godoy Cruz',      '7.13','12g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F31: Colon VISITANTE a All Boys -> colon_es_local default False
build_proximo_rival(fecha_rival=31, rival_nombre='All Boys', rival_ciudad='Floresta',
  rival_local_pj='15', rival_local_wdl='4-10-1', rival_local_xg='1.41', rival_local_xga='1.04',
  colon_visit_pj='15', colon_visit_wdl='4-5-6', colon_visit_xg='1.20', colon_visit_xga='1.31',
  rival_tag='ZA', rival_pts='32', diferencia_txt='COLÓN +16',
  goleador_rival='A. TABARES · 3g', goleador_colon='I. LAGO · 13g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 26/09')
print('ok')
