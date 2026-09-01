import datetime
from PIL import Image
from V1.pdf_lib import PDFDoc, wrap_text, text_width, PAGE_W, PAGE_H

BASE = "/home/fac/piscina"
CONV = PAGE_W / 1240.0  # mantém as proporções do layout original (1240x1754px)


def P(v):
    return v * CONV


MARGIN = P(70)
F_TITLE, F_SUBTITLE, F_H1, F_H2, F_BODY, F_SMALL = 24, 12, 15, 11, 9.5, 8

INK = (25, 28, 33)
MUTED = (95, 100, 110)
ACCENT = (176, 92, 41)
LINE = (210, 210, 210)
BG_SECTION = (245, 242, 238)
WHITE = (255, 255, 255)

doc = PDFDoc()
TOTAL_PAGES = 8


def footer(page, page_no, section_name):
    page.line(MARGIN, PAGE_H - P(60), PAGE_W - MARGIN, PAGE_H - P(60), color=LINE, width=1)
    page.text(MARGIN, PAGE_H - P(48), section_name, font="Helvetica", size=F_SMALL, color=MUTED)
    txt = f"{page_no} / {TOTAL_PAGES}"
    w = text_width(txt, F_SMALL)
    page.text(PAGE_W - MARGIN - w, PAGE_H - P(48), txt, font="Helvetica", size=F_SMALL, color=MUTED)


def section(page, y, title, rows):
    page.rect(MARGIN, y, PAGE_W - MARGIN, y + P(34), fill=BG_SECTION)
    page.text(MARGIN + P(12), y + P(24), title, font="Helvetica-Bold", size=F_H2, color=ACCENT)
    y += P(34) + P(10)
    col_w = P(320)
    for label, value in rows:
        page.text(MARGIN + P(12), y + P(16), label, font="Helvetica", size=F_BODY, color=MUTED)
        page.text(MARGIN + P(12) + col_w, y + P(16), value, font="Helvetica-Bold", size=F_BODY, color=INK)
        y += P(25)
    return y + P(18)


# ============================================================ PÁGINA 1 — CAPA
p = doc.new_page()
p.rect(0, 0, PAGE_W, P(8), fill=ACCENT)
today = datetime.date.today().strftime("%d/%m/%Y")
title_y = P(150)
subtitle_y = title_y + F_TITLE * 1.5
date_y = subtitle_y + F_SUBTITLE * 1.8
hero_y = date_y + F_SMALL * 3.0
p.text(MARGIN, title_y, "CADERNO DE OBRA", font="Helvetica-Bold", size=F_TITLE, color=INK)
p.text(MARGIN, subtitle_y, "Piscina Esmeralda & Quiosque – Projeto Executivo", font="Helvetica", size=F_SUBTITLE, color=MUTED)
p.text(MARGIN, date_y, f"Emitido em {today}", font="Helvetica", size=F_SMALL, color=MUTED)

hero_w, hero_h = p.fit_image(f"{BASE}/renders/projeto_render.png", MARGIN, hero_y, PAGE_W - 2 * MARGIN, P(560))
p.rect(MARGIN, hero_y, MARGIN + hero_w, hero_y + hero_h, stroke=LINE, width=1)

ty = hero_y + hero_h + F_H2 * 2.2
p.text(MARGIN, ty, "Conteúdo deste caderno", font="Helvetica-Bold", size=F_H2, color=INK)
ty += F_H2 * 2.0
items = [
    "1. Vista geral do projeto (render 3D)",
    "2. Planta técnica do quiosque – pilares e distâncias",
    "3. Especificações técnicas gerais",
    "4. Estrutura do telhado (meia-água em eucalipto)",
    "5. Ambientes e mobiliário",
    "6. Galeria de imagens adicionais",
    "7. Sequência de execução recomendada",
]
for it in items:
    p.text(MARGIN + P(10), ty, it, font="Helvetica", size=F_BODY, color=INK)
    ty += F_BODY * 1.9
footer(p, 1, "Capa")

# ==================================================== PÁGINA 2 — VISTA GERAL
p = doc.new_page()
p.w, p.h = PAGE_H, PAGE_W   # A4 em paisagem para a imagem grande
_hero = f"{BASE}/renders/projeto_render.png"
_im = Image.open(_hero)
_scale = max(p.w / _im.width, p.h / _im.height)   # preenche a página inteira (sangra)
_iw, _ih = _im.width * _scale, _im.height * _scale
p.image(_hero, (p.w - _iw) / 2.0, (p.h - _ih) / 2.0, _iw, _ih)
# faixa inferior com legenda (medidas em pontos, não na escala P())
p.rect(0, p.h - 34, p.w, p.h, fill=INK)
p.text(28, p.h - 13, "Piscina Esmeralda & Quiosque  —  vista geral do modelo 3D",
       font="Helvetica-Bold", size=10, color=WHITE)
_cap = f"2 / {TOTAL_PAGES}    ·    Caderno de Obra    ·    {today}"
p.text(p.w - 28 - text_width(_cap, 9), p.h - 13, _cap,
       font="Helvetica", size=9, color=(210, 210, 210))

# ============================================================ PÁGINA 2 — PLANTA
p = doc.new_page()
h1_y = P(50)
sub_y = h1_y + F_H1 * 1.7
img_y = sub_y + F_BODY * 2.2
p.text(MARGIN, h1_y, "1. Planta Técnica do Quiosque", font="Helvetica-Bold", size=F_H1, color=INK)
p.text(MARGIN, sub_y, "Nome, coordenadas e distâncias entre os 10 pilares de eucalipto.", font="Helvetica", size=F_BODY, color=MUTED)
plan_w, plan_h = p.fit_image(f"{BASE}/renders/planta_quiosque_anotada.png", MARGIN, img_y, PAGE_W - 2 * MARGIN, PAGE_H - img_y - P(60))
plan_x = MARGIN
p.rect(plan_x, img_y, plan_x + plan_w, img_y + plan_h, stroke=LINE, width=1)
footer(p, 3, "Planta técnica")

# ============================================================ PÁGINA 3 — ESPECIFICAÇÕES
p = doc.new_page()
p.text(MARGIN, P(50), "2. Especificações Técnicas Gerais", font="Helvetica-Bold", size=F_H1, color=INK)
y = P(90)

y = section(p, y, "Piscina Esmeralda", [
    ("Dimensões (largura x comprimento)", "3.70 x 10.50 m"),
    ("Profundidade", "1.30 m (rasa) a 1.70 m (funda)"),
    ("Volume aproximado", "~54 m³"),
    ("Posição do centro (x, y)", "-4.5, 0.25"),
    ("Nível da lâmina d'água", "-0.10 m em relação ao piso"),
])

y = section(p, y, "Piso do Quiosque", [
    ("Piso principal", "4.00 x 12.00 m"),
    ("Ala (banheiros/gourmet)", "~2.15 x 2.50 m"),
    ("Espessura do piso", "0.10 m"),
    ("Piso de concreto (área externa)", "9.00 x 16.50 m"),
])

y = section(p, y, "Pilares de Eucalipto (10 unidades)", [
    ("Classe / diâmetro", "Eucalipto roliço 12/14 (Ø ~0.13 m)"),
    ("Tora de madeira", "2.00 m, apoiada no topo do pedestal"),
    ("Pedestal de concreto", "Ø 0.30 m, de -0.30 m a +0.50 m do piso"),
    ("Topo dos pilares", "2.50 m (pilares 7 e 8 da ala: ~2.16 m)"),
    ("Alinhamento", "Pilares 6 e 9 no eixo x=0 (junto a 1 e 10)"),
])

y = section(p, y, "Parede de Fechamento", [
    ("Material", "Placa cimentícia"),
    ("Trecho", "Pilares 1-2-3-4-5 (lados sul e leste)"),
    ("Altura", "2.00 m (vão de ventilação até o beiral baixo)"),
])
footer(p, 4, "Especificações técnicas")

# ============================================================ PÁGINA 4 — ESTRUTURA DO TELHADO
p = doc.new_page()
h1_y = P(50)
sub_y = h1_y + F_H1 * 1.7
p.text(MARGIN, h1_y, "3. Estrutura do Telhado", font="Helvetica-Bold", size=F_H1, color=INK)
p.text(MARGIN, sub_y, "Telhado em meia-água, caimento de 15% escoando para oeste, em direção à piscina.",
       font="Helvetica", size=F_BODY, color=MUTED)
y = sub_y + F_BODY * 2.5

y = section(p, y, "Caimento", [
    ("Sistema", "Meia-água (uma só queda)"),
    ("Inclinação", "15% (~8,5°)"),
    ("Sentido do escoamento", "Para oeste (x = 0) - em direção à piscina"),
    ("Lado alto", "Leste (x = 4)"),
    ("Desnível no vão de 4,0 m", "0.60 m"),
])

y = section(p, y, "Telhas e estrutura", [
    ("Telha", "Metálica 1,00 x 4,50 m - vão livre máx. 2,50 m"),
    ("Montantes", "4 un., sobre a fileira leste (x=4), ~0.60 m"),
    ("Vigas transversais", "Eucalipto 12/14, sentido X, sobre pares de pilares"),
    ("Terças", "Eucalipto 12/14, sentido Y, em x = 0 / 2 / 4 (+ ala x = -2.25)"),
    ("Beiral", "0.40 m nas bordas externas"),
])

y = section(p, y, "Alturas de referência (a partir do piso)", [
    ("Topo dos pilares (corpo principal)", "2.50 m"),
    ("Topo dos pilares 7 e 8 (ala)", "~2.16 m (acompanham o caimento)"),
    ("Vão livre sob o telhado", "~2.6 m (oeste) a ~3.4 m (leste)"),
    ("Beiral baixo (oeste, piscina)", "~2.4 m"),
])
footer(p, 5, "Estrutura do telhado")

# ============================================================ PÁGINA 5 — AMBIENTES
p = doc.new_page()
p.text(MARGIN, P(50), "4. Ambientes e Mobiliário", font="Helvetica-Bold", size=F_H1, color=INK)
y = P(90)
y = section(p, y, "Banheiros (ala, pilares 6-7-8-9)", [
    ("Duchas quentes", "2, lado oeste (porta para o lado da piscina)"),
    ("Lavabos", "2, lado leste (porta para o corredor do quiosque)"),
    ("Corredor interno", "Removido - cabines ampliadas"),
])
y = section(p, y, "Área Gourmet (pilares 1-2-3)", [
    ("Bancada", "Pia + churrasqueira de bancada, acabamento rústico"),
    ("Geladeira e fogão", "Parede sul, entre pilares 1-2"),
    ("Mesa", "8 lugares, com bancos corridos"),
])
y = section(p, y, "Sala de Estar (pilares 4-5-6)", [
    ("Mobiliário", "2 sofás + mesa de centro + tapete"),
    ("TV", "Parede leste, entre pilares 4-5"),
])
y = section(p, y, "Mesas de Bar (pilares 3-4)", [
    ("Quantidade", "2 mesas altas, 2 banquetas cada"),
])

thumbs = ["vista_entrada.png", "vista_corredor.png", "vista_aerea.png"]
gap = P(16)
tw = (PAGE_W - 2 * MARGIN - 2 * gap) / 3
tx = MARGIN
for name in thumbs:
    iw, ih = p.fit_image(f"{BASE}/renders/{name}", tx, y, tw, P(220))
    p.rect(tx, y, tx + iw, y + ih, stroke=LINE, width=1)
    tx += tw + gap
footer(p, 6, "Ambientes e mobiliário")

# ============================================================ PÁGINA 6 — GALERIA DE IMAGENS
p = doc.new_page()
p.text(MARGIN, P(50), "5. Galeria de Imagens Adicionais", font="Helvetica-Bold", size=F_H1, color=INK)
gallery = [
    ("Área da Pia / Bancada Gourmet", "vista_area_pia.png"),
    ("Corredor Olhando para a Cozinha", "vista_corredor_cozinha.png"),
    ("Interior da Ducha", "banheiro_ducha_interior.png"),
    ("Interior do Lavabo", "banheiro_lavabo_interior.png"),
    ("Planta dos Banheiros", "banheiro_planta.png"),
    ("Vista 360° (Fisheye)", "vista_360_fisheye.png"),
]
g_gap_x, g_gap_y = P(16), P(14)
cell_w = (PAGE_W - 2 * MARGIN - g_gap_x) / 2
cell_h = (PAGE_H - P(90) - P(70) - 2 * g_gap_y) / 3
gy = P(90)
for i, (caption, fname) in enumerate(gallery):
    col = i % 2
    row = i // 2
    gx = MARGIN + col * (cell_w + g_gap_x)
    cy = gy + row * (cell_h + g_gap_y)
    p.text(gx, cy, caption, font="Helvetica-Bold", size=F_BODY, color=INK)
    iw, ih = p.fit_image(f"{BASE}/renders/{fname}", gx, cy + F_BODY * 1.6, cell_w, cell_h - F_BODY * 1.6)
    p.rect(gx, cy + F_BODY * 1.6, gx + iw, cy + F_BODY * 1.6 + ih, stroke=LINE, width=1)
footer(p, 7, "Galeria de imagens")

# ============================================================ PÁGINA 7 — SEQUÊNCIA DE EXECUÇÃO
p = doc.new_page()
p.text(MARGIN, P(50), "6. Sequência de Execução Recomendada", font="Helvetica-Bold", size=F_H1, color=INK)
y = P(90)
steps = [
    "Escavação e execução da casca/impermeabilização da piscina esmeralda.",
    "Execução do piso de concreto da área externa e piso do quiosque (principal + ala).",
    "Execução das brocas e pedestais de concreto (Ø 0.30 m, de -0.30 a +0.50 m) nas 10 posições da planta.",
    "Montagem dos 10 pilares de eucalipto 12/14 (tora de 2.00 m) sobre bases metálicas fixadas nos pedestais.",
    "Montagem dos montantes (leste) e das vigas transversais 12/14, formando o caimento de 15% para oeste.",
    "Montagem das terças 12/14 (x = 0 / 2 / 4 + ala) e assentamento das telhas 1,00 x 4,50 m (vão livre <= 2,5 m).",
    "Levantamento da parede de fechamento em placa cimentícia (pilares 1-2-3-4-5).",
    "Construção das paredes e instalação hidráulica dos banheiros (ala, pilares 6-7-8-9).",
    "Instalação da bancada, pia, churrasqueira, geladeira e fogão (área gourmet, pilares 1-2-3).",
    "Instalação da lâmina d'água e acabamento (azulejo) da piscina.",
    "Montagem do mobiliário: mesa de 8 lugares, mesas de bar, sala de estar e TV.",
    "Limpeza geral e vistoria final.",
]
STEP_INDENT = P(28) + 12
max_w = PAGE_W - MARGIN - STEP_INDENT
for i, st in enumerate(steps, start=1):
    p.text(MARGIN, y, f"{i:02d}.", font="Helvetica-Bold", size=F_BODY, color=ACCENT)
    lines = wrap_text(st, F_BODY, max_w)
    ly = y
    for ln in lines:
        p.text(MARGIN + STEP_INDENT, ly, ln, font="Helvetica", size=F_BODY, color=INK)
        ly += P(16)
    y = ly + P(6)

p.text(MARGIN, PAGE_H - P(140), "Observação:", font="Helvetica-Bold", size=F_H2, color=INK)
obs = ("Este caderno reflete o projeto 3D gerado até o momento da emissão. Medidas devem ser "
       "conferidas em campo antes da execução. Consultar responsável técnico para dimensionamento "
       "estrutural definitivo das vigas e fundações dos pilares.")
ly = PAGE_H - P(115)
for ln in wrap_text(obs, F_SMALL, PAGE_W - 2 * MARGIN):
    p.text(MARGIN, ly, ln, font="Helvetica", size=F_SMALL, color=MUTED)
    ly += P(15)
footer(p, 8, "Sequência de execução")

out_path = f"{BASE}/Caderno_de_Obra.pdf"
doc.save(out_path)
print("PDF_OK:", out_path)
