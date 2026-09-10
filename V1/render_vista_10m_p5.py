"""
Vistas externas do quiosque:

  1. vista_15m_T2_V1.png       - sobre o eixo da terça T2 (x=2,20), a 15,00 m
     ao norte da viga V1 (y=1,5), olhando para o sul ao longo do eixo do
     quiosque em direção a V1. Enquadra o quiosque inteiro no comprimento.
  2. vista_10m_entre_P6_P2.png - câmera a 10,00 m de P5, linha de visada
     P5 -> ponto médio de P6/P2 (eixo do quiosque).
"""
import bpy
import os
import sys
import math
import mathutils

scriptdir = os.path.dirname(os.path.abspath(__file__))
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import V1.extras as extras
extras.build_all(_projeto_ns)

import V1.fixes as fixes
fixes.apply_all()

# --- Iluminação de fim de tarde (mesma paleta de render_more_angles.py) ----
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
sun_obj.rotation_euler = (math.pi / 2 - sun_elevation, 0.0, sun_rotation + math.pi)

scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.render.engine = 'CYCLES'
scene.cycles.use_denoising = False
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'


def make_camera(name, location, target, lens=28):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = mathutils.Vector(location)
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj


def render_to(path, res_x=1600, res_y=900, samples=220):
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.cycles.samples = samples
    scene.render.filepath = path
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print("RENDER_OK:", path)


renders_dir = os.path.join(scriptdir, "renders")
os.makedirs(renders_dir, exist_ok=True)

DIST = 10.0
EYE_Z = 1.65
TGT_Z = 2.30
LENS = 45

P5 = mathutils.Vector((4.0, 12.0))
P9 = mathutils.Vector((0.4, 9.5))
P6 = mathutils.Vector((0.4, 12.0))
P2 = mathutils.Vector((4.0, 1.5))


def cam_a_10m_de_p5(mira_xy):
    """Câmera a 10 m de P5, sobre a reta P5->mira, do lado de fora."""
    look = (mira_xy - P5).normalized()
    pos = P5 - look * DIST
    return (pos.x, pos.y, EYE_Z), (mira_xy.x, mira_xy.y, TGT_Z)


# --- 1. Sobre o eixo de T2, a 15 m de V1, olhando para o sul (V1) --------
recuo_oeste = _projeto_ns.get("recuo_oeste", 0.4)
x_t2 = (recuo_oeste + 4.0) / 2.0        # eixo da terça central T2
y_v1 = 1.5                              # viga transversal V1 (P1-P2)
altura_pilar = _projeto_ns.get("altura_pilar", 2.5)
z_v1 = altura_pilar + 0.065 + 0.15 * (x_t2 - 0.0)   # ~ eixo de V1
loc1 = (x_t2, y_v1 + 15.0, 2.20)
tgt1 = (x_t2, y_v1, z_v1 - 0.2)
cam1 = make_camera("Cam_15m_T2_V1", loc1, tgt1, lens=30)
scene.camera = cam1
render_to(os.path.join(renders_dir, "vista_15m_T2_V1.png"))

# --- 2. Entre P6 e P2 ---------------------------------------------------
mira2 = (P6 + P2) / 2.0
loc2, tgt2 = cam_a_10m_de_p5(mira2)
cam2 = make_camera("Cam_10m_P6_P2", loc2, tgt2, lens=LENS)
scene.camera = cam2
render_to(os.path.join(renders_dir, "vista_10m_entre_P6_P2.png"))

print("ALL_DONE")
