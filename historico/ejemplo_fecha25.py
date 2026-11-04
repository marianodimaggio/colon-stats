import sys, os
sys.path.insert(0,'/home/claude/colon_kit_pack')
from colon_kit import build_portada, build_proximo_rival
OUT='/mnt/user-data/outputs'; o=lambda n: os.path.join(OUT,n)
F,PJ=25,25

build_portada(fecha=F, pj=PJ, pts=42, posicion_zona='3°', zona='A',
  en_este_hilo=[
    'SEGUNDA VICTORIA DE DELFINO',
    'EL MEJOR xGD DE LA TEMPORADA',
    'LA DEFINICIÓN SE DIO VUELTA',
    'TRES GOLES CON MENOS CHANCES',
    'PRÓXIMO: SAN MIGUEL DE VISITA',
  ], outpath=o(f'colon_f{F}_portada.jpg'), total_fechas=36)

# F26: Colon VISITANTE a San Miguel -> colon_es_local queda en False (default)
build_proximo_rival(fecha_rival=26, rival_nombre='San Miguel', rival_ciudad='San Miguel',
  rival_local_pj='12', rival_local_wdl='5-4-3', rival_local_xg='1.61', rival_local_xga='1.27',
  colon_visit_pj='12', colon_visit_wdl='3-5-4', colon_visit_xg='1.20', colon_visit_xga='1.27',
  rival_tag='ZA', rival_pts='29', diferencia_txt='COLÓN +13',
  goleador_rival='B. NASTA · 5g', goleador_colon='I. LAGO · 10g',
  outpath=o(f'f{F}_proximo_rival.jpg'),
  fecha_actual_pj_texto='SÁB 22/08')
print('portada y proximo rival ->', OUT)
