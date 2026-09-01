import json
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/home/fac/piscina"
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

for p in data["pillars"]:
    draw_pillar_tag(p["px"][0], p["px"][1], p["index"])

# --- Legenda com nome e coordenadas de cada pilar ---------------------------
legend_x0, legend_y0 = W - 330, 40
legend_w = 300
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
info_x0, info_y0 = W - 330, legend_y0 + legend_h + 24
info_lines = [
    ("Piso do Quiosque", None),
    ("Piso principal", "4.00 x 12.00 m"),
    ("Ala (banheiros)", "2.25 x 2.50 m"),
    ("Espessura do piso", f"{data.get('altura_piso', 0.10):.2f} m"),
    ("Nível", "0.00 m (nivel_quiosque)"),
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

# --- Título -------------------------------------------------------------
title = "Planta do Quiosque — Pilares e Distâncias"
draw.rectangle([0, 0, W, 44], fill=(20, 24, 30, 210))
draw.text((16, 8), title, font=F_TITLE, fill=(255, 255, 255, 255))

out_path = f"{BASE_DIR}/renders/planta_quiosque_anotada.png"
img.save(out_path)
print("PLAN_ANNOTATED_OK:", out_path)
