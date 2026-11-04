#!/usr/bin/env python3
"""
Arma el reporte completo de una fecha con un solo comando.

    python3 fecha.py 36 --matches datos/matches.csv --players datos/players.csv \
        --tabla datos/tabla.csv

Hace, en orden:
  1. calcula las 8 metricas y valida GF/GC contra la tabla oficial
  2. renderiza los 8 bloques
  3. renderiza portada, xG individual y proximo rival desde config/fechas/fNN.json
  4. arma el HTML con los tuits
  5. arma el PDF para compartir

La parte editorial (titulos de portada, datos del rival, textos de los tuits) vive
en config/fechas/fNN.json. El codigo no se toca fecha a fecha: se copia la plantilla,
se completan los datos y se corre este script.

Antes de escribir los tuits conviene mirar la salida del paso 1: imprime los ocho
numeros con su puesto y el delta contra la fecha anterior, que es de donde salen
los textos.
"""
import argparse, json, os, subprocess, sys, shutil

RAIZ = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.join(RAIZ, 'kit')
CFG = os.path.join(RAIZ, 'config')
sys.path.insert(0, KIT)


def corre(desc, cmd):
    print(f'\n=== {desc} ===')
    r = subprocess.run(cmd, cwd=KIT)
    if r.returncode:
        sys.exit(f'FALLO en: {desc}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fecha', type=int)
    ap.add_argument('--matches', required=True, help='CSV de partidos de FootyStats')
    ap.add_argument('--players', required=True, help='CSV de jugadores de FootyStats')
    ap.add_argument('--tabla', required=True, help='CSV de la tabla de posiciones por zona')
    ap.add_argument('--vs', type=int, default=None, help='fecha de comparacion (default: la anterior)')
    ap.add_argument('--outdir', default=os.path.join(RAIZ, 'salida'))
    ap.add_argument('--solo-calculo', action='store_true',
                    help='corre solo el paso 1, para mirar los numeros antes de escribir')
    a = ap.parse_args()
    vs = a.vs if a.vs is not None else a.fecha - 1
    os.makedirs(a.outdir, exist_ok=True)

    cfg_path = os.path.join(CFG, 'fechas', f'f{a.fecha}.json')
    if not a.solo_calculo and not os.path.exists(cfg_path):
        sys.exit(f'Falta {cfg_path}. Copiá config/fechas/_plantilla.json y completalo.')

    # ---- 1. calculo ----
    corre('CALCULO Y VALIDACION', [sys.executable, 'calc.py',
          '--fecha', str(a.fecha), '--vs', str(vs),
          '--matches', os.path.abspath(a.matches),
          '--players', os.path.abspath(a.players),
          '--plano', os.path.abspath(a.tabla)])
    if a.solo_calculo:
        print('\nListo el calculo. Revisá los números y después completá '
              f'config/fechas/f{a.fecha}.json')
        return

    cfg = json.load(open(cfg_path, encoding='utf-8'))

    # ---- 2. los 8 bloques ----
    corre('BLOQUES DE METRICA', [sys.executable, 'render.py', '--outdir', a.outdir])

    # ---- 3. piezas editoriales ----
    print('\n=== PORTADA, xG INDIVIDUAL Y PROXIMO RIVAL ===')
    from colon_kit import build_portada, build_top_jugadores, build_proximo_rival
    o = lambda n: os.path.join(a.outdir, n)
    p = cfg['portada']
    build_portada(fecha=a.fecha, pj=p['pj'], pts=p['pts'], posicion_zona=p['posicion'],
                  zona=p['zona'], en_este_hilo=p['items'],
                  outpath=o(f"colon_f{a.fecha}_portada.jpg"), total_fechas=36)
    print('  ok portada')

    # piezas opcionales: solo se generan si estan en la config
    if cfg.get('caratula'):
        from colon_kit import build_caratula
        c = cfg['caratula']
        build_caratula(header_txt=c['header'], linea1=c['linea1'], linea2=c['linea2'],
                       bajada=c['bajada'], dato_num=c['dato'], dato_label=c['dato_label'],
                       outpath=o(f"f{a.fecha}_caratula.jpg"))
        print('  ok caratula')

    if cfg.get('tramos'):
        import placa_tramos
        placa_tramos.build(a.fecha, [tuple(x) for x in cfg['tramos']],
                           o(f"f{a.fecha}_tramos.jpg"))
        print('  ok tramos')

    j = cfg['jugadores']
    build_top_jugadores(fecha=a.fecha, pj=p['pj'], jugador_nombre=j['nombre'],
        jugador_xg=j['xg'], jugador_goles=j['goles'], jugador_pj=j['pj'],
        jugador_min=j['minutos'], puesto_liga=j['puesto'], total_jugadores=j['universo'],
        sub_hero=j.get('sub_hero'), ambito=j.get('ambito', 'DEL TORNEO'),
        top5_rows=[tuple(r) for r in j['top5']],
        colon_row=tuple(j['colon_row']) if j.get('colon_row') else None,
        colon_rank=j.get('colon_rank'),
        outpath=o(f"f{a.fecha}_top_jugadores.jpg"))
    print('  ok xG individual')

    r = cfg['rival']
    build_proximo_rival(fecha_rival=r['fecha'], rival_nombre=r['nombre'],
        rival_ciudad=r['ciudad'],
        rival_local_pj=r['rival_pj'], rival_local_wdl=r['rival_wdl'],
        rival_local_xg=r['rival_xg'], rival_local_xga=r['rival_xga'],
        colon_visit_pj=r['colon_pj'], colon_visit_wdl=r['colon_wdl'],
        colon_visit_xg=r['colon_xg'], colon_visit_xga=r['colon_xga'],
        rival_tag=r['zona'], rival_pts=r['puntos'], diferencia_txt=r['diferencia'],
        goleador_rival=r['goleador_rival'], goleador_colon=r['goleador_colon'],
        outpath=o(f"f{a.fecha}_proximo_rival.jpg"),
        fecha_actual_pj_texto=r.get('cuando', ''),
        colon_es_local=r.get('colon_es_local', False),
        header_txt=r.get('header'), pie_txt=r.get('pie'))
    print('  ok proximo rival')

    # ---- tuits a archivo temporal para el HTML y el PDF ----
    tuits = os.path.join(a.outdir, f'_tuits_f{a.fecha}.json')
    json.dump(cfg['tuits'], open(tuits, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    meta = cfg.get('meta', {})
    sub = meta.get('subtitulo', '')
    notas = meta.get('notas', '')

    # ---- 4. HTML ----
    cmd = [sys.executable, 'html_reporte.py', '--fecha', str(a.fecha), '--tuits', tuits,
           '--imgdir', a.outdir, '--out', o(f'colon_v2_f{a.fecha}.html'), '--subtitulo', sub]
    if notas: cmd += ['--notas', notas]
    if meta.get('titulo'): cmd += ['--titulo', meta['titulo']]
    if meta.get('kicker'): cmd += ['--kicker', meta['kicker']]
    if meta.get('fuentes'): cmd += ['--fuentes', meta['fuentes']]
    corre('HTML', cmd)

    # ---- 5. PDF ----
    corre('PDF', [sys.executable, 'pdf_reporte.py', '--fecha', str(a.fecha),
          '--tuits', tuits, '--imgdir', a.outdir,
          '--out', o(f'colon_f{a.fecha}.pdf'),
          '--titulo', meta.get('titulo') or f'Colón · Fecha {a.fecha}',
          '--subtitulo', sub,
          '--pie', f'Colón · Fecha {a.fecha} · Primera Nacional 2026 · @MarianoDiMaggio'])

    print(f'\n=== LISTO · todo en {a.outdir} ===')
    for f in sorted(os.listdir(a.outdir)):
        if not f.startswith('_'):
            print(f'  {f}')


if __name__ == '__main__':
    main()
