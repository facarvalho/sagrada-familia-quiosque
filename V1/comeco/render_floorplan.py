"""
Planta baixa ortográfica do "esqueleto" da obra (piso, pilares, vigas,
terças - telhado escondido para revelar o resto visto de cima). Mesma
composição de V1/render_floorplan.py, sem paredes/banheiro/bancada/móveis.
"""
import bpy
import os
import sys
import json
import math
import mathutils
from bpy_extras.object_utils import world_to_camera_view

scriptdir = os.path.dirname(os.path.abspath(__file__))
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import build_comeco
ns, info = build_comeco.build()

_schedule = info.get("roof_frame", {}).get("schedule", {"transversais": [], "tercas": []})
_drenagem = info.get("calcadas", {}).get("drenagem", {})

pilares_coords = ns["pilares_coords"]
altura_piso = ns["altura_piso"]
altura_pilar = ns["altura_pilar"]
raio_pilar = ns["raio_pilar"]

# Esconde o telhado para revelar o piso e os pilares vistos de cima.
telhado = bpy.data.objects.get("Telhado_Zinco_L")
if telhado:
    telhado.hide_render = True

# ---------------------------------------------------------------------------
# Câmera ortográfica de topo, enquadrando todo o piso do quiosque
# ---------------------------------------------------------------------------
xs = [p[0] for p in pilares_coords]
ys = [p[1] for p in pilares_coords]
X0, X1 = min(xs) - 0.7, max(xs) + 4.8
Y0, Y1 = min(ys) - 0.7, max(ys) + 1.6
cx, cy = (X0 + X1) / 2.0, (Y0 + Y1) / 2.0
world_w, world_h = X1 - X0, Y1 - Y0

RES_Y = 1900
RES_X = max(200, round(RES_Y * (world_w / world_h)))

cam_data = bpy.data.cameras.new("Camera_FloorPlan")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = world_h
cam_obj = bpy.data.objects.new("Camera_FloorPlan", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (cx, cy, 15.0)
cam_obj.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# Iluminação suave e uniforme (sol quase vertical, sem sombras longas)
# ---------------------------------------------------------------------------
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World_Ceu")
    bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg_node = nt.nodes.new("ShaderNodeBackground")
out_node = nt.nodes.new("ShaderNodeOutputWorld")
bg_node.inputs["Color"].default_value = (0.75, 0.78, 0.82, 1.0)
bg_node.inputs["Strength"].default_value = 1.0
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

sun_data = bpy.data.lights.new("Sol_Plan", type='SUN')
sun_data.energy = 1.6
sun_data.angle = math.radians(8.0)
sun_obj = bpy.data.objects.new("Sol_Plan", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(20), 0.0, math.radians(35))

scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 150
scene.cycles.use_denoising = False
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

output_path = os.path.join(scriptdir, "renders", "planta_quiosque_base_comeco.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

# ---------------------------------------------------------------------------
# Projeção dos pilares e cálculo das distâncias sequenciais
# ---------------------------------------------------------------------------
bpy.context.view_layer.update()


def project(pt):
    co = world_to_camera_view(scene, cam_obj, mathutils.Vector(pt))
    px = co.x * scene.render.resolution_x
    py = (1.0 - co.y) * scene.render.resolution_y
    return [px, py]


centroid_x = sum(xs) / len(xs)
centroid_y = sum(ys) / len(ys)

pillars = []
for i, (px_w, py_w, _z) in enumerate(pilares_coords, start=1):
    pillars.append({
        "index": i,
        "name": f"Pilar_Eucalipto_{i}",
        "world": [px_w, py_w],
        "px": project((px_w, py_w, 0.05)),
    })

edges = []
n = len(pilares_coords)
for i in range(n):
    a = pilares_coords[i]
    b = pilares_coords[(i + 1) % n]
    dist = math.hypot(b[0] - a[0], b[1] - a[1])
    mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length
    to_centroid = (centroid_x - mx, centroid_y - my)
    if nx * to_centroid[0] + ny * to_centroid[1] > 0:
        nx, ny = -nx, -ny
    edges.append({
        "from": i + 1,
        "to": (i + 1) % n + 1,
        "dist": dist,
        "p1px": project((a[0], a[1], 0.05)),
        "p2px": project((b[0], b[1], 0.05)),
        "normal": [nx, ny],
    })

tercas_plan = []
for t in _schedule.get("tercas", []):
    x, y0, y1 = t["x"], t["y0"], t["y1"]
    tercas_plan.append({
        "n": t["n"], "comprimento": t["comprimento"],
        "x": x, "y0": y0, "y1": y1,
        "p1px": project((x, y0, 2.0)), "p2px": project((x, y1, 2.0)),
        "midpx": project((x, (y0 + y1) / 2.0, 2.0)),
    })
transv_plan = []
for v in _schedule.get("transversais", []):
    a, b = v["p1"], v["p2"]
    transv_plan.append({
        "n": v["n"], "comprimento": v["comprimento"], "y": v["y"],
        "p1px": project((a[0], a[1], 2.0)), "p2px": project((b[0], b[1], 2.0)),
        "midpx": project(((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, 2.0)),
    })

drenagem_plan = {}
if _drenagem:
    dx = _drenagem["eixo_x"]
    cy0, cy1 = _drenagem["cano"]
    gy0, gy1 = _drenagem["canaleta"]
    by0, by1 = _drenagem["sob_banheiro"]
    drenagem_plan = {
        "diam_mm": _drenagem.get("diam_mm", 100),
        "cano_px": [project((dx, cy0, 0.0)), project((dx, cy1, 0.0))],
        "canaleta_px": [project((dx, gy0, 0.0)), project((dx, gy1, 0.0))],
        "sob_banheiro_px": [project((dx, by0, 0.0)), project((dx, by1, 0.0))],
        "caixa_px": project((dx, _drenagem.get("caixa_y", cy1), 0.0)),
        "mid_px": project((dx, (cy0 + cy1) / 2.0, 0.0)),
    }

data = {
    "width": scene.render.resolution_x,
    "height": scene.render.resolution_y,
    "pillars": pillars,
    "edges": edges,
    "tercas": tercas_plan,
    "transversais": transv_plan,
    "drenagem": drenagem_plan,
    "altura_pilar": altura_pilar,
    "diametro_pilar": raio_pilar * 2,
    "altura_tora": ns.get("altura_tora", altura_pilar),
    "altura_pedestal": ns.get("altura_pedestal", 0.0),
    "prof_pedestal": ns.get("prof_pedestal", 0.0),
    "diametro_pedestal": ns.get("raio_pedestal", 0.0) * 2,
    "altura_piso": altura_piso,
    "esp_piso": ns.get("esp_piso", altura_piso or 0.10),
}
json_path = os.path.join(scriptdir, "renders", "planta_quiosque_comeco.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("PLAN_JSON_OK:", json_path)

bpy.ops.render.render(write_still=True)
print("PLAN_RENDER_OK:", output_path)
