import bpy
import bmesh
import os
import sys
import json
import math
import mathutils
from bpy_extras.object_utils import world_to_camera_view

scriptdir = os.path.dirname(os.path.abspath(__file__))
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import extras
extras.build_all(_projeto_ns)

pilares_coords = _projeto_ns["pilares_coords"]
altura_piso = _projeto_ns["altura_piso"]
altura_pilar = _projeto_ns["altura_pilar"]
raio_pilar = _projeto_ns["raio_pilar"]

# Correções não-destrutivas de bugs do projeto original (ver fixes.py)
import fixes
fixes.apply_all()

# Esconde o telhado para revelar o piso e os pilares vistos de cima.
telhado = bpy.data.objects.get("Telhado_Zinco_L")
if telhado:
    telhado.hide_render = True

# ---------------------------------------------------------------------------
# Câmera ortográfica de topo, enquadrando todo o piso do quiosque
# ---------------------------------------------------------------------------
xs = [p[0] for p in pilares_coords]
ys = [p[1] for p in pilares_coords]
X0, X1 = min(xs) - 0.7, max(xs) + 4.8   # margem extra à direita p/ legendas
Y0, Y1 = min(ys) - 0.7, max(ys) + 1.6   # margem extra no topo p/ cotas
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

output_path = os.path.join(scriptdir, "renders", "planta_quiosque_base.png")
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
    # aponta a normal para longe do centróide (heurística de "lado de fora")
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

data = {
    "width": scene.render.resolution_x,
    "height": scene.render.resolution_y,
    "pillars": pillars,
    "edges": edges,
    "altura_pilar": altura_pilar,
    "diametro_pilar": raio_pilar * 2,
    "altura_piso": altura_piso,
}
json_path = os.path.join(scriptdir, "renders", "planta_quiosque.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("PLAN_JSON_OK:", json_path)

bpy.ops.render.render(write_still=True)
print("PLAN_RENDER_OK:", output_path)
