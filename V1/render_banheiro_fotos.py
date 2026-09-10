"""Só as 2 fotos de interior de banheiro (ducha + lavabo), para iterar o
enquadramento sem re-renderizar as outras 3 vistas de render_more_angles.py.
Mesma iluminação e mesmas câmeras de render_more_angles.py."""
import bpy
import os
import sys
import math
import mathutils

scriptdir = os.path.dirname(os.path.abspath(__file__))
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _ns)

if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import V1.extras as extras
_info = extras.build_all(_ns)
bath_info = _info["bathroom"]
import V1.fixes as fixes
fixes.apply_all()

# --- Iluminação (igual a render_more_angles.py) ---------------------------
sun_elevation = math.radians(18)
sun_rotation = math.radians(228.8)
world = bpy.context.scene.world or bpy.data.worlds.new("World_Ceu")
bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
outw = nt.nodes.new("ShaderNodeOutputWorld")
bg.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
bg.inputs["Strength"].default_value = 1.1
nt.links.new(bg.outputs["Background"], outw.inputs["Surface"])
sd = bpy.data.lights.new("Sol", type='SUN')
sd.energy = 3.5
sd.angle = math.radians(3.0)
sd.color = (1.0, 0.82, 0.6)
so = bpy.data.objects.new("Sol", sd)
bpy.context.collection.objects.link(so)
so.rotation_euler = (math.pi / 2 - sun_elevation, 0.0, sun_rotation + math.pi)

X0, X1, Y0, Y1 = bath_info["bounds"]
XM = bath_info["center_wall_x"]
YM = bath_info["row_split"]
for qi, (qx, qy) in enumerate([
    ((X0 + XM) / 2.0, (Y0 + YM) / 2.0), ((X0 + XM) / 2.0, (YM + Y1) / 2.0),
    ((XM + X1) / 2.0, (Y0 + YM) / 2.0), ((XM + X1) / 2.0, (YM + Y1) / 2.0),
]):
    fd = bpy.data.lights.new(f"Luz_Interna_Banheiro_{qi+1}", type='POINT')
    fd.energy = 14
    fd.shadow_soft_size = 0.35
    fo = bpy.data.objects.new(f"Luz_Interna_Banheiro_{qi+1}", fd)
    bpy.context.collection.objects.link(fo)
    fo.location = (qx, qy, 2.05)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.use_denoising = False
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16
scene.cycles.device = 'CPU'
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'

renders_dir = os.path.join(scriptdir, "renders")
door_y1 = (Y0 + YM) / 2.0


def make_camera(name, location, target, lens=22):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    co = bpy.data.objects.new(name, cd)
    bpy.context.collection.objects.link(co)
    co.location = mathutils.Vector(location)
    d = mathutils.Vector(target) - mathutils.Vector(location)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return co


def render_to(path, res_x, res_y, samples, exposure, vt='AgX'):
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.cycles.samples = samples
    scene.view_settings.exposure = exposure
    scene.view_settings.view_transform = vt
    scene.render.filepath = path
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    scene.view_settings.exposure = 0.0
    scene.view_settings.view_transform = 'Standard'
    print("RENDER_OK:", path)


# --- Ducha ---
dd = bpy.data.objects.get("Banheiro_Parede_Oeste_1_Porta")
wh = dd.hide_render if dd else None
if dd:
    dd.hide_render = True
cam4 = make_camera("Cam_Ducha", (X0 + 0.14, Y0 + 0.14, 1.45),
                   (XM - 0.12, door_y1 + 0.04, 1.55), lens=20)
scene.camera = cam4
render_to(os.path.join(renders_dir, "banheiro_ducha_interior.png"), 1500, 1100, 420, -0.4)
if dd:
    dd.hide_render = wh

# --- Lavabo ---
dl = bpy.data.objects.get("Banheiro_Parede_Leste_1_Porta")
wh2 = dl.hide_render if dl else None
if dl:
    dl.hide_render = True
cam5 = make_camera("Cam_Lavabo", (X1 - 0.16, Y0 + 0.16, 1.55),
                   (XM + 0.22, door_y1 + 0.05, 0.55), lens=22)
scene.camera = cam5
render_to(os.path.join(renders_dir, "banheiro_lavabo_interior.png"), 1500, 1100, 420, 0.6)
if dl:
    dl.hide_render = wh2

print("BANHEIRO_FOTOS_OK")
