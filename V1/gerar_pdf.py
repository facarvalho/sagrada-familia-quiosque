import datetime
from PIL import Image
from V1.pdf_lib import PDFDoc, wrap_text, text_width, PAGE_W, PAGE_H

BASE = "/home/fac/piscina/V1"
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
TOTAL_PAGES = 22   # 6 de conteúdo + 15 de galeria + 1 de sequência


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
    "2. Planta técnica do quiosque – pilares, terças e vigas",
    "3. Especificações técnicas gerais",
    "4. Estrutura do telhado (meia-água, telha sanduíche PIR)",
    "5. Ambientes e mobiliário",
    "6. Galeria de imagens (15 pranchas, uma por página)",
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
    ("Posição do centro (x, y)", "-3.67, -0.15 (georreferenciada por GPS/KML)"),
    ("Nível da lâmina d'água", "-0.10 m em relação ao piso"),
])

y = section(p, y, "Piso do Quiosque", [
    ("Piso principal", "4.00 x 10.50 m (sólido único em L)"),
    ("Ala (banheiros)", "~2.65 x 2.50 m (borda leste em P9-P6)"),
    ("Espessura do piso", "0.10 m (topo no nível do deck da piscina)"),
    ("Piso de concreto (área externa)", "9.00 x 16.50 m"),
])

y = section(p, y, "Pilares de Eucalipto (10 unidades)", [
    ("Classe / diâmetro", "Eucalipto roliço 12/14 (Ø ~0.13 m)"),
    ("Tora de madeira", "2.00 m, apoiada no topo do pedestal"),
    ("Pedestal de concreto", "Ø 0.30 m, de -0.30 m a +0.50 m do piso"),
    ("Topo dos pilares", "2.50 m (fileira oeste P1/P10/P9/P6: 2.56 m; ala P7/P8: ~2.16 m)"),
    ("Fileira oeste (P1,P10,P9,P6)", "recuada 0.40 m para dentro (x = 0.40)"),
])

y = section(p, y, "Paredes de Fechamento", [
    ("Material", "Muro tendinoso (malla + varão tensionados, reboco rústico 2 faces)"),
    ("Corpo principal", "lados sul e leste - sobem até a face inferior do telhado"),
    ("Banheiros", "h 2.50 m, com respiro sob o telhado; verga acima das portas"),
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
    ("Telha", "Sanduíche trapezoidal PIR 30 mm - útil 1,00 m - vão máx. terça 2,60 m"),
    ("Quantidade", "12 telhas: 8 de 4,04 m (sul) + 4 de 7,03 m (norte)"),
    ("Comprar / peso", "~60,5 m2 de telha / ~561 kg"),
    ("Montantes", "4 un., sobre a fileira leste (x=4), ~0.60 m"),
    ("Vigas transversais", "Eucalipto 12/14, sentido X, sobre pares de pilares"),
    ("Terças (12/14, sentido Y)", "T1 x=0,40 / T2 x=2,20 / T3 x=4,00 (L 11,00 m); T4 ala x=-2,25 (L 3,50 m)"),
    ("Beiral", "leste 0 (morre em T3) | sul/oeste 0,40 | norte 0,50 | ala 0,70 m"),
])

y = section(p, y, "Alturas de referência (a partir do piso)", [
    ("Topo dos pilares (corpo)", "2.50 m (fileira oeste P1/P10/P9/P6: 2.56 m)"),
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
    ("Cabines", "4 (1,30 x 1,15 m): 2 duchas quentes (O) + 2 sanitários (L)"),
    ("Portas", "0,60 x 1,90 m; duchas abrem p/ a piscina, sanitários p/ o corredor"),
    ("Sanitários", "só o vaso (sem pia na cabine)"),
    ("Lava-mãos", "pia comunitária rústica de 1,80 m, 3 bicas, na parede P8-P9"),
    ("Piso", "caixa de brita (tabuleiro rebaixado ~0,14 m, meio-fio ~0,09 m)"),
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

footer(p, 6, "Ambientes e mobiliário")

# ============================================================ GALERIA DE IMAGENS
# Uma imagem por página, em PAISAGEM, ocupando toda a largura da página
# (ou toda a altura, para os desenhos verticais). Legenda em barra inferior.
gallery = [
    ("Vista geral do projeto", "projeto_render.png"),
    ("Planta técnica do quiosque - pilares, terças e vigas", "planta_quiosque_anotada.png"),
    ("Piso do quiosque + calçada - medidas", "piso_quiosque_medidas.png"),
    ("Projeto do telhado - telha sanduíche PIR, terças e telhas", "telhado_quiosque_medidas.png"),
    ("Banheiros da ala - planta e medidas (caixa de brita)", "banheiro_planta_medidas.png"),
    ("Vista da entrada (do lado da piscina)", "vista_entrada.png"),
    ("Vista aérea 3/4 da propriedade", "vista_aerea.png"),
    ("Vista interna do corredor", "vista_corredor.png"),
    ("Area da pia / bancada gourmet (de P9 para P2)", "vista_area_pia.png"),
    ("Corredor olhando para a cozinha", "vista_corredor_cozinha.png"),
    ("Interior da ducha", "banheiro_ducha_interior.png"),
    ("Interior do lavabo", "banheiro_lavabo_interior.png"),
    ("Vista externa - eixo da terça T2, 15 m ao norte", "vista_15m_T2_V1.png"),
    ("Vista externa - 10 m entre P6 e P2", "vista_10m_entre_P6_P2.png"),
    ("Vista 360 (fisheye) do interior", "vista_360_fisheye.png"),
]
GAL_START = 7
for gi, (caption, fname) in enumerate(gallery):
    p = doc.new_page()
    p.w, p.h = PAGE_H, PAGE_W          # A4 paisagem
    bar_h = 30
    pad = P(18)
    box_w = p.w - 2 * pad
    box_h = p.h - 2 * pad - bar_h
    _im = Image.open(f"{BASE}/renders/{fname}")
    _r = min(box_w / _im.width, box_h / _im.height)
    iw, ih = _im.width * _r, _im.height * _r
    ix = (p.w - iw) / 2.0
    iy = pad + (box_h - ih) / 2.0
    p.image(f"{BASE}/renders/{fname}", ix, iy, iw, ih)
    p.rect(ix, iy, ix + iw, iy + ih, stroke=LINE, width=1)
    p.rect(0, p.h - bar_h, p.w, p.h, fill=INK)
    p.text(28, p.h - 11, caption, font="Helvetica-Bold", size=10, color=WHITE)
    _cap = f"{GAL_START + gi} / {TOTAL_PAGES}    -    Galeria    -    {today}"
    p.text(p.w - 28 - text_width(_cap, 9), p.h - 11, _cap, font="Helvetica", size=9,
           color=(210, 210, 210))

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
    "Montagem das terças 12/14 (T1 x=0,40 / T2 x=2,20 / T3 x=4,00 + T4 ala) e assentamento das 12 telhas sanduíche PIR 30 mm (largura útil 1,00 m).",
    "Levantamento das paredes de fechamento em muro tendinoso (lados sul e leste, até o telhado).",
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
_LAST_PAGE = TOTAL_PAGES

p.text(MARGIN, PAGE_H - P(140), "Observação:", font="Helvetica-Bold", size=F_H2, color=INK)
obs = ("Este caderno reflete o projeto 3D gerado até o momento da emissão. Medidas devem ser "
       "conferidas em campo antes da execução. Consultar responsável técnico para dimensionamento "
       "estrutural definitivo das vigas e fundações dos pilares.")
ly = PAGE_H - P(115)
for ln in wrap_text(obs, F_SMALL, PAGE_W - 2 * MARGIN):
    p.text(MARGIN, ly, ln, font="Helvetica", size=F_SMALL, color=MUTED)
    ly += P(15)
footer(p, TOTAL_PAGES, "Sequência de execução")

out_path = f"{BASE}/Caderno_de_Obra.pdf"
doc.save(out_path)
print("PDF_OK:", out_path)
