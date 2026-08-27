import bpy
import bmesh
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
_extras_info = extras.build_all(_projeto_ns)
bath_info = _extras_info["bathroom"]
counter_info = _extras_info["counter"]

# --- Correções não-destrutivas de bugs do projeto original (ver fixes.py) --
import fixes
fixes.apply_all()

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

# luz de preenchimento fraca para dentro dos banheiros (cabines fechadas)
fill_data = bpy.data.lights.new("Luz_Interna_Banheiro", type='POINT')
fill_data.energy = 45
fill_obj = bpy.data.objects.new("Luz_Interna_Banheiro", fill_data)
bpy.context.collection.objects.link(fill_obj)
X0, X1, Y0, Y1 = bath_info["bounds"]
XM = bath_info["center_wall_x"]
YM = bath_info["row_split"]
fill_obj.location = ((X0 + X1) / 2.0, (Y0 + Y1) / 2.0, 2.4)

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

# --- 1. Vista da entrada (do lado da piscina, olhando para o quiosque) -----
cam1 = make_camera("Cam_Entrada", (-3.0, -9.0, 5.5), (-2.5, 5.0, 1.2), lens=28)
scene.camera = cam1
render_to(os.path.join(renders_dir, "vista_entrada.png"))

# --- 2. Vista aérea 3/4 (ângulo alto, mostrando toda a propriedade) --------
cam2 = make_camera("Cam_Aerea", (-9.0, -6.0, 15.0), (-1.0, 6.0, 0.0), lens=28)
scene.camera = cam2
render_to(os.path.join(renders_dir, "vista_aerea.png"))

# --- 3. Vista interna do corredor, olhando para a bancada/churrasqueira ----
cam3 = make_camera("Cam_Corredor", (0.5, 0.3, 1.65), (2.3, 9.7, 1.2), lens=28)
scene.camera = cam3
render_to(os.path.join(renders_dir, "vista_corredor.png"))

# --- 4. Interior da ducha 1 (porta oeste, linha 1, aberta so para a foto) --
door_ducha1 = bpy.data.objects.get("Banheiro_Parede_Oeste_1_Porta")
was_hidden = door_ducha1.hide_render if door_ducha1 else None
if door_ducha1:
    door_ducha1.hide_render = True
door_y1 = (Y0 + YM) / 2.0
cam4 = make_camera("Cam_Ducha", (X0 - 1.3, door_y1, 1.5), (XM - 0.2, door_y1, 1.1), lens=32)
scene.camera = cam4
render_to(os.path.join(renders_dir, "banheiro_ducha_interior.png"), res_x=1400, res_y=1000, samples=220)
if door_ducha1:
    door_ducha1.hide_render = was_hidden

# --- 5. Interior do lavabo 1 (porta leste, linha 1, aberta so para a foto) -
door_lavabo1 = bpy.data.objects.get("Banheiro_Parede_Leste_1_Porta")
was_hidden2 = door_lavabo1.hide_render if door_lavabo1 else None
if door_lavabo1:
    door_lavabo1.hide_render = True
cam5 = make_camera("Cam_Lavabo", (X1 + 1.3, door_y1, 1.5), (XM + 0.2, door_y1, 1.0), lens=32)
scene.camera = cam5
render_to(os.path.join(renders_dir, "banheiro_lavabo_interior.png"), res_x=1400, res_y=1000, samples=220)
if door_lavabo1:
    door_lavabo1.hide_render = was_hidden2

print("ALL_DONE")
