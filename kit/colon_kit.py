"""
COLON KIT - Generador de placas Primera Nacional (diseño F20+)
================================================================
Uso en un chat nuevo:
Motor de diseño. Las fuentes y los escudos se leen de ../assets/.
No se edita fecha a fecha: la parte editorial vive en config/fechas/fNN.json.
3. from colon_kit import build_metric, build_portada, build_top_jugadores, build_proximo_rival
4. Llamar cada función con los datos reales de la fecha (nunca inventar).

Todas las funciones reciben `fecha` (int) y `pj` (int, partidos jugados de Colón)
para que el footer/contexto se actualice solo, sin tocar el código cada vez.
"""

from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.abspath(__file__))
BEBAS = os.path.join(BASE, "..", "assets", "fonts", "BebasNeue.ttf")
MONO_R = os.path.join(BASE, "..", "assets", "fonts", "DMMono-Regular.ttf")
MONO_M = os.path.join(BASE, "..", "assets", "fonts", "DMMono-Medium.ttf")
CREST_DIR = os.path.join(BASE, "..", "assets", "escudos")
COLON_CREST = os.path.join(CREST_DIR, "colon.png")

W = H = 1080
MICRO, LABEL, BODY = 22, 26, 30
SPLIT_X = 740
ROW_CENTER = 310
ROW_TOP, ROW_H = 198, 224

# ------------------------------------------------------------------
# ZONAS (Primera Nacional 2026, nombres FootyStats) - fijo, no cambia por fecha
# ------------------------------------------------------------------
ZONA_A = ['Ferro Carril Oeste', 'Deportivo Morón', 'Los Andes', 'Colón', 'Ciudad de Bolívar',
          'Estudiantes Caseros', 'Almirante Brown', 'Deportivo Madryn', 'Godoy Cruz', 'San Miguel',
          'Defensores de Belgrano', 'Racing Córdoba', 'All Boys', 'San Telmo', 'Central Norte',
          'Acassuso', 'Club Atlético Mitre', 'Chaco For Ever']
ZONA_B = ['Gimnasia Jujuy', 'Atlanta', 'Tristán Suárez', 'Temperley', 'Deportivo Maipú', 'Midland',
          'Atlético Rafaela', 'San Martín Tucumán', 'Nueva Chicago', 'Almagro', 'Quilmes',
          'Gimnasia y Tiro', 'Colegiales', 'San Martín San Juan', 'Chacarita Juniors', 'Patronato',
          'Club Atlético Güemes', 'Agropecuario']
ZONA_DE = {t: 'ZA' for t in ZONA_A}
ZONA_DE.update({t: 'ZB' for t in ZONA_B})


def F(path, size):
    return ImageFont.truetype(path, size)


def _corner(draw, x, y, dx, dy, size=44, w=3, color='#FFC533'):
    draw.line([(x, y), (x + dx * size, y)], fill=color, width=w)
    draw.line([(x, y), (x, y + dy * size)], fill=color, width=w)


def _base_canvas(fecha, header_txt=None):
    """Fondo negro/rojo, escudo fantasma, marco de esquina, header de marca. Comun a todos los bloques."""
    img = Image.new('RGB', (W, H), '#080808')
    draw = ImageDraw.Draw(img)
    draw.rectangle([SPLIT_X, 0, W, H], fill='#C8102E')
    draw.line([(SPLIT_X, 0), (SPLIT_X, H)], fill='#FFC533', width=6)

    crest = Image.open(COLON_CREST).convert('RGBA')
    ghost = crest.resize((420, 420), Image.LANCZOS)
    a = ghost.split()[3].point(lambda v: int(v * 0.16))
    ghost.putalpha(a)
    img.paste(ghost, (SPLIT_X + 20, H - 440), ghost)

    _corner(draw, 28, 28, 1, 1)
    _corner(draw, W - 28, 28, -1, 1)
    _corner(draw, 28, H - 28, 1, -1)
    _corner(draw, W - 28, H - 28, -1, -1)

    small_crest = crest.resize((66, 66), Image.LANCZOS)
    img.paste(small_crest, (46, 36), small_crest)
    draw.text((126, 38), 'COLÓN', font=F(BEBAS, 40), fill='#FFFFFF')
    draw.text((126, 84), 'DE SANTA FE', font=F(MONO_M, MICRO), fill='#A9B4BE')

    draw.text((46, 128), header_txt or f'PRIMERA NACIONAL 2026 · FECHA {fecha}',
              font=F(MONO_M, LABEL), fill='#A9B4BE')
    draw.line([(46, 166), (SPLIT_X - 30, 166)], fill='#2a0810', width=2)
    return img, draw, crest


def zona_de(nombre_footystats):
    """Devuelve 'ZA' o 'ZB' para un nombre de equipo (formato FootyStats)."""
    return ZONA_DE.get(nombre_footystats, '??')


# ====================================================================
# BLOQUE DE METRICA (xG, xGA, xGD, xG vs real, remates, conversion...)
# ====================================================================
def build_metric(fecha, pj, label_lines, label_font_size, sub_lines, val_txt, val_font_size,
                  delta_txt, arrow_dir, worst, avg, best, val, signed, local_val, visit_val, is_pct,
                  top5_rows, colon_inline_idx, colon_row, colon_rank,
                  outpath, puesto_txt, avg_line_txt, top5_title,
                  fuente_txt='Fuente: FootyStats · Promiedos', bar_dec=2):
    """
    arrow_dir: 'stable' | 'up' | 'down_good'
    top5_rows: lista de (nombre, valor_str, "#N", "ZA"/"ZB") - los primeros 5 (o menos) del ranking real de liga
    colon_inline_idx: si Colón esta DENTRO del top5_rows, su posicion (1-5). Si no, pasar None.
    colon_row: si Colón NO esta en el top5, su fila aparte (nombre, valor_str, "#N", "ZA/ZB"). Si esta inline, pasar None.
    colon_rank: puesto real de Colón (para la fila aparte)
    puesto_txt: ej '#8' -> puesto de Colón en el ranking de ESTA metrica, de 36
    avg_line_txt: ej '1.28 xG' -> promedio liga con unidad, para el panel rojo
    """
    img, draw, crest = _base_canvas(fecha)

    col1_font = F(MONO_M, label_font_size)
    sub_font = F(MONO_M, LABEL)
    sub_line_h = LABEL + 8

    if len(label_lines) == 1:
        b1 = draw.textbbox((0, 0), label_lines[0], font=col1_font)
        h1 = b1[3] - b1[1]
        gap = 16
        sub_h = sub_line_h * len(sub_lines)
        block1_h = h1 + gap + sub_h
        c1_top = ROW_CENTER - block1_h / 2
        draw.text((46, c1_top - b1[1]), label_lines[0], font=col1_font, fill='#FFC533',
                   stroke_width=2, stroke_fill='#FFC533')
        sub_y = c1_top + h1 + gap
        for line in sub_lines:
            draw.text((46, sub_y), line, font=sub_font, fill='#A9B4BE')
            sub_y += sub_line_h
        widths = [b1[2]] + [draw.textbbox((0, 0), l, font=sub_font)[2] for l in sub_lines]
    else:
        b1 = draw.textbbox((0, 0), label_lines[0], font=col1_font)
        lh = b1[3] - b1[1]
        line_gap = 20
        block_lines_h = lh * 2 + line_gap
        sub_h = sub_line_h * len(sub_lines)
        block1_h = block_lines_h + 18 + sub_h
        c1_top = ROW_CENTER - block1_h / 2
        y1 = c1_top - b1[1]
        draw.text((46, y1), label_lines[0], font=col1_font, fill='#FFC533',
                   stroke_width=2, stroke_fill='#FFC533')
        y2 = c1_top + lh + line_gap - b1[1]
        draw.text((46, y2), label_lines[1], font=col1_font, fill='#FFC533',
                   stroke_width=2, stroke_fill='#FFC533')
        sub_y = c1_top + block_lines_h + 18
        for line in sub_lines:
            draw.text((46, sub_y), line, font=sub_font, fill='#A9B4BE')
            sub_y += sub_line_h
        widths = ([b1[2], draw.textbbox((0, 0), label_lines[1], font=col1_font)[2]] +
                  [draw.textbbox((0, 0), l, font=sub_font)[2] for l in sub_lines])

    col1_w = max(widths) + 40
    divider_x = 46 + col1_w
    draw.line([(divider_x, ROW_TOP), (divider_x, ROW_TOP + ROW_H)], fill='#2a0810', width=2)

    col2_font = F(BEBAS, val_font_size)
    b2 = draw.textbbox((0, 0), val_txt, font=col2_font)
    h2 = b2[3] - b2[1]
    c2_top = ROW_CENTER - h2 / 2
    col2_x = divider_x + 30
    draw.text((col2_x, c2_top - b2[1]), val_txt, font=col2_font, fill='#FFFFFF')

    # --- LOCAL / VISITANTE (tamaño fijo 26/16, siempre igual entre bloques) ---
    # Si local_val es None se omite la columna entera: hay fuentes (SICS) que dan
    # solo el total de temporada y no el desglose por localía. Inventarlo seria mentir.
    suf = '%' if is_pct else ''
    def fmt_lv(v):
        return f'{v:+.2f}{suf}' if signed else f'{v}{suf}'

    col3_x = col2_x + b2[2] + 44
    if local_val is None:
        pass
    else:
      local_str, visit_str = fmt_lv(local_val), fmt_lv(visit_val)
      main_top, main_bottom = c2_top, c2_top + h2
      avail_h = main_bottom - main_top

      lv_size, lab_size = 26, 16
      half_font = F(BEBAS, lv_size)
      lab_font = F(MONO_R, lab_size)
      lb = draw.textbbox((0, 0), 'VIS', font=lab_font)
      lb_h = lb[3] - lb[1]
      vb_local = draw.textbbox((0, 0), local_str, font=half_font)
      vb_visit = draw.textbbox((0, 0), visit_str, font=half_font)
      vb_h = max(vb_local[3] - vb_local[1], vb_visit[3] - vb_visit[1])
      content_h = 2 * lb_h + 2 * vb_h
      gap = (avail_h - content_h) / 3

      y_cursor = main_top
      draw.text((col3_x, y_cursor - lb[1]), 'LOC', font=lab_font, fill='#7a7a7a')
      y_cursor += lb_h + gap
      draw.text((col3_x, y_cursor - vb_local[1]), local_str, font=half_font, fill='#FFFFFF')
      y_cursor += vb_h + gap
      draw.text((col3_x, y_cursor - lb[1]), 'VIS', font=lab_font, fill='#7a7a7a')
      y_cursor += lb_h + gap
      draw.text((col3_x, y_cursor - vb_visit[1]), visit_str, font=half_font, fill='#FFFFFF')
      draw.line([(col3_x - 22, ROW_TOP + 18), (col3_x - 22, ROW_TOP + ROW_H - 18)], fill='#2a0810', width=1)
      # Chequeo de seguridad: avisar si LOC/VIS se acerca demasiado al panel rojo
      max_needed = max(vb_local[2], vb_visit[2], lb[2])
      if col3_x + max_needed > SPLIT_X - 20:
          print(f"[AVISO] {outpath}: LOCAL/VISITANTE casi toca el panel rojo -- "
                f"achicar val_font_size o el label de columna 1")

    row_bottom = ROW_TOP + ROW_H
    delta_y = row_bottom + 36
    ax = 46
    if arrow_dir == 'stable':
        draw.line([(ax, delta_y), (ax + 40, delta_y)], fill='#8C99A8', width=4)
        draw.polygon([(ax + 40, delta_y - 7), (ax + 50, delta_y), (ax + 40, delta_y + 7)], fill='#8C99A8')
    elif arrow_dir == 'up':
        draw.line([(ax, delta_y), (ax + 40, delta_y)], fill='#3BD16F', width=4)
        draw.polygon([(ax + 20, delta_y - 16), (ax + 40, delta_y), (ax, delta_y)], fill='#3BD16F')
    elif arrow_dir == 'down_good':
        draw.line([(ax, delta_y), (ax + 40, delta_y)], fill='#3BD16F', width=4)
        draw.polygon([(ax, delta_y), (ax + 40, delta_y), (ax + 20, delta_y + 16)], fill='#3BD16F')
    tf = F(MONO_R, LABEL)
    tb = draw.textbbox((0, 0), delta_txt, font=tf)
    th = tb[3] - tb[1]
    draw.text((ax + 62, delta_y - th / 2 - tb[1]), delta_txt, font=tf, fill='#A9B4BE')

    bar_y = delta_y + 60
    bar_x0 = 46
    bar_w = SPLIT_X - 30 - 46
    def xpos(v):
        return bar_x0 + int((v - worst) / (best - worst) * bar_w)
    draw.rounded_rectangle([bar_x0, bar_y, bar_x0 + bar_w, bar_y + 10], radius=5, fill='#1c1c1c')
    avg_x = xpos(avg)
    draw.line([(avg_x, bar_y - 6), (avg_x, bar_y + 16)], fill='#5a5a5a', width=2)
    val_x = xpos(val)
    draw.ellipse([val_x - 9, bar_y - 4, val_x + 9, bar_y + 14], fill='#FFC533', outline='#080808', width=2)

    bar_label_y = bar_y + 34
    def fmt(v):
        # decimales explicitos: sin esto un 15.40 se imprime "15.4" al lado de un
        # "11.00" y las tres etiquetas de la barra quedan con formatos distintos.
        if signed:
            return f'{v:+.{bar_dec}f}{suf}'
        return f'{v:.{bar_dec}f}{suf}'
    draw.text((bar_x0, bar_label_y), f'PEOR {fmt(worst)}', font=F(MONO_R, LABEL), fill='#A9B4BE')
    w2 = draw.textlength(f'PROM {fmt(avg)}', font=F(MONO_R, LABEL))
    draw.text((bar_x0 + bar_w / 2 - w2 / 2, bar_label_y), f'PROM {fmt(avg)}', font=F(MONO_R, LABEL), fill='#A9B4BE')
    w3 = draw.textlength(f'MEJOR {fmt(best)}', font=F(MONO_R, LABEL))
    draw.text((bar_x0 + bar_w - w3, bar_label_y), f'MEJOR {fmt(best)}', font=F(MONO_R, LABEL), fill='#A9B4BE')

    div_y = bar_label_y + 46
    draw.line([(46, div_y), (SPLIT_X - 30, div_y)], fill='#2a0810', width=2)
    draw.text((46, div_y + 18), top5_title, font=F(MONO_M, LABEL - 2), fill='#FFC533')

    num_col_w = 60
    name_x = 46 + num_col_w
    row_font = F(MONO_M, BODY)
    tag_font = F(MONO_R, MICRO)
    row_h_list = 42

    all_rows = list(top5_rows)
    if colon_row is not None:
        all_rows = all_rows + [colon_row]
    tag_col_w = max(draw.textlength(f'{posz} ({zona})', font=tag_font) for _, _, posz, zona in all_rows)
    val_right_x = SPLIT_X - 30 - tag_col_w - 14

    y = div_y + 18 + LABEL + 18
    for i, (name, v, posz, zona) in enumerate(top5_rows, 1):
        is_colon = (colon_inline_idx == i)
        if is_colon:
            draw.rectangle([46, y - 2, SPLIT_X - 30, y - 2 + row_h_list], fill='#1a0508')
        num_col = '#C8102E' if is_colon else '#7a7a7a'
        name_col = '#FFC533' if is_colon else '#FFFFFF'
        val_col = '#FFC533' if is_colon else '#A9B4BE'
        tag_col = '#e0a94a' if is_colon else '#5a5a5a'
        draw.text((46, y), f'{i}.', font=row_font, fill=num_col)
        draw.text((name_x, y), name, font=row_font, fill=name_col)
        tag = f'{posz} ({zona})'
        vw = draw.textlength(v, font=row_font)
        draw.text((val_right_x - vw, y), v, font=row_font, fill=val_col)
        draw.text((SPLIT_X - 30 - draw.textlength(tag, font=tag_font), y + 6), tag, font=tag_font, fill=tag_col)
        y += row_h_list

    if colon_row is not None:
        name, v, posz, zona = colon_row
        draw.rectangle([46, y - 2, SPLIT_X - 30, y - 2 + row_h_list], fill='#1a0508')
        draw.text((46, y + 4), f'{colon_rank}.', font=row_font, fill='#C8102E')
        draw.text((name_x, y + 4), name, font=row_font, fill='#FFC533')
        tag = f'{posz} ({zona})'
        vw = draw.textlength(v, font=row_font)
        draw.text((val_right_x - vw, y + 4), v, font=row_font, fill='#FFC533')
        draw.text((SPLIT_X - 30 - draw.textlength(tag, font=tag_font), y + 10), tag, font=tag_font, fill='#e0a94a')
        y += row_h_list

    footer_y = y + 20
    draw.line([(46, footer_y), (SPLIT_X - 30, footer_y)], fill='#2a0810', width=1)
    footer_text_y = footer_y + 18
    draw.text((46, footer_text_y), fuente_txt, font=F(MONO_R, MICRO), fill='#7a7a7a')

    px = SPLIT_X + 40
    draw.text((px, 166), 'PUESTO', font=F(MONO_M, LABEL), fill='#FFC533')
    pf = F(BEBAS, 190)
    pb = draw.textbbox((0, 0), puesto_txt, font=pf)
    h_p = pb[3] - pb[1]
    c_top = ROW_CENTER - h_p / 2
    new_y = c_top - pb[1]
    draw.text((px - pb[0], new_y), puesto_txt, font=pf, fill='#FFC533')
    glyph_bottom = new_y + pb[3]
    label_y = glyph_bottom + 40
    draw.text((px, label_y), 'DE 36 EQUIPOS', font=F(MONO_M, LABEL), fill='#FFC533')

    line2_y = label_y + LABEL + 32
    draw.line([(px, line2_y), (W - 40, line2_y)], fill='#FFC533', width=2)
    draw.text((px, line2_y + 26), 'PROMEDIO LIGA', font=F(MONO_M, LABEL - 4), fill='#FFC533')
    draw.text((px, line2_y + 26 + LABEL + 10), avg_line_txt, font=F(BEBAS, 48), fill='#FFC533')

    draw.text((px, footer_text_y), f'F{fecha} · {pj} PJ', font=F(MONO_R, MICRO), fill='#FFC533')

    img.save(outpath, quality=92)
    return outpath


# ====================================================================
# PORTADA (unificada: progreso de temporada + PTS/posicion en el panel rojo)
# ====================================================================
def build_portada(fecha, pj, pts, posicion_zona, zona, en_este_hilo, outpath,
                   total_fechas=36, fuente_txt='Fuente: FootyStats · Promiedos.com.ar'):
    img, draw, crest = _base_canvas(fecha)
    split_x = SPLIT_X

    draw.text((54, 188), 'ANÁLISIS ESTADÍSTICO', font=F(MONO_M, 26), fill='#FFC533')
    draw.text((54, 222), f'PRIMERA NACIONAL 2026 · ZONA {zona}', font=F(MONO_M, 24), fill='#A9B4BE')

    num_font = F(BEBAS, 230)
    slash_font = F(BEBAS, 80)
    x0 = 50
    pj_str = str(pj)
    bbox_pj = draw.textbbox((0, 0), pj_str, font=num_font)
    top_pj = 280
    draw.text((x0, top_pj - bbox_pj[1]), pj_str, font=num_font, fill='#FFFFFF')
    baseline_y = top_pj - bbox_pj[1] + bbox_pj[3]
    x1 = x0 + (bbox_pj[2] - bbox_pj[0]) + 18
    bboxs = draw.textbbox((0, 0), '/', font=slash_font)
    draw.text((x1, baseline_y - bboxs[3]), '/', font=slash_font, fill='#FFC533')
    x2 = x1 + (bboxs[2] - bboxs[0]) + 4
    bboxd = draw.textbbox((0, 0), str(total_fechas), font=slash_font)
    draw.text((x2, baseline_y - bboxd[3]), str(total_fechas), font=slash_font, fill='#FFC533')

    label_y = top_pj - bbox_pj[1] + bbox_pj[3] + 34
    draw.text((54, label_y), f'FECHAS JUGADAS · ZONA {zona}', font=F(MONO_M, 30), fill='#A9B4BE')

    bar_y = label_y + 52
    bar_h = 16
    bar_w = split_x - 30 - 54
    frac = pj / total_fechas
    fill_w = int(bar_w * frac)
    step = 14
    bg_stripe = Image.new('RGB', (bar_w, bar_h), '#1c1c1c')
    bgd = ImageDraw.Draw(bg_stripe)
    for off in range(-bar_h, bar_w, step):
        bgd.line([(off, bar_h), (off + bar_h, 0)], fill='#0a0a0a', width=6)
    fg_stripe = Image.new('RGB', (bar_w, bar_h), '#FFC533')
    fgd = ImageDraw.Draw(fg_stripe)
    for off in range(-bar_h, bar_w, step):
        fgd.line([(off, bar_h), (off + bar_h, 0)], fill='#0d0d0d', width=6)
    bar_canvas = bg_stripe.copy()
    bar_canvas.paste(fg_stripe.crop((0, 0, fill_w, bar_h)), (0, 0))
    mask = Image.new('L', (bar_w, bar_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bar_w, bar_h], radius=8, fill=255)
    img.paste(bar_canvas, (54, bar_y), mask)
    pct_txt = f'{round(100*frac)}% DEL TORNEO JUGADO'
    draw.text((54, bar_y + 30), pct_txt, font=F(MONO_M, 22), fill='#FFC533')

    line_y = bar_y + 80
    draw.line([(54, line_y), (split_x - 30, line_y)], fill='#2a0810', width=2)
    draw.text((54, line_y + 28), 'EN ESTE HILO', font=F(MONO_M, 26), fill='#FFC533')

    y = line_y + 28 + 42
    mono_item = F(MONO_M, 29)
    for item in en_este_hilo:
        draw.ellipse([54, y + 9, 65, y + 20], fill='#FFC533')
        draw.text((80, y), item, font=mono_item, fill='#FFFFFF')
        y += 42

    draw.line([(54, H - 80), (split_x - 30, H - 80)], fill='#2a0810', width=1)
    draw.text((54, H - 58), fuente_txt, font=F(MONO_R, 20), fill='#7a7a7a')

    # PANEL ROJO: PUNTOS + POSICION
    px = split_x + 40
    draw.text((px, 166), 'PUNTOS', font=F(MONO_M, 26), fill='#FFC533')
    pf = F(BEBAS, 180)
    pb = draw.textbbox((0, 0), str(pts), font=pf)
    draw.text((px - pb[0], 222), str(pts), font=pf, fill='#FFC533')
    glyph_bottom = 222 + pb[3]
    label_y2 = glyph_bottom + 34
    draw.text((px, label_y2), f'ZONA {zona}', font=F(MONO_M, 26), fill='#FFC533')

    line2_y = label_y2 + 26 + 30
    draw.line([(px, line2_y), (W - 40, line2_y)], fill='#FFC533', width=2)
    draw.text((px, line2_y + 26), 'POSICIÓN', font=F(MONO_M, 22), fill='#FFC533')
    pf2 = F(BEBAS, 120)
    draw.text((px, line2_y + 26 + 30), posicion_zona, font=pf2, fill='#FFC533')

    draw.text((px, H - 58), f'F{fecha} · {pj} PJ', font=F(MONO_R, 20), fill='#FFC533')

    img.save(outpath, quality=92)
    return outpath


# ====================================================================
# TOP JUGADORES xG (liga completa, Colón resaltado)
# ====================================================================
def build_top_jugadores(fecha, pj, jugador_nombre, jugador_xg, jugador_goles, jugador_pj, jugador_min,
                         puesto_liga, total_jugadores, top5_rows, outpath,
                         ambito='DEL TORNEO', sub_hero=None,
                         colon_row=None, colon_rank=None):
    """ambito: alcance del ranking que se muestra. 'DEL TORNEO' (default, comportamiento
    anterior) o 'DEL PLANTEL' si el top 5 solo compara jugadores de Colon. Importa porque
    FootyStats reescribe el xG por jugador entre exports y el ranking de liga no es estable."""
    """
    top5_rows: lista de (nombre_corto, club_o_'Colón', xg_str, 'Ng') p/ los primeros de la liga.
               Si el jugador de Colón NO esta en el top5 mostrado, agregarlo aparte vos mismo
               con el mismo criterio que build_metric (fila con su puesto real).
    """
    img, draw, crest = _base_canvas(fecha)
    split_x = SPLIT_X

    col1_font = F(MONO_M, 58)
    label_txt = jugador_nombre.split()[-1].upper()  # apellido como titular
    b1 = draw.textbbox((0, 0), label_txt, font=col1_font)
    h1 = b1[3] - b1[1]
    gap = 16
    sub_font = F(MONO_M, LABEL)
    sub_line_h = LABEL + 8
    # sub_hero permite describir al jugador destacado cuando NO es el lider del ambito
    # (por ejemplo, mostrarlo 6to del torneo sin afirmar que es el maximo).
    sub_lines = sub_hero if sub_hero else ['MÁXIMO xG', ambito]
    sub_h = sub_line_h * 2
    block1_h = h1 + gap + sub_h
    c1_top = ROW_CENTER - block1_h / 2
    draw.text((46, c1_top - b1[1]), label_txt, font=col1_font, fill='#FFC533',
               stroke_width=2, stroke_fill='#FFC533')
    sub_y = c1_top + h1 + gap
    draw.text((46, sub_y), sub_lines[0], font=sub_font, fill='#A9B4BE')
    draw.text((46, sub_y + sub_line_h), sub_lines[1], font=sub_font, fill='#A9B4BE')

    # El divisor tiene que considerar tambien el ancho de los subtitulos, no solo el
    # del nombre: con sub_lines largos el texto se montaba sobre la linea divisoria.
    _sub_w = max(draw.textbbox((0, 0), t, font=sub_font)[2] for t in sub_lines)
    col1_w = max(b1[2], _sub_w) + 40
    divider_x = 46 + col1_w
    draw.line([(divider_x, ROW_TOP), (divider_x, ROW_TOP + ROW_H)], fill='#2a0810', width=2)

    col2_font = F(BEBAS, 200)
    val_txt = f'{jugador_xg:.2f}'
    b2 = draw.textbbox((0, 0), val_txt, font=col2_font)
    h2 = b2[3] - b2[1]
    c2_top = ROW_CENTER - h2 / 2
    col2_x = divider_x + 30
    draw.text((col2_x, c2_top - b2[1]), val_txt, font=col2_font, fill='#FFFFFF')

    row_bottom = ROW_TOP + ROW_H
    ctx_y = row_bottom + 48
    draw.text((46, ctx_y), f'{jugador_goles} GOLES · {jugador_pj} PJ · {jugador_min} MIN',
              font=F(MONO_R, LABEL), fill='#A9B4BE')

    div_y = ctx_y + 90
    draw.line([(46, div_y), (split_x - 30, div_y)], fill='#2a0810', width=2)
    draw.text((46, div_y + 22), f'TOP 5 xG {ambito}', font=F(MONO_M, LABEL), fill='#FFC533')

    num_col_w = 60
    name_x = 46 + num_col_w
    row_font = F(MONO_M, BODY)
    tag_font = F(MONO_R, MICRO)
    row_h_list = 46

    # top5_rows lleva los 5 primeros del ambito. El renglon de Colon va aparte, en la
    # 6ta fila y con su PUESTO REAL, no con el indice del bucle (misma convencion que
    # build_metric). Si Colon ya esta entre los 5, no hace falta pasar colon_row.
    _filas = [(i, r) for i, r in enumerate(top5_rows, 1)]
    if colon_row is not None:
        _filas.append((colon_rank if colon_rank is not None else len(top5_rows) + 1, colon_row))

    y = div_y + 22 + LABEL + 24
    for i, (name, club, xg, goles) in _filas:
        is_colon = (club == 'Colón')
        if is_colon:
            draw.rectangle([46, y - 2, split_x - 30, y - 2 + row_h_list], fill='#1a0508')
        num_col = '#C8102E' if is_colon else '#7a7a7a'
        name_col = '#FFC533' if is_colon else '#FFFFFF'
        club_col = '#e0a94a' if is_colon else '#5a5a5a'
        val_col = '#FFC533' if is_colon else '#A9B4BE'
        draw.text((46, y), f'{i}.', font=row_font, fill=num_col)
        draw.text((name_x, y), name, font=row_font, fill=name_col)
        draw.text((name_x + draw.textlength(name, font=row_font) + 16, y + 8), club,
                  font=tag_font, fill=club_col)
        combo = f'{xg} · {goles}'
        vw = draw.textlength(combo, font=row_font)
        draw.text((split_x - 30 - vw, y), combo, font=row_font, fill=val_col)
        y += row_h_list

    footer_y = y + 30
    draw.line([(46, footer_y), (split_x - 30, footer_y)], fill='#2a0810', width=1)
    footer_text_y = footer_y + 18
    draw.text((46, footer_text_y), 'Fuente: FootyStats', font=F(MONO_R, MICRO), fill='#7a7a7a')

    px = split_x + 40
    draw.text((px, 166), 'PUESTO', font=F(MONO_M, LABEL), fill='#FFC533')
    pf = F(BEBAS, 190)
    p_txt = f'#{puesto_liga}'
    pb = draw.textbbox((0, 0), p_txt, font=pf)
    h_p = pb[3] - pb[1]
    c_top = ROW_CENTER - h_p / 2
    new_y = c_top - pb[1]
    draw.text((px - pb[0], new_y), p_txt, font=pf, fill='#FFC533')
    glyph_bottom = new_y + pb[3]
    label_y = glyph_bottom + 40
    draw.text((px, label_y), f'DE {total_jugadores} JUGADORES', font=F(MONO_M, LABEL - 2), fill='#FFC533')

    line2_y = label_y + LABEL + 32
    draw.line([(px, line2_y), (W - 40, line2_y)], fill='#FFC533', width=2)
    draw.text((px, line2_y + 26), 'MINUTOS', font=F(MONO_M, LABEL - 4), fill='#FFC533')
    draw.text((px, line2_y + 26 + LABEL + 10), str(jugador_min), font=F(BEBAS, 48), fill='#FFC533')

    draw.text((px, footer_text_y), f'F{fecha} · {pj} PJ', font=F(MONO_R, MICRO), fill='#FFC533')

    img.save(outpath, quality=92)
    return outpath


# ====================================================================
# PROXIMO RIVAL
# ====================================================================
def build_proximo_rival(fecha_rival, rival_nombre, rival_ciudad,
                         rival_local_pj, rival_local_wdl, rival_local_xg, rival_local_xga,
                         colon_visit_pj, colon_visit_wdl, colon_visit_xg, colon_visit_xga,
                         rival_tag, rival_pts, diferencia_txt,
                         goleador_rival, goleador_colon,
                         outpath, fecha_actual_pj_texto='PENDIENTE', colon_es_local=False,
                         header_txt=None, pie_txt=None):
    """colon_es_local=False (default) -> Colon visita: se esperan los numeros del rival
    como LOCAL y los de Colon como VISITANTE. Con colon_es_local=True se invierten las
    etiquetas: pasar los numeros del rival como VISITANTE y los de Colon como LOCAL.
    El default preserva el comportamiento de todas las fechas anteriores."""
    img, draw, crest = _base_canvas(fecha_rival, header_txt=header_txt)
    split_x = SPLIT_X

    draw.text((46, 186), 'PRÓXIMO RIVAL', font=F(MONO_M, 26), fill='#FFC533', stroke_width=1, stroke_fill='#FFC533')
    draw.text((46, 220), rival_nombre.upper(), font=F(BEBAS, 150), fill='#FFFFFF', stroke_width=1, stroke_fill='#FFFFFF')
    _cond = 'LOCAL' if colon_es_local else 'VISITANTE'
    draw.text((46, 375), f'{_cond} · {rival_ciudad.upper()}', font=F(MONO_M, 26), fill='#A9B4BE')

    y0 = 440
    draw.line([(46, y0), (split_x - 30, y0)], fill='#2a0810', width=2)

    def stat_row(y, title, pj, wdl, xg, xga):
        draw.text((46, y), title, font=F(MONO_M, 26), fill='#FFC533', stroke_width=1, stroke_fill='#FFC533')
        yy = y + 40
        items = [('PJ', pj), ('G-E-P', wdl), ('xG', xg), ('xGA', xga)]
        colw = (split_x - 30 - 46) // 4
        for i, (lab, val) in enumerate(items):
            x = 46 + i * colw
            draw.text((x, yy), lab, font=F(MONO_R, MICRO), fill='#7a7a7a')
            draw.text((x, yy + 28), str(val), font=F(BEBAS, 44), fill='#FFFFFF')
        return yy + 90

    _rc = 'COMO VISITANTE' if colon_es_local else 'COMO LOCAL'
    y1 = stat_row(y0 + 24, f'{rival_nombre.upper()} · {_rc}', rival_local_pj, rival_local_wdl,
                  rival_local_xg, rival_local_xga)
    draw.line([(46, y1), (split_x - 30, y1)], fill='#2a0810', width=1)
    _cc = 'COMO LOCAL' if colon_es_local else 'COMO VISITANTE'
    y2 = stat_row(y1 + 24, f'COLÓN · {_cc}', colon_visit_pj, colon_visit_wdl,
                  colon_visit_xg, colon_visit_xga)

    y = y2 + 10
    draw.text((46, y), 'GOLEADORES', font=F(MONO_M, 26), fill='#FFC533', stroke_width=1, stroke_fill='#FFC533')
    y += 42
    row_font = F(MONO_M, 28)
    label_font = F(MONO_R, 24)
    # Los dos goleadores van al lado si entran; si no, se apilan. Antes el bloque de
    # Colon arrancaba en un x fijo de 370 y se pisaba con nombres de rival largos.
    _lim = split_x - 30

    def _gol(x, yy, etiqueta, valor, color):
        draw.text((x, yy), f'{etiqueta}:', font=label_font, fill='#7a7a7a')
        x2 = x + draw.textlength(f'{etiqueta}: ', font=label_font)
        draw.text((x2, yy - 3), valor, font=row_font, fill=color)
        return x2 + draw.textbbox((0, 0), valor, font=row_font)[2]

    fin_rival = _gol(46, y, rival_nombre, goleador_rival, '#FFFFFF')
    ancho_colon = (draw.textlength('Colón: ', font=label_font)
                   + draw.textbbox((0, 0), goleador_colon, font=row_font)[2])
    x_colon = max(370, fin_rival + 30)
    if x_colon + ancho_colon <= _lim:
        _gol(x_colon, y, 'Colón', goleador_colon, '#FFC533')
        footer_y = y + 56
    else:
        y += 40
        _gol(46, y, 'Colón', goleador_colon, '#FFC533')
        footer_y = y + 56
    draw.line([(46, footer_y), (split_x - 30, footer_y)], fill='#2a0810', width=1)
    draw.text((46, footer_y + 18), 'Fuente: FootyStats', font=F(MONO_R, 22), fill='#7a7a7a')

    px = split_x + 40
    draw.text((px, 166), rival_tag, font=F(MONO_M, 26), fill='#FFC533')
    pf = F(BEBAS, 150)
    pb = draw.textbbox((0, 0), str(rival_pts), font=pf)
    draw.text((px, 222), str(rival_pts), font=pf, fill='#FFC533')
    draw.text((px, 222 + (pb[3] - pb[1]) + 30), 'PUNTOS', font=F(MONO_M, 26), fill='#FFC533')

    line2_y = 222 + (pb[3] - pb[1]) + 30 + 26 + 40
    draw.line([(px, line2_y), (W - 40, line2_y)], fill='#FFC533', width=2)
    draw.text((px, line2_y + 26), 'DIFERENCIA', font=F(MONO_M, 22), fill='#FFC533')
    draw.text((px, line2_y + 26 + 26 + 10), diferencia_txt, font=F(BEBAS, 38), fill='#FFC533')

    _pie = pie_txt or f'F{fecha_rival} · {fecha_actual_pj_texto}'
    _fs = 22
    while _fs > 14 and px + draw.textbbox((0, 0), _pie, font=F(MONO_R, _fs))[2] > W - 40:
        _fs -= 1
    draw.text((px, H - 58), _pie, font=F(MONO_R, _fs), fill='#FFC533')

    img.save(outpath, quality=92)
    return outpath


def build_portada_identidad(header_txt, kicker, subtitulo, hero_num, hero_label,
                            en_este_hilo, mejor_puesto, mejor_label,
                            peor_puesto, peor_label, outpath,
                            fuente_txt='Fuente: SICS.tv · Team.Studio',
                            rotulo_mejor='MEJOR PUESTO', rotulo_peor='PEOR PUESTO'):
    """Portada del hilo de IDENTIDAD DE JUEGO.

    Es una funcion aparte y no un parametro de build_portada a proposito: esa portada
    tiene barra de progreso del torneo y panel de puntos/posicion, que son elementos de
    un reporte de fecha. Aca el panel rojo muestra el mejor y el peor puesto del equipo,
    que es la tesis del hilo (un equipo de extremos), y no hay barra de progreso.
    Misma paleta y misma tipografia para que se reconozca la marca, distinta arquitectura
    de informacion para que nadie confunda los dos hilos.
    """
    img, draw, crest = _base_canvas(None, header_txt=header_txt)
    split_x = SPLIT_X
    LIM = split_x - 30

    # ---- columna negra ----
    y = 196
    draw.text((46, y), kicker, font=F(MONO_M, 44), fill='#FFC533', stroke_width=2, stroke_fill='#FFC533')
    y += 62
    draw.text((46, y), subtitulo, font=F(MONO_M, LABEL), fill='#A9B4BE')

    # numero grande
    y += 58
    fh = F(BEBAS, 200)
    bb = draw.textbbox((0, 0), hero_num, font=fh)
    draw.text((46, y - bb[1]), hero_num, font=fh, fill='#FFFFFF')
    hx = 46 + bb[2] + 24
    lf = F(MONO_M, 30)
    for i, ln in enumerate(hero_label):
        draw.text((hx, y + 40 + i * 42), ln, font=lf, fill='#FFC533')
    y = y + bb[3] + 34
    draw.line([(46, y), (LIM, y)], fill='#2a0810', width=2)

    # lista
    y += 30
    draw.text((46, y), 'EN ESTE HILO', font=F(MONO_M, LABEL), fill='#FFC533')
    y += 44
    for it in en_este_hilo:
        draw.ellipse([46, y + 10, 56, y + 20], fill='#FFC533')
        draw.text((72, y), it, font=F(MONO_M, 29), fill='#FFFFFF')
        y += 42

    draw.text((46, H - 62), fuente_txt, font=F(MONO_R, 22), fill='#555555')

    # ---- panel rojo: el mejor y el peor puesto ----
    def bloque(y0, rotulo, num, detalle, linea=True):
        cx = split_x + (W - split_x) // 2
        draw.text((split_x + 40, y0), rotulo, font=F(MONO_M, LABEL), fill='#FFC533')
        fn = F(BEBAS, 170)
        b = draw.textbbox((0, 0), num, font=fn)
        draw.text((cx - b[2] // 2 - b[0], y0 + 34), num, font=fn, fill='#FFC533')
        yy = y0 + 34 + b[3] + 10
        for ln in detalle:
            draw.text((split_x + 40, yy), ln, font=F(MONO_M, 24), fill='#FFC533')
            yy += 34
        if linea:
            draw.line([(split_x + 40, yy + 16), (W - 40, yy + 16)], fill='#FFC533', width=2)
        return yy + 52

    ny = bloque(190, rotulo_mejor, mejor_puesto, mejor_label)
    bloque(ny, rotulo_peor, peor_puesto, peor_label, linea=False)

    img.save(outpath, 'JPEG', quality=92)
    return outpath


def build_caratula(header_txt, linea1, linea2, bajada, dato_num, dato_label,
                   outpath, fuente_txt='Fuente: FootyStats · Promiedos.com.ar'):
    """Caratula de apertura para piezas anuales o tematicas. Casi sin datos: su trabajo
    es avisar que lo que viene no es el hilo de cada fecha. Lleva un solo numero para
    que la imagen frene el scroll, pero sin tabla ni barras ni top 5."""
    img, draw, crest = _base_canvas(None, header_txt=header_txt)
    split_x = SPLIT_X
    LIM = split_x - 30

    f1 = F(MONO_M, 88)
    y = 300
    for ln in (linea1, linea2):
        bb = draw.textbbox((0, 0), ln, font=f1)
        draw.text((46, y - bb[1]), ln, font=f1, fill='#FFC533',
                  stroke_width=3, stroke_fill='#FFC533')
        y += 104
    draw.line([(46, y + 10), (LIM, y + 10)], fill='#2a0810', width=3)
    y += 56
    for ln in bajada:
        draw.text((46, y), ln, font=F(MONO_M, 30), fill='#A9B4BE')
        y += 44
    draw.text((46, H - 62), fuente_txt, font=F(MONO_R, 22), fill='#555555')

    px, cx = split_x + 40, split_x + (W - split_x) // 2
    fn = F(BEBAS, 230)
    bb = draw.textbbox((0, 0), dato_num, font=fn)
    draw.text((cx - bb[2] // 2 - bb[0], 380), dato_num, font=fn, fill='#FFC533')
    yy = 380 + bb[3] + 24
    for ln in dato_label:
        draw.text((px, yy), ln, font=F(MONO_M, LABEL), fill='#FFC533')
        yy += 36
    img.save(outpath, 'JPEG', quality=92)
    return outpath


def build_llave(etapa_txt, label_lines, sub_lines, colon_val, rival_val, rival_nombre,
                mejor_es_mayor, contexto_izq, contexto_der, lectura, outpath,
                decimales=2, sufijo='', fuente_txt='Fuente: FootyStats'):
    """Placa del REDUCIDO. Cambia el marco de comparacion respecto de la placa de fecha.

    En la fase regular comparabamos contra el promedio del equipo y su puesto entre 36.
    En el Reducido eso no sirve: un partido no mueve un promedio de 33, y despues de la
    primera fase ya no hay 36 equipos contra quien rankear. Aca se compara contra el
    rival de la llave, que es la unica comparacion que importa en un mata-mata.

    colon_val y rival_val son el dato de cada uno; mejor_es_mayor define quien gana la
    comparacion. El panel rojo lleva el numero del rival, no el puesto.
    """
    img, draw, crest = _base_canvas(None, header_txt=etapa_txt)
    LIM = SPLIT_X - 30
    fmt = lambda v: f'{v:.{decimales}f}{sufijo}'

    y = 206
    lf = F(MONO_M, 46)
    for ln in label_lines:
        draw.text((46, y), ln, font=lf, fill='#FFC533', stroke_width=2, stroke_fill='#FFC533')
        y += 58
    for ln in sub_lines:
        draw.text((46, y), ln, font=F(MONO_M, LABEL), fill='#A9B4BE')
        y += 34

    # --- el cara a cara: dos barras proporcionales ---
    y += 26
    # la escala va por valor absoluto: con metricas negativas (xG vs Real) tomar el
    # maximo a secas hace que la barra mas chica se dibuje mas larga que el panel.
    tope = max(abs(colon_val), abs(rival_val)) or 1
    gana_colon = (colon_val > rival_val) if mejor_es_mayor else (colon_val < rival_val)
    for nombre, val, es_colon in [('COLÓN', colon_val, True), (rival_nombre.upper(), rival_val, False)]:
        gana = (es_colon and gana_colon) or (not es_colon and not gana_colon)
        col = '#C8102E' if gana else '#2a2a2a'
        txt_col = '#FFFFFF' if gana else '#8C99A8'
        draw.text((46, y), nombre, font=F(MONO_M, 30), fill='#FFC533' if es_colon else '#8C99A8')
        bx0, bw = 46, LIM - 46 - 150
        draw.rounded_rectangle([bx0, y + 46, bx0 + bw, y + 70], 10, fill='#161616')
        draw.rounded_rectangle([bx0, y + 46, bx0 + int(bw * abs(val) / abs(tope)), y + 70], 10, fill=col)
        fn = F(BEBAS, 62)
        t = fmt(val)
        draw.text((LIM - draw.textbbox((0, 0), t, font=fn)[2], y + 20), t, font=fn, fill=txt_col)
        y += 116

    draw.line([(46, y + 4), (LIM, y + 4)], fill='#2a0810', width=2)
    y += 28
    for ln in lectura:
        draw.text((46, y), ln, font=F(MONO_M, 26), fill='#A9B4BE')
        y += 36
    draw.text((46, H - 76), fuente_txt, font=F(MONO_R, MICRO), fill='#7a7a7a')

    # --- panel rojo: el dato del rival en su contexto, no el puesto ---
    px, cx = SPLIT_X + 40, SPLIT_X + (W - SPLIT_X) // 2
    draw.text((px, 196), rival_nombre.upper(), font=F(MONO_M, LABEL), fill='#FFC533')
    fn = F(BEBAS, 150)
    t = fmt(rival_val)
    bb = draw.textbbox((0, 0), t, font=fn)
    draw.text((cx - bb[2] // 2 - bb[0], 236), t, font=fn, fill='#FFC533')
    yy = 236 + bb[3] + 20
    for ln in contexto_der:
        draw.text((px, yy), ln, font=F(MONO_M, 23), fill='#FFC533')
        yy += 32
    draw.line([(px, yy + 16), (W - 40, yy + 16)], fill='#FFC533', width=2)
    yy += 48
    for ln in contexto_izq:
        draw.text((px, yy), ln, font=F(MONO_M, 22), fill='#FFC533')
        yy += 30
    draw.text((px, H - 58), 'PARTIDO ÚNICO', font=F(MONO_R, 20), fill='#FFC533')
    img.save(outpath, 'JPEG', quality=92)
    return outpath
