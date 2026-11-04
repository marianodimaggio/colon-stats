import sys, os
sys.path.insert(0,'/home/claude/pack/colon_kit_pack')
from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
OUT='/mnt/user-data/outputs'
o=lambda n: os.path.join(OUT,n)
F,PJ=23,23

build_portada(fecha=F, pj=PJ, pts=36, posicion_zona='3°', zona='A',
  en_este_hilo=[
    'LOS NÚMEROS DEL CICLO',
    'UN PUNTO DE LOS ÚLTIMOS NUEVE',
    'SIN VALLA INVICTA DESDE LA F20',
    'LA EFICIENCIA OFENSIVA, EN DECLIVE',
    'DEBUTA DELFINO CON SAN TELMO',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# xG individual: ranking DEL TORNEO. Los 5 primeros en top5_rows y Colón aparte,
# en la 6ta fila y con su puesto real vía colon_rank. Lago va con 9 goles por la
# regla de prensa; el resto de los goles sale del CSV de FootyStats.
build_top_jugadores(fecha=F, pj=PJ, jugador_nombre='Ignacio Lago',
  jugador_xg=5.08, jugador_goles='9', jugador_pj='22', jugador_min='1862',
  puesto_liga='6', total_jugadores='596',
  sub_hero=['xG ACUMULADO','EN EL TORNEO'], ambito='DEL TORNEO',
  top5_rows=[
    ('MACHADO',  'CA Mitre',        '6.30','8g'),
    ('FUNEZ',    'San Martín (SJ)', '5.99','8g'),
    ('PINO',     'Godoy Cruz',      '5.65','8g'),
    ('FAGUNDEZ', 'Morón',           '5.45','9g'),
    ('CHAVARRÍA','Racing (Cba)',    '5.36','8g'),
  ],
  colon_row=('LAGO','Colón','5.08','9g'), colon_rank=6,
  outpath=o(f'f{F}_top_jugadores.jpg'))

build_proximo_rival(fecha_rival=24, rival_nombre='San Telmo', rival_ciudad='Santa Fe',
  rival_local_pj='10', rival_local_wdl='0-6-4', rival_local_xg='0.86', rival_local_xga='1.76',
  colon_visit_pj='11', colon_visit_wdl='6-4-1', colon_visit_xg='1.45', colon_visit_xga='0.96',
  rival_tag='ZA', rival_pts='23', diferencia_txt='COLÓN +13',
  goleador_rival='M. BATALLINI · 4g', goleador_colon='I. LAGO · 9g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 08/08 · BRIGADIER LÓPEZ',
  colon_es_local=True)
print('portada, xG individual y proximo rival ->', OUT)
