import sys, json
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'kit'))
from colon_kit import build_llave
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'salida')
os.makedirs(OUT, exist_ok=True)
ET='REDUCIDO 2026 · COLÓN vs MIDLAND'
B=[
 dict(k='xg', lab=['xG GENERADO'], sub=['PROMEDIO POR PARTIDO','EN LA FASE REGULAR'],
   c=1.38, r=1.56, may=True,
   der=['GENERÓ MÁS QUE','NADIE EN LOS 36'], izq=['Y TERMINÓ 5° DE','SU ZONA IGUAL'],
   lec=['MIDLAND GENERA MÁS QUE COLÓN.','FUE EL QUE MÁS GENERÓ DEL','TORNEO Y TERMINÓ QUINTO.']),
 dict(k='xga', lab=['xG EN CONTRA'], sub=['PROMEDIO POR PARTIDO','EN LA FASE REGULAR'],
   c=1.17, r=1.16, may=False,
   der=['CONCEDE CASI','EXACTAMENTE LO','MISMO QUE COLÓN'], izq=['NINGUNO SACA','VENTAJA ACÁ'],
   lec=['EMPATE TÉCNICO ATRÁS.','LOS DOS CONCEDEN LO MISMO.','LA LLAVE NO SE DEFINE ACÁ.']),
 dict(k='xgd', lab=['BALANCE','DE FONDO'], sub=['xG MENOS xGA','POR PARTIDO'],
   c=0.21, r=0.40, may=True,
   der=['EL MEJOR BALANCE','DE LOS 36 EQUIPOS'], izq=['COLÓN ES 6°','DE LOS 36'],
   lec=['SOBRE EL PAPEL, MIDLAND ES','MEJOR EQUIPO. POR ESO ESTE','ES UN CRUCE DURO.']),
 dict(k='xgvr', lab=['xG vs REAL'], sub=['GOLES MENOS xG','POR PARTIDO'],
   c=-0.14, r=-0.33, may=True,
   der=['LE DEBE 12 GOLES','A SU PROPIO xG','EN LA TEMPORADA'], izq=['COLÓN APENAS','LE DEBE 4'],
   lec=['ACÁ ESTÁ LA GRIETA DE MIDLAND.','GENERA COMO NADIE Y NO LA','METE. COLÓN SÍ LA METE.']),
 dict(k='rem', lab=['REMATES'], sub=['POR PARTIDO','EN LA FASE REGULAR'],
   c=10.21, r=12.53, may=True, dec=2,
   der=['EL QUE MÁS','REMATA DE TODA','LA CATEGORÍA'], izq=['COLÓN REMATA','DOS MENOS'],
   lec=['MIDLAND VA A PATEAR MÁS.','COLÓN TIENE QUE AGUANTAR','VOLUMEN Y GOLPEAR POCO.']),
 dict(k='arco', lab=['REMATES','AL ARCO'], sub=['POR PARTIDO','EN LA FASE REGULAR'],
   c=4.21, r=4.61, may=True,
   der=['TAMBIÉN LLEGA','MÁS AL ARCO'], izq=['PERO DE VISITANTE','BAJA A 3.33'],
   lec=['PAREJO EN PUNTERÍA.','Y DE VISITANTE MIDLAND','CAE A 3.33 POR PARTIDO.']),
 dict(k='rg', lab=['REMATES','POR GOL'], sub=['CUÁNTO LE CUESTA','CADA GOL'],
   c=8.22, r=10.25, may=False,
   der=['NECESITA DOS','REMATES MÁS QUE','COLÓN POR GOL'], izq=['ES LA MAYOR','DIFERENCIA DE','LA LLAVE'],
   lec=['LA VENTAJA MÁS CLARA DE COLÓN.','CADA GOL LE CUESTA DOS','REMATES MENOS QUE A MIDLAND.']),
 dict(k='conv', lab=['CONVERSIÓN'], sub=['QUÉ PARTE DE LOS','REMATES ENTRA'],
   c=12.17, r=9.76, may=True, dec=1, suf='%',
   der=['CONVIERTE COMO','EL PROMEDIO DE','LA CATEGORÍA'], izq=['COLÓN ESTÁ MUY','POR ENCIMA'],
   lec=['ACÁ COLÓN SACA VENTAJA.','MIDLAND CONVIERTE COMO EL','PROMEDIO. COLÓN, MUCHO MÁS.']),
]
for b in B:
    build_llave(etapa_txt=ET, label_lines=b['lab'], sub_lines=b['sub'],
        colon_val=b['c'], rival_val=b['r'], rival_nombre='Midland',
        mejor_es_mayor=b['may'], contexto_der=b['der'], contexto_izq=b['izq'],
        lectura=b['lec'], decimales=b.get('dec',2), sufijo=b.get('suf',''),
        outpath=os.path.join(OUT,f"llave1_{b['k']}.jpg"))
    print(f"ok {b['k']}")
