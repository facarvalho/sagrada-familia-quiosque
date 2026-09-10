"""
Projeto do TELHADO do quiosque — desenho 2D em escala (mesmo padrão de
render_piso_medidas.py), com as telhas posicionadas em tamanho real.

Telha: SANDUÍCHE TRAPEZOIDAL TÉRMICA, núcleo PIR 30 mm, aço 0,43 mm nas
duas faces, branco (tipo Kingspan Isotelha Trapezoidal / Isoeste).
Ficha (fabricante):
  - largura útil ......... 1,00 m  (largura total ~1,06 m; transpasse
                          lateral = 1 trapézio, já embutido na útil)
  - núcleo .............. PIR 30 mm  (poliisocianurato, autoextinguível)
  - peso ............... 9,69 kg/m²
  - inclinação mínima ... 6 %   (telhado do quiosque: 15 %  -> OK)
  - vão máx. entre terças 2,60 m
  - comprimento ......... sob medida, 1 a 8 m  -> peça única por água,
                          SEM emenda de topo (sem transpasse longitudinal)

Telhado: meia-água, caimento 15 % escoando para OESTE (x baixo = 0; a ala
fica ainda mais baixa, x = -2,95). Lado alto: leste - o telhado MORRE NA
TERÇA T3 (x = 4,0), sem beiral desse lado.

Saída: V1/renders/telhado_quiosque_medidas.png
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "renders", "telhado_quiosque_medidas.png")


def _font(bold, size):
    n = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{n}", size)


F_TITLE = _font(True, 32)
F_H = _font(True, 22)
F_DIM = _font(True, 22)
F_T = _font(False, 18)
F_TS = _font(False, 16)

# ----------------------------------------------------------------------
# Geometria do telhado (de projeto.py: _contorno_telhado)
# ----------------------------------------------------------------------
CAI = 0.15
K = math.sqrt(1.0 + CAI * CAI)          # fator rampa (comprimento inclinado)

EAST = 4.00         # borda leste do telhado = terça T3 (sem beiral)
A = (EAST, 12.50)   # NE (em T3)
B = (EAST, 1.10)    # SE (em T3)
C = (0.00, 1.10)    # SO (corpo)
D = (0.00, 8.80)    # canto reentrante do L
E = (-2.95, 8.80)   # SO da ala
F = (-2.95, 12.70)  # NO da ala
ROOF = [A, B, C, D, E, F]

# --- Campos de telhas: correm no sentido do caimento (X), útil 1,00 m em Y
UTIL = 1.00
# Campo Sul: y 1,10..8,80 (corpo, x 0..EAST)
SUL_Y0, SUL_Y1, SUL_X0, SUL_X1 = 1.10, 8.80, 0.00, EAST
# Campo Norte: y 8,80..12,70 (corpo + ala, x -2,95..EAST)
NOR_Y0, NOR_Y1, NOR_X0, NOR_X1 = 8.80, 12.70, -2.95, EAST


def _rows(y0, y1):
    rows, y = [], y0
    while y < y1 - 1e-6:
        rows.append((y, min(y + UTIL, y1)))
        y += UTIL
    return rows


SUL_ROWS = _rows(SUL_Y0, SUL_Y1)          # 8 telhas
NOR_ROWS = _rows(NOR_Y0, NOR_Y1)          # 4 telhas
L_SUL = (SUL_X1 - SUL_X0) * K             # comprimento na rampa
L_NOR = (NOR_X1 - NOR_X0) * K

n_sul, n_nor = len(SUL_ROWS), len(NOR_ROWS)
buy_sul = n_sul * UTIL * L_SUL
buy_nor = n_nor * UTIL * L_NOR
buy_total = buy_sul + buy_nor

# área do telhado (planta) via shoelace, e na rampa
sh = 0.0
for i in range(len(ROOF)):
    x1, y1 = ROOF[i]
    x2, y2 = ROOF[(i + 1) % len(ROOF)]
    sh += x1 * y2 - x2 * y1
area_planta = abs(sh) / 2.0
area_rampa = area_planta * K
perda = buy_total - area_rampa
peso = area_rampa * 9.69

# ----------------------------------------------------------------------
# Canvas
# ----------------------------------------------------------------------
WX0, WX1 = -2.95, EAST
WY0, WY1 = 1.10, 12.70
SCALE = 146
MARGIN = 205
PANEL = 660

plan_w = int((WX1 - WX0) * SCALE)
plan_h = int((WY1 - WY0) * SCALE)
GAP = 130                              # espaço p/ a cota "11,40 m" à direita do plano
W = MARGIN + plan_w + GAP + PANEL + 40
H = 80 + MARGIN + plan_h + MARGIN


def wx(x):
    return MARGIN + (x - WX0) * SCALE


def wy(y):
    return 80 + MARGIN + (WY1 - y) * SCALE


img = Image.new("RGB", (W, H), (250, 250, 248))
d = ImageDraw.Draw(img, "RGBA")

d.rectangle([0, 0, W, 60], fill=(20, 24, 30))
d.text((20, 12), "Projeto do Telhado — Telha Sanduíche Trapezoidal PIR 30 mm",
       font=F_TITLE, fill=(255, 255, 255))

BLUE = (30, 90, 170, 255)
GREEN = (35, 140, 90, 255)
ORANGE = (205, 105, 20, 255)
GUIDE = (120, 120, 120, 150)
BG = (250, 250, 248)
TILE_A = (150, 190, 225, 95)
TILE_B = (120, 170, 210, 95)
TILE_CUT = (150, 190, 225, 95)

# --- Telhas (retângulos em tamanho real, projeção horizontal) ----------
tile_no = 0


def draw_tile(x0, x1, y0, y1, idx, cut):
    fill = TILE_B if idx % 2 else TILE_A
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)], fill=fill, outline=(40, 90, 140), width=2)
    # nervuras trapezoidais (3 por telha), no sentido do caimento (X)
    wdt = y1 - y0
    for r in range(1, 4):
        ry = y0 + wdt * r / 4.0
        d.line([(wx(x0), wy(ry)), (wx(x1), wy(ry))], fill=(40, 90, 140, 70), width=1)
    if cut:
        for k in range(int((x1 - x0) / 0.35) + int((y1 - y0) / 0.35) + 2):
            xx = wx(x0) + k * 26
            d.line([(xx, wy(y1)), (xx - 40, wy(y0))], fill=(200, 60, 40, 90), width=2)
    cx, cy = (wx(x0) + wx(x1)) / 2, (wy(y0) + wy(y1)) / 2
    lab = f"{idx}"
    tb = d.textbbox((0, 0), lab, font=F_DIM)
    d.text((cx - (tb[2] - tb[0]) / 2, cy - (tb[3] - tb[1]) / 2 - 4), lab, font=F_DIM,
           fill=(20, 40, 70))


for (y0, y1) in SUL_ROWS:
    tile_no += 1
    draw_tile(SUL_X0, SUL_X1, y0, y1, tile_no, cut=(y1 - y0) < UTIL - 1e-6)
for (y0, y1) in NOR_ROWS:
    tile_no += 1
    draw_tile(NOR_X0, NOR_X1, y0, y1, tile_no, cut=(y1 - y0) < UTIL - 1e-6)

# --- Contorno do telhado por cima -------------------------------------
d.line([(wx(x), wy(y)) for (x, y) in ROOF] + [(wx(ROOF[0][0]), wy(ROOF[0][1]))],
       fill=(20, 24, 30), width=5)

# --- Terças (verde) + terça sugerida ---------------------------------
def terca(x, y0, y1, name, dashed=False):
    if dashed:
        yy = y0
        while yy < y1:
            d.line([(wx(x), wy(yy)), (wx(x), wy(min(yy + 0.25, y1)))], fill=GREEN, width=5)
            yy += 0.45
    else:
        d.line([(wx(x), wy(y0)), (wx(x), wy(y1))], fill=GREEN, width=6)
    d.ellipse([wx(x) - 15, wy(y1) + 6, wx(x) + 15, wy(y1) + 36], fill=GREEN,
              outline=(255, 255, 255), width=2)
    tb = d.textbbox((0, 0), name, font=F_TS)
    d.text((wx(x) - (tb[2] - tb[0]) / 2, wy(y1) + 21 - (tb[3] - tb[1]) / 2), name,
           font=F_TS, fill=(255, 255, 255))


terca(0.40, 1.10, 12.70, "T1")
terca(2.20, 1.10, 12.70, "T2")
terca(4.00, 1.10, 12.70, "T3")
terca(-2.25, 8.80, 12.70, "T4")
terca(-0.90, 8.80, 12.70, "T5", dashed=True)
d.text((wx(-0.90) - 60, wy(8.8) + 44), "T5 sugerida", font=F_TS, fill=GREEN)

# --- Seta do caimento ----------------------------------------------
for yy in (3.0, 6.5, 10.8):
    x_hi, x_lo = 3.8, 0.2 if yy < 8.8 else -2.7
    d.line([(wx(x_hi), wy(yy)), (wx(x_lo), wy(yy))], fill=ORANGE, width=3)
    d.polygon([(wx(x_lo), wy(yy)), (wx(x_lo) + 16, wy(yy) - 7),
               (wx(x_lo) + 16, wy(yy) + 7)], fill=ORANGE)
d.text((wx(2.0), wy(6.5) - 26), "caimento 15%  (escoa p/ oeste)", font=F_T, fill=ORANGE)


def _lab(mx, my, text, color):
    tb = d.textbbox((0, 0), text, font=F_DIM)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rectangle([mx - tw / 2 - 5, my - th / 2 - 5, mx + tw / 2 + 5, my + th / 2 + 7], fill=BG)
    d.text((mx - tw / 2 - tb[0], my - th / 2 - tb[1]), text, font=F_DIM, fill=color)


def dim_h(x0, x1, y, text, color=BLUE, above=True, depth=1):
    py = wy(y) + (-46 if above else 46) * depth
    d.line([(wx(x0), wy(y)), (wx(x0), py)], fill=GUIDE, width=1)
    d.line([(wx(x1), wy(y)), (wx(x1), py)], fill=GUIDE, width=1)
    d.line([(wx(x0), py), (wx(x1), py)], fill=color, width=3)
    d.polygon([(wx(x0), py), (wx(x0) + 10, py - 5), (wx(x0) + 10, py + 5)], fill=color)
    d.polygon([(wx(x1), py), (wx(x1) - 10, py - 5), (wx(x1) - 10, py + 5)], fill=color)
    _lab((wx(x0) + wx(x1)) / 2, py, text, color)


def dim_v(y0, y1, x, text, color=BLUE, right=True, depth=1):
    px = wx(x) + (46 if right else -46) * depth
    d.line([(wx(x), wy(y0)), (px, wy(y0))], fill=GUIDE, width=1)
    d.line([(wx(x), wy(y1)), (px, wy(y1))], fill=GUIDE, width=1)
    d.line([(px, wy(y0)), (px, wy(y1))], fill=color, width=3)
    d.polygon([(px, wy(y0)), (px - 5, wy(y0) - 10), (px + 5, wy(y0) - 10)], fill=color)
    d.polygon([(px, wy(y1)), (px - 5, wy(y1) + 10), (px + 5, wy(y1) + 10)], fill=color)
    _lab(px, (wy(y0) + wy(y1)) / 2, text, color)


# medidas gerais
dim_v(1.10, 12.50, EAST, "11,40 m", BLUE, right=True, depth=1)
dim_h(0.0, EAST, 1.10, f"{EAST:.2f} m (proj.)".replace('.', ','), BLUE, above=False, depth=1)
dim_h(-2.95, 0.0, 12.70, "2,95 m (proj.)", BLUE, above=True, depth=1)
dim_v(8.80, 12.70, -2.95, "3,90 m", BLUE, right=False, depth=1)
# vãos das terças (eixo em baixo) - o telhado morre em T3, sem beiral leste
for (xa, xb, tx) in [(0.0, 0.40, "0,40"), (0.40, 2.20, "1,80"),
                     (2.20, 4.00, "1,80")]:
    dim_h(xa, xb, 1.10, tx, GREEN, above=False, depth=2)
dim_h(-2.95, -2.25, 8.80, "0,70", GREEN, above=False, depth=1)
dim_h(-2.25, 0.40, 8.80, "2,65 !", (200, 40, 30, 255), above=False, depth=2)

# ----------------------------------------------------------------------
# Painel lateral (ficha + tabela)
# ----------------------------------------------------------------------
px0 = MARGIN + plan_w + GAP
py = 100
d.rectangle([px0, py, px0 + PANEL, H - 60], outline=(20, 24, 30), width=2, fill=(255, 255, 255))
tx = px0 + 20
py += 18


def line(txt, font=F_T, dy=26, color=(20, 24, 30)):
    global py
    d.text((tx, py), txt, font=font, fill=color)
    py += dy


line("TELHA  ·  ficha do fabricante", F_H, 34)
for s in ["Sanduíche trapezoidal, núcleo PIR 30 mm, aço 0,43 mm",
          "Largura útil 1,00 m  ·  peso 9,69 kg/m²",
          "Inclinação mín. 6%  (telhado: 15%  ->  OK)",
          "Vão máx. entre terças 2,60 m",
          "Comprimento sob medida  ->  peça única por água,",
          "   sem emenda de topo (sem transpasse longitudinal)"]:
    line(s, F_TS, 23)
py += 8

line("DISTRIBUIÇÃO DAS TELHAS", F_H, 34)
line("Correm no sentido do caimento (leste -> oeste).", F_TS, 24)
line("Largura útil 1,00 m no sentido norte-sul.", F_TS, 26)
# tabela
cols = [tx, tx + 150, tx + 250, tx + 430]
d.text((cols[0], py), "Campo", font=F_TS, fill=(90, 90, 90))
d.text((cols[1], py), "Nº", font=F_TS, fill=(90, 90, 90))
d.text((cols[2], py), "Comp. rampa", font=F_TS, fill=(90, 90, 90))
d.text((cols[3], py), "Detalhe", font=F_TS, fill=(90, 90, 90))
py += 24
rows = [
    ("Sul (corpo)", f"{n_sul}", f"{L_SUL:.2f} m".replace('.', ','),
     f"{n_sul-1}x1,00 + 1x{SUL_ROWS[-1][1]-SUL_ROWS[-1][0]:.2f}".replace('.', ',')),
    ("Norte (corpo+ala)", f"{n_nor}", f"{L_NOR:.2f} m".replace('.', ','),
     f"{n_nor-1}x1,00 + 1x{NOR_ROWS[-1][1]-NOR_ROWS[-1][0]:.2f}".replace('.', ',')),
]
for r in rows:
    for c, v in zip(cols, r):
        d.text((c, py), v, font=F_TS, fill=(20, 24, 30))
    py += 24
d.text((cols[0], py), "TOTAL", font=F_T, fill=(20, 24, 30))
d.text((cols[1], py), f"{n_sul + n_nor} telhas", font=F_T, fill=(20, 24, 30))
py += 34

line("METRAGEM", F_H, 34)
for s in [
    f"Telha a comprar (retangular): {buy_total:.2f} m²".replace('.', ','),
    f"   {n_sul} x {L_SUL:.2f} m  +  {n_nor} x {L_NOR:.2f} m".replace('.', ','),
    f"Área de cobertura (na rampa): {area_rampa:.2f} m²".replace('.', ','),
    f"Projeção horizontal: {area_planta:.2f} m²".replace('.', ','),
    f"Recorte / perda: {perda:.2f} m²  (~{100*perda/buy_total:.0f}%)".replace('.', ','),
    f"Peso total das telhas: {peso:.0f} kg".replace('.', ','),
]:
    line(s, F_TS, 24)
py += 8

line("TERÇAS  ·  apoio das telhas", F_H, 34)
for s in ["Corpo: beiral-T1-T2-T3 = 0,40 / 1,80 / 1,80 m  (T3 = borda leste)",
          "Ala: beiral-T4-T1 = 0,70 / 2,65 m",
          "   -> 2,65 m passa dos 2,60 m do fabricante:",
          "   acrescentar T5 em x = -0,90 (tracejada no desenho)"]:
    line(s, F_TS, 23, color=((200, 40, 30) if "2,65" in s or "T5" in s else (20, 24, 30)))
py += 8

line("COMPLEMENTOS", F_H, 34)
for s in [f"Rufo de testeira (lado alto = T3, leste): ~11,40 m",
          f"Rufos de empena: sul {L_SUL:.2f} + norte {L_NOR:.2f} + oeste ala 3,90 m".replace('.', ','),
          "Calha no beiral baixo (oeste): já existe",
          "Pingadeira no beiral baixo: ~11,50 m",
          "Fixação: ~120 parafusos 6,3 mm (terças)",
          "   + ~70 de costura 4,8 mm (transpasse lateral)"]:
    line(s, F_TS, 23)

img.save(OUT)
print("TELHADO_MEDIDAS_OK:", OUT)
