"""
Legenda 2D para as 6 imagens de renders/sol_*.png (gerado por
render_sun_study.py): data/hora, azimute e elevação solar reais, e rótulo
"N" (norte verdadeiro) na ponta da seta vermelha desenhada em cena.

Roda com python3 puro (sem Blender): python3 V1/annotate_sun_study.py
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/home/fac/piscina/V1"
RENDERS = os.path.join(BASE_DIR, "renders")

FONT_BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
FONT_REG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
FONT_N = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)

BOX_FILL = (15, 18, 24, 210)
BOX_OUTLINE = (255, 210, 60, 255)
TEXT_COLOR = (255, 255, 255, 255)

with open(os.path.join(RENDERS, "sun_study_meta.json"), "r", encoding="utf-8") as f:
    meta = json.load(f)

arrow_x, arrow_y = meta["arrow_tip_px"]

for cena in meta["cenas"]:
    path = os.path.join(RENDERS, cena["arquivo"])
    if not os.path.exists(path):
        print(f"AUSENTE: {path}")
        continue
    img = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    estacao_label = "VERAO (solsticio 21/dez)" if cena["estacao"] == "verao" else "INVERNO (solsticio 21/jun)"
    lines = [
        estacao_label,
        f"{cena['data']}  {cena['hora']}  (horario de Brasilia)",
        f"Azimute solar real: {cena['azimute_real_deg']:.1f}°   Elevacao: {cena['elevacao_deg']:.1f}°",
        f"Lat/Lon do terreno: {meta['lat']:.5f}, {meta['lon']:.5f}",
    ]
    pad = 16
    box_w = 620
    line_h = [40, 30, 30, 28]
    box_h = pad * 2 + sum(line_h)
    draw.rounded_rectangle([20, 20, 20 + box_w, 20 + box_h], radius=10, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    ty = 20 + pad
    for i, ln in enumerate(lines):
        font = FONT_BOLD if i == 0 else FONT_REG
        draw.text((20 + pad, ty), ln, font=font, fill=TEXT_COLOR)
        ty += line_h[i]

    r = 9
    draw.ellipse([arrow_x - r, arrow_y - r, arrow_x + r, arrow_y + r], outline=(255, 40, 40, 255), width=3)
    draw.text((arrow_x + 12, arrow_y - 20), "N", font=FONT_N, fill=(255, 60, 60, 255))

    out_path = os.path.join(RENDERS, cena["arquivo"].replace(".png", "_anotado.png"))
    img.save(out_path)
    print(f"OK: {out_path}")

print("ALLDONE_ANNOTATE_SUN")
