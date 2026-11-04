#!/usr/bin/env python3
"""
Arma el HTML final: cada placa con su tuit copiable, boton de copiar y de descarga.

Uso:
  python3 html_reporte.py --fecha 23 --tuits tuits.json --imgdir . --out colon_v2_f23.html

tuits.json es una lista en ORDEN de hilo:
  [{"img":"colon_f23_portada","titulo":"PORTADA · APERTURA DEL HILO","tuit":"..."}, ...]

El "Sigue abajo 👇" se agrega automaticamente a todos menos al ultimo,
como ultima linea antes del bloque de hashtags.
"""
import base64, html, json, os, argparse


def con_sigue(tw):
    lineas = tw.split('\n')
    idx = next((i for i, l in enumerate(lineas) if l.strip().startswith('#')), len(lineas))
    return '\n'.join(lineas[:idx] + ['Sigue abajo 👇', ''] + lineas[idx:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fecha', type=int, required=True)
    ap.add_argument('--tuits', required=True)
    ap.add_argument('--imgdir', default='.')
    ap.add_argument('--out', default=None)
    ap.add_argument('--subtitulo', default='')
    ap.add_argument('--titulo', default=None, help='H1 del header; por defecto "Colón · Fecha N"')
    ap.add_argument('--kicker', default='PRIMERA NACIONAL 2026 · ZONA A')
    ap.add_argument('--fuentes', default='FootyStats (matches + players) · Promiedos.com.ar (tablas por zona).')
    ap.add_argument('--notas', default='xG vs Real se calcula por partido. La fecha 4 se jugó el 20/06 y FootyStats '
                                       'la trae sin datos de evento — se incluye igual para no romper la serie. '
                                       'Los goles de Lago se toman de prensa.')
    a = ap.parse_args()
    out = a.out or f'colon_v2_f{a.fecha}.html'

    secc = json.load(open(a.tuits, encoding='utf-8'))
    n = len(secc)
    cards = []
    for i, s in enumerate(secc):
        tw = s['tuit'] if i == n - 1 else con_sigue(s['tuit'])
        with open(os.path.join(a.imgdir, s['img'] + '.jpg'), 'rb') as f:
            im = base64.b64encode(f.read()).decode()
        cards.append(f'''
  <section class="card">
    <div class="card-h"><span class="idx">{i:02d}</span><h2>{html.escape(s['titulo'])}</h2></div>
    <img src="data:image/jpeg;base64,{im}" alt="{html.escape(s['titulo'])}">
    <div class="acts">
      <button class="btn im" data-name="{s['img']}.jpg">Copiar imagen</button>
      <button class="btn cp" data-t="{html.escape(tw)}">Copiar tuit</button>
    </div>
    <pre class="tw">{html.escape(tw)}</pre>
  </section>''')

    doc = f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Colón · Fecha {a.fecha} · Primera Nacional 2026</title>
<style>
 *{{box-sizing:border-box}}
 body{{margin:0;background:#080808;color:#fff;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;-webkit-text-size-adjust:100%}}
 header{{padding:28px 18px 22px;border-bottom:2px solid #2a0810;
   background:linear-gradient(90deg,#080808 0%,#080808 62%,#C8102E 62%,#C8102E 100%)}}
 header .k{{color:#FFC533;font-size:13px;letter-spacing:.12em}}
 header h1{{margin:6px 0 4px;font-size:26px}}
 header .s{{color:#A9B4BE;font-size:13px}}
 main{{max-width:760px;margin:0 auto;padding:18px 14px 60px}}
 .card{{background:#0d0d0d;border:1px solid #1f1f1f;border-radius:14px;padding:14px;margin:0 0 22px}}
 .card-h{{display:flex;align-items:center;gap:10px;margin-bottom:12px}}
 .idx{{background:#C8102E;color:#FFC533;font-size:12px;padding:4px 8px;border-radius:6px;letter-spacing:.08em}}
 .card h2{{margin:0;font-size:14px;color:#FFC533;letter-spacing:.06em;font-weight:600}}
 .card img{{width:100%;display:block;border-radius:10px}}
 .acts{{display:flex;gap:10px;margin:12px 0 10px;flex-wrap:wrap}}
 .btn{{flex:1 1 150px;text-align:center;padding:12px 10px;border-radius:9px;font-size:13px;
   font-family:inherit;letter-spacing:.05em;cursor:pointer;border:1px solid #333;background:#141414;color:#fff;text-decoration:none}}
 .btn.cp{{background:#FFC533;color:#0a0a0a;border-color:#FFC533;font-weight:700}}
 .btn.cp.done{{background:#3BD16F;border-color:#3BD16F}}
 .btn.im.done{{background:#3BD16F;border-color:#3BD16F;color:#0a0a0a;font-weight:700}}
 .btn.im.warn{{background:#8a6d1f;border-color:#8a6d1f;color:#fff}}
 .btn:disabled{{opacity:.6;cursor:default}}
 .tw{{white-space:pre-wrap;word-wrap:break-word;background:#000;border:1px solid #1f1f1f;border-radius:9px;
   padding:14px;font-size:14px;line-height:1.62;color:#e8e8e8;margin:0;font-family:inherit}}
 footer{{max-width:760px;margin:0 auto;padding:0 14px 50px;color:#6a6a6a;font-size:12px;line-height:1.7}}
 footer b{{color:#FFC533;font-weight:600}}
</style></head><body>
<header>
  <div class="k">{html.escape(a.kicker)}</div>
  <h1>{html.escape(a.titulo or f'Colón · Fecha {a.fecha}')}</h1>
  <div class="s">{html.escape(a.subtitulo)}</div>
</header>
<main>{''.join(cards)}</main>
<footer>
  <b>Fuentes:</b> {html.escape(a.fuentes)}<br>
  <b>Notas:</b> {html.escape(a.notas)}
</footer>
<script>
 // ---- copiar imagen ----
 // El portapapeles solo acepta PNG y las placas son JPEG, asi que se convierten
 // con un canvas en el momento del clic. Si el navegador lo bloquea, se descarga.
 function pngBlob(src){{
   return new Promise(function(res, rej){{
     var img = new Image();
     img.onload = function(){{
       var c = document.createElement('canvas');
       c.width = img.naturalWidth; c.height = img.naturalHeight;
       c.getContext('2d').drawImage(img, 0, 0);
       c.toBlob(function(b){{ b ? res(b) : rej(new Error('canvas vacio')); }}, 'image/png');
     }};
     img.onerror = function(){{ rej(new Error('no carga')); }};
     img.src = src;
   }});
 }}
 document.querySelectorAll('.btn.im').forEach(function(b){{
   b.addEventListener('click', function(){{
     var src = b.closest('.card').querySelector('img').src;
     var name = b.getAttribute('data-name');
     function flash(txt, cls){{
       b.textContent = txt; b.classList.add(cls);
       setTimeout(function(){{ b.textContent='Copiar imagen'; b.classList.remove(cls); }}, 1800);
     }}
     function bajar(){{
       var a = document.createElement('a');
       a.href = src; a.download = name;
       document.body.appendChild(a); a.click(); document.body.removeChild(a);
       flash('Descargada', 'warn');
     }}
     b.textContent = 'Copiando...'; b.disabled = true;
     var listo = function(){{ b.disabled = false; }};
     try {{
       // Se pasa la promesa al ClipboardItem: es lo que acepta Safari.
       var item = new ClipboardItem({{'image/png': pngBlob(src)}});
       navigator.clipboard.write([item]).then(function(){{
         listo(); flash('¡Copiada!', 'done');
       }}, function(){{ listo(); bajar(); }});
     }} catch(e) {{
       listo(); bajar();
     }}
   }});
 }});
 // ---- copiar tuit ----
 document.querySelectorAll('.btn.cp').forEach(function(b){{
   b.addEventListener('click',function(){{
     var t=b.getAttribute('data-t');
     function done(){{b.textContent='¡Copiado!';b.classList.add('done');
       setTimeout(function(){{b.textContent='Copiar tuit';b.classList.remove('done');}},1600);}}
     function fb(){{var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');
       ta.style.position='absolute';ta.style.left='-9999px';document.body.appendChild(ta);
       ta.select();ta.setSelectionRange(0,t.length);
       try{{document.execCommand('copy');done();}}catch(e){{}}
       document.body.removeChild(ta);}}
     if(navigator.clipboard&&navigator.clipboard.writeText){{
       navigator.clipboard.writeText(t).then(done,fb);
     }} else {{ fb(); }}
   }});
 }});
</script>
</body></html>'''
    open(out, 'w', encoding='utf-8').write(doc)
    print(f'ok {out} ({len(doc)} bytes, {n} tarjetas)')


if __name__ == '__main__':
    main()
