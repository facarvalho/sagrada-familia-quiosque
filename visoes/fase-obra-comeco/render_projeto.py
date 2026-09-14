"""
Vista 3/4 do "esqueleto" da obra - piso, calçada, pilares, vigas, terças e
telhado, SEM paredes/banheiro/bancada/móveis. Mesma câmera e luz de
render_projeto.py (fim de tarde), só que sem os acabamentos.
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

# ---------------------------------------------------------------------------
# Câmera (mesma composição de render_projeto.py)
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
# Iluminação (fundo plano + sol de fim de tarde, igual render_projeto.py)
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
sun_obj.rotation_euler = (math.pi / 2 - sun_elevation, 0.0, sun_rotation + math.pi)

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# Render (Cycles)
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

output_path = os.path.join(scriptdir, "renders", "projeto_render_comeco.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

bpy.ops.render.render(write_still=True)
print(f"RENDER_OK:{output_path}")
