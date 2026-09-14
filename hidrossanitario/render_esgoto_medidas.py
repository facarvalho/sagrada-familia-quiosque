"""
Planta técnica 2D da REDE HIDROSSANITÁRIA do quiosque (mesmo padrão de
render_piso_medidas.py / render_banheiro_medidas.py). Não usa Blender —
desenho vetorial PIL.

Cobre o sistema SANITÁRIO (água fria + esgoto -> fossa + sumidouro), que é
NOVO e ainda não existe em nenhum módulo Blender do projeto — separado da
drenagem PLUVIAL (calha/canaleta/cano Ø100 já modelados em calcadas.py e
desenhados em render_piso_medidas.py).

Pontos de consumo/esgoto (coordenadas derivadas de bathroom.py / counter.py):
  - Ducha 1 (-1,29 ; 10,175)   Ducha 2 (-1,29 ; 11,325)
  - Sanit. 1 (-0,59 ; 10,175)  Sanit. 2 (-0,59 ; 11,325)   [vaso, caixa acoplada]
  - Pia comunitária (-0,90 ; 9,32)
  - Pia da bancada (3,675 ; 2,65)

Fossa séptica biodigestora 1.300 L + sumidouro: posição esquemática ao
norte da Calçada Norte (y > 13,0) — local definitivo a medir em campo.

Saída: renders/esgoto_quiosque_medidas.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "..", "renders", "esgoto_quiosque_medidas.png")


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


F_TITLE = _font(True, 34)
F_DIM = _font(True, 22)
F_NOTE = _font(True, 20)
F_SMALL = _font(False, 18)
F_TINY = _font(False, 16)

# --- Geometria base (projeto.py / calcadas.py / bathroom.py / counter.py) --
PISO_OUTLINE = [
    (0.0, 1.5), (0.0, 9.5), (-2.25, 9.5), (-2.25, 12.0),
    (4.0, 12.0), (4.0, 1.5),
]
CALCADAS = [
    (0.0, 4.0, 1.0, 1.5),
    (-3.25, -2.25, 9.5, 13.0),
    (-2.25, 4.0, 12.0, 13.0),
]
DECK_EXISTENTE = (-3.25, 0.0, 8.5, 9.5)

# ala (banheiro)
WT = 0.08
BX0, BX1 = -2.20, 0.40
BY0, BY1 = 9.60, 11.90
BXM = (BX0 + BX1) / 2.0
BYM = (BY0 + BY1) / 2.0
D1Y = (BY0 + BYM) / 2.0
D2Y = (BYM + BY1) / 2.0

# pontos de consumo / esgoto
DUCHA_X = BXM - WT / 2.0 - 0.35
VASO_X = BXM + WT / 2.0 + 0.27
PIA_COM = (-0.90, 9.32)
PIA_BAN = (3.675, 2.65)

# fossa/sumidouro (posição esquemática)
FOSSA = (1.0, 14.2)
FOSSA_W, FOSSA_H = 1.2, 0.7
SUMIDOURO = (1.0, 15.7)
SUM_R = 0.75
CAIXA_SANIT = (1.0, 13.6)     # inspeção antes da fossa (só vasos)
CAIXA_CINZA = (-1.29, 13.6)   # inspeção da água servida (duchas + pia comunitária)

# represa: destino da água servida (duchas + pia comunitária) — posição
# esquemática, fora do terreno mapeado; local real e distância a definir.
REPRESA = (-3.5, 15.1)
REP_R = 0.85

WX0, WX1 = -4.5, 4.3
WY0, WY1 = 8.9, 16.6
MARGIN = 210
SCALE = 120

world_w, world_h = WX1 - WX0, WY1 - WY0
W = int(world_w * SCALE) + 2 * MARGIN + 380
H = int(world_h * SCALE) + 2 * MARGIN + 40


def wx(x):
    return MARGIN + (x - WX0) * SCALE


def wy(y):
    return 25 + MARGIN + (WY1 - y) * SCALE


img = Image.new("RGB", (W, H), (250, 250, 248))
d = ImageDraw.Draw(img, "RGBA")

d.rectangle([0, 0, W, 60], fill=(20, 24, 30))
d.text((20, 13), "Rede Hidrossanitária — Planta Esquemática", font=F_TITLE, fill=(255, 255, 255))

BLUE = (30, 90, 170, 255)       # água fria
BROWN = (150, 90, 40, 255)      # esgoto sanitário (vasos -> fossa)
GREY = (10, 140, 130, 255)      # água servida (duchas + pia comunitária -> represa)
GREEN = (60, 130, 70, 255)      # fossa / sumidouro
GUIDE = (120, 120, 120, 150)
BG = (250, 250, 248)

# --- Contexto: piso da piscina existente ---------------------------------
ex0, ex1, ey0, ey1 = DECK_EXISTENTE
d.rectangle([wx(ex0), wy(ey1), wx(ex1), wy(ey0)], fill=(200, 200, 198, 90), outline=(150, 150, 148), width=1)

# --- Contexto: calçadas + piso do quiosque (fundo neutro) ----------------
for x0, x1, y0, y1 in CALCADAS:
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)], fill=(210, 180, 140, 55), outline=(190, 150, 100), width=1)
poly = [(wx(px), wy(py)) for px, py in PISO_OUTLINE]
d.polygon(poly, fill=(150, 150, 145, 40), outline=(120, 120, 115), width=2)

# --- Contexto: paredes da ala (muro tendinoso) ---------------------------
def wall_rect(x0, x1, y0, y1):
    d.rectangle([wx(x0), wy(y1), wx(x1), wy(y0)], fill=(150, 145, 135, 140))

wall_rect(BX0 - WT / 2, BX1 + WT / 2, BY1 - WT / 2, BY1 + WT / 2)
wall_rect(BX0 - WT / 2, BX1 + WT / 2, BY0 - WT / 2, BY0 + WT / 2)
wall_rect(BX0 - WT / 2, BX0 + WT / 2, BY0 - WT / 2, BY1 + WT / 2)
wall_rect(BX1 - WT / 2, BX1 + WT / 2, BY0 - WT / 2, BY1 + WT / 2)
wall_rect(BXM - WT / 2, BXM + WT / 2, BY0, BY1)
wall_rect(BX0, BXM, BYM - WT / 2, BYM + WT / 2)
wall_rect(BXM, BX1, BYM - WT / 2, BYM + WT / 2)

# --- Pilares (referência, pontos vermelhos) -------------------------------
PILARES = [(0.4, 1.5), (4.0, 1.5), (4.0, 5.5), (4.0, 9.5), (4.0, 12.0),
           (0.4, 12.0), (-2.25, 12.0), (-2.25, 9.5), (0.4, 9.5), (0.4, 5.5)]
for px_, py_ in PILARES:
    d.ellipse([wx(px_) - 4, wy(py_) - 4, wx(px_) + 4, wy(py_) + 4], fill=(180, 40, 40, 200))


# --- Roteamento das tubulações (esquemático, ortogonal) -------------------
def pline(pts, color, width):
    for i in range(len(pts) - 1):
        d.line([(wx(pts[i][0]), wy(pts[i][1])), (wx(pts[i + 1][0]), wy(pts[i + 1][1]))],
               fill=color, width=width)


TRUNK_Y = 13.6
# colunas ligeiramente deslocadas da posição real do ponto (±0,06 m) para a
# linha de água fria e a de esgoto/água servida não correrem exatamente
# sobrepostas (senão uma "engole" visualmente a outra).
X_DUCHA_AG, X_DUCHA_CZ = DUCHA_X - 0.06, DUCHA_X + 0.06
X_VASO_AG, X_VASO_ES = VASO_X - 0.06, VASO_X + 0.06
X_PIA_AG, X_PIA_CZ = PIA_COM[0] - 0.06, PIA_COM[0] + 0.06

# --- água fria: ramal principal ao longo de y=13,6 ------------------------
agua_trunk = [(X_DUCHA_AG, TRUNK_Y), (3.675, TRUNK_Y)]
pline(agua_trunk, BLUE, 5)
agua_ramais = [
    [(X_DUCHA_AG, TRUNK_Y), (X_DUCHA_AG, D1Y)],
    [(X_DUCHA_AG, D2Y), (X_DUCHA_AG, TRUNK_Y)],
    [(X_VASO_AG, TRUNK_Y), (X_VASO_AG, D1Y)],
    [(X_VASO_AG, D2Y), (X_VASO_AG, TRUNK_Y)],
    [(X_PIA_AG, TRUNK_Y), (X_PIA_AG, PIA_COM[1]), (PIA_COM[0], PIA_COM[1])],
]
for r in agua_ramais:
    pline(r, BLUE, 3)
d.line([(wx(X_DUCHA_AG), wy(TRUNK_Y) - 14), (wx(X_DUCHA_AG), wy(TRUNK_Y))], fill=BLUE, width=3)
d.polygon([(wx(X_DUCHA_AG) - 8, wy(TRUNK_Y) - 14), (wx(X_DUCHA_AG) + 8, wy(TRUNK_Y) - 14), (wx(X_DUCHA_AG), wy(TRUNK_Y) - 30)],
          fill=BLUE)
d.text((wx(X_DUCHA_AG) - 62, wy(TRUNK_Y) - 52), "entrada de água\n(ponto a definir)", font=F_TINY, fill=BLUE)

# --- esgoto SANITÁRIO: só os 2 vasos -> fossa -----------------------------
esg_coletor = [(X_VASO_ES, TRUNK_Y), CAIXA_SANIT, FOSSA]
pline(esg_coletor, BROWN, 6)
esg_ramais = [
    [(X_VASO_ES, D1Y), (X_VASO_ES, TRUNK_Y)],
    [(X_VASO_ES, D2Y), (X_VASO_ES, TRUNK_Y)],
]
for r in esg_ramais:
    pline(r, BROWN, 3)
pline([FOSSA, SUMIDOURO], GREEN, 6)

# --- água servida (greywater): duchas + pia comunitária -> represa --------
# NÃO passa pela fossa — vaso é o único ponto que vai para lá.
cinza_coletor = [(X_DUCHA_CZ, TRUNK_Y), CAIXA_CINZA, (REPRESA[0], TRUNK_Y), REPRESA]
pline(cinza_coletor, GREY, 6)
cinza_ramais = [
    [(X_DUCHA_CZ, D1Y), (X_DUCHA_CZ, TRUNK_Y)],
    [(X_DUCHA_CZ, D2Y), (X_DUCHA_CZ, TRUNK_Y)],
    [(X_PIA_CZ, PIA_COM[1]), (X_PIA_CZ, TRUNK_Y), CAIXA_CINZA],
]
for r in cinza_ramais:
    pline(r, GREY, 3)

# represa (lagoa/reservatório) — ícone esquemático
d.ellipse([wx(REPRESA[0] - REP_R), wy(REPRESA[1] + REP_R * 0.6),
           wx(REPRESA[0] + REP_R), wy(REPRESA[1] - REP_R * 0.6)],
          fill=(70, 150, 190, 130), outline=(20, 90, 130), width=3)
for _k in range(3):
    _yy = REPRESA[1] - 0.18 + _k * 0.16
    d.line([(wx(REPRESA[0] - REP_R * 0.55), wy(_yy)), (wx(REPRESA[0] + REP_R * 0.55), wy(_yy))],
           fill=(20, 90, 130, 140), width=2)
d.text((wx(REPRESA[0]) - 40, wy(REPRESA[1] + REP_R * 0.6) + 6), "REPRESA", font=F_NOTE, fill=(15, 80, 120))
d.text((wx(REPRESA[0]) - 78, wy(REPRESA[1] + REP_R * 0.6) + 28),
       "água servida (duchas + pia)\nposição esquemática — local\nreal e distância a definir",
       font=F_TINY, fill=(15, 80, 120))

# pia da bancada (cozinha) fica ~11 m ao sul, fora do recorte -> ramal
# INDEPENDENTE (não se junta ao coletor da ala), indicado por 2 setas que
# saem de quadro, deslocadas uma da outra para não se sobreporem.
_pbx_agua, _pbx_esg = 3.60, 3.80
d.line([(wx(_pbx_agua), wy(TRUNK_Y) - 34), (wx(_pbx_agua), wy(TRUNK_Y) - 4)], fill=BLUE, width=4)
d.polygon([(wx(_pbx_agua) - 7, wy(TRUNK_Y) - 34), (wx(_pbx_agua) + 7, wy(TRUNK_Y) - 34), (wx(_pbx_agua), wy(TRUNK_Y) - 48)],
          fill=BLUE)
d.line([(wx(_pbx_esg), wy(TRUNK_Y) - 34), (wx(_pbx_esg), wy(TRUNK_Y) - 4)], fill=BROWN, width=4)
d.polygon([(wx(_pbx_esg) - 7, wy(TRUNK_Y) - 34), (wx(_pbx_esg) + 7, wy(TRUNK_Y) - 34), (wx(_pbx_esg), wy(TRUNK_Y) - 48)],
          fill=BROWN)
d.text((wx(_pbx_agua) - 200, wy(TRUNK_Y) - 100),
       "PIA DA BANCADA (cozinha)\nramal independente\n~11 m ao sul, fora do recorte",
       font=F_TINY, fill=(90, 90, 90), align="right")

for cx_, cy_ in (CAIXA_CINZA, CAIXA_SANIT):
    d.rectangle([wx(cx_) - 7, wy(cy_) - 7, wx(cx_) + 7, wy(cy_) + 7], fill=(90, 90, 88, 230),
                outline=(255, 255, 255), width=1)

# --- Fixtures (marcadores duplos: água fria + destino do esgoto) ----------
def fixture(cx_, cy_, label, sub, color):
    d.ellipse([wx(cx_) - 9, wy(cy_) - 9, wx(cx_) + 9, wy(cy_) + 9], fill=color, outline=(255, 255, 255), width=2)


fixture(X_DUCHA_AG, D1Y, "", "", BLUE)
fixture(X_DUCHA_CZ, D1Y, "", "", GREY)
fixture(X_DUCHA_AG, D2Y, "", "", BLUE)
fixture(X_DUCHA_CZ, D2Y, "", "", GREY)
fixture(X_VASO_AG, D1Y, "", "", BLUE)
fixture(X_VASO_ES, D1Y, "", "", BROWN)
fixture(X_VASO_AG, D2Y, "", "", BLUE)
fixture(X_VASO_ES, D2Y, "", "", BROWN)
fixture(X_PIA_AG, PIA_COM[1], "", "", BLUE)
fixture(X_PIA_CZ, PIA_COM[1], "", "", GREY)

d.text((wx(DUCHA_X) - 58, wy(D1Y) - 34), "DUCHA 1", font=F_TINY, fill=(20, 24, 30))
d.text((wx(DUCHA_X) - 58, wy(D2Y) + 14), "DUCHA 2", font=F_TINY, fill=(20, 24, 30))
d.text((wx(VASO_X) + 12, wy(D1Y) - 34), "SANIT. 1", font=F_TINY, fill=(20, 24, 30))
d.text((wx(VASO_X) + 12, wy(D2Y) + 14), "SANIT. 2", font=F_TINY, fill=(20, 24, 30))
d.text((wx(PIA_COM[0]) - 70, wy(PIA_COM[1]) - 30), "PIA COMUNITÁRIA", font=F_TINY, fill=(20, 24, 30))

# --- Fossa + sumidouro -----------------------------------------------------
d.rectangle([wx(FOSSA[0] - FOSSA_W / 2), wy(FOSSA[1] + FOSSA_H / 2),
             wx(FOSSA[0] + FOSSA_W / 2), wy(FOSSA[1] - FOSSA_H / 2)],
            fill=(180, 220, 190, 200), outline=GREEN, width=3)
d.text((wx(FOSSA[0]) - 30, wy(FOSSA[1]) - 11), "FOSSA", font=F_NOTE, fill=(20, 90, 40))
d.text((wx(FOSSA[0]) - 92, wy(FOSSA[1] + FOSSA_H / 2) + 8),
       "biodigestora 1.300 L", font=F_TINY, fill=(20, 90, 40))

d.ellipse([wx(SUMIDOURO[0] - SUM_R), wy(SUMIDOURO[1] + SUM_R),
           wx(SUMIDOURO[0] + SUM_R), wy(SUMIDOURO[1] - SUM_R)],
          fill=(180, 220, 190, 160), outline=GREEN, width=3)
d.text((wx(SUMIDOURO[0]) - 44, wy(SUMIDOURO[1]) - 24), "SUMIDOURO", font=F_NOTE, fill=(20, 90, 40))
d.text((wx(SUMIDOURO[0]) - 68, wy(SUMIDOURO[1]) + 2), "anéis Ø1,50 m\nprof. ≈2,00 m",
       font=F_TINY, fill=(20, 90, 40))


def _label(mx, my, text, color, font=F_DIM):
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.rectangle([mx - tw / 2 - 5, my - th / 2 - 5, mx + tw / 2 + 5, my + th / 2 + 7], fill=BG)
    d.text((mx - tw / 2 - tb[0], my - th / 2 - tb[1]), text, font=font, fill=color)


# --- Rótulos de diâmetro nos trechos principais ---------------------------
_label(wx(0.9), wy(TRUNK_Y) - 22, "água fria 25 mm", BLUE, F_TINY)
_label(wx(FOSSA[0]) + 90, (wy(FOSSA[1]) + wy(CAIXA_SANIT[1])) / 2, "esgoto\nsanitário\n100 mm", BROWN, F_TINY)
_label((wx(CAIXA_CINZA[0]) + wx(REPRESA[0] + 1.0)) / 2, wy(TRUNK_Y) + 24, "água servida 40 mm", GREY, F_TINY)

# --- Ficha lateral ----------------------------------------------------
fx0 = wx(WX1) + 30
fy0 = wy(WY1) + 10
lines = [
    "8 pontos de consumo (água fria):",
    "  2 registros de chuveiro elétrico (duchas)",
    "  2 caixas acopladas (vasos sanitários)",
    "  3 torneiras/bicas (pia comunitária)",
    "  1 torneira (pia da bancada)",
    "",
    "REDE SEPARADA EM 2 DESTINOS (esgoto):",
    "  SANITÁRIO (só os 2 vasos) -> fossa -> sumidouro",
    "  ÁGUA SERVIDA (2 duchas + pia comunitária) -> represa",
    "  (a ducha NÃO passa pela fossa — só água de banho/sabão)",
    "  Pia da bancada (cozinha, tem gordura): segue p/ a fossa",
    "  — ver ramal independente à parte, no topo direito",
    "",
    "Água fria: PVC soldável 25 mm (ramal) / 20 mm (pontos)",
    "Esgoto sanitário (vasos): PVC 100 mm",
    "Água servida (duchas/pia): PVC 40 mm",
    "",
    "Fossa séptica biodigestora 1.300 L (só 2 vasos + pia da",
    "  bancada — carga reduzida) + sumidouro Ø1,50 m",
    "  — dimensão final do sumidouro depende de teste",
    "  de infiltração do solo (não feito)",
    "",
    "1 caixa de inspeção antes da fossa + 1 antes da represa",
    "",
    "SISTEMA SEPARADO da drenagem PLUVIAL (calha/",
    "  canaleta/cano Ø100 do telhado) — ver",
    "  piso_quiosque_medidas.png",
    "",
    "Posições da fossa/sumidouro e da represa são",
    "  ESQUEMÁTICAS — locais reais, distâncias e a ligação",
    "  até o ponto de água existente precisam ser medidos",
    "  em campo.",
]
for i, ln in enumerate(lines):
    d.text((fx0 + 14, fy0 + 46 + i * 19), ln, font=F_TINY, fill=(20, 24, 30))

lg = fy0 + 46 + len(lines) * 19 + 10
d.line([(fx0 + 14, lg), (fx0 + 30, lg)], fill=BLUE, width=4)
d.text((fx0 + 38, lg - 9), "água fria", font=F_TINY, fill=(20, 24, 30))
d.line([(fx0 + 14, lg + 22), (fx0 + 30, lg + 22)], fill=BROWN, width=4)
d.text((fx0 + 38, lg + 13), "esgoto sanitário (vasos -> fossa)", font=F_TINY, fill=(20, 24, 30))
d.line([(fx0 + 14, lg + 44), (fx0 + 30, lg + 44)], fill=GREY, width=4)
d.text((fx0 + 38, lg + 35), "água servida (duchas+pia -> represa)", font=F_TINY, fill=(20, 24, 30))
d.line([(fx0 + 14, lg + 66), (fx0 + 30, lg + 66)], fill=GREEN, width=4)
d.text((fx0 + 38, lg + 57), "fossa / sumidouro", font=F_TINY, fill=(20, 24, 30))

img.save(OUT)
print("ESGOTO_MEDIDAS_OK:", OUT)
