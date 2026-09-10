"""
Planta técnica 2D dos BANHEIROS da ala (mesmo padrão de render_piso_medidas.py
e render_telhado_medidas.py). Não usa Blender — desenho vetorial PIL.

Geometria (bathroom.py, derivada de projeto.py):
  - Ala entre P6-P7-P8-P9. Footprint interno: x -2,20..0,40 ; y 9,60..11,90
  - Parede central em x = -0,90 (duchas a oeste | sanitários a leste)
  - Divisão de fileira em y = 10,75 (cabine sul | cabine norte)
  - 4 cabines: 2 duchas quentes (porta a OESTE, p/ a piscina) +
    2 sanitários só com vaso (porta a LESTE, p/ o corredor). Portas 0,60 m.
  - Piso = CAIXA DE BRITA (tabuleiro rebaixado ~14 cm, brita ~1 cm abaixo do
    piso, contida por meio-fio de ~9 cm).
  - PIA COMUNITÁRIA rústica de 1,80 m na face sul da parede P8-P9, 3 bicas.

Saída: V1/renders/banheiro_planta_medidas.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "renders", "banheiro_planta_medidas.png")


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


F_TITLE = _font(True, 32)
F_DIM = _font(True, 22)
F_NOTE = _font(True, 20)
F_SMALL = _font(False, 18)
F_TINY = _font(False, 16)

# --- Geometria (coordenadas de mundo, metros) ---------------------------
WT = 0.08
X0, X1 = -2.20, 0.40
Y0, Y1 = 9.60, 11.90
XM = (X0 + X1) / 2.0        # -0,90
YM = (Y0 + Y1) / 2.0        # 10,75
DOOR_W = 0.60
# eixo dos pilares da ala
PIL = [(-2.25, 12.0), (-2.25, 9.5), (0.40, 9.5), (0.40, 12.0)]

WX0, WX1 = -2.95, 1.15
WY0, WY1 = 8.75, 12.55
MARGIN = 200
SCALE = 210

world_w, world_h = WX1 - WX0, WY1 - WY0
W = int(world_w * SCALE) + 2 * MARGIN + 380
H = int(world_h * SCALE) + 2 * MARGIN + 40


def wx(x):
    return MARGIN + (x - WX0) * SCALE


def wy(y):
    return 70 + MARGIN + (WY1 - y) * SCALE


img = Image.new("RGB", (W, H), (250, 250, 248))
d = ImageDraw.Draw(img, "RGBA")

d.rectangle([0, 0, W, 58], fill=(20, 24, 30))
d.text((20, 11), "Banheiros da Ala — Planta e Medidas", font=F_TITLE, fill=(255, 255, 255))

BLUE = (30, 90, 170, 255)
ORANGE = (205, 105, 20, 255)
GREEN = (25, 130, 60, 255)
GUIDE = (120, 120, 120, 150)
BG = (250, 250, 248)
GRAVEL = (150, 140, 120, 255)

# --- Caixa de brita (piso das 4 cabines) --------------------------------
_bx0, _bx1 = wx(X0 + WT / 2), wx(X1 - WT / 2)
_by0, _by1 = wy(Y1 - WT / 2), wy(Y0 + WT / 2)
d.rectangle([_bx0, _by0, _bx1, _by1], fill=(150, 140, 120, 90))
_brita = Image.new("RGBA", (int(_bx1 - _bx0), int(_by1 - _by0)), (0, 0, 0, 0))
_bd = ImageDraw.Draw(_brita)
for k in range(-20, 80):
    xx = k * 12
    _bd.line([(xx, _by1 - _by0), (xx + (_by1 - _by0) * 0.5, 0)], fill=(120, 110, 95, 70), width=1)
img.paste(_brita, (int(_bx0), int(_by0)), _brita)

# --- Paredes (muro tendinoso, ~8 cm) -----------------------------------
def wall_rect(x0, x1, y0, y1):
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)], fill=(90, 85, 78, 255))

wall_rect(X0 - WT / 2, X1 + WT / 2, Y1 - WT / 2, Y1 + WT / 2)   # norte
wall_rect(X0 - WT / 2, X1 + WT / 2, Y0 - WT / 2, Y0 + WT / 2)   # sul (P8-P9)
wall_rect(X0 - WT / 2, X0 + WT / 2, Y0 - WT / 2, Y1 + WT / 2)   # oeste
wall_rect(X1 - WT / 2, X1 + WT / 2, Y0 - WT / 2, Y1 + WT / 2)   # leste
wall_rect(XM - WT / 2, XM + WT / 2, Y0, Y1)                     # central
wall_rect(X0, XM, YM - WT / 2, YM + WT / 2)                     # partição duchas
wall_rect(XM, X1, YM - WT / 2, YM + WT / 2)                     # partição lavabos

# --- Vãos de porta (recorte branco na parede) + folha 0,60 m ----------
def door_x(x_fixed, yc, swing_out):
    # recorte do vão na parede
    d.rectangle([wx(x_fixed) - 7, wy(yc + DOOR_W / 2), wx(x_fixed) + 7, wy(yc - DOOR_W / 2)],
                fill=BG)
    # folha da porta aberta ~90° (para fora)
    px = wx(x_fixed) + swing_out * (wx(DOOR_W) - wx(0.0))
    d.line([(wx(x_fixed), wy(yc + DOOR_W / 2)), (px, wy(yc + DOOR_W / 2))],
           fill=(150, 90, 40), width=4)
    # arco de varredura
    r = wx(DOOR_W) - wx(0.0)
    bx0, bx1 = wx(x_fixed) - r, wx(x_fixed) + r
    by0, by1 = wy(yc + DOOR_W / 2) - r, wy(yc + DOOR_W / 2) + r
    a0, a1 = (270, 360) if swing_out > 0 else (180, 270)
    d.arc([bx0, by0, bx1, by1], start=a0, end=a1, fill=(150, 90, 40, 90), width=1)


D1y = (Y0 + YM) / 2.0
D2y = (YM + Y1) / 2.0
door_x(X0, D1y, -1)   # ducha 1 - porta oeste
door_x(X0, D2y, -1)   # ducha 2 - porta oeste
door_x(X1, D1y, +1)   # sanitário 1 - porta leste
door_x(X1, D2y, +1)   # sanitário 2 - porta leste

# --- Meio-fio da caixa de brita (linha interna verde) -----------------
mf = 0.06
d.rectangle([wx(X0 + WT / 2 + mf), wy(Y1 - WT / 2 - mf),
             wx(X1 - WT / 2 - mf), wy(Y0 + WT / 2 + mf)],
            outline=(25, 130, 60, 200), width=3)

# --- Louças ----------------------------------------------------------
def box(x0, x1, y0, y1, col):
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)], fill=col, outline=(60, 60, 60), width=2)

for cy in (D1y, D2y):
    # duchas: base + coluna junto da parede central
    box(XM - WT / 2 - 0.70, XM - WT / 2, cy - 0.50, cy + 0.50, (210, 225, 235, 220))
    d.ellipse([wx(XM - WT / 2 - 0.10) - 5, wy(cy) - 5, wx(XM - WT / 2 - 0.10) + 5, wy(cy) + 5],
              fill=(120, 130, 140))
    # sanitários: vaso encostado na parede central
    box(XM + WT / 2, XM + WT / 2 + 0.20, cy - 0.19, cy + 0.19, (235, 235, 232, 230))
    d.ellipse([wx(XM + WT / 2 + 0.18), wy(cy + 0.20), wx(XM + WT / 2 + 0.62), wy(cy - 0.20)],
              fill=(235, 235, 232, 230), outline=(60, 60, 60), width=2)

# --- Pia comunitária (face sul da parede P8-P9) ----------------------
pia_len = 1.80
pia_cx = (X0 + X1) / 2.0
d.rectangle([wx(pia_cx - pia_len / 2), wy(Y0 - WT / 2),
             wx(pia_cx + pia_len / 2), wy(Y0 - WT / 2 - 0.44)],
            fill=(150, 120, 95, 230), outline=(70, 55, 40), width=2)
d.rectangle([wx(pia_cx - pia_len / 2 + 0.17), wy(Y0 - WT / 2 - 0.07),
             wx(pia_cx + pia_len / 2 - 0.17), wy(Y0 - WT / 2 - 0.37)],
            fill=(90, 90, 88, 230))
for k in range(3):
    tx = pia_cx + (k - 1) * (pia_len / 3.0)
    d.ellipse([wx(tx) - 4, wy(Y0 - WT / 2) - 4, wx(tx) + 4, wy(Y0 - WT / 2) + 4],
              fill=(120, 130, 140))

# --- Eixos dos pilares ----------------------------------------------
for px, py in PIL:
    d.line([(wx(px) - 13, wy(py)), (wx(px) + 13, wy(py))], fill=(180, 40, 40), width=2)
    d.line([(wx(px), wy(py) - 13), (wx(px), wy(py) + 13)], fill=(180, 40, 40), width=2)

# --- Cotas ---------------------------------------------------------
def _label(mx, my, text, color, font=F_DIM):
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rectangle([mx - tw / 2 - 5, my - th / 2 - 5, mx + tw / 2 + 5, my + th / 2 + 7], fill=BG)
    d.text((mx - tw / 2 - tb[0], my - th / 2 - tb[1]), text, font=font, fill=color)


def dim_h(x0, x1, y, text, color=BLUE, above=True, depth=1):
    off = (-46 if above else 46) * depth
    py = wy(y) + off
    d.line([(wx(x0), wy(y)), (wx(x0), py)], fill=GUIDE, width=1)
    d.line([(wx(x1), wy(y)), (wx(x1), py)], fill=GUIDE, width=1)
    d.line([(wx(x0), py), (wx(x1), py)], fill=color, width=3)
    d.polygon([(wx(x0), py), (wx(x0) + 10, py - 5), (wx(x0) + 10, py + 5)], fill=color)
    d.polygon([(wx(x1), py), (wx(x1) - 10, py - 5), (wx(x1) - 10, py + 5)], fill=color)
    _label((wx(x0) + wx(x1)) / 2, py, text, color)


def dim_v(y0, y1, x, text, color=BLUE, right=True, depth=1):
    off = (46 if right else -46) * depth
    px = wx(x) + off
    d.line([(wx(x), wy(y0)), (px, wy(y0))], fill=GUIDE, width=1)
    d.line([(wx(x), wy(y1)), (px, wy(y1))], fill=GUIDE, width=1)
    d.line([(px, wy(y0)), (px, wy(y1))], fill=color, width=3)
    d.polygon([(px, wy(y0)), (px - 5, wy(y0) - 10), (px + 5, wy(y0) - 10)], fill=color)
    d.polygon([(px, wy(y1)), (px - 5, wy(y1) + 10), (px + 5, wy(y1) + 10)], fill=color)
    _label(px, (wy(y0) + wy(y1)) / 2, text, color)


# larguras (X)
dim_h(X0, XM, Y1 + WT / 2, "1,30 m", BLUE, above=True, depth=1)
dim_h(XM, X1, Y1 + WT / 2, "1,30 m", BLUE, above=True, depth=1)
dim_h(X0 - WT / 2, X1 + WT / 2, Y1 + WT / 2, "2,68 m (ext.)", BLUE, above=True, depth=2)
dim_h(-2.25, 0.40, 9.5, "2,65 m (eixo P8-P9)", (120, 120, 120, 255),
      above=False, depth=5)
# profundidades (Y)
dim_v(Y0, YM, X1 + WT / 2, "1,15", BLUE, right=True, depth=1)
dim_v(YM, Y1, X1 + WT / 2, "1,15", BLUE, right=True, depth=1)
dim_v(Y0 - WT / 2, Y1 + WT / 2, X1 + WT / 2, "2,38 m", BLUE, right=True, depth=2)
dim_v(9.5, 12.0, -2.25, "2,50 m", (120, 120, 120, 255), right=False, depth=2)
# portas
dim_v(D2y - DOOR_W / 2, D2y + DOOR_W / 2, X0 - WT / 2, "0,60", ORANGE, right=False, depth=1)
d.text((wx(X0) - 168, wy(D1y) - 8), "portas 0,60 x 1,90 m", font=F_TINY, fill=ORANGE)
# pia
dim_h(pia_cx - pia_len / 2, pia_cx + pia_len / 2, Y0 - WT / 2 - 0.44, "1,80 m",
      ORANGE, above=False, depth=2)

# --- Rótulos das cabines ------------------------------------------
def _cap(cx, cy, l1, l2):
    _label(wx(cx), wy(cy) - 12, l1, (30, 60, 110), F_NOTE)
    _label(wx(cx), wy(cy) + 12, l2, (90, 90, 90), F_TINY)

_cap((X0 + XM) / 2, D1y, "DUCHA 1", "quente")
_cap((X0 + XM) / 2, D2y, "DUCHA 2", "quente")
_cap((XM + X1) / 2, D1y, "SANIT. 1", "só vaso")
_cap((XM + X1) / 2, D2y, "SANIT. 2", "só vaso")
_label(wx(pia_cx), wy(Y0 - WT / 2 - 0.22), "PIA COMUNITÁRIA", (150, 90, 30), F_TINY)

# --- Ficha lateral ----------------------------------------------
fx0 = wx(WX1) + 40
fy0 = wy(WY1) + 10
d.rectangle([fx0, fy0, fx0 + 372, fy0 + 510], outline=(20, 24, 30), width=2, fill=(255, 255, 255))
d.text((fx0 + 14, fy0 + 12), "FICHA", font=F_NOTE, fill=(20, 24, 30))
lines = [
    "Módulo (ala P6-P9): 2,65 x 2,50 m",
    "4 cabines: 2 duchas quentes + 2 sanitários",
    "Cabine (livre): 1,30 x 1,15 m",
    "Parede central em x = -0,90 m",
    "",
    "Portas: 0,60 x 1,90 m (4 un.)",
    "  duchas abrem p/ a piscina (Oeste)",
    "  sanitários abrem p/ o corredor (Leste)",
    "",
    "Paredes: muro tendinoso ~8 cm, h 2,50 m",
    "  (respiro sob o telhado inclinado)",
    "",
    "PISO — CAIXA DE BRITA:",
    "  tabuleiro rebaixado ~0,14 m",
    "  topo da brita ~0,01 m abaixo do piso",
    "  meio-fio (verde) ~0,09 m acima do piso",
    "  contém a brita nas soleiras das portas",
    "",
    "Sanitários: só o vaso (sem pia na cabine)",
    "Lava-mãos: pia comunitária 1,80 m, 3 bicas,",
    "  na face sul da parede P8-P9",
]
for i, ln in enumerate(lines):
    d.text((fx0 + 14, fy0 + 44 + i * 18), ln, font=F_TINY,
           fill=(20, 24, 30) if ln[:2].strip() and not ln.startswith("  ") else (60, 60, 60))

# legenda de cores
lg = fy0 + 44 + len(lines) * 18 + 16
d.rectangle([fx0 + 14, lg, fx0 + 30, lg + 14], fill=(150, 140, 120, 160))
d.text((fx0 + 38, lg - 2), "brita solta", font=F_TINY, fill=(20, 24, 30))
d.rectangle([fx0 + 14, lg + 22, fx0 + 30, lg + 36], fill=(90, 85, 78))
d.text((fx0 + 38, lg + 20), "parede (muro tendinoso)", font=F_TINY, fill=(20, 24, 30))
d.line([(fx0 + 14, lg + 46), (fx0 + 30, lg + 46)], fill=(25, 130, 60), width=3)
d.text((fx0 + 38, lg + 39), "meio-fio da caixa de brita", font=F_TINY, fill=(20, 24, 30))

img.save(OUT)
print("BANHEIRO_MEDIDAS_OK:", OUT)
