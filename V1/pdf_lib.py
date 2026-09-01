"""
Gerador mínimo de PDF em Python puro (sem dependências externas).

Suporta: texto com fontes padrão (Helvetica/Helvetica-Bold, sem precisar
embutir fonte -> nítido e selecionável em qualquer zoom), retângulos e
linhas vetoriais, e imagens JPEG embutidas (via DCTDecode, usando Pillow só
para converter/comprimir a imagem de origem).
"""
import io
import zlib
from PIL import Image

PAGE_W, PAGE_H = 595.28, 841.89  # A4 em pontos (72pt = 1 polegada)


def _esc(s):
    return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _text_bytes(s):
    return _esc(s).encode("cp1252", errors="replace")


NARROW = set("iIljt.,'\":;!|()[]")
WIDE = set("mwMW@%")


def char_width_em(ch):
    if ch == " ":
        return 0.278
    if ch in NARROW:
        return 0.30
    if ch in WIDE:
        return 0.82
    if ch.isupper():
        return 0.67
    if ch.isdigit():
        return 0.556
    return 0.52


def text_width(text, size, bold=False):
    w = sum(char_width_em(c) for c in text) * size
    return w * (1.06 if bold else 1.0)


def wrap_text(text, size, max_width, bold=False):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, size, bold) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Page:
    def __init__(self, doc, w=PAGE_W, h=PAGE_H):
        self.doc = doc
        self.w = w
        self.h = h
        self.ops = []
        self.fonts_used = set()
        self.images_used = []  # list of (xobj_name, image_id)

    # --- coordenadas: origem no topo-esquerda, Y crescendo pra baixo -----
    def _y(self, y):
        return self.h - y

    def text(self, x, y, s, font="Helvetica", size=12, color=(0, 0, 0)):
        if not s:
            return
        self.fonts_used.add(font)
        r, g, b = [c / 255.0 for c in color]
        baseline = self._y(y) - size * 0.80
        self.ops.append(
            f"BT /{font} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {baseline:.2f} Td ("
            .encode("latin-1") + _text_bytes(s) + b") Tj ET\n"
        )

    def text_centered(self, cx, y, s, font="Helvetica", size=12, color=(0, 0, 0)):
        w = text_width(s, size, bold="Bold" in font)
        self.text(cx - w / 2, y, s, font=font, size=size, color=color)

    def rect(self, x0, y0, x1, y1, fill=None, stroke=None, width=1.0):
        y0p, y1p = self._y(y0), self._y(y1)
        yb, yt = min(y0p, y1p), max(y0p, y1p)
        w, h = x1 - x0, yt - yb
        cmds = []
        if fill:
            r, g, b = [c / 255.0 for c in fill]
            cmds.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        if stroke:
            r, g, b = [c / 255.0 for c in stroke]
            cmds.append(f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w")
        op = "B" if (fill and stroke) else ("f" if fill else ("S" if stroke else "n"))
        cmds.append(f"{x0:.2f} {yb:.2f} {w:.2f} {h:.2f} re {op}")
        self.ops.append((" ".join(cmds) + "\n").encode("latin-1"))

    def line(self, x0, y0, x1, y1, color=(0, 0, 0), width=1.0):
        r, g, b = [c / 255.0 for c in color]
        self.ops.append(
            f"{r:.3f} {g:.3f} {b:.3f} RG {width:.2f} w {x0:.2f} {self._y(y0):.2f} m "
            f"{x1:.2f} {self._y(y1):.2f} l S\n".encode("latin-1")
        )

    def image(self, path, x, y, w, h):
        img_id = self.doc._add_image(path)
        name = f"Im{img_id}"
        self.images_used.append((name, img_id))
        y_bottom = self._y(y) - h
        self.ops.append(
            f"q {w:.2f} 0 0 {h:.2f} {x:.2f} {y_bottom:.2f} cm /{name} Do Q\n".encode("latin-1")
        )

    def fit_image(self, path, x, y, max_w, max_h):
        im = Image.open(path)
        ratio = min(max_w / im.width, max_h / im.height)
        w, h = im.width * ratio, im.height * ratio
        self.image(path, x, y, w, h)
        return w, h


class PDFDoc:
    def __init__(self):
        self.pages = []
        self._objects = {}
        self._next_id = 1
        self._image_cache = {}

    def new_page(self):
        p = Page(self)
        self.pages.append(p)
        return p

    def _alloc(self):
        oid = self._next_id
        self._next_id += 1
        return oid

    def _add_image(self, path):
        if path in self._image_cache:
            return self._image_cache[path]
        im = Image.open(path).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=92)
        jpeg_bytes = buf.getvalue()
        oid = self._alloc()
        self._objects[oid] = (
            f"<< /Type /XObject /Subtype /Image /Width {im.width} /Height {im.height} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode "
            f"/Length {len(jpeg_bytes)} >>\nstream\n"
        ).encode("latin-1") + jpeg_bytes + b"\nendstream"
        self._image_cache[path] = oid
        return oid

    def save(self, path):
        font_ids = {}
        for name in ("Helvetica", "Helvetica-Bold"):
            oid = self._alloc()
            self._objects[oid] = (
                f"<< /Type /Font /Subtype /Type1 /BaseFont /{name} "
                f"/Encoding /WinAnsiEncoding >>"
            ).encode("latin-1")
            font_ids[name] = oid

        pages_id = self._alloc()
        page_ids = []
        for page in self.pages:
            content = b"".join(page.ops)
            content_id = self._alloc()
            self._objects[content_id] = (
                f"<< /Length {len(content)} >>\nstream\n".encode("latin-1")
                + content + b"\nendstream"
            )

            font_res = " ".join(f"/{n} {font_ids[n]} 0 R" for n in page.fonts_used) or ""
            xobj_res = " ".join(f"/{n} {iid} 0 R" for n, iid in page.images_used) or ""
            resources = "<< /Font << " + font_res + " >> /XObject << " + xobj_res + " >> >>"

            page_id = self._alloc()
            page_ids.append(page_id)
            self._objects[page_id] = (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {page.w:.2f} {page.h:.2f}] "
                f"/Resources {resources} /Contents {content_id} 0 R >>"
            ).encode("latin-1")

        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        self._objects[pages_id] = (
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>"
        ).encode("latin-1")

        catalog_id = self._alloc()
        self._objects[catalog_id] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin-1")

        out = io.BytesIO()
        out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}
        for oid in sorted(self._objects.keys()):
            offsets[oid] = out.tell()
            body = self._objects[oid]
            out.write(f"{oid} 0 obj\n".encode("latin-1"))
            out.write(body)
            out.write(b"\nendobj\n")

        xref_offset = out.tell()
        max_id = self._next_id - 1
        out.write(f"xref\n0 {max_id + 1}\n".encode("latin-1"))
        out.write(b"0000000000 65535 f \n")
        for oid in range(1, max_id + 1):
            off = offsets.get(oid, 0)
            out.write(f"{off:010d} 00000 n \n".encode("latin-1"))

        out.write(
            f"trailer\n<< /Size {max_id + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF".encode("latin-1")
        )

        with open(path, "wb") as f:
            f.write(out.getvalue())
