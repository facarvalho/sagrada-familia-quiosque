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
import extras
extras.build_all(_projeto_ns)

import fixes
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

# ---------------------------------------------------------------------------
# Câmera no fundo do corredor (perto da sala de estar), olhando para a
# cozinha/área gourmet (pilares 1-2-3, extremidade sul)
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Cam_Corredor_Cozinha")
cam_data.lens = 24
cam_obj = bpy.data.objects.new("Cam_Corredor_Cozinha", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = mathutils.Vector((1.8, 10.6, 1.65))
target = mathutils.Vector((3.2, 1.2, 1.1))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 250
scene.cycles.use_denoising = False
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

out_path = os.path.join(scriptdir, "renders", "vista_corredor_cozinha.png")
scene.render.filepath = out_path
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("OK:", out_path)
