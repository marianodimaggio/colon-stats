#!/usr/bin/env python3
"""
Pieza tematica: CONSISTENCIA Y REDUCIDO.
Mide la varianza del proceso contra la varianza del resultado, y traduce el nivel del
equipo a probabilidad de matamata con un Poisson simple.

    python3 varianza_reducido.py --fecha 28 --outdir /mnt/user-data/outputs

Es un hilo aparte: no toca el reporte de fecha. Fuente: FootyStats.

Aviso importante: la probabilidad por llave se calcula contra un rival PROMEDIO de la
categoria. Cuando se sepa el cruce real hay que recalcularla con el xG/xGA del rival.
"""
import pandas as pd, numpy as np, csv, os, sys, argparse, unicodedata
from math import exp, factorial
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from colon_kit import (build_metric, build_portada_identidad, _base_canvas, _corner,
                       F, MONO_M, MONO_R, BEBAS, LABEL, MICRO, SPLIT_X, W, H)

BASE = os.path.dirname(os.path.abspath(__file__))
probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))
FUENTE = 'Fuente: FootyStats · modelo propio'

SHORT = {'Colón':'COLÓN','Ferro Carril Oeste':'FERRO','Deportivo Morón':'MORÓN','Gimnasia Jujuy':'GIMNASIA (J)',
 'Temperley':'TEMPERLEY','Tristán Suárez':'TRISTÁN SUÁREZ','Atlanta':'ATLANTA','Almirante Brown':'ALTE. BROWN',
 'Midland':'MIDLAND','Godoy Cruz':'GODOY CRUZ','Ciudad de Bolívar':'BOLÍVAR','Los Andes':'LOS ANDES',
 'Deportivo Madryn':'DEP. MADRYN','Deportivo Maipú':'MAIPÚ','Estudiantes Caseros':'ESTUDIANTES',
 'Gimnasia y Tiro':'GIMNASIA Y TIRO','Atlético Rafaela':'ATL. RAFAELA','San Martín Tucumán':'SAN MARTÍN (T)',
 'Colegiales':'COLEGIALES','Nueva Chicago':'CHICAGO','Almagro':'ALMAGRO','San Martín San Juan':'SAN MARTÍN (SJ)',
 'Racing Córdoba':'RACING (CBA)','Chacarita Juniors':'CHACARITA','San Miguel':'SAN MIGUEL','Quilmes':'QUILMES',
 'Defensores de Belgrano':'DEFENSORES','Club Atlético Mitre':'CA MITRE','San Telmo':'SAN TELMO',
 'Patronato':'PATRONATO','All Boys':'ALL BOYS','Agropecuario':'AGROPECUARIO','Chaco For Ever':'CHACO FOR EVER',
 'Central Norte':'CENTRAL NORTE','Acassuso':'ACASSUSO','Club Atlético Güemes':'GÜEMES'}


def _norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return s.strip().lower()


def pois(l, k):
    return exp(-l) * l ** k / factorial(k)


def probs(xg, xga):
    pw = pd_ = pl = 0.0
    for a in range(10):
        for b in range(10):
            p = pois(xg, a) * pois(xga, b)
            if a > b: pw += p
            elif a == b: pd_ += p
            else: pl += p
    return pw, pd_, pl


def autofit(labels, subs, val_txt):
    for vsz in (200, 190, 175, 160, 148):
        for lsz in (58, 52, 46, 42):
            w  = [probe.textbbox((0,0), l, font=F(MONO_M, lsz))[2] for l in labels]
            w += [probe.textbbox((0,0), s, font=F(MONO_M, LABEL))[2] for s in subs]
            if 46 + max(w) + 70 + probe.textbbox((0,0), val_txt, font=F(BEBAS, vsz))[2] <= SPLIT_X - 42:
                return lsz, vsz
    return 42, 148


def placa_llaves(fecha, filas, tot_con, tot_sin, outpath):
    """Placa a medida: el camino real del Reducido son 7 partidos en 4 rondas, y solo
    el primero es a partido unico. La 'ventaja' (al mejor ubicado le alcanza el empate)
    casi duplica las chances, asi que se muestran las dos columnas."""
    img, draw, crest = _base_canvas(fecha)
    LIM = SPLIT_X - 30
    draw.text((46, 196), 'EL CAMINO DEL', font=F(MONO_M, 42), fill='#FFC533',
              stroke_width=2, stroke_fill='#FFC533')
    draw.text((46, 246), 'REDUCIDO', font=F(MONO_M, 42), fill='#FFC533',
              stroke_width=2, stroke_fill='#FFC533')
    draw.text((46, 304), 'SIETE PARTIDOS EN CUATRO RONDAS', font=F(MONO_M, LABEL), fill='#A9B4BE')

    CA, CB = 520, LIM
    for txt, xr in [('CON VENT.', CA), ('SIN VENT.', CB)]:
        w = draw.textbbox((0, 0), txt, font=F(MONO_M, LABEL))[2]
        draw.text((xr - w, 352), txt, font=F(MONO_M, LABEL), fill='#FFC533')
    draw.line([(46, 388), (LIM, 388)], fill='#242424', width=2)

    y = 404
    for rot, pc, ps in filas:
        fl = F(MONO_M, 28)
        bb = draw.textbbox((0, 0), rot, font=fl)
        draw.text((46, y + (52 - (bb[3] - bb[1])) // 2 - 4), rot, font=fl, fill='#FFFFFF')
        for val, xr, col, fs in [(pc, CA, '#FFC533', 46), (ps, CB, '#8C99A8', 40)]:
            t = f'{val*100:.1f}%'
            fn = F(BEBAS, fs)
            w = draw.textbbox((0, 0), t, font=fn)[2]
            draw.text((xr - w, y - 2), t, font=fn, fill=col)
        y += 66

    draw.line([(46, y + 4), (LIM, y + 4)], fill='#FFC533', width=2)
    y += 24
    draw.text((46, y + 18), 'LLEGAR AL ASCENSO', font=F(MONO_M, 30), fill='#FFC533')
    for val, xr, col, fs in [(tot_con, CA, '#FFFFFF', 74), (tot_sin, CB, '#8C99A8', 60)]:
        t = f'{val*100:.1f}%'
        fn = F(BEBAS, fs)
        w = draw.textbbox((0, 0), t, font=fn)[2]
        draw.text((xr - w, y), t, font=fn, fill=col)

    draw.text((46, H - 76), FUENTE, font=F(MONO_R, MICRO), fill='#7a7a7a')

    px = SPLIT_X + 40
    cx = SPLIT_X + (W - SPLIT_X) // 2
    draw.text((px, 220), 'LA VENTAJA', font=F(MONO_M, LABEL), fill='#FFC533')
    draw.text((px, 252), 'DEPORTIVA VALE', font=F(MONO_M, LABEL), fill='#FFC533')
    fn = F(BEBAS, 170)
    t = f'{tot_con/tot_sin:.1f}X'.replace('.0X', 'X')
    bb = draw.textbbox((0, 0), t, font=fn)
    draw.text((cx - bb[2] // 2 - bb[0], 300), t, font=fn, fill='#FFC533')
    yy = 300 + bb[3] + 20
    draw.line([(px, yy), (W - 40, yy)], fill='#FFC533', width=2)
    yy += 34
    for ln in ['AL MEJOR UBICADO', 'LE ALCANZA EL', 'EMPATE EN CADA', 'LLAVE QUE JUEGA']:
        draw.text((px, yy), ln, font=F(MONO_M, 23), fill='#FFC533')
        yy += 32
    draw.text((px, H - 58), f'F{fecha} · MODELO POISSON', font=F(MONO_R, 20), fill='#FFC533')
    img.save(outpath, 'JPEG', quality=92)
    return outpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, default=28)
    ap.add_argument('--outdir', default=os.getcwd())
    ap.add_argument('--matches', required=True)
    ap.add_argument('--plano', required=True)
    a = ap.parse_args()

    # ---- posiciones para los tags del top5 ----
    pos = {}
    for x in csv.DictReader(open(a.plano, encoding='utf-8-sig')):
        if x['tipo'] == 'tabla':
            pos[_norm(x['equipo'])] = ('Z' + x['zona'].strip(), int(x['posicion']))

    def zona_de(nombre_fs):
        for cand in (nombre_fs, SHORT.get(nombre_fs, nombre_fs)):
            k = _norm(cand)
            if k in pos: return pos[k]
        fk = _norm(nombre_fs)
        for k, v in pos.items():
            if len(k) > 4 and (k in fk or fk in k): return v
        raise KeyError(nombre_fs)

    # ---- datos ----
    m = pd.read_csv(a.matches); d = m[m.status == 'complete']
    rows = []
    for _, r in d.iterrows():
        rows.append(dict(team=r.home_team_name, gf=r.home_team_goal_count, ga=r.away_team_goal_count,
                         xg=r.team_a_xg, xga=r.team_b_xg, sh=r.home_team_shots))
        rows.append(dict(team=r.away_team_name, gf=r.away_team_goal_count, ga=r.home_team_goal_count,
                         xg=r.team_b_xg, xga=r.team_a_xg, sh=r.away_team_shots))
    t = pd.DataFrame(rows)
    t = t[t.sh > 0]          # los partidos sin datos de evento fingirian dispersion
    t['pts'] = np.where(t.gf > t.ga, 3, np.where(t.gf == t.ga, 1, 0))
    g = t.groupby('team').agg(PJ=('pts','size'), xg=('xg','mean'), xga=('xga','mean'),
        xg_sd=('xg','std'), pts_m=('pts','mean'), pts_sd=('pts','std')).reset_index()
    g['xg_cv'] = g.xg_sd / g.xg
    g[['pw','pd','pl']] = g.apply(lambda r: pd.Series(probs(r.xg, r.xga)), axis=1)
    g['pe'] = g.pw * 3 + g.pd
    g['sobre'] = g.pts_m - g.pe
    g['llave'] = g.pw + g.pd * 0.5
    i = g.index[g.team == 'Colón'][0]
    c = g.loc[i]

    BLOQUES = [
      dict(key='xg_cv', labels=['CUÁN','PAREJO'], subs=['ES SU GENERACIÓN','FECHA A FECHA'],
           asc=True, dec=2, pct=False, unidad='CV',
           t5='TOP 5 MÁS PAREJOS GENERANDO',
           delta=f"DESVÍO {c.xg_sd:.2f} SOBRE UN xG DE {c.xg:.2f}"),
      dict(key='pts_sd', labels=['CUÁNTO','OSCILA'], subs=['EL RESULTADO','FECHA A FECHA'],
           asc=False, dec=2, pct=False, unidad='PTS',
           t5='TOP 5 RESULTADOS MÁS ERRÁTICOS',
           delta=f"DESVÍO DE PUNTOS SOBRE {c.pts_m:.2f} POR PARTIDO"),
      dict(key='pe', labels=['PUNTOS','ESPERADOS'], subs=['POR PARTIDO','SEGÚN SU NIVEL'],
           asc=False, dec=2, pct=False, unidad='PTS',
           t5='TOP 5 PUNTOS ESPERADOS',
           delta=f"GANA {c.pw*100:.0f}% · EMPATA {c.pd*100:.0f}% · PIERDE {c.pl*100:.0f}%"),
      dict(key='sobre', labels=['LO QUE SACA','DE MÁS'], subs=['SOBRE LOS PUNTOS','QUE MERECE'],
           asc=False, dec=2, pct=False, unidad='PTS',
           t5='TOP 5 SACA MÁS DE LO QUE MERECE',
           delta=f"SACA {c.pts_m:.2f} Y MERECE {c.pe:.2f} POR PARTIDO"),
      dict(key='llave', labels=['PASAR','UNA LLAVE'], subs=['A PARTIDO ÚNICO','SEGÚN SU NIVEL'],
           asc=False, dec=1, pct=True, unidad='',
           t5='TOP 5 PASAR A PARTIDO ÚNICO',
           delta='EL EMPATE CUENTA COMO CARA O CECA'),
    ]

    hechos = []
    for b in BLOQUES:
        k, asc, dec, pct = b['key'], b['asc'], b['dec'], b['pct']
        s = g[k] * (100 if pct else 1)
        rk = s.rank(ascending=asc, method='min').astype(int)
        fmt = lambda v: f'{v:.{dec}f}' + ('%' if pct else '')
        val = round(float(s[i]), dec)
        worst = round(float(s.max() if asc else s.min()), dec)
        best = round(float(s.min() if asc else s.max()), dec)
        avg = round(float(s.mean()), dec)
        top = g.assign(v=s, r=rk).sort_values('v', ascending=asc).head(5)
        top5, inline = [], None
        for n, (_, x) in enumerate(top.iterrows(), 1):
            z, p = zona_de(x.team)
            top5.append((SHORT[x.team], fmt(x.v), f'#{p}', z))
            if x.team == 'Colón': inline = n
        crow = None
        if inline is None:
            z, p = zona_de('Colón')
            crow = ('COLÓN', fmt(val), f'#{p}', z)
        val_txt = fmt(val)
        lsz, vsz = autofit(b['labels'], b['subs'], val_txt)
        path = os.path.join(a.outdir, f"var_f{a.fecha}_{k}.jpg")
        build_metric(fecha=a.fecha, pj=a.fecha, label_lines=b['labels'], label_font_size=lsz,
            sub_lines=b['subs'], val_txt=val_txt, val_font_size=vsz,
            delta_txt=b['delta'], arrow_dir='stable',
            worst=worst, avg=avg, best=best, val=val, signed=False,
            local_val=None, visit_val=None, is_pct=pct,
            top5_rows=top5, colon_inline_idx=inline, colon_row=crow, colon_rank=int(rk[i]),
            outpath=path, puesto_txt=f'#{int(rk[i])}',
            avg_line_txt=(fmt(avg) if pct else f"{fmt(avg)} {b['unidad']}").strip(),
            top5_title=b['t5'], fuente_txt=FUENTE, bar_dec=dec)
        hechos.append(path)
        print(f"ok {k:8s} {val_txt:>8s}  #{int(rk[i]):2d} de 36")

    # Formato real (Boletin AFA 6823): 7 partidos en 4 rondas, solo la primera a
    # partido unico; las otras tres son series de ida y vuelta (180 min -> xG x2).
    w1, d1, l1 = probs(c.xg, c.xga)
    W, D, L = probs(c.xg * 2, c.xga * 2)
    pu_con, pu_sin = w1 + d1, w1 + d1 * 0.5
    se_con, se_sin = W + D, W + D * 0.5
    filas = [('1 · PARTIDO ÚNICO', pu_con, pu_sin), ('2 · CUARTOS', se_con, se_sin),
             ('3 · SEMIFINAL', se_con, se_sin), ('4 · FINAL', se_con, se_sin)]
    tot_con, tot_sin = pu_con * se_con ** 3, pu_sin * se_sin ** 3
    placa_llaves(a.fecha, filas, tot_con, tot_sin,
                 os.path.join(a.outdir, f'var_f{a.fecha}_llaves.jpg'))
    print(f'   camino completo: con ventaja {tot_con:.1%} · sin ventaja {tot_sin:.1%}')
    print('ok llaves')

    build_portada_identidad(
        header_txt=f'PRIMERA NACIONAL 2026 · {a.fecha} FECHAS',
        kicker='CONSISTENCIA Y REDUCIDO',
        subtitulo='POR QUÉ SER PAREJO NO ALCANZA',
        hero_num=f'{tot_sin*100:.0f}-{tot_con*100:.0f}%',
        hero_label=['DE LLEGAR AL', 'ASCENSO SEGÚN', 'DÓNDE ENTRE'],
        en_este_hilo=[
            'EL EQUIPO MÁS PAREJO DE LOS 36',
            'PERO RESULTADOS DEL MONTÓN',
            'EL PROBLEMA NO ES LA VARIANZA',
            'ES EL NIVEL: UNA VENTAJA CHICA',
            'QUE SE MULTIPLICA MAL',
            'Y LA VENTAJA DEPORTIVA, QUE VALE',
        ],
        mejor_puesto='1°', mejor_label=['DE 36 EN', 'SER PAREJO'],
        peor_puesto='18°', peor_label=['DE 36 EN', 'OSCILAR'],
        rotulo_mejor='GENERANDO', rotulo_peor='EN RESULTADOS',
        outpath=os.path.join(a.outdir, f'var_f{a.fecha}_portada.jpg'),
        fuente_txt=FUENTE)
    print('ok portada')

    for p in hechos:
        arr = np.array(Image.open(p).convert('RGB'))[198:422]
        mk = (arr[:,:,0] > 150) & (arr[:,:,1] > 150) & (arr[:,:,2] > 150)
        xs = np.where(mk.any(axis=0))[0]; xs = xs[xs < 739]
        if len(xs) and xs.max() > 716:
            print(f"  [AVISO] {os.path.basename(p)}: texto hasta x={xs.max()}")


if __name__ == '__main__':
    main()
