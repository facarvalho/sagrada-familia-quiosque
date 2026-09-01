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
info = extras.build_all(_projeto_ns)
bath_info = info["bathroom"]
print("BATH_INFO:", bath_info)

for name in ["Telhado_Zinco_L"]:
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = True
for i in range(1, 11):
    o = bpy.data.objects.get(f"Pilar_Eucalipto_{i}")
    if o:
        o.hide_render = True
for obj in bpy.data.objects:
    if obj.name.startswith("Viga_"):
        obj.hide_render = True

X0, X1, Y0, Y1 = bath_info["bounds"]
margin = 0.35
cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
width = (X1 - X0) + 2 * margin
height = (Y1 - Y0) + 2 * margin

cam_data = bpy.data.cameras.new("Camera_Plan")
cam_data.type = 'ORTHO'
cam_data.ortho_scale = max(width, height)
cam_obj = bpy.data.objects.new("Camera_Plan", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (cx, cy, 8.0)
cam_obj.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'FLAT'
scene.display.shading.color_type = 'RANDOM'
scene.display.shading.show_shadows = False
res = 1000
if width >= height:
    scene.render.resolution_x = res
    scene.render.resolution_y = round(res * height / width)
else:
    scene.render.resolution_y = res
    scene.render.resolution_x = round(res * width / height)

out = os.path.join(scriptdir, "renders", "banheiro_planta.png")
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("PLAN_OK:", out)
