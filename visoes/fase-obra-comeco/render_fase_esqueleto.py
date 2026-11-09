"""
Fotos da "fase esqueleto" usadas no site (caderno-sequencia.html e galeria):
renders/fase_esqueleto_{estrutura,detalhe_estrutura,fileira_pilares,
lateral,telhado,entrada,aerea,corredor}.png.

Antes essas 8 imagens eram renders avulsos, sem script. Criado em
09/11/2026 (pilares enterrados, sem pedestal) para poder regerá-las:
mesma cena de build_comeco.build() e mesma luz de render_more_angles.py.
As câmeras de entrada/aérea/corredor são as de render_more_angles.py; as
outras 5 reproduzem aproximadamente os enquadramentos originais.

Rodar:
  blender --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python visoes/fase-obra-comeco/render_fase_esqueleto.py
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

REPO_ROOT = os.path.dirname(os.path.dirname(scriptdir))
renders_dir = os.path.join(REPO_ROOT, "renders")

# --- Iluminação (mesma de render_more_angles.py) ----------------------------
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
scene.render.engine = 'CYCLES'
scene.cycles.diffuse_bounces = 8
scene.cycles.max_bounces = 16
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

# Com OpenImageDenoise (Blender 4.2 oficial) dá pra baixar as amostras;
# o 4.0.2 do sistema não tem denoiser -> amostras cheias.
SAMPLES = 220
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.use_denoising = True
    SAMPLES = 48
except TypeError:
    scene.cycles.use_denoising = False


def make_camera(name, location, target, lens=32):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = mathutils.Vector(location)
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj


def render_to(name, cam, res_x=1600, res_y=900):
    scene.camera = cam
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.cycles.samples = SAMPLES
    scene.view_settings.view_transform = 'Standard'
    scene.render.filepath = os.path.join(renders_dir, name)
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print("RENDER_OK:", scene.render.filepath)


# --- Vistas com telhado ------------------------------------------------------
render_to("fase_esqueleto_entrada.png",
          make_camera("Cam_Entrada", (-3.0, -9.0, 5.5), (-2.5, 5.0, 1.2), lens=28))
render_to("fase_esqueleto_aerea.png",
          make_camera("Cam_Aerea", (-9.0, -6.0, 15.0), (-1.0, 6.0, 0.0), lens=28))
render_to("fase_esqueleto_corredor.png",
          make_camera("Cam_Corredor", (0.7, 2.2, 1.65), (1.9, 10.5, 1.2), lens=28))
render_to("fase_esqueleto_telhado.png",
          make_camera("Cam_Telhado", (-9.0, -15.0, 11.0), (0.5, 5.0, 0.5), lens=30),
          1920, 1080)
render_to("fase_esqueleto_lateral.png",
          make_camera("Cam_Lateral", (10.5, 15.5, 2.8), (0.5, 4.0, 1.6), lens=30))
render_to("fase_esqueleto_fileira_pilares.png",
          make_camera("Cam_Fileira", (5.6, 14.5, 1.5), (0.6, 2.0, 2.2), lens=28))
render_to("fase_esqueleto_detalhe_estrutura.png",
          make_camera("Cam_Detalhe", (2.6, 6.6, 0.9), (-0.8, 11.5, 2.4), lens=24))

# --- Planta da estrutura vista de cima, sem a telha ------------------------
telhado = bpy.data.objects.get("Telhado_Zinco_L")
if telhado is not None:
    telhado.hide_render = True
cam_top = make_camera("Cam_Estrutura", (0.9, 6.9, 30.0), (0.9, 6.9, 0.0))
cam_top.data.type = 'ORTHO'
cam_top.data.ortho_scale = 13.8
render_to("fase_esqueleto_estrutura.png", cam_top, 1744, 1900)

print("ALL_DONE")
