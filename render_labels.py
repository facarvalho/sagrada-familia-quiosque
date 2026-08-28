import bpy
import bmesh
import os
import sys
import json
import math
import mathutils
from bpy_extras.object_utils import world_to_camera_view

# ---------------------------------------------------------------------------
# 1. EXECUTA O PROJETO ORIGINAL (SEM MODIFICAR O ARQUIVO)
# ---------------------------------------------------------------------------
scriptdir = os.path.dirname(os.path.abspath(__file__))
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

centro_x_piscina = _projeto_ns["centro_x_piscina"]
centro_y_piscina = _projeto_ns["centro_y_piscina"]
# Posição real da piscina (casca/água) - pode diferir do centro do piso de
# concreto ao redor, que não se move junto (ver projeto.py).
centro_y_piscina_agua = _projeto_ns.get("centro_y_piscina_agua", centro_y_piscina)
altura_pilar = _projeto_ns["altura_pilar"]
raio_pilar = _projeto_ns["raio_pilar"]
altura_tora = _projeto_ns.get("altura_tora", altura_pilar)
altura_pedestal = _projeto_ns.get("altura_pedestal", 0.0)
prof_pedestal = _projeto_ns.get("prof_pedestal", 0.0)
altura_piso = _projeto_ns["altura_piso"]
largura_piscina = _projeto_ns["largura_piscina"]
comprimento_piscina = _projeto_ns["comprimento_piscina"]

# ---------------------------------------------------------------------------
# 1a. ADIÇÕES SOLICITADAS PELO USUÁRIO (ver extras.py)
# ---------------------------------------------------------------------------
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import extras
extras.build_all(_projeto_ns)

# ---------------------------------------------------------------------------
# 1b. CORREÇÕES NÃO-DESTRUTIVAS DE BUGS DO PROJETO ORIGINAL (ver fixes.py)
# ---------------------------------------------------------------------------
import fixes
fixes.apply_all()

# ---------------------------------------------------------------------------
# 2. CÂMERA
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_Render")
cam_data.lens = 32
cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_location = mathutils.Vector((-16.0, -12.0, 9.0))
target = mathutils.Vector((-2.0, 4.0, 0.8))

cam_obj.location = cam_location
direction = target - cam_location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# 3. ILUMINAÇÃO REALISTA (CÉU UNIFORME + SOL ÚNICO)
# ---------------------------------------------------------------------------
sun_elevation = math.radians(18)
sun_rotation = math.radians(228.8)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World_Ceu")
    bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

bg_node = nt.nodes.new("ShaderNodeBackground")
out_node = nt.nodes.new("ShaderNodeOutputWorld")
bg_node.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
bg_node.inputs["Strength"].default_value = 1.1
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.energy = 3.5
sun_data.angle = math.radians(3.0)
sun_data.color = (1.0, 0.82, 0.6)
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (
    math.pi / 2 - sun_elevation,
    0.0,
    sun_rotation + math.pi,
)

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# 4. CONFIGURAÇÃO DE RENDER (CYCLES)
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 300
scene.cycles.use_denoising = False
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False

prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

output_path = os.path.join(scriptdir, "renders", "projeto_render_base.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

# ---------------------------------------------------------------------------
# 4b. PONTOS DE ANOTAÇÃO (nomes + medidas), projetados para a câmera do render
# ---------------------------------------------------------------------------
x0 = centro_x_piscina - largura_piscina / 2
x1 = centro_x_piscina + largura_piscina / 2
y0 = centro_y_piscina_agua - comprimento_piscina / 2
y1 = centro_y_piscina_agua + comprimento_piscina / 2

anchors = [
    {
        "point": (4.0, 4.0, altura_pilar / 2),
        "text": (f"Pilares de Eucalipto (10x)\n"
                 f"tora 12/14 Ø {raio_pilar * 2:.2f} m · H {altura_tora:.2f} m\n"
                 f"sobre pedestal concreto (+{altura_pedestal:.2f}/-{prof_pedestal:.2f} m)"),
        "side": "right",
    },
    {
        "point": (2.0, 6.0, altura_piso),
        "text": "Piso do Quiosque (L)\n4.00 x 12.00 m (+ala 2.25 x 2.50 m)\nesp. 0.10 m",
        "side": "right",
    },
    {
        "point": (2.0, 3.0, 3.0),
        "text": ("Telhado de Zinco\n"
                 "meia-água, caimento 15% p/ oeste (piscina)\n"
                 "telhas 1,00 x 4,50 m · terças a cada ~2 m"),
        "side": "top",
    },
    {
        "point": (-8.0, -1.0, 0.0),
        "text": "Piso de Concreto (Área Externa)\n9.00 x 16.50 m",
        "side": "left",
    },
    {
        "point": (centro_x_piscina, y0 + 1.5, -0.05),
        "text": "Piscina Esmeralda\n3.70 x 10.50 m\nprof. 1.30 - 1.70 m (~54 m³)",
        "side": "left",
    },
    {
        "point": (centro_x_piscina, y1 - 1.5, -0.10),
        "text": "Lâmina d'Água\n(nível -0.10 m)",
        "side": "right",
    },
]

dimensions = [
    {"p1": (x0, y0, 0.0), "p2": (x0, y1, 0.0), "text": "10.50 m", "offset_side": "left"},
    {"p1": (x0, y1, 0.0), "p2": (x1, y1, 0.0), "text": "3.70 m", "offset_side": "top"},
    {"p1": (4.0, 4.0, 0.0), "p2": (4.0, 4.0, altura_pilar), "text": f"{altura_pilar:.2f} m", "offset_side": "left"},
]

bpy.context.view_layer.update()

def project(pt):
    co = world_to_camera_view(scene, cam_obj, mathutils.Vector(pt))
    px = co.x * scene.render.resolution_x
    py = (1.0 - co.y) * scene.render.resolution_y
    return [px, py, co.z]

data = {
    "width": scene.render.resolution_x,
    "height": scene.render.resolution_y,
    "anchors": [
        {"px": project(a["point"]), "text": a["text"], "side": a["side"]}
        for a in anchors
    ],
    "dimensions": [
        {"p1px": project(d["p1"]), "p2px": project(d["p2"]), "text": d["text"], "offset_side": d["offset_side"]}
        for d in dimensions
    ],
}

json_path = os.path.join(scriptdir, "renders", "labels.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"LABELS_OK:{json_path}")

# ---------------------------------------------------------------------------
# 5. RENDERIZA
# ---------------------------------------------------------------------------
bpy.ops.render.render(write_still=True)
print(f"RENDER_OK:{output_path}")
