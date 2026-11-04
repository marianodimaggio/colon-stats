import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=31,31

build_portada(fecha=F, pj=PJ, pts=49, posicion_zona='5°', zona='A',
  en_este_hilo=[
    'UN PUNTO RESCATADO EN FLORESTA',
    'DOS REMATES, MÍNIMO DEL AÑO',
    'EL PEOR xG DE LA TEMPORADA',
    'LA DEFENSA SALVÓ EL PUNTO',
    'PRÓXIMO: ESTUDIANTES EN CASA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# Lago #5 del torneo: inline. Goles por prensa = CSV + 1 (reasignacion de julio).
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=6.96, jugador_goles='13', jugador_pj='28', jugador_min='2361',
  puesto_liga='5', total_jugadores='695',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '9.67','11g'),
    ('FAGUNDEZ', 'Morón',           '9.24','15g'),
    ('SILBA',    'Dep. Madryn',     '7.63','13g'),
    ('GORDILLO', 'Gimnasia y Tiro', '7.55','13g'),
    ('LAGO',     'Colón',           '6.96','13g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F32: Colon LOCAL recibe a Estudiantes (Caseros) -> colon_es_local=True
build_proximo_rival(fecha_rival=32, rival_nombre='Estudiantes', rival_ciudad='Santa Fe',
  rival_local_pj='15', rival_local_wdl='5-4-6', rival_local_xg='1.08', rival_local_xga='1.15',
  colon_visit_pj='15', colon_visit_wdl='9-4-2', colon_visit_xg='1.50', colon_visit_xga='1.02',
  rival_tag='ZA', rival_pts='45', diferencia_txt='COLÓN +4',
  goleador_rival='F. ARDILES · 6g', goleador_colon='I. LAGO · 13g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 03/10 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('ok')
