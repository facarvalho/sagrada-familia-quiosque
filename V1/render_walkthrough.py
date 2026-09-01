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
import V1.extras as extras
extras.build_all(_projeto_ns)

# --- Correções não-destrutivas de bugs do projeto original (ver fixes.py) --
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

# ---------------------------------------------------------------------------
# Caminho de câmera (passeio a pé por toda a propriedade)
# ---------------------------------------------------------------------------
EYE_Z = 1.65
waypoints = [
    (3.0, -7.0, EYE_Z),   # inicio, ao sul da piscina
    (-4.5, -5.5, EYE_Z),  # borda sul da piscina (piscina deslocada 1m)
    (-4.7, 5.0, EYE_Z),   # ao longo da borda oeste da piscina
    (-1.0, 8.8, EYE_Z),   # curva em direção ao quiosque, perto dos banheiros
    (0.9, 1.2, EYE_Z),    # entra no corredor pelo lado da piscina (oeste),
                          # perto da área gourmet/mesa de 8 lugares
    (0.9, 6.0, EYE_Z),    # passa pelas mesas de bar
    (0.6, 9.0, EYE_Z),    # aproxima da sala de estar, pelo lado livre (oeste)
    (0.6, 11.0, EYE_Z),   # termina ao lado da sala de estar, sem cruzar os móveis
]

curve_data = bpy.data.curves.new("CaminhoPasseio", type='CURVE')
curve_data.dimensions = '3D'
spline = curve_data.splines.new('BEZIER')
spline.bezier_points.add(len(waypoints) - 1)
for i, co in enumerate(waypoints):
    bp = spline.bezier_points[i]
    bp.co = co
    bp.handle_left_type = 'AUTO'
    bp.handle_right_type = 'AUTO'
curve_obj = bpy.data.objects.new("CaminhoPasseio", curve_data)
bpy.context.collection.objects.link(curve_obj)

FPS = 12
DURATION_S = 20
TOTAL_FRAMES = FPS * DURATION_S

look_empty = bpy.data.objects.new("AlvoOlhar", None)
bpy.context.collection.objects.link(look_empty)
c_look = look_empty.constraints.new('FOLLOW_PATH')
c_look.target = curve_obj
c_look.use_fixed_location = True
c_look.offset_factor = 0.03
c_look.keyframe_insert(data_path="offset_factor", frame=1)
c_look.offset_factor = 1.0
c_look.keyframe_insert(data_path="offset_factor", frame=TOTAL_FRAMES)

cam_data = bpy.data.cameras.new("Cam_Passeio")
cam_data.lens = 28
cam_obj = bpy.data.objects.new("Cam_Passeio", cam_data)
bpy.context.collection.objects.link(cam_obj)
c_follow = cam_obj.constraints.new('FOLLOW_PATH')
c_follow.target = curve_obj
c_follow.use_fixed_location = True
c_follow.use_curve_follow = False
c_follow.offset_factor = 0.0
c_follow.keyframe_insert(data_path="offset_factor", frame=1)
c_follow.offset_factor = 1.0
c_follow.keyframe_insert(data_path="offset_factor", frame=TOTAL_FRAMES)

c_track = cam_obj.constraints.new('TRACK_TO')
c_track.target = look_empty
c_track.track_axis = 'TRACK_NEGATIVE_Z'
c_track.up_axis = 'UP_Y'

# interpolação linear (ritmo de caminhada constante)
for obj, cname in [(cam_obj, "Follow Path"), (look_empty, "Follow Path")]:
    action = obj.animation_data.action
    for fcurve in action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'

bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# Configuração de render (qualidade reduzida, otimizada para animação)
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES
scene.render.fps = FPS

scene.view_settings.view_transform = 'Standard'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.use_denoising = False
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'
scene.cycles.device = 'CPU'

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.gopsize = 12
scene.render.ffmpeg.audio_codec = 'NONE'

renders_dir = os.path.join(scriptdir, "renders")
os.makedirs(renders_dir, exist_ok=True)
scene.render.filepath = os.path.join(renders_dir, "passeio_quiosque.mp4")

print(f"TOTAL_FRAMES={TOTAL_FRAMES} FPS={FPS}")
bpy.ops.render.render(animation=True)
print("WALKTHROUGH_OK:", scene.render.filepath)
