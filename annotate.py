import json
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = "/home/fac/piscina"
img = Image.open(f"{BASE_DIR}/renders/projeto_render_base.png").convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

with open(f"{BASE_DIR}/renders/labels.json", "r", encoding="utf-8") as f:
    data = json.load(f)

W, H = data["width"], data["height"]

FONT_BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
FONT_REG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

LINE_COLOR = (255, 210, 60, 255)
MARKER_COLOR = (255, 210, 60, 255)
BOX_FILL = (20, 24, 30, 225)
BOX_OUTLINE = (255, 210, 60, 255)
TEXT_COLOR = (255, 255, 255, 255)
DIM_COLOR = (255, 255, 255, 255)

PAD = 12
RIGHT_BOX_X0 = 1478
RIGHT_BOX_W = 420
LEFT_BOX_X0 = 22
LEFT_BOX_W = 420


def text_block_size(lines, box_w):
    total_h = PAD * 2
    for i, ln in enumerate(lines):
        font = FONT_BOLD if i == 0 else FONT_REG
        h = draw.textbbox((0, 0), ln, font=font)[3]
        total_h += h + (6 if i == 0 else 4)
    return box_w, total_h


def draw_box_at(bx0, by0, box_w, box_h, lines, anchor_px, elbow_x=None):
    anchor_px = (anchor_px[0], anchor_px[1])
    bx1, by1 = bx0 + box_w, by0 + box_h
    box_cy = (by0 + by1) / 2
    from_right = bx0 > anchor_px[0]
    edge_x = bx0 if from_right else bx1
    edge = (edge_x, box_cy)

    if elbow_x is not None:
        draw.line([edge, (elbow_x, box_cy), (elbow_x, anchor_px[1]), anchor_px], fill=LINE_COLOR, width=2)
    else:
        draw.line([edge, anchor_px], fill=LINE_COLOR, width=2)

    r = 5
    ax, ay = anchor_px
    draw.ellipse([ax - r, ay - r, ax + r, ay + r], fill=MARKER_COLOR, outline=(0, 0, 0, 255))

    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=BOX_FILL, outline=BOX_OUTLINE, width=2)
    ty = by0 + PAD
    for i, ln in enumerate(lines):
        font = FONT_BOLD if i == 0 else FONT_REG
        draw.text((bx0 + PAD, ty), ln, font=font, fill=TEXT_COLOR)
        ty += draw.textbbox((0, 0), ln, font=font)[3] + (6 if i == 0 else 4)


def layout_column(entries, box_x0, box_w, elbow_x, top_margin=20, gap=18):
    sized = []
    for e in entries:
        lines = e["text"].split("\n")
        _, h = text_block_size(lines, box_w)
        sized.append((e, lines, h))
    sized.sort(key=lambda t: t[0]["px"][1])

    total_h = sum(h for _, _, h in sized) + gap * (len(sized) - 1)
    start_y = max(top_margin, min(H - total_h - top_margin, (H - total_h) / 2))
    y = start_y
    for e, lines, h in sized:
        draw_box_at(box_x0, y, box_w, h, lines, e["px"], elbow_x=elbow_x)
        y += h + gap


def draw_arrowhead(tip, direction, size=10, color=DIM_COLOR):
    angle = math.atan2(direction[1], direction[0])
    a1 = angle + math.radians(150)
    a2 = angle - math.radians(150)
    p1 = (tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1))
    p2 = (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2))
    draw.polygon([tip, p1, p2], fill=color)


def draw_dimension(p1, p2, text, offset_side, label_t=0.5, label_off=34):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    draw.line([(x1, y1), (x2, y2)], fill=DIM_COLOR, width=2)
    draw_arrowhead((x1, y1), (x1 - x2, y1 - y2))
    draw_arrowhead((x2, y2), (x2 - x1, y2 - y1))

    mx, my = x1 + (x2 - x1) * label_t, y1 + (y2 - y1) * label_t
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    if offset_side == "top" and ny > 0:
        nx, ny = -nx, -ny
    if offset_side == "left" and nx > 0:
        nx, ny = -nx, -ny
    tx, ty = mx + nx * label_off, my + ny * label_off

    w, h = draw.textbbox((0, 0), text, font=FONT_BOLD)[2:]
    bx0, by0 = tx - w / 2 - 8, ty - h / 2 - 6
    bx1, by1 = tx + w / 2 + 8, ty + h / 2 + 6
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=6, fill=(20, 24, 30, 225), outline=DIM_COLOR, width=1)
    draw.text((tx - w / 2, ty - h / 2), text, font=FONT_BOLD, fill=TEXT_COLOR)


dims = data["dimensions"]
draw_dimension(dims[0]["p1px"], dims[0]["p2px"], dims[0]["text"], "left", label_t=0.28)
draw_dimension(dims[1]["p1px"], dims[1]["p2px"], dims[1]["text"], "top")
draw_dimension(dims[2]["p1px"], dims[2]["p2px"], dims[2]["text"], "left")

anchors = {a["text"].split("\n")[0]: a for a in data["anchors"]}

right_entries = [
    anchors["Telhado de Zinco"],
    anchors["Pilares de Eucalipto (10x)"],
    anchors["Piso do Quiosque (L)"],
]
left_entries = [
    anchors["Lâmina d'Água"],
    anchors["Piscina Esmeralda"],
    anchors["Piso de Concreto (Área Externa)"],
]

layout_column(right_entries, RIGHT_BOX_X0, RIGHT_BOX_W, elbow_x=RIGHT_BOX_X0 - 60)
layout_column(left_entries, LEFT_BOX_X0, LEFT_BOX_W, elbow_x=LEFT_BOX_X0 + LEFT_BOX_W + 60)

out_path = f"{BASE_DIR}/renders/projeto_render_anotado.png"
img.save(out_path)
print("ANNOTATED_OK:", out_path)
