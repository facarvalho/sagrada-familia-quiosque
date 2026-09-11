"""
Ângulos externos/internos do "esqueleto" da obra - versão reduzida de
V1/render_more_angles.py: mantém vista_entrada, vista_aerea e
vista_corredor (fazem sentido sem acabamento). As fotos de banheiro
(ducha/lavabo) foram removidas - não há banheiro nesta cena.
"""
import bpy
import os
import sys
import math
import mathutils

scriptdir = os.path.dirname(os.path.abspath(__file__))
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import build_comeco
ns, info = build_comeco.build()

# --- Iluminação (mesma configuração de fim de tarde) ------------------------
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


def make_camera(name, location, target, lens=32):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = mathutils.Vector(location)
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj


def render_to(path, res_x=1600, res_y=900, samples=220, exposure=0.0,
              view_transform='Standard'):
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.cycles.samples = samples
    scene.view_settings.exposure = exposure
    scene.view_settings.view_transform = view_transform
    scene.render.filepath = path
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = 'Standard'
    print("RENDER_OK:", path)


renders_dir = os.path.join(scriptdir, "renders")
os.makedirs(renders_dir, exist_ok=True)

# --- 1. Vista da entrada (do lado da piscina, olhando para o quiosque) -----
cam1 = make_camera("Cam_Entrada", (-3.0, -9.0, 5.5), (-2.5, 5.0, 1.2), lens=28)
scene.camera = cam1
render_to(os.path.join(renders_dir, "vista_entrada_comeco.png"))

# --- 2. Vista aérea 3/4 (ângulo alto, mostrando toda a propriedade) --------
cam2 = make_camera("Cam_Aerea", (-9.0, -6.0, 15.0), (-1.0, 6.0, 0.0), lens=28)
scene.camera = cam2
render_to(os.path.join(renders_dir, "vista_aerea_comeco.png"))

# --- 3. Vista interna do corredor, olhando para o fundo (sem bancada) ------
cam3 = make_camera("Cam_Corredor", (0.7, 2.2, 1.65), (1.9, 10.5, 1.2), lens=28)
scene.camera = cam3
render_to(os.path.join(renders_dir, "vista_corredor_comeco.png"))

print("ALL_DONE")
