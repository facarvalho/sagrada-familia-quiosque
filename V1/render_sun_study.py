"""
"Prova de sol": renderiza o projeto (piscina + quiosque, geometria e
posições ORIGINAIS de projeto.py/extras.py - nada foi redimensionado)
iluminado pela posição REAL do sol, calculada a partir das coordenadas
geográficas do terreno (V1/cordenadas.kml -> V1/sun_geo.py).

Gera 6 imagens: solstício de verão (21/12) e de inverno (21/06), às
13h, 15h e 17h (horário de Brasília), conforme pedido pelo usuário.

Uso (bootstrap obrigatório, ver memória piscina-render-import-bootstrap):
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python V1/render_sun_study.py
"""
import bpy
import os
import sys
import math
import json
import mathutils

scriptdir = os.path.dirname(os.path.abspath(__file__))
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
repo_root = os.path.dirname(scriptdir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# ---------------------------------------------------------------------------
# 1. CONSTRÓI O PROJETO (igual render_projeto.py)
# ---------------------------------------------------------------------------
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

import V1.extras as extras
extras.build_all(_projeto_ns)

import V1.fixes as fixes
fixes.apply_all()

import V1.sun_geo as sun_geo

# ---------------------------------------------------------------------------
# 2. SETA DE NORTE VERDADEIRO (referência visual em cena)
# ---------------------------------------------------------------------------
nx, ny = sun_geo.true_north_vector_project_xy()
arrow_origin = mathutils.Vector((6.5, 3.0, 0.03))
arrow_len = 2.2
arrow_tip = arrow_origin + mathutils.Vector((nx, ny, 0.0)) * arrow_len

mesh_arrow = bpy.data.meshes.new("Mesh_Seta_Norte")
obj_arrow = bpy.data.objects.new("Seta_Norte_Verdadeiro", mesh_arrow)
bpy.context.collection.objects.link(obj_arrow)
perp = mathutils.Vector((-ny, nx, 0.0))
w = 0.18
p1 = arrow_origin - perp * w
p2 = arrow_origin + perp * w
p3 = arrow_tip
p4 = arrow_tip + perp * (w * 2.2) - mathutils.Vector((nx, ny, 0.0)) * 0.35
p5 = arrow_tip - perp * (w * 2.2) - mathutils.Vector((nx, ny, 0.0)) * 0.35
verts = [p1, p2, p3, p4, arrow_tip + mathutils.Vector((nx, ny, 0.0)) * 0.35, p5]
mesh_arrow.from_pydata([tuple(v) for v in verts], [], [[0, 1, 2], [3, 4, 5]])
mesh_arrow.update()
mat_norte = bpy.data.materials.new("Material_Seta_Norte")
mat_norte.use_nodes = True
mat_norte.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.05, 0.05, 1.0)
mat_norte.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
obj_arrow.data.materials.append(mat_norte)

# ---------------------------------------------------------------------------
# 3. CÂMERA (mesma composição de render_projeto.py, para comparar as 6 fotos)
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_Render")
cam_data.lens = 32
cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_location = mathutils.Vector((-16.0, -12.0, 9.0))
target = mathutils.Vector((-2.0, 4.0, 0.8))
cam_obj.location = cam_location
direction = target - cam_location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# 4. MUNDO (fundo plano = luz de preenchimento, igual render_projeto.py)
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
bg_node.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
# Fraco de propósito: aqui o objetivo é a "prova de sol" mostrar sombra
# nítida e correta (não uma foto bonita) - se o fundo domina como
# preenchimento onidirecional (era 1.1 no render_projeto.py), a sombra do
# quiosque sobre o deck/piscina praticamente desaparece.
bg_node.inputs["Strength"].default_value = 0.3
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# 5. RENDER (Cycles, com denoiser OIDN se disponível - blender 4.2.23 LTS)
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
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

has_denoiser = False
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    has_denoiser = True
    scene.cycles.use_denoising = True
    scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.denoising_prefilter = 'ACCURATE'
    scene.cycles.samples = 96
except TypeError:
    scene.cycles.use_denoising = False
    scene.cycles.samples = 300

print(f"Denoiser disponivel: {has_denoiser}, samples={scene.cycles.samples}")

# ---------------------------------------------------------------------------
# 6. SOL: 6 combinações (verao/inverno x 13h/15h/17h)
# ---------------------------------------------------------------------------
sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.angle = math.radians(3.0)
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)

CENAS = [
    ("verao", 2026, 12, 21, 13, 0),
    ("verao", 2026, 12, 21, 15, 0),
    ("verao", 2026, 12, 21, 17, 0),
    ("inverno", 2026, 6, 21, 13, 0),
    ("inverno", 2026, 6, 21, 15, 0),
    ("inverno", 2026, 6, 21, 17, 0),
]

out_dir = os.path.join(scriptdir, "renders")
os.makedirs(out_dir, exist_ok=True)

# posição de tela (px) da ponta da seta de norte, para a legenda 2D
region = bpy.context.scene.render
from bpy_extras.object_utils import world_to_camera_view
co2d = world_to_camera_view(bpy.context.scene, cam_obj, arrow_tip)
arrow_tip_px = (co2d.x * region.resolution_x, (1 - co2d.y) * region.resolution_y)

meta = {"cenas": []}

for estacao, y, m, d, h, mi in CENAS:
    azimuth, elevation = sun_geo.solar_position(y, m, d, h, mi)
    dx, dy, dz = sun_geo.sun_direction_project_xyz(azimuth, elevation)
    travel_dir = mathutils.Vector((-dx, -dy, -dz))
    sun_obj.rotation_euler = travel_dir.to_track_quat('-Z', 'Y').to_euler()

    # energia/cor: sol precisa DOMINAR sobre o preenchimento do fundo (0.3)
    # para lançar sombra nítida e visível - sol baixo = mais quente.
    t = max(0.0, min(1.0, elevation / 70.0))
    sun_data.energy = 5.0 + 3.0 * t
    sun_data.color = (1.0, 0.55 + 0.35 * t, 0.35 + 0.45 * t)

    fname = f"sol_{estacao}_{h:02d}h.png"
    fpath = os.path.join(out_dir, fname)
    scene.render.filepath = fpath
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print(f"RENDER_OK:{fpath} azimuth={azimuth:.1f} elevation={elevation:.1f}")

    meta["cenas"].append({
        "arquivo": fname, "estacao": estacao,
        "data": f"{d:02d}/{m:02d}/{y}", "hora": f"{h:02d}:{mi:02d}",
        "azimute_real_deg": round(azimuth, 1),
        "elevacao_deg": round(elevation, 1),
    })

meta["arrow_tip_px"] = arrow_tip_px
meta["rotation_offset_deg"] = sun_geo.ROTATION_OFFSET_DEG
meta["lat"] = sun_geo.LAT
meta["lon"] = sun_geo.LON
with open(os.path.join(out_dir, "sun_study_meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print("ALLDONE_SUN_STUDY")
