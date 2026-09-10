"""
Desenho técnico 2D do PISO do quiosque (planta em "L") + a CALÇADA de
concreto em volta, com as medidas. Não usa Blender — desenho vetorial PIL.

  - Cotas do PISO      -> azul
  - Cotas da CALÇADA   -> laranja

Saída: V1/renders/piso_quiosque_medidas.png

Geometria (projeto.py / calcadas.py):
  - Piso principal:  x 0..4,0 ; y 1,5..12,0     -> 4,00 x 10,50 m
  - Ala (banheiros): x -2,25..0,0 ; y 9,5..12,0 -> 2,25 x 2,50 m
  - Calçada nova: 0,50 m ao sul (P1-P2) + 1,00 m a oeste da ala e ao norte.
    O sul da ala não leva calçada nova (já é o piso da piscina existente).
  - Laje: 0,10 m de espessura ; topo em z = 0,00 (= deck da piscina)
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "renders", "piso_quiosque_medidas.png")


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


F_TITLE = _font(True, 34)
F_DIM = _font(True, 24)
F_NOTE = _font(False, 22)
F_SMALL = _font(False, 19)

# --- Geometria (coordenadas de mundo, metros) -----------------------------
OUTLINE = [
    (0.0, 1.5), (0.0, 9.5), (-2.25, 9.5), (-2.25, 12.0),
    (4.0, 12.0), (4.0, 1.5),
]
CALCADAS = [                       # (x0, x1, y0, y1) — calçada NOVA
    (0.0, 4.0, 1.0, 1.5),          # sul (P1-P2), 0,50 m
    (-3.25, -2.25, 9.5, 13.0),     # oeste da ala, 1,00 m (pega o canto NO)
    (-2.25, 4.0, 12.0, 13.0),      # norte (P6-P5 + canto), 1,00 m
]
# piso de concreto da piscina JÁ EXISTENTE, ao sul da ala (referência)
DECK_EXISTENTE = (-3.25, 0.0, 8.5, 9.5)

WX0, WX1 = -3.25, 4.0
WY0, WY1 = 1.0, 13.0

MARGIN = 210
SCALE = 135

world_w, world_h = WX1 - WX0, WY1 - WY0
W = int(world_w * SCALE) + 2 * MARGIN + 90
H = int(world_h * SCALE) + 2 * MARGIN + 80


def wx(x):
    return MARGIN + (x - WX0) * SCALE


def wy(y):
    return 80 + MARGIN + (WY1 - y) * SCALE


img = Image.new("RGB", (W, H), (250, 250, 248))
d = ImageDraw.Draw(img, "RGBA")

# --- Título -------------------------------------------------------------
d.rectangle([0, 0, W, 60], fill=(20, 24, 30))
d.text((20, 12), "Piso do Quiosque + Calçada — Medidas", font=F_TITLE, fill=(255, 255, 255))

BLUE = (30, 90, 170, 255)
ORANGE = (205, 105, 20, 255)
GUIDE = (120, 120, 120, 150)
BG = (250, 250, 248)

# --- Piso da piscina existente (ao sul da ala) — cinza tracejado ------
ex0, ex1, ey0, ey1 = DECK_EXISTENTE
d.rectangle([wx(ex0), wy(ey1), wx(ex1), wy(ey0)],
            fill=(200, 200, 198, 120), outline=(120, 120, 120), width=2)
for k in range(0, 40):
    xx = wx(ex0) + k * 14
    d.line([(xx, wy(ey1)), (xx - 40, wy(ey0))], fill=(120, 120, 120, 60), width=1)
d.text((wx(-1.7), wy(9.0) - 10), "piso da piscina", font=F_SMALL, fill=(90, 90, 90))
d.text((wx(-1.7) + 6, wy(9.0) + 12), "(existente)", font=F_SMALL, fill=(90, 90, 90))

# --- Calçada NOVA (fundo) -------------------------------------------
for x0, x1, y0, y1 in CALCADAS:
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)],
                fill=(210, 180, 140, 85), outline=(170, 120, 60), width=3)

# --- Laje do piso (por cima) ----------------------------------------
poly = [(wx(px), wy(py)) for px, py in OUTLINE]
d.polygon(poly, fill=(70, 130, 190, 70), outline=(30, 70, 130), width=4)
for gx in range(int(WX0 * 2), int(WX1 * 2) + 1):
    x = gx / 2.0
    d.line([(wx(x), wy(1.5)), (wx(x), wy(12.0))], fill=(30, 70, 130, 22), width=1)

# --- Drenagem pluvial: canaleta + cano Ø100, alinhada com a calha ----
DREN = (20, 145, 200, 255)
xd = -0.10
yd0, yd1, yb0, yb1 = 1.0, 13.3, 9.5, 12.0
py = wy(yd0)
while py > wy(yd1):                 # tracejado ao longo de y
    d.line([(wx(xd), py), (wx(xd), py - 13)], fill=DREN, width=4)
    py -= 22
# trecho sob o banheiro: faixa mais grossa + chave
d.line([(wx(xd), wy(yb0)), (wx(xd), wy(yb1))], fill=(20, 145, 200, 130), width=14)
ymid = (wy(yb0) + wy(yb1)) / 2
d.line([(wx(xd) + 9, wy(yb0)), (wx(xd) + 26, wy(yb0)),
        (wx(xd) + 26, wy(yb1)), (wx(xd) + 9, wy(yb1))], fill=DREN, width=2)
for i, s in enumerate(["cano Ø100 sob", "o banheiro", "(subterrâneo)"]):
    d.text((wx(xd) + 34, ymid - 30 + i * 22), s, font=F_SMALL, fill=DREN)
# caixa de inspeção ao norte
d.ellipse([wx(xd) - 10, wy(yd1) - 10, wx(xd) + 10, wy(yd1) + 10], fill=DREN,
          outline=(255, 255, 255), width=2)
d.text((wx(xd) + 16, wy(yd1) - 10), "caixa de inspeção", font=F_SMALL, fill=DREN)
# rótulo da canaleta aberta (trecho sul)
d.text((wx(xd) + 20, wy(4.0)), "canaleta c/ grelha", font=F_SMALL, fill=DREN)
d.text((wx(xd) + 20, wy(4.0) + 22), "no chão da piscina", font=F_SMALL, fill=DREN)
d.text((wx(xd) + 20, wy(4.0) + 44), "(alinhada c/ a calha)", font=F_SMALL, fill=DREN)


def _label(mx, my, text, color):
    tb = d.textbbox((0, 0), text, font=F_DIM)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rectangle([mx - tw / 2 - 6, my - th / 2 - 6, mx + tw / 2 + 6, my + th / 2 + 8], fill=BG)
    d.text((mx - tw / 2 - tb[0], my - th / 2 - tb[1]), text, font=F_DIM, fill=color)


def dim_h(x0, x1, y, text, color=BLUE, above=True, depth=1):
    off = (-52 if above else 52) * depth
    py = wy(y) + off
    d.line([(wx(x0), wy(y)), (wx(x0), py)], fill=GUIDE, width=1)
    d.line([(wx(x1), wy(y)), (wx(x1), py)], fill=GUIDE, width=1)
    d.line([(wx(x0), py), (wx(x1), py)], fill=color, width=3)
    d.polygon([(wx(x0), py), (wx(x0) + 11, py - 5), (wx(x0) + 11, py + 5)], fill=color)
    d.polygon([(wx(x1), py), (wx(x1) - 11, py - 5), (wx(x1) - 11, py + 5)], fill=color)
    _label((wx(x0) + wx(x1)) / 2, py, text, color)


def dim_v(y0, y1, x, text, color=BLUE, right=True, depth=1):
    off = (52 if right else -52) * depth
    px = wx(x) + off
    d.line([(wx(x), wy(y0)), (px, wy(y0))], fill=GUIDE, width=1)
    d.line([(wx(x), wy(y1)), (px, wy(y1))], fill=GUIDE, width=1)
    d.line([(px, wy(y0)), (px, wy(y1))], fill=color, width=3)
    d.polygon([(px, wy(y0)), (px - 5, wy(y0) - 11), (px + 5, wy(y0) - 11)], fill=color)
    d.polygon([(px, wy(y1)), (px - 5, wy(y1) + 11), (px + 5, wy(y1) + 11)], fill=color)
    _label(px, (wy(y0) + wy(y1)) / 2, text, color)


# --- Cotas do PISO (azul) --------------------------------------------
dim_h(0.0, 4.0, 1.5, "4,00 m", BLUE, above=False, depth=1)
dim_h(-2.25, 4.0, 1.5, "6,25 m", BLUE, above=False, depth=2)
dim_v(1.5, 12.0, 4.0, "10,50 m", BLUE, right=True, depth=1)
dim_h(-2.25, 0.0, 12.0, "2,25 m", BLUE, above=True, depth=1)
dim_v(9.5, 12.0, -2.25, "2,50 m", BLUE, right=False, depth=1)

# --- Cotas da CALÇADA nova (laranja) -------------------------------
dim_v(1.0, 1.5, 4.0, "0,50 m", ORANGE, right=True, depth=2)       # faixa sul
dim_v(12.0, 13.0, 4.0, "1,00 m", ORANGE, right=True, depth=2)     # faixa norte
dim_h(-3.25, -2.25, 9.5, "1,00 m", ORANGE, above=False, depth=1)  # faixa oeste da ala
dim_h(-3.25, 4.0, 1.0, "7,25 m", ORANGE, above=False, depth=3)    # envelope (larg.)
dim_v(1.0, 13.0, 4.0, "12,00 m", ORANGE, right=True, depth=3)     # envelope (compr.)

# --- Rótulos internos ----------------------------------------------
d.text((wx(2.0) - 70, wy(6.7)), "PISO PRINCIPAL", font=F_NOTE, fill=(30, 60, 110))
d.text((wx(2.0) - 45, wy(6.7) + 28), "42,00 m²", font=F_SMALL, fill=(30, 60, 110))
d.text((wx(-1.13) - 62, wy(10.75) - 10), "ALA / BANHEIROS", font=F_SMALL, fill=(30, 60, 110))
d.text((wx(-1.13) - 32, wy(10.75) + 14), "5,63 m²", font=F_SMALL, fill=(30, 60, 110))
d.text((wx(1.6), wy(12.5) - 12), "CALÇADA", font=F_SMALL, fill=(150, 90, 30))

# --- Ficha + legenda (área livre a sudoeste, sem invadir o piso) -----
F_FICHA = _font(False, 17)
fx0, fy0 = wx(-3.25) + 6, wy(7.9)
d.rectangle([fx0, fy0, fx0 + 424, fy0 + 262], outline=(20, 24, 30), width=2, fill=(255, 255, 255))
d.text((fx0 + 12, fy0 + 10), "FICHA", font=F_NOTE, fill=(20, 24, 30))
d.rectangle([fx0 + 12, fy0 + 48, fx0 + 30, fy0 + 66], fill=(70, 130, 190, 160), outline=(30, 70, 130))
d.text((fx0 + 40, fy0 + 45), "Piso (azul) — L, 47,63 m²", font=F_FICHA, fill=(20, 24, 30))
d.rectangle([fx0 + 12, fy0 + 74, fx0 + 30, fy0 + 92], fill=(210, 180, 140, 160), outline=(170, 120, 60))
d.text((fx0 + 40, fy0 + 71), "Calçada nova (laranja) — 11,75 m²", font=F_FICHA, fill=(20, 24, 30))
for i, line in enumerate([
    "Espessura da laje: 0,10 m",
    "Nível do topo: 0,00 m (= deck da piscina)",
    "Calçada nova: 0,50 m (sul) + 1,00 m (oeste ala",
    "   + norte)",
    "Sul da ala: já é o piso da piscina existente",
    "Envelope piso + calçada: 7,25 x 12,00 m",
]):
    d.text((fx0 + 12, fy0 + 112 + i * 25), line, font=F_FICHA, fill=(20, 24, 30))

img.save(OUT)
print("PISO_MEDIDAS_OK:", OUT)
