import json
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/home/fac/piscina/V1"
img = Image.open(f"{BASE_DIR}/renders/planta_quiosque_base.png").convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

with open(f"{BASE_DIR}/renders/planta_quiosque.json", "r", encoding="utf-8") as f:
    data = json.load(f)

W, H = data["width"], data["height"]

F_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
F_BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 19)
F_REG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 17)
F_TAG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
F_DIM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 17)

TAG_COLOR = (196, 90, 30, 255)
TAG_TEXT = (255, 255, 255, 255)
DIM_COLOR = (30, 90, 170, 255)
DIM_TEXT = (255, 255, 255, 255)
BOX_FILL = (20, 24, 30, 225)
BOX_OUTLINE = (255, 210, 60, 255)


def draw_pillar_tag(px, py, number):
    r = 15
    draw.ellipse([px - r, py - r, px + r, py + r], fill=TAG_COLOR, outline=(255, 255, 255, 255), width=2)
    text = str(number)
    bbox = draw.textbbox((0, 0), text, font=F_TAG)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((px - tw / 2 - bbox[0], py - th / 2 - bbox[1]), text, font=F_TAG, fill=TAG_TEXT)


def draw_arrowhead(tip, direction, size=9, color=DIM_COLOR):
    angle = math.atan2(direction[1], direction[0])
    a1 = angle + math.radians(150)
    a2 = angle - math.radians(150)
    p1 = (tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1))
    p2 = (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2))
    draw.polygon([tip, p1, p2], fill=color)


def draw_dimension(p1, p2, normal, dist_m, offset_px=46):
    x1, y1 = p1
    x2, y2 = p2
    nx, ny = normal
    # normal está em espaço-mundo (Y para cima); a imagem tem Y para baixo,
    # entao invertemos o componente Y ao converter para deslocamento em pixels.
    ox1, oy1 = x1 + nx * offset_px, y1 - ny * offset_px
    ox2, oy2 = x2 + nx * offset_px, y2 - ny * offset_px

    draw.line([(x1, y1), (ox1, oy1)], fill=(120, 120, 120, 160), width=1)
    draw.line([(x2, y2), (ox2, oy2)], fill=(120, 120, 120, 160), width=1)
    draw.line([(ox1, oy1), (ox2, oy2)], fill=DIM_COLOR, width=3)
    draw_arrowhead((ox1, oy1), (ox1 - ox2, oy1 - oy2))
    draw_arrowhead((ox2, oy2), (ox2 - ox1, oy2 - oy1))

    mx, my = (ox1 + ox2) / 2.0, (oy1 + oy2) / 2.0
    text = f"{dist_m:.2f} m"
    bbox = draw.textbbox((0, 0), text, font=F_DIM)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = 5
    bx0, by0 = mx - tw / 2 - pad - bbox[0], my - th / 2 - pad - bbox[1]
    bx1, by1 = bx0 + tw + pad * 2, by0 + th + pad * 2
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=5, fill=DIM_COLOR, outline=(255, 255, 255, 255), width=1)
    draw.text((mx - tw / 2 - bbox[0], my - th / 2 - bbox[1]), text, font=F_DIM, fill=DIM_TEXT)


for e in data["edges"]:
    draw_dimension(e["p1px"], e["p2px"], e["normal"], e["dist"])

# --- Terças (T1..T4) e vigas transversais (V1..V6) sobre a planta ----------
TERCA_COLOR = (35, 140, 90, 255)
VIGA_COLOR = (150, 95, 30, 255)


def draw_beam_tag(midpx, label, color):
    x, y = midpx
    r = 15
    draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=(255, 255, 255, 255), width=2)
    bbox = draw.textbbox((0, 0), label, font=F_DIM)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw / 2 - bbox[0], y - th / 2 - bbox[1]), label, font=F_DIM, fill=(255, 255, 255, 255))


for v in data.get("transversais", []):
    draw.line([tuple(v["p1px"]), tuple(v["p2px"])], fill=VIGA_COLOR, width=4)
for v in data.get("transversais", []):
    draw_beam_tag(v["midpx"], v["n"], VIGA_COLOR)

for t in data.get("tercas", []):
    draw.line([tuple(t["p1px"]), tuple(t["p2px"])], fill=TERCA_COLOR, width=6)

# marca de apoio: anel verde nos pilares em que cada terça se apoia
# (deixa claro que T1 corre sobre P1-P10-P9-P6, T3 sobre P2-P3-P4-P5, etc.)
for t in data.get("tercas", []):
    y_lo = min(t["p1px"][1], t["p2px"][1])
    y_hi = max(t["p1px"][1], t["p2px"][1])
    for p in data["pillars"]:
        if abs(p["px"][0] - t["p1px"][0]) <= 6 and y_lo - 6 <= p["px"][1] <= y_hi + 6:
            cx_p, cy_p = p["px"]
            draw.ellipse([cx_p - 19, cy_p - 19, cx_p + 19, cy_p + 19],
                         outline=TERCA_COLOR, width=3)

for t in data.get("tercas", []):
    draw_beam_tag(t["midpx"], t["n"], TERCA_COLOR)

# --- Drenagem pluvial: canaleta (aparente) + cano Ø100 (enterrado) ---------
DREN_COLOR = (40, 150, 210, 255)


def _dashed(p1, p2, color, width, dash=16, gap=12):
    x1, y1 = p1
    x2, y2 = p2
    total = math.hypot(x2 - x1, y2 - y1)
    if total < 1:
        return
    ux, uy = (x2 - x1) / total, (y2 - y1) / total
    s = 0.0
    while s < total:
        e = min(s + dash, total)
        draw.line([(x1 + ux * s, y1 + uy * s), (x1 + ux * e, y1 + uy * e)],
                  fill=color, width=width)
        s = e + gap


dren = data.get("drenagem") or {}
if dren:
    # cano Ø100 enterrado: tracejado fino em todo o percurso
    _dashed(tuple(dren["cano_px"][0]), tuple(dren["cano_px"][1]), DREN_COLOR, 3)
    # trecho sob o banheiro: tracejado mais espaçado + rótulo "subterrâneo"
    b0, b1 = tuple(dren["sob_banheiro_px"][0]), tuple(dren["sob_banheiro_px"][1])
    _dashed(b0, b1, DREN_COLOR, 5, dash=10, gap=16)
    bm = ((b0[0] + b1[0]) / 2, (b0[1] + b1[1]) / 2)
    draw.text((bm[0] + 12, bm[1] - 8), "sob o banheiro\n(subterrâneo)", font=F_REG,
              fill=DREN_COLOR)
    # canaleta aparente: linha grossa com "dentes" de grelha
    g0, g1 = tuple(dren["canaleta_px"][0]), tuple(dren["canaleta_px"][1])
    draw.line([g0, g1], fill=DREN_COLOR, width=9)
    n_teeth = 22
    for k in range(n_teeth + 1):
        gy = g0[1] + (g1[1] - g0[1]) * k / n_teeth
        gx = g0[0] + (g1[0] - g0[0]) * k / n_teeth
        draw.line([(gx - 9, gy), (gx + 9, gy)], fill=(20, 24, 30, 200), width=2)
    # caixa de inspeção
    cx_, cy_ = dren["caixa_px"]
    draw.rectangle([cx_ - 13, cy_ - 13, cx_ + 13, cy_ + 13],
                   fill=DREN_COLOR, outline=(255, 255, 255, 255), width=2)
    # rótulo principal: à ESQUERDA da canaleta, sobre o deck da piscina
    # (área vazia) — longe das terças T1/T2 que ficam logo a leste.
    (canal_x, cg0y), (_, cg1y) = dren["canaleta_px"]
    anchor_y = cg0y + (cg1y - cg0y) * 0.62       # trecho sul, sobre o deck
    txt = f"Canaleta c/ grelha +\ncano Ø{dren.get('diam_mm', 100)} mm (dren. pluvial)"
    tb = draw.textbbox((0, 0), txt, font=F_REG)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    lx = canal_x - tw - 34
    ly = anchor_y - th / 2
    draw.rectangle([lx - 6, ly - 5, lx + tw + 6, ly + th + 9], fill=(255, 255, 255, 235))
    draw.text((lx, ly), txt, font=F_REG, fill=DREN_COLOR)
    draw.line([(lx + tw + 8, anchor_y), (canal_x - 3, anchor_y)], fill=DREN_COLOR, width=2)
    draw.polygon([(canal_x - 3, anchor_y), (canal_x - 13, anchor_y - 5),
                  (canal_x - 13, anchor_y + 5)], fill=DREN_COLOR)

for p in data["pillars"]:
    draw_pillar_tag(p["px"][0], p["px"][1], p["index"])

# --- Legenda com nome e coordenadas de cada pilar ---------------------------
legend_x0, legend_y0 = W - 400, 40
legend_w = 370
line_h = 24
legend_h = 40 + line_h * len(data["pillars"])
draw.rounded_rectangle(
    [legend_x0, legend_y0, legend_x0 + legend_w, legend_y0 + legend_h],
    radius=10, fill=BOX_FILL, outline=BOX_OUTLINE, width=2,
)
draw.text((legend_x0 + 16, legend_y0 + 12), "Pilares de Eucalipto", font=F_BOLD, fill=(255, 255, 255, 255))
ty = legend_y0 + 40
for p in data["pillars"]:
    wx, wy = p["world"]
    r = 8
    cy = ty + 9
    draw.ellipse([legend_x0 + 16 - r, cy - r, legend_x0 + 16 + r, cy + r], fill=TAG_COLOR)
    txt = str(p["index"])
    bbox = draw.textbbox((0, 0), txt, font=F_TAG)
    draw.text((legend_x0 + 16 - (bbox[2] - bbox[0]) / 2 - bbox[0], cy - (bbox[3] - bbox[1]) / 2 - bbox[1]),
              txt, font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12), fill=TAG_TEXT)
    label = f"P{p['index']} — ({wx:.2f}, {wy:.2f})"
    draw.text((legend_x0 + 34, ty), label, font=F_REG, fill=(255, 255, 255, 255))
    ty += line_h

# --- Ficha técnica do piso do quiosque ---------------------------------------
info_x0, info_y0 = W - 400, legend_y0 + legend_h + 24
info_lines = [
    ("Piso do Quiosque", None),
    ("Piso principal", "4.00 x 10.50 m"),
    ("Ala (banheiros)", "~2.65 x 2.50 m (leste em P9-P6)"),
    ("Espessura do piso", f"{data.get('esp_piso', 0.10):.2f} m"),
    ("Nível do piso", "0.00 m (= deck da piscina)"),
    ("Topo dos pilares", f"{data.get('altura_pilar', 2.50):.2f} m"),
    ("Tora de eucalipto 12/14", f"{data.get('altura_tora', 2.00):.2f} m · Ø {data.get('diametro_pilar', 0.13):.2f} m"),
    ("Pedestal de concreto", f"Ø {data.get('diametro_pedestal', 0.30):.2f} m · +{data.get('altura_pedestal', 0.50):.2f} / -{data.get('prof_pedestal', 0.30):.2f} m"),
]
info_h = 40 + (line_h + 22) * (len(info_lines) - 1)
draw.rounded_rectangle(
    [info_x0, info_y0, info_x0 + legend_w, info_y0 + info_h],
    radius=10, fill=BOX_FILL, outline=BOX_OUTLINE, width=2,
)
draw.text((info_x0 + 16, info_y0 + 12), info_lines[0][0], font=F_BOLD, fill=(255, 255, 255, 255))
ty = info_y0 + 40
for label, value in info_lines[1:]:
    draw.text((info_x0 + 16, ty), f"{label}:", font=F_REG, fill=(210, 210, 210, 255))
    bbox = draw.textbbox((0, 0), f"{label}:", font=F_REG)
    draw.text((info_x0 + 16, ty + 20), value, font=F_BOLD, fill=(255, 255, 255, 255))
    ty += line_h + 22

# --- Esquadro de terças e vigas (numeração + comprimentos) -----------------
sched_x0 = W - 400
sched_y0 = info_y0 + info_h + 24
tercas = data.get("tercas", [])
transv = data.get("transversais", [])
sched_rows = len(tercas) + len(transv) + 2  # + 2 cabecalhos
sched_h = 44 + line_h * sched_rows
draw.rounded_rectangle(
    [sched_x0, sched_y0, sched_x0 + legend_w, sched_y0 + sched_h],
    radius=10, fill=BOX_FILL, outline=BOX_OUTLINE, width=2,
)
draw.text((sched_x0 + 16, sched_y0 + 12), "Terças (T) e Vigas (V) · 12/14",
          font=F_BOLD, fill=(255, 255, 255, 255))
ty = sched_y0 + 44
draw.ellipse([sched_x0 + 16 - 7, ty + 2, sched_x0 + 16 + 7, ty + 16], fill=TERCA_COLOR)
draw.text((sched_x0 + 34, ty), "Terças  ·  sentido Y  ·  L = comprim.", font=F_REG, fill=(210, 210, 210, 255))
ty += line_h
for t in tercas:
    draw.text((sched_x0 + 20, ty),
              f"{t['n']}   x = {t['x']:.2f} m     L = {t['comprimento']:.2f} m",
              font=F_REG, fill=(255, 255, 255, 255))
    ty += line_h
ty += 6
draw.ellipse([sched_x0 + 16 - 7, ty + 2, sched_x0 + 16 + 7, ty + 16], fill=VIGA_COLOR)
draw.text((sched_x0 + 34, ty), "Vigas transversais  ·  sentido X", font=F_REG, fill=(210, 210, 210, 255))
ty += line_h
for v in transv:
    draw.text((sched_x0 + 20, ty),
              f"{v['n']}  y={v['y']:.2f} m   L = {v['comprimento']:.2f} m",
              font=F_REG, fill=(255, 255, 255, 255))
    ty += line_h

# --- Título -------------------------------------------------------------
title = "Planta do Quiosque — Pilares, Terças e Distâncias"
draw.rectangle([0, 0, W, 44], fill=(20, 24, 30, 210))
draw.text((16, 8), title, font=F_TITLE, fill=(255, 255, 255, 255))

out_path = f"{BASE_DIR}/renders/planta_quiosque_anotada.png"
img.save(out_path)
print("PLAN_ANNOTATED_OK:", out_path)
