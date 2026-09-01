import bpy
import os
import sys
import math

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

# --- Iluminação (fim de tarde) ----------------------------------------------
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

# luz de preenchimento para suavizar o interior sob o telhado
fill_data = bpy.data.lights.new("Luz_Interior_360", type='POINT')
fill_data.energy = 120
fill_obj = bpy.data.objects.new("Luz_Interior_360", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (2.0, 6.0, 2.7)

# ---------------------------------------------------------------------------
# Câmera panorâmica olho de peixe (360°), no meio do corredor principal
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_360_Fisheye")
cam_data.type = 'PANO'
cam_obj = bpy.data.objects.new("Camera_360_Fisheye", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (2.0, 6.0, 1.55)
cam_obj.rotation_euler = (math.radians(90), 0.0, math.radians(90))
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
cam_data.panorama_type = 'FISHEYE_EQUISOLID'
cam_data.fisheye_fov = math.radians(360)
cam_data.fisheye_lens = 10.5

scene.view_settings.view_transform = 'Standard'
scene.cycles.samples = 300
scene.cycles.use_denoising = False
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16
scene.render.resolution_x = 2000
scene.render.resolution_y = 2000
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

out_path = os.path.join(scriptdir, "renders", "vista_360_fisheye.png")
scene.render.filepath = out_path
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("OK:", out_path)
