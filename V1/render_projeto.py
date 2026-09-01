import bpy
import bmesh
import os
import sys
import math
import mathutils

# ---------------------------------------------------------------------------
# 1. EXECUTA O PROJETO ORIGINAL (SEM MODIFICAR O ARQUIVO)
# ---------------------------------------------------------------------------
scriptdir = os.path.dirname(os.path.abspath(__file__))
projeto_path = os.path.join(scriptdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

# ---------------------------------------------------------------------------
# 1a. ADIÇÕES SOLICITADAS PELO USUÁRIO (banheiros, área gourmet, parede,
# sala de estar, mesas de bar) - ver extras.py
# ---------------------------------------------------------------------------
if scriptdir not in sys.path:
    sys.path.insert(0, scriptdir)
import V1.extras as extras
extras.build_all(_projeto_ns)

# ---------------------------------------------------------------------------
# 1b. CORREÇÕES NÃO-DESTRUTIVAS DE BUGS DO PROJETO ORIGINAL (ver fixes.py)
# ---------------------------------------------------------------------------
import V1.fixes as fixes
fixes.apply_all()

# ---------------------------------------------------------------------------
# 2. CÂMERA
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_Render")
cam_data.lens = 32
cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_location = mathutils.Vector((-16.0, -12.0, 9.0))
target = mathutils.Vector((-2.0, 4.0, 0.8))

cam_obj.location = cam_location
direction = target - cam_location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# 3. ILUMINAÇÃO REALISTA (CÉU UNIFORME + SOL DE FIM DE TARDE)
# ---------------------------------------------------------------------------
# Um céu Nishita físico + um Sun lamp em cima somam energia demais e o Nishita
# retorna preto abaixo do horizonte (péssimo para luz indireta dentro da
# piscina). Um fundo de cor plana funciona como luz de preenchimento em todas
# as direções e é fácil de expor corretamente.
#
# Azimute escolhido para o sol aparecer do lado direito da câmera (calculado a
# partir do vetor "direita" da própria câmera) e elevação baixa para simular
# fim de tarde. Nessa direção a luz entra pelo lado aberto do quiosque
# (x=4, a face voltada para o sol) em vez de só raspar o telhado por cima.
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
sun_obj.rotation_euler = (
    math.pi / 2 - sun_elevation,
    0.0,
    sun_rotation + math.pi,
)

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# 4. CONFIGURAÇÃO DE RENDER (CYCLES)
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

# Usa CPU (ambiente WSL2 sem GPU passthrough configurado)
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

output_path = os.path.join(scriptdir, "renders", "projeto_render.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'PNG'

# ---------------------------------------------------------------------------
# 5. RENDERIZA
# ---------------------------------------------------------------------------
bpy.ops.render.render(write_still=True)
print(f"RENDER_OK:{output_path}")
