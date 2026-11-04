#!/usr/bin/env python3
"""
Calcula las 8 metricas de la serie desde los CSV de FootyStats + la tabla de zonas.

Uso:
  python3 calc.py --fecha 23 --vs 22 \
      --matches ruta/matches.csv --players ruta/players.csv --tablas ruta/tablas.csv

Salida: datos.json (lo consume render.py)

El archivo --tablas es el CSV con las dos tablas de Promiedos + los resultados de la fecha,
en el formato: linea "ZONA A" / "ZONA B", header, y filas "pos,equipo,pts,j,gol,dif,g,e,p,ultimas".
"""
import pandas as pd, numpy as np, json, re, argparse, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

MAP = {'Ferro Carril Oeste':'Ferro','Deportivo Morón':'Morón','Los Andes':'Los Andes','Colón':'Colón',
 'Ciudad de Bolívar':'Bolívar','Estudiantes Caseros':'Estudiantes','Almirante Brown':'Alte. Brown',
 'Deportivo Madryn':'Dep. Madryn','Godoy Cruz':'Godoy Cruz','San Miguel':'San Miguel',
 'Defensores de Belgrano':'Defensores','Racing Córdoba':'Racing (Cba)','All Boys':'All Boys',
 'San Telmo':'San Telmo','Central Norte':'Central Norte','Acassuso':'Acassuso',
 'Club Atlético Mitre':'CA Mitre','Chaco For Ever':'Chaco For Ever','Gimnasia Jujuy':'Gimnasia (J)',
 'Atlanta':'Atlanta','Tristán Suárez':'Tristán Suárez','Temperley':'Temperley','Deportivo Maipú':'Maipú',
 'Midland':'Midland','Atlético Rafaela':'Atlético Rafaela','San Martín Tucumán':'San Martín (T)',
 'Nueva Chicago':'Chicago','Almagro':'Almagro','Quilmes':'Quilmes','Gimnasia y Tiro':'Gimnasia y Tiro',
 'Colegiales':'Colegiales','San Martín San Juan':'San Martín','Chacarita Juniors':'Chacarita',
 'Patronato':'Patronato','Club Atlético Güemes':'Güemes','Agropecuario':'Agropecuario'}

SHORT = {'Ferro Carril Oeste':'FERRO','Deportivo Morón':'MORÓN','Los Andes':'LOS ANDES','Colón':'COLÓN',
 'Ciudad de Bolívar':'BOLÍVAR','Estudiantes Caseros':'ESTUDIANTES','Almirante Brown':'ALTE. BROWN',
 'Deportivo Madryn':'DEP. MADRYN','Godoy Cruz':'GODOY CRUZ','San Miguel':'SAN MIGUEL',
 'Defensores de Belgrano':'DEFENSORES','Racing Córdoba':'RACING (CBA)','All Boys':'ALL BOYS',
 'San Telmo':'SAN TELMO','Central Norte':'CENTRAL NORTE','Acassuso':'ACASSUSO',
 'Club Atlético Mitre':'CA MITRE','Chaco For Ever':'CHACO FOR EVER','Gimnasia Jujuy':'GIMNASIA (J)',
 'Atlanta':'ATLANTA','Tristán Suárez':'TRISTÁN SUÁREZ','Temperley':'TEMPERLEY','Deportivo Maipú':'MAIPÚ',
 'Midland':'MIDLAND','Atlético Rafaela':'ATL. RAFAELA','San Martín Tucumán':'SAN MARTÍN (T)',
 'Nueva Chicago':'CHICAGO','Almagro':'ALMAGRO','Quilmes':'QUILMES','Gimnasia y Tiro':'GIMNASIA Y TIRO',
 'Colegiales':'COLEGIALES','San Martín San Juan':'SAN MARTÍN (SJ)','Chacarita Juniors':'CHACARITA',
 'Patronato':'PATRONATO','Club Atlético Güemes':'GÜEMES','Agropecuario':'AGROPECUARIO'}


def _norm(s):
    """Compara nombres de equipo sin depender de acentos ni mayusculas."""
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return s.strip().lower()


def leer_tablas(path_combinado=None, zona_a=None, zona_b=None, plano=None):
    """Acepta tres formatos:
    a) plano: un CSV con columna 'tipo' donde las filas tipo=tabla traen zona,posicion,equipo,pts
    b) dos CSV por zona con header 'posicion,equipo,puntos,jugados,...'
    c) un solo CSV con las lineas 'ZONA A' / 'ZONA B' como separadores
    Devuelve {nombre_normalizado: (zona, puesto, puntos)}
    """
    pos = {}
    if plano:
        df = pd.read_csv(plano, encoding='utf-8-sig')
        df.columns = [c.strip().lower() for c in df.columns]
        t = df[df['tipo'].astype(str).str.strip() == 'tabla']
        for _, r in t.iterrows():
            pos[_norm(r['equipo'])] = ('Z' + str(r['zona']).strip().upper(),
                                       int(r['posicion']), int(r['pts']))
        return pos

    if zona_a or zona_b:
        for path, z in [(zona_a, 'ZA'), (zona_b, 'ZB')]:
            if not path:
                continue
            df = pd.read_csv(path, encoding='utf-8-sig')
            df.columns = [c.strip().lower() for c in df.columns]
            for _, r in df.iterrows():
                pos[_norm(r['equipo'])] = (z, int(r['posicion']), int(r['puntos']))
        return pos

    zona = None
    for ln in open(path_combinado, encoding='utf-8-sig').read().splitlines():
        u = ln.strip().upper()
        if u.startswith('ZONA A'): zona = 'ZA'; continue
        if u.startswith('ZONA B'): zona = 'ZB'; continue
        if u.startswith('RESULTADOS'): zona = None; continue
        if zona and re.match(r'^\d+,', ln):
            p = ln.split(',')
            pos[_norm(p[1])] = (zona, int(p[0]), int(p[2]))
    return pos


def resolver(pos, nombre_fs):
    """Encuentra un equipo en la tabla probando variantes del nombre. Las exportaciones
    lo cambian entre fechas ('Bolivar', 'Ciudad de Bolivar', 'Ciudad De Bolivar'), asi que
    la coincidencia exacta se rompe seguido. Prueba el nombre corto, el de FootyStats, y
    por ultimo que uno contenga al otro."""
    for cand in (MAP.get(nombre_fs, nombre_fs), nombre_fs):
        k = _norm(cand)
        if k in pos:
            return pos[k]
    nk = _norm(MAP.get(nombre_fs, nombre_fs)); fk = _norm(nombre_fs)
    for k, v in pos.items():
        if len(k) > 4 and (k in nk or nk in k or k in fk or fk in k):
            return v
    raise KeyError(f'No encuentro "{nombre_fs}" en la tabla de posiciones')


def long_format(matches_csv):
    m = pd.read_csv(matches_csv)
    d = m[m.status == 'complete']
    rows = []
    for _, r in d.iterrows():
        rows.append(dict(team=r.home_team_name, loc='L', gf=r.home_team_goal_count,
            ga=r.away_team_goal_count, xg=r.team_a_xg, xga=r.team_b_xg,
            sh=r.home_team_shots, sot=r.home_team_shots_on_target, gw=r['Game Week']))
        rows.append(dict(team=r.away_team_name, loc='V', gf=r.away_team_goal_count,
            ga=r.home_team_goal_count, xg=r.team_b_xg, xga=r.team_a_xg,
            sh=r.away_team_shots, sot=r.away_team_shots_on_target, gw=r['Game Week']))
    T = pd.DataFrame(rows)
    # Descartar filas cuyo dato de evento se contradice a si mismo: remates al arco
    # negativos (centinela de faltante), o goles convertidos con 2 remates o menos.
    # No toca partidos simplemente pobres (0 goles con 0-2 remates), que son reales.
    malo = (T.sot < 0) | ((T.sh <= 2) & (T.gf >= 1)) | (T.sh < T.gf)
    if malo.sum():
        print(f'[dato] descarto {malo.sum()} filas equipo-partido con evento imposible')
    return T[~malo].copy()


def agg(df):
    g = df.groupby('team').agg(PJ=('gf','size'), GF=('gf','sum'), xGs=('xg','sum'),
        xG=('xg','mean'), xGA=('xga','mean'), SH=('sh','sum'), SOT=('sot','sum')).reset_index()
    g['xGD']    = g.xG - g.xGA
    g['xgvr']   = (g.GF - g.xGs) / g.PJ          # POR PARTIDO, nunca acumulado
    g['rem_pj'] = g.SH / g.PJ
    g['sot_pj'] = g.SOT / g.PJ
    g['rem_gol']= g.SH / g.GF.replace(0, np.nan)
    g['conv']   = 100 * g.GF / g.SH
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, required=True)
    ap.add_argument('--vs', type=int, required=True, help='fecha de comparacion para los deltas')
    ap.add_argument('--matches', required=True)
    ap.add_argument('--players', required=True)
    ap.add_argument('--tablas', help='CSV combinado con las lineas ZONA A / ZONA B')
    ap.add_argument('--zona-a', dest='zona_a', help='CSV de la tabla de Zona A')
    ap.add_argument('--zona-b', dest='zona_b', help='CSV de la tabla de Zona B')
    ap.add_argument('--plano', help='CSV plano con columna tipo (tabla/partido)')
    ap.add_argument('--out', default=os.path.join(BASE, 'datos.json'))
    a = ap.parse_args()

    spec = json.load(open(os.path.join(BASE, '..', 'config', 'bloques.json'), encoding='utf-8'))
    if not (a.tablas or a.plano or (a.zona_a and a.zona_b)):
        sys.exit('Falta la tabla: pasar --plano, o --tablas, o --zona-a y --zona-b.')
    pos = leer_tablas(a.tablas, a.zona_a, a.zona_b, a.plano)
    faltan = []
    for fs in MAP:
        try: resolver(pos, fs)
        except KeyError: faltan.append(fs)
    if faltan:
        sys.exit(f'Estos equipos no aparecen en la tabla: {faltan}')
    t = long_format(a.matches)
    now, prev = agg(t), agg(t[t.gw <= a.vs])

    out = {}
    for b in spec['bloques']:
        k, asc, dec = b['key'], b['menor_es_mejor'], b['decimales']
        for g in (now, prev):
            g[k+'_r'] = g[k].rank(ascending=asc, method='min').astype(int)
        c = now[now.team == 'Colón'].iloc[0]
        p = prev[prev.team == 'Colón'].iloc[0]
        ser = now[k].dropna()
        top5 = []
        for _, r in now.sort_values(k, ascending=asc).head(5).iterrows():
            z, pp, _ = resolver(pos, r.team)
            top5.append([SHORT[r.team], round(float(r[k]), dec), f'#{pp}', z])
        inline = next((i for i, r in enumerate(top5, 1) if r[0] == 'COLÓN'), None)
        cz, cp, _ = resolver(pos, 'Colón')
        out[k] = dict(val=round(float(c[k]), dec), rank=int(c[k+'_r']),
            prev_val=round(float(p[k]), dec), prev_rank=int(p[k+'_r']),
            wmin=round(float(ser.min()), dec), wmax=round(float(ser.max()), dec),
            avg=round(float(ser.mean()), dec), top5=top5, inline=inline,
            colon_row=None if inline else [SHORT['Colón'], round(float(c[k]), dec), f'#{cp}', cz],
            colon_rank=int(c[k+'_r']))

    # splits local / visitante
    col = t[t.team == 'Colón']
    lv = {}
    for b in spec['bloques']:
        k, dec = b['key'], b['decimales']
        v = {}
        for loc, tag in [('L','local'), ('V','visit')]:
            s = col[col['loc'] == loc]
            x = {'xG':      lambda: s.xg.mean(),
                 'xGA':     lambda: s.xga.mean(),
                 'xGD':     lambda: s.xg.mean() - s.xga.mean(),
                 'xgvr':    lambda: (s.gf.sum() - s.xg.sum()) / len(s),
                 'rem_pj':  lambda: s.sh.sum() / len(s),
                 'sot_pj':  lambda: s.sot.sum() / len(s),
                 'rem_gol': lambda: s.sh.sum() / s.gf.sum(),
                 'conv':    lambda: 100 * s.gf.sum() / s.sh.sum()}[k]()
            v[tag] = round(float(x), dec)
        lv[k] = v

    # jugadores: universo elegible = xg_total_overall > 0
    pl = pd.read_csv(a.players).drop_duplicates(subset=['full_name','Current Club']).copy()
    pl['xg'] = pd.to_numeric(pl.xg_total_overall, errors='coerce')
    el = pl[pl.xg > 0].copy()
    el['rk'] = el.xg.rank(ascending=False, method='min').astype(int)
    jug_colon = [dict(nombre=r.full_name, xg=round(float(r.xg),2), goles=int(r.goals_overall),
                      pj=int(r.appearances_overall), min=int(r.minutes_played_overall), rk=int(r.rk))
                 for _, r in el[el['Current Club']=='Colón'].sort_values('xg', ascending=False).head(5).iterrows()]
    jug_liga = [dict(nombre=r.full_name, club=r['Current Club'], xg=round(float(r.xg),2),
                     goles=int(r.goals_overall))
                for _, r in el.sort_values('xg', ascending=False).head(5).iterrows()]

    meta = dict(fecha=a.fecha, vs=a.vs, pj=int(len(col)), GF=int(col.gf.sum()), GC=int(col.ga.sum()),
                pts=resolver(pos,'Colón')[2], puesto=resolver(pos,'Colón')[1], zona=resolver(pos,'Colón')[0],
                elegibles=int(len(el)))
    json.dump(dict(mets=out, lv=lv, meta=meta, jug_colon=jug_colon, jug_liga=jug_liga),
              open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ---- control de validacion contra los valores publicados ----
    print(f"Colón F{a.fecha}: {meta['pj']} PJ · {meta['pts']} pts · {meta['puesto']}° {meta['zona']} · "
          f"{meta['GF']} GF / {meta['GC']} GC · {meta['elegibles']} jugadores elegibles")
    print("Cruzar GF/GC contra la tabla de Promiedos antes de seguir.\n")
    for b in spec['bloques']:
        k = b['key']; o = out[k]
        print(f"{k:8s} {o['val']:8.2f} #{o['rank']:2d} | F{a.vs} {o['prev_val']:8.2f} #{o['prev_rank']:2d} | "
              f"prom {o['avg']:7.2f} | L {lv[k]['local']:7.2f} V {lv[k]['visit']:7.2f}")
    v20 = spec.get('validacion_f20', {})
    if a.vs == 20:
        print("\nValidacion contra F20 publicado:")
        for b in spec['bloques']:
            k = b['key']
            if k in v20:
                esp_v, esp_r = v20[k]
                got_v, got_r = out[k]['prev_val'], out[k]['prev_rank']
                ok = abs(got_v - esp_v) < 0.06 and got_r == esp_r
                print(f"  {'OK ' if ok else 'REVISAR'} {k:8s} esperado {esp_v} #{esp_r} / obtenido {got_v} #{got_r}")
    print(f"\n-> {a.out}")


if __name__ == '__main__':
    main()
