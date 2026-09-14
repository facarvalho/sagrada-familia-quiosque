"""
Exporta o modelo do quiosque como KML NATIVO (poligonos extrudados),
sem usar <Model>/COLLADA - funciona no Google Earth Web (navegador), que
nao suporta modelos 3D importados. Versao mais simples/"em blocos" do
que o .kmz com modelo COLLADA (nucleo/export_google_earth.py, esse sim
com todos os detalhes, mas so funciona no Google Earth Pro desktop).

Uso:
    blender --background --factory-startup \
        --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
        --python nucleo/export_google_earth_web.py

Gera:
    documentacao/google-earth/quiosque_piscina_web.kml
"""
import bpy
import os
import sys
import math
import mathutils

REPO_ROOT = "/home/fac/piscina"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import nucleo.sun_geo as sun_geo

OUT_DIR = os.path.join(REPO_ROOT, "documentacao", "google-earth")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Constroi a cena completa (projeto real, posicao atual)
# ---------------------------------------------------------------------------
projeto_path = os.path.join(REPO_ROOT, "arquitetonico", "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _ns)

import arquitetonico.extras as extras
extras.build_all(_ns)
import arquitetonico.fixes as fixes
fixes.apply_all()
import estrutural.roof_frame as roof_frame

# ---------------------------------------------------------------------------
# 2. Transformacao projeto XY -> GPS real (mesma calibracao de 4 pontos)
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
_C, _S = math.cos(THETA), math.sin(THETA)


def project_to_gps(px, py):
    x = px - _ctx
    y = py - _cty
    inv_c, inv_s = math.cos(-THETA), math.sin(-THETA)
    xr = (x * inv_c - y * inv_s) / SCALE
    yr = (x * inv_s + y * inv_c) / SCALE
    xr += _csx
    yr += _csy
    return from_local_m(xr, yr)


def coord_str(px, py, z):
    lat, lon = project_to_gps(px, py)
    return f"{lon:.9f},{lat:.9f},{z:.3f}"


# ---------------------------------------------------------------------------
# 3. Helpers KML
# ---------------------------------------------------------------------------
_placemarks = []


def add_extruded(name, style_id, footprint_xy, z_top, z_bottom=0.0):
    """footprint_xy: lista de (x,y) no plano do projeto; extruda de
    z_bottom ate z_top (altitudeMode relativeToGround)."""
    coords = " ".join(coord_str(x, y, z_top) for x, y in footprint_xy)
    coords += " " + coord_str(*footprint_xy[0], z_top)
    pm = f"""  <Placemark>
    <name>{name}</name>
    <styleUrl>#{style_id}</styleUrl>
    <Polygon>
      <extrude>1</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>{coords}</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""
    _placemarks.append(pm)


def add_flat(name, style_id, footprint_xyz):
    """footprint_xyz: lista de (x,y,z) no plano do projeto, cada vertice
    com sua propria altitude (relativeToGround) - usado pro telhado
    inclinado e pras superficies planas no chao."""
    coords = " ".join(coord_str(x, y, z) for x, y, z in footprint_xyz)
    coords += " " + coord_str(*footprint_xyz[0])
    pm = f"""  <Placemark>
    <name>{name}</name>
    <styleUrl>#{style_id}</styleUrl>
    <Polygon>
      <extrude>0</extrude>
      <altitudeMode>relativeToGround</altitudeMode>
      <outerBoundaryIs>
        <LinearRing>
          <coordinates>{coords}</coordinates>
        </LinearRing>
      </outerBoundaryIs>
    </Polygon>
  </Placemark>"""
    _placemarks.append(pm)


def bbox_xy_z(obj):
    pts = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    footprint = [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
    return footprint, min(zs), max(zs)


# ---------------------------------------------------------------------------
# 4. PISO + DECK + PISCINA (poligonos planos, rente ao chao)
# ---------------------------------------------------------------------------
PISO_OUTLINE = [
    (0.0, 1.5), (4.0, 1.5), (4.0, 12.0), (-2.25, 12.0), (-2.25, 9.5), (0.0, 9.5),
]
add_flat("Piso do quiosque", "style_piso", [(x, y, 0.03) for x, y in PISO_OUTLINE])

deck = bpy.data.objects.get("Piso_Area_Piscina")
if deck:
    fp, zmin, zmax = bbox_xy_z(deck)
    add_flat("Deck da piscina", "style_deck", [(x, y, 0.02) for x, y in fp])

agua = bpy.data.objects.get("Piscina_Esmeralda_Agua")
if agua:
    fp, zmin, zmax = bbox_xy_z(agua)
    add_flat("Piscina (ja existe)", "style_piscina", [(x, y, 0.01) for x, y in fp])

# ---------------------------------------------------------------------------
# 5. PILARES (10x, extrudados do chao ate o topo)
# ---------------------------------------------------------------------------
altura_pilar = _ns["altura_pilar"]
R = 0.065
for i in range(1, 11):
    obj = bpy.data.objects.get(f"Pilar_Eucalipto_{i}")
    if not obj:
        continue
    loc = obj.matrix_world.translation
    cx, cy = loc.x, loc.y
    fp = [(cx - R, cy - R), (cx + R, cy - R), (cx + R, cy + R), (cx - R, cy + R)]
    add_extruded(f"Pilar {i}", "style_pilar", fp, altura_pilar)

# ---------------------------------------------------------------------------
# 6. PAREDES (extrudadas do chao ate o topo de cada segmento)
# ---------------------------------------------------------------------------
for obj in bpy.data.objects:
    if obj.name.startswith("Parede_"):
        fp, zmin, zmax = bbox_xy_z(obj)
        add_extruded(obj.name.replace("_", " "), "style_parede", fp, zmax, zmin)

# ---------------------------------------------------------------------------
# 7. TELHADO (plano inclinado, mesmo contorno em L do piso, cada canto na
#    sua propria altura - reflete o caimento real de 15%)
# ---------------------------------------------------------------------------
roof_pts = []
for x, y in PISO_OUTLINE:
    z = roof_frame.roof_underside_z(_ns, x) + 0.03
    roof_pts.append((x, y, z))
add_flat("Telhado", "style_telhado", roof_pts)

# ---------------------------------------------------------------------------
# 8. Escreve o KML
# ---------------------------------------------------------------------------
STYLES = """
  <Style id="style_piso">
    <PolyStyle><color>ffd9d9d9</color><outline>0</outline></PolyStyle>
  </Style>
  <Style id="style_deck">
    <PolyStyle><color>ffe8e8e8</color><outline>0</outline></PolyStyle>
  </Style>
  <Style id="style_piscina">
    <PolyStyle><color>ffe8c49a</color><outline>0</outline></PolyStyle>
  </Style>
  <Style id="style_pilar">
    <PolyStyle><color>ff2e6ea3</color></PolyStyle>
    <LineStyle><color>ff1a4a75</color><width>1</width></LineStyle>
  </Style>
  <Style id="style_parede">
    <PolyStyle><color>d9b8c4cc</color></PolyStyle>
    <LineStyle><color>ff8f9daf</color><width>1</width></LineStyle>
  </Style>
  <Style id="style_telhado">
    <PolyStyle><color>ff5f6b7a</color><outline>1</outline></PolyStyle>
    <LineStyle><color>ff3d4552</color><width>2</width></LineStyle>
  </Style>
"""

kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Quiosque da Piscina - Sitio Sagrada Familia (blocos)</name>
  <description>Modelo 3D simplificado (poligonos extrudados nativos do
  KML - piso, pilares, paredes e telhado inclinado), na posicao GPS real.
  Funciona no Google Earth Web (navegador). Versao com todos os detalhes
  (mobilia, banheiros, etc) esta em quiosque_piscina.kmz, mas essa exige
  o Google Earth Pro (desktop) por causa do modelo 3D (COLLADA).</description>
{STYLES}
{chr(10).join(_placemarks)}
</Document>
</kml>
"""
kml_path = os.path.join(OUT_DIR, "quiosque_piscina_web.kml")
with open(kml_path, "w", encoding="utf-8") as f:
    f.write(kml)
print("KML_WEB_OK:", kml_path)
print("N_PLACEMARKS:", len(_placemarks))
print("ALLDONE_EXPORT_WEB")
