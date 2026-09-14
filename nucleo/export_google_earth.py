"""
Exporta o modelo 3D do quiosque (projeto real, posição atual) para um
pacote .kmz importável no Google Earth: modelo COLLADA (.dae) + KML que
posiciona ele na coordenada GPS real, com a orientação real (norte
verdadeiro) já calculada em nucleo/sun_geo.py.

Uso:
    blender --background --factory-startup \
        --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
        --python nucleo/export_google_earth.py

Gera:
    documentacao/google-earth/quiosque_piscina.dae
    documentacao/google-earth/quiosque_piscina.kml
    documentacao/google-earth/quiosque_piscina.kmz  (os dois de cima, zipados)
"""
import bpy
import os
import sys
import math
import zipfile

REPO_ROOT = "/home/fac/piscina"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import nucleo.sun_geo as sun_geo

OUT_DIR = os.path.join(REPO_ROOT, "documentacao", "google-earth")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Constrói a cena completa (projeto real, posição atual - sem girar/mover)
# ---------------------------------------------------------------------------
projeto_path = os.path.join(REPO_ROOT, "arquitetonico", "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _ns)

import arquitetonico.extras as extras
extras.build_all(_ns)
import arquitetonico.fixes as fixes
fixes.apply_all()

# remove câmeras/luzes que não fazem sentido no modelo exportado
for o in list(bpy.data.objects):
    if o.type in {"CAMERA", "LIGHT"}:
        bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.object.select_all(action='SELECT')

# ---------------------------------------------------------------------------
# 2. Exporta COLLADA (.dae) - Blender grava a metainformação de eixo (Z-up)
#    corretamente no arquivo; leitores compatíveis (Google Earth) respeitam.
# ---------------------------------------------------------------------------
dae_path = os.path.join(OUT_DIR, "quiosque_piscina.dae")
bpy.ops.wm.collada_export(
    filepath=dae_path,
    selected=True,
    apply_modifiers=True,
    triangulate=False,
)
print("DAE_OK:", dae_path)

# ---------------------------------------------------------------------------
# 3. Posição/orientação real: origem do projeto (0,0) -> GPS real, usando a
#    mesma calibração de 4 pontos (piso da piscina) já validada nesta sessão.
# ---------------------------------------------------------------------------
LAT0 = sun_geo.LAT
LON0 = sun_geo.LON


def to_local_m(lat, lon):
    x = (lon - LON0) * math.cos(math.radians(LAT0)) * 111320.0
    y = (lat - LAT0) * 110540.0
    return (x, y)


def from_local_m(x, y):
    lon = x / (math.cos(math.radians(LAT0)) * 111320.0) + LON0
    lat = y / 110540.0 + LAT0
    return (lat, lon)


_kml_pts = [
    (-45.99002249156514, -21.35313781731155),
    (-45.98996998766656, -21.35307670124178),
    (-45.99009254660934, -21.35297156333806),
    (-45.9901414095965, -21.35302559618331),
]
_local = [to_local_m(lat, lon) for lon, lat in _kml_pts]
_proj = [(0.0, 9.5), (-9.0, 9.5), (-9.0, -7.0), (0.0, -7.0)]

_n = 4
_csx = sum(p[0] for p in _local) / _n
_csy = sum(p[1] for p in _local) / _n
_ctx = sum(p[0] for p in _proj) / _n
_cty = sum(p[1] for p in _proj) / _n
_sxx = _sxy = _syx = _syy = _saa = 0.0
for _s, _t in zip(_local, _proj):
    _ax, _ay = _s[0] - _csx, _s[1] - _csy
    _bx, _by = _t[0] - _ctx, _t[1] - _cty
    _sxx += _ax * _bx
    _sxy += _ax * _by
    _syx += _ay * _bx
    _syy += _ay * _by
    _saa += _ax * _ax + _ay * _ay
THETA = math.atan2(_sxy - _syx, _sxx + _syy)
SCALE = math.hypot(_sxx + _syy, _sxy - _syx) / _saa


def project_to_gps(px, py):
    x = px - _ctx
    y = py - _cty
    inv_c, inv_s = math.cos(-THETA), math.sin(-THETA)
    xr = (x * inv_c - y * inv_s) / SCALE
    yr = (x * inv_s + y * inv_c) / SCALE
    xr += _csx
    yr += _csy
    return from_local_m(xr, yr)


origin_lat, origin_lon = project_to_gps(0.0, 0.0)
heading = sun_geo.ROTATION_OFFSET_DEG  # graus, sentido horário a partir do norte real

print(f"ORIGIN_GPS: {origin_lat}, {origin_lon}")
print(f"HEADING_DEG: {heading}")

# ---------------------------------------------------------------------------
# 4. Escreve o KML referenciando o .dae, na posição/orientação real
# ---------------------------------------------------------------------------
kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Quiosque da Piscina - Sitio Sagrada Familia</name>
  <description>Modelo 3D do projeto do quiosque (piso, pilares, telhado,
  paredes, banheiros, area gourmet), posicionado na coordenada GPS real
  e orientado para o norte verdadeiro (heading calculado a partir do
  levantamento em nucleo/sun_geo.py). A piscina ja existe e esta incluida
  no modelo so como referencia visual.</description>
  <Placemark>
    <name>Quiosque (projeto)</name>
    <Model id="quiosque_model">
      <altitudeMode>clampToGround</altitudeMode>
      <Location>
        <longitude>{origin_lon:.10f}</longitude>
        <latitude>{origin_lat:.10f}</latitude>
        <altitude>0</altitude>
      </Location>
      <Orientation>
        <heading>{heading:.4f}</heading>
        <tilt>0</tilt>
        <roll>0</roll>
      </Orientation>
      <Scale>
        <x>1</x>
        <y>1</y>
        <z>1</z>
      </Scale>
      <Link>
        <href>quiosque_piscina.dae</href>
      </Link>
    </Model>
  </Placemark>
</Document>
</kml>
"""
kml_path = os.path.join(OUT_DIR, "quiosque_piscina.kml")
with open(kml_path, "w", encoding="utf-8") as f:
    f.write(kml_content)
print("KML_OK:", kml_path)

# ---------------------------------------------------------------------------
# 5. Empacota .kmz (kml + dae + texturas, se houver)
# ---------------------------------------------------------------------------
kmz_path = os.path.join(OUT_DIR, "quiosque_piscina.kmz")
with zipfile.ZipFile(kmz_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(kml_path, arcname="doc.kml")
    z.write(dae_path, arcname="quiosque_piscina.dae")
    tex_dir = os.path.join(OUT_DIR, "textures")
    if os.path.isdir(tex_dir):
        for fn in os.listdir(tex_dir):
            z.write(os.path.join(tex_dir, fn), arcname=f"textures/{fn}")
print("KMZ_OK:", kmz_path)
print("ALLDONE_EXPORT_GOOGLE_EARTH")
