"""
V5 - Quiosque da V4 GIRADO 90 GRAUS NO SENTIDO HORARIO e realinhado a laje:
o "L" passa a abracar a borda NORTE da laje da piscina, com a perna
principal correndo em L-O e o lado aberto voltado para a piscina (sul).

  1. Constroi a cena original (projeto.py + extras.py + fixes.py) sem tocar
     nos arquivos originais.
  2. Aplica o espelhamento da V4 (quina NW), gira -90 graus em Z em torno
     do centro do quiosque e translada para encostar a face aberta na
     borda norte da laje e a face oeste na borda oeste da laje.
  3. Gera SOMENTE a vista "projeto_render.png", uma por hora cheia das
     07h as 18h, com o Sol na posicao real do ceu para a data/local abaixo.
     Saidas em V5/renders/projeto_render_7h.png ... _18h.png

Local/data assumidos para o calculo solar (ajuste as constantes se o
terreno ficar em outra cidade):
    LAT/LON = Sao Paulo/SP   |   fuso -3   |   data = 2026-08-31

Execucao:
    blender --background --factory-startup --python V5/render_v5_sol.py
"""
import bpy
import os
import sys
import math
import datetime
import mathutils

# ---------------------------------------------------------------------------
# PARAMETROS DO ESTUDO SOLAR  (edite aqui se o terreno for em outra cidade)
# ---------------------------------------------------------------------------
LAT_DEG = -23.55          # latitude  (sul negativo)
LON_DEG = -46.63          # longitude (oeste negativo)
TZ_HOURS = -3.0           # fuso horario (Brasilia)
DATA = datetime.date(2026, 8, 31)
HORAS = [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

# ---------------------------------------------------------------------------
# 1. EXECUTA O PROJETO ORIGINAL + EXTRAS + FIXES (sem modificar os arquivos)
# ---------------------------------------------------------------------------
scriptdir = os.path.dirname(os.path.abspath(__file__))
rootdir = os.path.join(os.path.dirname(scriptdir), "V1")  # projeto principal foi movido para V1/
if rootdir not in sys.path:
    sys.path.insert(0, rootdir)

projeto_path = os.path.join(rootdir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

import extras
extras.build_all(_projeto_ns)

import fixes
fixes.apply_all()

# ---------------------------------------------------------------------------
# 2. V5 = V4 GIRADO 90 GRAUS NO SENTIDO HORARIO + ALINHADO A LAJE
# ---------------------------------------------------------------------------
# Parte da posicao da V4 (quiosque espelhado, "L" na quina NW, perna
# principal N-S ao longo da borda oeste, lado aberto para leste).
# Depois:
#   a) gira -90 graus em Z (horario visto de cima) em torno do centro do
#      quiosque -> a perna de 12 m passa a correr em L-O e o lado aberto
#      passa a apontar para -Y (sul).
#   b) translada para encaixar o "L" na borda NORTE da laje: face aberta
#      (sul) rente a borda norte da laje (y = 9.5) e face oeste do quiosque
#      rente a borda oeste da laje (x = -9), abraçando a quina NW.
_manter = {"Piso_Area_Piscina", "Piscina_Cortador_Boolean"}
def _e_piscina(nome):
    return nome in _manter or nome.startswith("Piscina_")

_quiosque = [o for o in bpy.data.objects
             if o.type in {"MESH", "EMPTY"} and not _e_piscina(o.name)]

_deck = bpy.data.objects["Piso_Area_Piscina"]
_dpts = [_deck.matrix_world @ mathutils.Vector(c) for c in _deck.bound_box]
deck_min_x = min(p.x for p in _dpts); deck_max_x = max(p.x for p in _dpts)
deck_min_y = min(p.y for p in _dpts); deck_max_y = max(p.y for p in _dpts)
deck_cx = (deck_min_x + deck_max_x) / 2.0

# --- V4: espelho em torno do eixo N-S da laje ---
_mirror = mathutils.Matrix((
    (-1.0, 0.0, 0.0, 2.0 * deck_cx),
    (0.0, 1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0, 0.0),
    (0.0, 0.0, 0.0, 1.0),
))
for obj in _quiosque:
    obj.matrix_world = _mirror @ obj.matrix_world
bpy.context.view_layer.update()

def _bbox_quiosque():
    pts = []
    for o in _quiosque:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ mathutils.Vector(c))
    return (min(p.x for p in pts), max(p.x for p in pts),
            min(p.y for p in pts), max(p.y for p in pts))

# --- a) rotacao 90 graus horaria em torno do centro do quiosque ---
qminx, qmaxx, qminy, qmaxy = _bbox_quiosque()
qcx, qcy = (qminx + qmaxx) / 2.0, (qminy + qmaxy) / 2.0
_rot_cw = (
    mathutils.Matrix.Translation((qcx, qcy, 0.0))
    @ mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Z')
    @ mathutils.Matrix.Translation((-qcx, -qcy, 0.0))
)
for obj in _quiosque:
    obj.matrix_world = _rot_cw @ obj.matrix_world
bpy.context.view_layer.update()

# --- b) alinhamento: face sul (aberta) na borda norte da laje;
#        face oeste na borda oeste da laje ---
qminx, qmaxx, qminy, qmaxy = _bbox_quiosque()
dx = deck_min_x - qminx
dy = deck_max_y - qminy
_align = mathutils.Matrix.Translation((dx, dy, 0.0))
for obj in _quiosque:
    obj.matrix_world = _align @ obj.matrix_world
bpy.context.view_layer.update()

# --- Terreno (gramado) sob a area, para o quiosque nao "flutuar" e para
#     receber as sombras do estudo. Recebe o mesmo recorte booleano da
#     piscina para nao tapar a agua.
bpy.ops.mesh.primitive_plane_add(size=80.0, location=(-6.0, -2.0, -0.05))
terreno = bpy.context.active_object
terreno.name = "Terreno_V5"
mat_terreno = bpy.data.materials.new("Material_Terreno_V5")
mat_terreno.use_nodes = True
_bsdf = mat_terreno.node_tree.nodes.get("Principled BSDF")
_bsdf.inputs["Base Color"].default_value = (0.40, 0.46, 0.34, 1.0)
_bsdf.inputs["Roughness"].default_value = 0.95
terreno.data.materials.append(mat_terreno)
_cutter = bpy.data.objects.get("Piscina_Cortador_Boolean")
if _cutter:
    _mb = terreno.modifiers.new(name="Corte_Piscina", type='BOOLEAN')
    _mb.operation = 'DIFFERENCE'
    _mb.object = _cutter

# ---------------------------------------------------------------------------
# 3. CAMERA  (mesmo enquadramento do render principal do projeto)
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_Render")
cam_data.lens = 33
cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_location = mathutils.Vector((-19.0, -18.0, 15.0))
target = mathutils.Vector((-2.0, 8.0, 1.0))
cam_obj.location = cam_location
direction = target - cam_location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# 4. POSICAO REAL DO SOL  (algoritmo NOAA)
# ---------------------------------------------------------------------------
def sol_elev_azim(lat_deg, lon_deg, tz_h, data, hora_decimal):
    """Retorna (elevacao, azimute) em graus. Azimute: 0=N, 90=L, 180=S, 270=O."""
    N = data.timetuple().tm_yday
    gamma = 2.0 * math.pi / 365.0 * (N - 1 + (hora_decimal - 12.0) / 24.0)

    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.001480 * math.sin(3 * gamma)
    )

    time_offset = eqtime + 4.0 * lon_deg - 60.0 * tz_h
    tst = hora_decimal * 60.0 + time_offset          # minutos de tempo solar verdadeiro
    ha = math.radians(tst / 4.0 - 180.0)             # angulo horario

    lat = math.radians(lat_deg)
    cos_zen = (math.sin(lat) * math.sin(decl)
               + math.cos(lat) * math.cos(decl) * math.cos(ha))
    cos_zen = max(-1.0, min(1.0, cos_zen))
    zen = math.acos(cos_zen)
    elev = 90.0 - math.degrees(zen)

    denom = math.cos(lat) * math.sin(zen)
    if abs(denom) < 1e-6:
        azim = 180.0 if lat_deg >= decl else 0.0
    else:
        cos_az = (math.sin(lat) * math.cos(zen) - math.sin(decl)) / denom
        cos_az = max(-1.0, min(1.0, cos_az))
        ac = math.degrees(math.acos(cos_az))
        # convencao NOAA: azimute em graus, horario a partir do Norte
        if ha > 0:                                    # tarde
            azim = (ac + 180.0) % 360.0
        else:                                         # manha
            azim = (540.0 - ac) % 360.0
    return elev, azim


# ---------------------------------------------------------------------------
# 5. MUNDO + SOL  (fundo de ceu plano como luz de preenchimento + Sun lamp)
# ---------------------------------------------------------------------------
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World_Ceu")
    bpy.context.scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
bg_node = nt.nodes.new("ShaderNodeBackground")
out_node = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.angle = math.radians(0.53)      # disco solar real
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# 6. CONFIGURACAO DE RENDER (CYCLES)
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
scene.render.image_settings.file_format = 'PNG'

outdir = os.path.join(scriptdir, "renders")
os.makedirs(outdir, exist_ok=True)

# ---------------------------------------------------------------------------
# 7. LOOP: um render por hora, com o Sol na posicao real
# ---------------------------------------------------------------------------
print(f"V3 | Estudo solar {DATA.isoformat()} | lat {LAT_DEG} lon {LON_DEG} tz {TZ_HOURS}")
for h in HORAS:
    elev, azim = sol_elev_azim(LAT_DEG, LON_DEG, TZ_HOURS, DATA, float(h))

    if elev <= 0.5:
        # Sol abaixo (ou rente) do horizonte: sem luz direta, cena em penumbra.
        sun_data.energy = 0.0
        bg_node.inputs["Color"].default_value = (0.06, 0.07, 0.10, 1.0)
        bg_node.inputs["Strength"].default_value = 0.5
    else:
        sun_data.energy = 4.0
        # cor mais quente e ceu mais fraco quando o sol esta baixo
        q = max(0.0, min(1.0, elev / 40.0))
        sun_data.color = (1.0, 0.72 + 0.18 * q, 0.45 + 0.35 * q)
        bg_node.inputs["Color"].default_value = (0.48, 0.56, 0.68, 1.0)
        bg_node.inputs["Strength"].default_value = 0.7 + 0.6 * q

    sun_elevation = math.radians(elev)
    sun_rotation = math.radians(-azim)        # convencao do rig (ver projeto)
    sun_obj.rotation_euler = (
        math.pi / 2 - sun_elevation,
        0.0,
        sun_rotation + math.pi,
    )

    out_path = os.path.join(outdir, f"projeto_render_{h}h.png")
    scene.render.filepath = out_path
    print(f"  {h:02d}h -> elev {elev:5.1f} deg  azim {azim:5.1f} deg  -> {os.path.basename(out_path)}")
    bpy.ops.render.render(write_still=True)

print("RENDER_V3_OK")
