import sys, os
sys.path.insert(0,'/home/claude/pack/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=24,24

build_portada(fecha=F, pj=PJ, pts=39, posicion_zona='3°', zona='A',
  en_este_hilo=[
    'DEBUT GANADOR DE DELFINO',
    'EL MEJOR xG DE LA TEMPORADA',
    'RÉCORD DE REMATES AL ARCO',
    'Y UN SOLO GOL, DE PENAL',
    'PRÓXIMO: PATRONATO EN CASA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# xG individual. Lago quedo #2 del torneo, o sea DENTRO del top 5: va inline, sin colon_row.
# Goles de Lago por prensa: 9 antes de esta fecha (prensa + SICS coincidian) + el penal = 10.
# FootyStats dice 9 porque venia con 8. Los del resto salen del CSV.
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=6.85, jugador_goles='10', jugador_pj='23', jugador_min='1952',
  puesto_liga='2', total_jugadores='633',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '8.11','10g'),
    ('LAGO',     'Colón',           '6.85','10g'),
    ('FAGUNDEZ', 'Morón',           '6.84','11g'),
    ('GORDILLO', 'Gimnasia y Tiro', '6.42','11g'),
    ('FUNEZ',    'San Martín (SJ)', '6.01','8g'),
  ],
  outpath=o(f'f{F}_top_jugadores.jpg'))

# F25: Colon LOCAL vs Patronato (Zona B). colon_es_local=True.
build_proximo_rival(fecha_rival=25, rival_nombre='Patronato', rival_ciudad='Santa Fe',
  rival_local_pj='12', rival_local_wdl='1-7-4', rival_local_xg='1.03', rival_local_xga='1.16',
  colon_visit_pj='12', colon_visit_wdl='7-4-1', colon_visit_xg='1.52', colon_visit_xga='0.96',
  rival_tag='ZB', rival_pts='24', diferencia_txt='COLÓN +15',
  goleador_rival='M. RUEDA · 5g', goleador_colon='I. LAGO · 10g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 15/08 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('portada, xG individual y proximo rival ->', OUT)
