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
info = extras.build_all(_projeto_ns)
counter_info = info["counter"]

import V1.fixes as fixes
fixes.apply_all()

X_FRONT, X_WALL, Y0, Y1 = counter_info["bounds"]
cx, cy = (X_FRONT + X_WALL) / 2.0, (Y0 + Y1) / 2.0

cam_data = bpy.data.cameras.new("Camera_Counter")
cam_data.lens = 30
cam_obj = bpy.data.objects.new("Camera_Counter", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_location = mathutils.Vector((-2.58, -1.14, 2.05))
target = mathutils.Vector((3.6, 2.0, 1.1))
cam_obj.location = cam_location
direction = target - cam_location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

sun_elevation = math.radians(18)
sun_rotation = math.radians(228.8)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World_Ceu")
    bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
bg.inputs["Strength"].default_value = 1.2
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.energy = 3.5
sun_data.angle = math.radians(3.0)
sun_data.color = (1.0, 0.85, 0.65)
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.pi / 2 - sun_elevation, 0.0, sun_rotation + math.pi)

fill_data = bpy.data.lights.new("Luz_Preenchimento", type='POINT')
fill_data.energy = 18
fill_obj = bpy.data.objects.new("Luz_Preenchimento", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (1.5, 1.0, 2.6)

scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 250
scene.cycles.use_denoising = False
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'
out_path = os.path.join(scriptdir, "renders", "vista_area_pia.png")
scene.render.filepath = out_path
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
print("OK:", out_path)
