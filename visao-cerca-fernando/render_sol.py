"""
Visão "cerca do Fernando" - Quiosque na QUINA SUDESTE da laje da piscina (outro canto, a pedido do
usuario) + prova de incidencia de sol REAL (verao/inverno), mesmo metodo de
renders/scripts/render_sun_study.py (algoritmo NOAA + coordenadas geograficas reais do
terreno, nucleo/sun_geo.py) - NAO usa o azimute/elevacao simplificado de
visões antigas (já removidas).

--- De onde veio a posicao ------------------------------------------------
O usuario marcou 3 pontos de referencia num novo KML ("Projeto sem titulo
(1).kml"): p1, P8, p9 - mesmos nomes dos pilares originais, mas em outro
lugar do terreno. Esses pontos foram convertidos de GPS para o referencial
do projeto usando a MESMA calibracao ja validada em nucleo/sun_geo.py (ancora
em P9, rotacao 133.7 graus, ~3cm de erro conhecido nessa ancora).

Ajuste por Procrustes 2D (rotacao+translacao, sem distorcer escala) usando
os 3 pontos (P1,P8,P9 do projeto <-> p1,P8,p9 novos): rotacao otima -87,5
graus, erro RMS ~1,8 m (esperado - sao cliques aproximados sobre imagem de
satelite, nao um levantamento GPS preciso como o par P1/P9 original).
P8 e P9 (os dois pontos mais proximos entre si) bateram bem (~1-1,3 m);
P1 (a 8 m de P9) teve o pior ajuste (~2,5 m) - provavelmente o clique menos
preciso dos tres.

Em vez de usar o ajuste ruidoso, foi adotada a leitura geometrica limpa que
esses 3 pontos indicam: girar o quiosque -90 graus em Z e ancorar o pilar
P9 (canto reentrante do "L") exatamente na quina SUDESTE da laje da
piscina (Piso_Area_Piscina, x em [-9,0], y em [-7,9.5] -> quina SE = (0,-7)),
o mesmo tipo de ancoragem "canto reentrante = quina da laje" que ja existe
no projeto original (P9 casa com a quina NORDESTE). O lado aberto passa a
apontar para o NORTE (de volta para a laje/piscina), em vez de para OESTE.

Transformacao aplicada a todo objeto do quiosque (pilares, piso, telhado,
paredes, moveis):
    novo_ponto = Rot(-90 graus, Z) aplicado a (ponto - P9_original) + quina_SE
    P9_original = (0.4, 9.5, 0) ; quina_SE = (0.0, -7.0, 0)

Gera 6 imagens (verao 21/12 e inverno 21/06, as 13h/15h/17h, sol na posicao
REAL do ceu para o terreno) em visao-cerca-fernando/renders/sol_{estacao}_{h}h.png, iguais em
formato as de renders/sol_*.png (mesma legenda depois, via
visao-cerca-fernando/annotate_sun_study.py).

Uso (bootstrap obrigatorio - ver memoria piscina-render-import-bootstrap):
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python visao-cerca-fernando/render_sol.py
"""
import bpy
import os
import sys
import math
import json
import mathutils

scriptdir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(scriptdir)
arq_dir = os.path.join(repo_root, "arquitetonico")
if arq_dir not in sys.path:
    sys.path.insert(0, arq_dir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# ---------------------------------------------------------------------------
# 1. CONSTROI O PROJETO ORIGINAL (igual render_sun_study.py, nada mudado)
# ---------------------------------------------------------------------------
projeto_path = os.path.join(arq_dir, "projeto.py")
with open(projeto_path, "r", encoding="utf-8") as f:
    _projeto_ns = {"__name__": "__main__"}
    exec(compile(f.read(), projeto_path, "exec"), _projeto_ns)

import arquitetonico.extras as extras
extras.build_all(_projeto_ns)

import arquitetonico.fixes as fixes
fixes.apply_all()

import nucleo.sun_geo as sun_geo
import arquitetonico.contexto_externo as contexto_externo
contexto_externo.build(_projeto_ns)

# ---------------------------------------------------------------------------
# 2. QUIOSQUE NA QUINA SUDESTE DA LAJE (-90 graus em Z, P9 -> quina SE)
# ---------------------------------------------------------------------------
_manter = {"Piso_Area_Piscina", "Piscina_Cortador_Boolean"}
def _e_piscina(nome):
    return nome in _manter or nome.startswith("Piscina_")

_quiosque = [o for o in bpy.data.objects
             if o.type in {"MESH", "EMPTY"} and not _e_piscina(o.name)
             and not o.name.startswith(("Cerca_", "Cafe_", "Terreno_", "CasaMae_"))]

_pivot = mathutils.Vector((0.4, 9.5, 0.0))   # P9 original (canto reentrante do "L")
_target = mathutils.Vector((0.0, -7.0, 0.0))  # quina SE da laje (Piso_Area_Piscina)
_Rz = mathutils.Matrix.Rotation(math.radians(-90.0), 4, 'Z')
_transform = mathutils.Matrix.Translation(_target) @ _Rz @ mathutils.Matrix.Translation(-_pivot)

for obj in _quiosque:
    obj.matrix_world = _transform @ obj.matrix_world
bpy.context.view_layer.update()

# --- Terreno (gramado) sob a nova area, para o quiosque nao "flutuar" e
#     para receber as sombras do estudo. Mesmo recorte booleano da piscina.
bpy.ops.mesh.primitive_plane_add(size=80.0, location=(-4.0, -8.0, -0.05))
terreno = bpy.context.active_object
terreno.name = "Terreno_CercaFernando"
mat_terreno = bpy.data.materials.new("Material_Terreno_CercaFernando")
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
# 3. SETA DE NORTE VERDADEIRO (mesma logica de render_sun_study.py)
# ---------------------------------------------------------------------------
nx, ny = sun_geo.true_north_vector_project_xy()
arrow_origin = mathutils.Vector((5.0, -5.5, 0.03))
arrow_len = 2.2
arrow_tip = arrow_origin + mathutils.Vector((nx, ny, 0.0)) * arrow_len

mesh_arrow = bpy.data.meshes.new("Mesh_Seta_Norte_CercaFernando")
obj_arrow = bpy.data.objects.new("Seta_Norte_Verdadeiro_CercaFernando", mesh_arrow)
bpy.context.collection.objects.link(obj_arrow)
perp = mathutils.Vector((-ny, nx, 0.0))
w = 0.18
p1 = arrow_origin - perp * w
p2 = arrow_origin + perp * w
p3 = arrow_tip
p4 = arrow_tip + perp * (w * 2.2) - mathutils.Vector((nx, ny, 0.0)) * 0.35
p5 = arrow_tip - perp * (w * 2.2) - mathutils.Vector((nx, ny, 0.0)) * 0.35
verts = [p1, p2, p3, p4, arrow_tip + mathutils.Vector((nx, ny, 0.0)) * 0.35, p5]
mesh_arrow.from_pydata([tuple(v) for v in verts], [], [[0, 1, 2], [3, 4, 5]])
mesh_arrow.update()
mat_norte = bpy.data.materials.new("Material_Seta_Norte_CercaFernando")
mat_norte.use_nodes = True
mat_norte.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.05, 0.05, 1.0)
mat_norte.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
obj_arrow.data.materials.append(mat_norte)

# ---------------------------------------------------------------------------
# 4. CAMERA - ponto de vista REAL pedido pelo usuario (lat -21.3530973,
#    lon -45.9900076 -> convertido pro referencial do projeto com a mesma
#    calibracao de nucleo/sun_geo.py, ancora P1/P9): (-3.93, 7.63), na borda
#    norte do deck/piscina, olhando para o quiosque na nova posicao (quina
#    SE) - a piscina fica em primeiro plano, o quiosque ao fundo.
# ---------------------------------------------------------------------------
cam_data = bpy.data.cameras.new("Camera_Render")
cam_data.lens = 20   # mais aberta p/ pegar a cerca/cafe no entorno tambem
cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
bpy.context.collection.objects.link(cam_obj)

cam_location = mathutils.Vector((-3.93, 7.63, 1.6))   # altura de olho humano
target = mathutils.Vector((-2.5, -7.5, 0.8))          # centro do quiosque na nova posicao
cam_obj.location = cam_location
direction = target - cam_location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

# ---------------------------------------------------------------------------
# 5. MUNDO (fundo fraco, igual render_sun_study.py - sombra tem que aparecer)
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
bg_node.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)
bg_node.inputs["Strength"].default_value = 0.3
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])

scene_view = bpy.context.scene.view_settings
scene_view.view_transform = 'Standard'
scene_view.exposure = 0.0

# ---------------------------------------------------------------------------
# 6. RENDER (Cycles, denoiser OIDN se disponivel)
# ---------------------------------------------------------------------------
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
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

has_denoiser = False
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    has_denoiser = True
    scene.cycles.use_denoising = True
    scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
    scene.cycles.denoising_prefilter = 'ACCURATE'
    scene.cycles.samples = 96
except TypeError:
    scene.cycles.use_denoising = False
    scene.cycles.samples = 300

print(f"Denoiser disponivel: {has_denoiser}, samples={scene.cycles.samples}")

# ---------------------------------------------------------------------------
# 7. SOL: 6 combinacoes (verao/inverno x 13h/15h/17h), posicao REAL (NOAA)
# ---------------------------------------------------------------------------
sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.angle = math.radians(3.0)
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)

HORAS = [15, 16, 17, 18, 19]
CENAS = [("verao", 2026, 12, 21, h, 0) for h in HORAS] \
    + [("inverno", 2026, 6, 21, h, 0) for h in HORAS]

out_dir = os.path.join(scriptdir, "renders")
os.makedirs(out_dir, exist_ok=True)

region = bpy.context.scene.render
from bpy_extras.object_utils import world_to_camera_view
co2d = world_to_camera_view(bpy.context.scene, cam_obj, arrow_tip)
arrow_tip_px = (co2d.x * region.resolution_x, (1 - co2d.y) * region.resolution_y)

meta = {"cenas": [], "posicao": "Cerca do Fernando - quina sudeste da laje (-90 graus, P9 ancorado em (0,-7))"}

for estacao, y, m, d, h, mi in CENAS:
    azimuth, elevation = sun_geo.solar_position(y, m, d, h, mi)
    dx, dy, dz = sun_geo.sun_direction_project_xyz(azimuth, elevation)
    travel_dir = mathutils.Vector((-dx, -dy, -dz))
    sun_obj.rotation_euler = travel_dir.to_track_quat('-Z', 'Y').to_euler()

    t = max(0.0, min(1.0, elevation / 70.0))
    sun_data.energy = 5.0 + 3.0 * t
    sun_data.color = (1.0, 0.55 + 0.35 * t, 0.35 + 0.45 * t)

    fname = f"sol_{estacao}_{h:02d}h.png"
    fpath = os.path.join(out_dir, fname)
    scene.render.filepath = fpath
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print(f"RENDER_OK:{fpath} azimuth={azimuth:.1f} elevation={elevation:.1f}")

    meta["cenas"].append({
        "arquivo": fname, "estacao": estacao,
        "data": f"{d:02d}/{m:02d}/{y}", "hora": f"{h:02d}:{mi:02d}",
        "azimute_real_deg": round(azimuth, 1),
        "elevacao_deg": round(elevation, 1),
    })

meta["arrow_tip_px"] = arrow_tip_px
meta["rotation_offset_deg"] = sun_geo.ROTATION_OFFSET_DEG
meta["lat"] = sun_geo.LAT
meta["lon"] = sun_geo.LON
with open(os.path.join(out_dir, "sun_study_meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print("ALLDONE_SUN_STUDY_CERCA_FERNANDO")
