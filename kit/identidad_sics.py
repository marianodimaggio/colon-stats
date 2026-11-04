#!/usr/bin/env python3
"""
Hilo de IDENTIDAD DE JUEGO con datos de SICS.tv.
Calcula, rankea y renderiza los 8 bloques + la portada.

    python3 identidad_sics.py --fecha 23 --outdir /mnt/user-data/outputs

Necesita en /mnt/user-data/uploads: defensive.csv, offensive.csv, goalkeeper.csv,
duels.csv, passes.csv, SICS_tv-teams__2_.csv (por el Tiempo de juego), el CSV de
partidos de FootyStats (por los goles concedidos) y las tablas de zona.
"""
import pandas as pd, numpy as np, json, csv, os, sys, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from colon_kit import build_metric, build_portada, build_portada_identidad, F, MONO_M, MONO_R, BEBAS, LABEL, SPLIT_X

BASE = os.path.dirname(os.path.abspath(__file__))
UP = '/mnt/user-data/uploads'
probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))

# SICS -> nombre FootyStats -> nombre corto de placa
EQ = [
 ('CA COLON','Colón','COLÓN'),('CLUB FERRO CARRIL OESTE','Ferro Carril Oeste','FERRO'),
 ('CLUB DEPORTIVO MORON','Deportivo Morón','MORÓN'),('CLUB ATLETICO GIMNASIA Y ESGRIMA JUJUY','Gimnasia Jujuy','GIMNASIA (J)'),
 ('CLUB ATLETICO TEMPERLEY','Temperley','TEMPERLEY'),('CSD TRISTAN SUAREZ','Tristán Suárez','TRISTÁN SUÁREZ'),
 ('CLUB ATLETICO ATLANTA','Atlanta','ATLANTA'),('CLUB ALMIRANTE BROWN','Almirante Brown','ALTE. BROWN'),
 ('MIDLAND','Midland','MIDLAND'),('CD GODOY CRUZ ANTONIO TOMBA','Godoy Cruz','GODOY CRUZ'),
 ('CLUB CIUDAD DE BOLIVAR','Ciudad de Bolívar','BOLÍVAR'),('CLUB ATLETICO LOS ANDES','Los Andes','LOS ANDES'),
 ('CLUB SOCIAL Y DEPORTIVO MADRYN','Deportivo Madryn','DEP. MADRYN'),("CLUB DEPORTIVO MAIPU'",'Deportivo Maipú','MAIPÚ'),
 ('CA ESTUDIANTES BUENOS AIRES','Estudiantes Caseros','ESTUDIANTES'),('CLUB DE GIMNASIA Y TIRO','Gimnasia y Tiro','GIMNASIA Y TIRO'),
 ('ATLETICO DE RAFAELA','Atlético Rafaela','ATL. RAFAELA'),('CLUB ATLETICO SAN MARTIN TUCUMAN','San Martín Tucumán','SAN MARTÍN (T)'),
 ('CLUB ATLETICO COLEGIALES','Colegiales','COLEGIALES'),('NUEVA CHICAGO','Nueva Chicago','CHICAGO'),
 ('CLUB ALMAGRO','Almagro','ALMAGRO'),('CA SAN MARTIN','San Martín San Juan','SAN MARTÍN (SJ)'),
 ('CLUB ATLETICO RACING','Racing Córdoba','RACING (CBA)'),('CA CHACARITA JUNIORS','Chacarita Juniors','CHACARITA'),
 ('CLUB ATLETICO SAN MIGUEL','San Miguel','SAN MIGUEL'),('QUILMES ATLETICO CLUB','Quilmes','QUILMES'),
 ('DEFENSORES DE BELGRANO','Defensores de Belgrano','DEFENSORES'),('CLUB ATLETICO MITRE','Club Atlético Mitre','CA MITRE'),
 ('CLUB ATLETICO SAN TELMO','San Telmo','SAN TELMO'),('CLUB ATLETICO PATRONATO','Patronato','PATRONATO'),
 ('CLUB ATLETICO ALL BOYS','All Boys','ALL BOYS'),('ARGENTINO AGROPECUARIO','Agropecuario','AGROPECUARIO'),
 ('CHACO FOR EVER','Chaco For Ever','CHACO FOR EVER'),('CLUB ATLETICO CENTRAL NORTE','Central Norte','CENTRAL NORTE'),
 ('CLUB ATLETICO ACASSUSO','Acassuso','ACASSUSO'),('CLUB ATLETICO GUEMES','Club Atlético Güemes','GÜEMES'),
]
SICS2FS = {a: b for a, b, _ in EQ}
SICS2SHORT = {a: c for a, _, c in EQ}
# nombre corto de placa -> nombre en las tablas de zona de Promiedos
SHORT2TABLA = {'COLÓN':'Colón','FERRO':'Ferro','MORÓN':'Morón','GIMNASIA (J)':'Gimnasia (J)','TEMPERLEY':'Temperley',
 'TRISTÁN SUÁREZ':'Tristán Suárez','ATLANTA':'Atlanta','ALTE. BROWN':'Alte. Brown','MIDLAND':'Midland',
 'GODOY CRUZ':'Godoy Cruz','BOLÍVAR':'Bolívar','LOS ANDES':'Los Andes','DEP. MADRYN':'Dep. Madryn','MAIPÚ':'Maipú',
 'ESTUDIANTES':'Estudiantes','GIMNASIA Y TIRO':'Gimnasia y Tiro','ATL. RAFAELA':'Atlético Rafaela',
 'SAN MARTÍN (T)':'San Martín (T)','COLEGIALES':'Colegiales','CHICAGO':'Chicago','ALMAGRO':'Almagro',
 'SAN MARTÍN (SJ)':'San Martín','RACING (CBA)':'Racing (Cba)','CHACARITA':'Chacarita','SAN MIGUEL':'San Miguel',
 'QUILMES':'Quilmes','DEFENSORES':'Defensores','CA MITRE':'CA Mitre','SAN TELMO':'San Telmo','PATRONATO':'Patronato',
 'ALL BOYS':'All Boys','AGROPECUARIO':'Agropecuario','CHACO FOR EVER':'Chaco For Ever','CENTRAL NORTE':'Central Norte',
 'ACASSUSO':'Acassuso','GÜEMES':'Güemes'}


def load(f):
    d = pd.read_csv(f'{UP}/{f}.csv')
    d.columns = [c.strip() for c in d.columns]
    d = d.rename(columns={'Equipos': 'team'})
    for c in d.columns:
        if c != 'team':
            d[c] = pd.to_numeric(d[c].astype(str).str.strip().replace({'': np.nan, '-': np.nan}),
                                 errors='coerce').fillna(0)
    return d


def autofit(labels, subs, val_txt):
    """Sin columna LOC/VIS sobra ancho, pero el label igual puede empujar al numero."""
    for vsz in (200, 190, 175, 160, 148):
        for lsz in (58, 52, 46, 42):
            w  = [probe.textbbox((0,0), l, font=F(MONO_M, lsz))[2] for l in labels]
            w += [probe.textbbox((0,0), s, font=F(MONO_M, LABEL))[2] for s in subs]
            col2_x = 46 + max(w) + 40 + 30
            if col2_x + probe.textbbox((0,0), val_txt, font=F(BEBAS, vsz))[2] <= SPLIT_X - 42:
                return lsz, vsz
    return 42, 148


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, default=23)
    ap.add_argument('--outdir', default=os.getcwd())
    ap.add_argument('--matches', default=f'{UP}/argentina-prim-b-nacional-matches-2026-to-2026-stats__9_.csv')
    a = ap.parse_args()
    spec = json.load(open(os.path.join(BASE, '..', 'config', 'bloques_identidad.json'), encoding='utf-8'))

    # --- datos ---
    M = load('SICS_tv-teams__2_')[['team', 'Tiempo de juego']]
    for f in ['defensive', 'offensive', 'goalkeeper', 'duels', 'passes']:
        M = M.merge(load(f), on='team', suffixes=('', '_' + f[:2]))
    M['p90'] = M['Tiempo de juego'] / 90
    M['fs'] = M.team.map(SICS2FS)
    M['corto'] = M.team.map(SICS2SHORT)

    # goles concedidos de FootyStats (SICS no los trae en estos exports)
    mm = pd.read_csv(a.matches); mm = mm[mm.status == 'complete']
    rows = []
    for _, r in mm.iterrows():
        rows.append((r.home_team_name, r.away_team_goal_count))
        rows.append((r.away_team_name, r.home_team_goal_count))
    GC = pd.DataFrame(rows, columns=['fs', 'gc']).groupby('fs').gc.sum().reset_index()
    M = M.merge(GC, on='fs')

    # tablas de zona para los tags del top5
    pos = {}
    for f, z in [('zona_a', 'ZA'), ('zona_b', 'ZB')]:
        for r in csv.DictReader(open(f'/home/claude/f23/{f}.csv', encoding='utf-8-sig')):
            pos[r['equipo'].strip()] = (z, int(r['posicion']))

    # --- series por bloque ---
    def serie(b):
        if b['key'] == 'claves_x_area':
            return 100 * M['Pases claves'] / M['Pases en el área']
        if b['key'] == 'pct_atajadas':
            return 100 * M['Salvadas'] / (M['Salvadas'] + M['gc'])
        return M[b['col']] / M.p90

    i = M.index[M.team == 'CA COLON'][0]
    hechos = []
    for b in spec['bloques']:
        s = serie(b)
        asc = b['menor_es_mejor']
        rk = s.rank(ascending=asc, method='min').astype(int)
        dec = b['decimales']
        pct = b.get('is_pct', False)
        fmt = lambda v: f'{v:.{dec}f}' + ('%' if pct else '')

        val = round(float(s[i]), dec)
        worst = round(float(s.max() if asc else s.min()), dec)
        best  = round(float(s.min() if asc else s.max()), dec)
        avg   = round(float(s.mean()), dec)

        top = M.assign(v=s, r=rk).sort_values('v', ascending=asc).head(5)
        top5, inline = [], None
        for n, (_, x) in enumerate(top.iterrows(), 1):
            z, p = pos[SHORT2TABLA[x.corto]]
            top5.append((x.corto, fmt(x.v), f'#{p}', z))
            if x.corto == 'COLÓN':
                inline = n
        crow = None
        if inline is None:
            z, p = pos['Colón']
            crow = ('COLÓN', fmt(val), f'#{p}', z)

        # sin delta por fecha: la fila se usa para el total crudo de la temporada
        if b['key'] == 'claves_x_area':
            delta = f"{int(M['Pases claves'][i])} CLAVES SOBRE {int(M['Pases en el área'][i])} AL ÁREA"
        elif b['key'] == 'pct_atajadas':
            delta = f"{int(M['Salvadas'][i])} ATAJADAS · {int(M['gc'][i])} GOLES RECIBIDOS"
        else:
            delta = f"{int(M[b['col']][i])} EN TOTAL · {a.fecha} FECHAS"

        val_txt = fmt(val)
        lsz, vsz = autofit(b['label_lines'], b['sub_lines'], val_txt)
        path = os.path.join(a.outdir, f"ident_f{a.fecha}_{b['key']}.jpg")
        build_metric(fecha=a.fecha, pj=a.fecha, label_lines=b['label_lines'], label_font_size=lsz,
            sub_lines=b['sub_lines'], val_txt=val_txt, val_font_size=vsz,
            delta_txt=delta, arrow_dir='stable',
            worst=worst, avg=avg, best=best, val=val, signed=False,
            local_val=None, visit_val=None, is_pct=pct,
            top5_rows=top5, colon_inline_idx=inline, colon_row=crow, colon_rank=int(rk[i]),
            outpath=path, puesto_txt=f'#{int(rk[i])}',
            avg_line_txt=(fmt(avg) if pct else f"{fmt(avg)} {b['unidad_panel']}").strip(),
            top5_title=b['top5_title'], fuente_txt=spec['fuente_txt'], bar_dec=dec)
        hechos.append(path)
        print(f"ok {b['key']:20s} {val_txt:>8s}  #{int(rk[i]):2d} de 36   (label {lsz} / val {vsz})")

    # --- portada propia del hilo (no la de reporte de fecha) ---
    build_portada_identidad(
        header_txt='PRIMERA NACIONAL 2026 · 23 FECHAS',
        kicker='IDENTIDAD DE JUEGO',
        subtitulo='LO QUE LA TABLA NO MUESTRA',
        hero_num='8',
        hero_label=['DATOS PARA', 'ENTENDER CÓMO', 'JUEGA COLÓN'],
        en_este_hilo=[
            'EL MENOS GAMBETEADO DEL TORNEO',
            'CASI NO COMETE FALTAS',
            'TAMPOCO GAMBETEA A NADIE',
            'LLENA EL ÁREA DE PASES SIN PELIGRO',
            'Y EL ARQUERO TAPA POCO',
        ],
        mejor_puesto='1°', mejor_label=['DE 36 EN', 'GAMBETAS EN CONTRA'],
        peor_puesto='35°', peor_label=['DE 36 EN', 'GAMBETAS LOGRADAS'],
        outpath=os.path.join(a.outdir, f'ident_f{a.fecha}_portada.jpg'),
        fuente_txt=spec['fuente_txt'])

    # control de desborde
    import numpy as _np
    for p in hechos:
        arr = _np.array(Image.open(p).convert('RGB'))[198:422]
        m = (arr[:,:,0] > 150) & (arr[:,:,1] > 150) & (arr[:,:,2] > 150)
        xs = _np.where(m.any(axis=0))[0]; xs = xs[xs < 739]
        if len(xs) and xs.max() > 716:
            print(f"  [AVISO] {os.path.basename(p)}: texto hasta x={xs.max()}")
    print(f"\n{len(hechos)} bloques + portada en {a.outdir}")


if __name__ == '__main__':
    main()
