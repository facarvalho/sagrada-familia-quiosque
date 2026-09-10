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

import V1.fixes as fixes
fixes.apply_all()

altura_piso = _projeto_ns["altura_piso"]

# ---------------------------------------------------------------------------
# Iluminacao: sol de fim de tarde + luzes internas suaves e fora de quadro
# ---------------------------------------------------------------------------
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
bg_node.inputs["Strength"].default_value = 1.35
nt.links.new(bg_node.outputs["Background"], out_node.inputs["Surface"])
sun_data = bpy.data.lights.new("Sol", type='SUN')
sun_data.energy = 3.3
sun_data.angle = math.radians(3.0)
sun_data.color = (1.0, 0.82, 0.6)
sun_obj = bpy.data.objects.new("Sol", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.pi / 2 - sun_elevation, 0.0, sun_rotation + math.pi)


def add_point(name, loc, energy, color=(1.0, 0.95, 0.88), soft=0.6):
    ld = bpy.data.lights.new(name, type='POINT')
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = soft
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    return ob, ld


# --- geometria util dos modulos -----------------------------------------
bX0, bX1, bY0, bY1 = info["bathroom"]["bounds"]
bXM = info["bathroom"]["center_wall_x"]
bYM = info["bathroom"]["row_split"]
pia_cx, pia_cy, pia_top = info["bathroom"]["pia_comunitaria"]
cX_front, cX_wall, cY0, cY1 = info["counter"]["bounds"]
c_top = info["counter"]["top_z"]
c_sink_cy = cY0 + 0.55
fr_cx, fr_cy = info["appliances"]["fridge_pos"]
st_cx, st_cy = info["appliances"]["stove_pos"]
tv_x, tv_y, tv_z = info["tv"]["position"]

cy_cab = (bYM + bY1) / 2.0          # cabine NORTE (a que o passeio visita)
wc_bowl_x = bXM + 0.31
lid_hinge_x = bXM + 0.14
dsouth, dnorth = cy_cab - 0.30, cy_cab + 0.30   # vao das portas da cabine norte

# luzes internas: energia baixa, fonte grande, sempre atras/acima da camera
add_point("Luz_Ducha", (bX0 + 0.25, cy_cab, altura_piso + 1.95), 14, soft=0.7)
add_point("Luz_Sanitario", (bX1 - 0.20, cy_cab, altura_piso + 1.95), 13, soft=0.7)
add_point("Luz_Corredor", (1.7, 7.6, altura_piso + 2.3), 22)
add_point("Luz_Gourmet", (cX_wall - 1.0, c_sink_cy + 0.2, altura_piso + 2.25), 34)
add_point("Luz_Cozinha", (2.3, 3.0, altura_piso + 2.25), 34)
add_point("Luz_Pia_Comunitaria", (pia_cx, pia_cy - 0.9, altura_piso + 1.95), 20)
add_point("Luz_Sala", (2.3, 10.75, altura_piso + 2.35), 26)

_, fridge_light = add_point("Luz_Geladeira", (fr_cx, fr_cy, altura_piso + 1.15), 0.0,
                            color=(1.0, 0.97, 0.9), soft=0.12)
_, stove_light = add_point("Luz_Fogao", (st_cx, st_cy, altura_piso + 1.2), 0.0,
                           color=(1.0, 0.6, 0.3), soft=0.15)
_, tv_light = add_point("Luz_TV", (tv_x - 0.7, tv_y, tv_z), 0.0,
                        color=(0.6, 0.72, 1.0), soft=0.5)

# ---------------------------------------------------------------------------
# Materiais e objetos animados (so para o passeio)
# ---------------------------------------------------------------------------
def _mat(name, color, roughness=0.5, metallic=0.0, alpha=1.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = color
        b.inputs["Roughness"].default_value = roughness
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        m.blend_method = 'BLEND'
    return m


def add_bump(mat, scale=45.0, strength=0.25):
    """Bump procedural (noise) numa material existente - da textura a brita."""
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if not bsdf:
        return
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 6.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


mat_louca = bpy.data.materials.get("Material_Banheiro_Louca") or _mat(
    "Material_Banheiro_Louca", (0.90, 0.89, 0.86, 1.0), roughness=0.35)
mat_inox = bpy.data.materials.get("Material_Eletro_Inox") or _mat(
    "Material_Eletro_Inox", (0.72, 0.73, 0.75, 1.0), roughness=0.3, metallic=0.85)
mat_agua = _mat("Material_Agua_Torneira", (0.78, 0.88, 0.98, 1.0), roughness=0.1, alpha=0.55)
for _bn in ("Material_Banheiro_Brita",):
    _bm = bpy.data.materials.get(_bn)
    if _bm:
        add_bump(_bm, scale=55.0, strength=0.35)

mat_chama = _mat("Material_Chama_Fogao", (0.02, 0.02, 0.02, 1.0))
_bc = mat_chama.node_tree.nodes.get("Principled BSDF")
if _bc:
    _bc.inputs["Emission Color"].default_value = (1.0, 0.42, 0.10, 1.0)
    _bc.inputs["Emission Strength"].default_value = 8.0
mat_tv_on = _mat("Material_TV_Ligada", (0.02, 0.02, 0.02, 1.0))
_bt = mat_tv_on.node_tree.nodes.get("Principled BSDF")
if _bt:
    _bt.inputs["Emission Color"].default_value = (0.55, 0.68, 1.0, 1.0)
    _bt.inputs["Emission Strength"].default_value = 0.0
tv_emit = _bt.inputs["Emission Strength"] if _bt else None


def _cube(name, loc, scale, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.rotation_euler = rot
    if mat:
        o.data.materials.append(mat)
    return o


def _cyl(name, loc, r, d, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = rot
    if mat:
        o.data.materials.append(mat)
    return o


def _origin_to(o, point):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.context.scene.cursor.location = point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


# --- portas das cabines visitadas: giram para abrir --------------------
porta_ducha = bpy.data.objects.get("Banheiro_Parede_Oeste_2_Porta")
porta_wc = bpy.data.objects.get("Banheiro_Parede_Leste_2_Porta")
if porta_ducha:
    _origin_to(porta_ducha, (bX0, dsouth, altura_piso + 0.9))
if porta_wc:
    _origin_to(porta_wc, (bX1, dnorth, altura_piso + 0.9))

# tampa do vaso (cabine norte) - dobradica atras do assento
tampa = _cube("Tampa_Vaso_Anim", (lid_hinge_x + 0.20, cy_cab, altura_piso + 0.445),
              (0.42, 0.32, 0.03), mat_louca)
_origin_to(tampa, (lid_hinge_x, cy_cab, altura_piso + 0.445))

# porta da geladeira - dobradica na aresta leste
fridge_door = _cube("Geladeira_Porta_Anim", (fr_cx - 0.02, fr_cy + 0.335, altura_piso + 0.92),
                    (0.64, 0.05, 1.62), mat_inox)
_origin_to(fridge_door, (fr_cx + 0.32, fr_cy + 0.335, altura_piso + 0.92))

# chamas do fogao (4 bocas)
flames = []
for i, sx in enumerate((-1, 1)):
    for j, sy in enumerate((-1, 1)):
        bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.0, depth=0.10,
                                        location=(st_cx + sx * 0.132, st_cy + sy * 0.132,
                                                  altura_piso + 0.98))
        o = bpy.context.active_object
        o.name = f"Chama_Fogao_{i}_{j}"
        o.data.materials.append(mat_chama)
        flames.append(o)

# jatos de agua
agua_bancada = _cyl("Agua_Torneira_Bancada", (cX_wall - 0.34, c_sink_cy, c_top - 0.06),
                    0.011, 0.26, mat_agua)
agua_pia = _cyl("Agua_Pia_Comunitaria", (pia_cx, bY0 - 0.18, pia_top - 0.02),
                0.011, 0.34, mat_agua)

# tela da TV ligada
tv_screen = _cube("TV_Tela_Ligada", (tv_x - 0.03, tv_y, tv_z), (0.01, 1.24, 0.70), mat_tv_on)

# --- gramado apenas ao SUL do deck (nunca sob a piscina/quiosque) --------
_grass = _mat("Material_Gramado", (0.20, 0.28, 0.13, 1.0), roughness=1.0)
_gravel = _mat("Material_Caminho_Saida", (0.55, 0.53, 0.49, 1.0), roughness=0.95)
add_bump(_gravel, scale=90.0, strength=0.3)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-1.3, -34.0, -0.02))
_g = bpy.context.active_object
_g.name = "Gramado_Passeio"
_g.scale = (90.0, 55.0, 1.0)
_g.data.materials.append(_grass)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-1.3, -28.0, -0.015))
_r = bpy.context.active_object
_r.name = "Caminho_Saida"
_r.scale = (1.5, 48.0, 1.0)
_r.data.materials.append(_gravel)

# ---------------------------------------------------------------------------
# Camera + alvo do olhar (keyframes)
# ---------------------------------------------------------------------------
FPS = 20
EZ = 1.60

cam_data = bpy.data.cameras.new("Cam_Passeio")
cam_data.lens = 24
cam_obj = bpy.data.objects.new("Cam_Passeio", cam_data)
bpy.context.collection.objects.link(cam_obj)
look = bpy.data.objects.new("AlvoOlhar", None)
bpy.context.collection.objects.link(look)
trk = cam_obj.constraints.new('TRACK_TO')
trk.target = look
trk.track_axis = 'TRACK_NEGATIVE_Z'
trk.up_axis = 'UP_Y'
bpy.context.scene.camera = cam_obj

_last_t = [0.0]


def _f(t):
    return 1 + round(t * FPS)


def kc(t, loc):
    cam_obj.location = loc
    cam_obj.keyframe_insert("location", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kl(t, loc):
    look.location = loc
    look.keyframe_insert("location", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kw(t, loc, tgt):
    kc(t, loc)
    kl(t, tgt)


def krot(o, t, rot):
    if o is None:
        return
    o.rotation_euler = rot
    o.keyframe_insert("rotation_euler", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kvis(o, t, visible):
    o.hide_render = not visible
    o.hide_viewport = not visible
    o.keyframe_insert("hide_render", frame=_f(t))
    o.keyframe_insert("hide_viewport", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kscale(o, t, s):
    o.scale = (s, s, s)
    o.keyframe_insert("scale", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kenergy(ld, t, e):
    ld.energy = e
    ld.keyframe_insert("energy", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


def kemit(inp, t, v):
    inp.default_value = v
    inp.keyframe_insert("default_value", frame=_f(t))
    _last_t[0] = max(_last_t[0], t)


# ============================== ROTEIRO =================================
# 1) Chega pelo deck, sobe pela borda LESTE da piscina ate a ala
kw(0.0,  (-1.0, -6.3, EZ),  (-2.6, -2.0, 1.4))
kw(2.2,  (-1.7, -1.6, EZ),  (-2.3, 4.5, 1.45))
kw(4.2,  (-2.2, 5.2, EZ),   (-3.0, 9.0, 1.5))
kw(5.8,  (-3.9, 9.2, EZ),   (-2.35, 11.25, 1.4))       # afastado no deck, ve a fachada oeste da ala

# porta da ducha abre PARA FORA (lado da piscina), antes da camera chegar
krot(porta_ducha, 4.2, (0, 0, 0))
krot(porta_ducha, 5.6, (0, 0, math.radians(80)))

# 2) ENTRA NA DUCHA -> panoramica suave do CHAO ate o TETO (crivo + respiro)
#    Porta aberta p/ oeste (folha rente ao muro, y 11.0-11.13). A camera sobe
#    pela calcada rente ao muro e cruza o vao pela METADE NORTE (y > 11.2),
#    ao norte da folha.
kw(7.2,  (-3.0, 9.4, 1.60),    (-2.3, 11.3, 1.40))     # deck -> calcada, fachada em quadro
kw(8.6,  (-2.9, 11.3, 1.58),   (-2.0, 11.5, 1.30))     # na calcada, a NW da folha aberta
kw(9.6,  (-2.3, 11.55, 1.56),  (-1.5, 11.42, 1.20))    # cruza o vao pela metade norte
kw(10.6, (-1.95, 11.42, 1.54), (-1.50, 11.32, 0.10))   # dentro: olha o chao (brita)
kw(12.2, (-1.93, 11.38, 1.52), (-1.35, 11.33, 1.50))   # sobe pelo crivo/coluna
kw(13.8, (-1.90, 11.34, 1.50), (-1.35, 11.34, 2.28))   # topo: respiro parede/telhado
kw(14.8, (-1.90, 11.34, 1.50), (-1.35, 11.34, 2.28))

# 3) Sai da ducha, contorna pelo sul (fora da ala) e entra no SANITARIO.
#    A porta fica na parede leste e abre PARA FORA (corredor / sala).
kw(16.2, (-2.5, 9.9, EZ),    (-1.2, 8.9, 1.5))
kw(17.4, (-0.3, 8.7, EZ),    (0.9, 9.6, 1.5))
kw(18.6, (1.6, 9.7, EZ),     (0.7, 11.0, 1.5))         # ja a leste da ala, no corredor
krot(porta_wc, 16.8, (0, 0, 0))
krot(porta_wc, 18.4, (0, 0, math.radians(75)))         # abre para fora (corredor)
kw(20.0, (1.55, 10.5, EZ),   (-0.2, 11.35, 1.35))      # afastado, de frente p/ a porta aberta
kw(21.2, (0.62, 11.10, 1.58), (-0.6, 11.32, 0.9))      # passa a folha pelo sul, entra
kw(22.2, (0.18, 11.32, 1.55), (-0.6, 11.32, 0.08))     # dentro: olha o chao
kw(23.6, (0.16, 11.32, 1.52), (-0.62, 11.33, 2.05))    # sobe: parede/verga

# 4) ABRE A TAMPA do vaso
kw(25.0, (0.12, 11.32, 1.40), (wc_bowl_x, 11.34, 0.42))
krot(tampa, 25.2, (0, 0, 0))
krot(tampa, 26.6, (0, math.radians(-95), 0))
kw(27.4, (0.13, 11.32, 1.42), (wc_bowl_x, 11.34, 0.32))
kw(28.2, (0.13, 11.32, 1.42), (wc_bowl_x, 11.34, 0.32))

# 5) TOUR pelo corredor (desviando das mesas de bar) ate a bancada gourmet
kw(30.2, (0.8, 10.4, 1.62), (0.9, 8.0, 1.5))
kw(32.0, (0.9, 7.8, 1.62),  (2.3, 6.0, 1.45))
kw(34.0, (2.5, 5.2, 1.55),  (3.3, 3.0, 1.3))
kw(35.4, (2.85, 3.1, 1.42), (cX_wall - 0.32, c_sink_cy, 0.85))

# 6) ABRE A TORNEIRA da bancada
kvis(agua_bancada, 0.0, False)
kvis(agua_bancada, 36.0, True)
kw(37.2, (2.85, 3.1, 1.42), (cX_wall - 0.32, c_sink_cy, 0.85))

# 7) GELADEIRA - abre a porta (acende a luz interna)
kw(38.6, (2.95, 3.2, 1.55), (fr_cx, fr_cy, 1.15))
krot(fridge_door, 38.8, (0, 0, 0))
krot(fridge_door, 40.2, (0, 0, math.radians(-118)))
kenergy(fridge_light, 39.1, 0.0)
kenergy(fridge_light, 40.2, 26.0)
kw(41.0, (2.9, 3.25, 1.55), (fr_cx, fr_cy, 1.2))

# 8) FOGAO - acende as 4 bocas em sequencia
kw(42.4, (1.55, 2.95, 1.42), (st_cx, st_cy, 0.95))
for k, fl in enumerate(flames):
    t0 = 43.0 + k * 0.35
    kvis(fl, 0.0, False)
    kscale(fl, 0.0, 0.1)
    kvis(fl, t0, True)
    kscale(fl, t0, 0.1)
    kscale(fl, t0 + 0.4, 1.0)
kenergy(stove_light, 42.9, 0.0)
kenergy(stove_light, 44.8, 9.0)
kw(45.2, (1.5, 2.95, 1.42), (st_cx, st_cy, 0.97))
kw(46.0, (1.5, 2.95, 1.42), (st_cx, st_cy, 0.97))

# 9) Volta pelo corredor ate a PIA COMUNITARIA (canto do L) - lava as maos
kw(47.6, (1.0, 5.4, 1.6),   (-0.1, 7.8, 1.5))
kw(49.2, (-0.2, 7.6, 1.58), (-1.0, 9.0, 1.4))
kw(50.4, (pia_cx + 0.04, pia_cy - 0.85, 1.58), (pia_cx, pia_cy + 0.04, 1.05))
kvis(agua_pia, 0.0, False)
kvis(agua_pia, 50.6, True)
kw(51.8, (pia_cx + 0.04, pia_cy - 0.72, 1.44), (pia_cx, pia_cy + 0.05, 0.92))   # inclina p/ lavar
kw(53.2, (pia_cx + 0.04, pia_cy - 0.72, 1.44), (pia_cx, pia_cy + 0.05, 0.92))
kw(54.2, (pia_cx + 0.04, pia_cy - 0.85, 1.58), (pia_cx, pia_cy + 0.04, 1.02))
kvis(agua_pia, 54.8, False)

# 10) Vira para a SALA e LIGA A TV
kw(55.4, (0.2, 9.6, 1.58), (2.8, 10.5, 1.5))
kw(56.8, (0.9, 9.7, 1.66), (tv_x, tv_y, tv_z))
kvis(tv_screen, 0.0, False)
kvis(tv_screen, 57.4, True)
if tv_emit is not None:
    kemit(tv_emit, 57.2, 0.0)
    kemit(tv_emit, 58.2, 3.4)
kenergy(tv_light, 57.2, 0.0)
kenergy(tv_light, 58.2, 22.0)
kw(59.6, (0.9, 9.7, 1.66), (tv_x, tv_y, tv_z))
# FIM: segura na TV ligada (sem a sequencia de saida a pe).
kw(62.0, (0.9, 9.7, 1.66), (tv_x, tv_y, tv_z))

TOTAL_FRAMES = 1 + round((_last_t[0] + 0.6) * FPS)
_maxf = int(os.environ.get("WALK_MAX_FRAMES", "0"))
if _maxf:
    TOTAL_FRAMES = min(TOTAL_FRAMES, _maxf)

# --- interpolacao ------------------------------------------------------
for ob in (cam_obj, look, tampa, fridge_door, porta_ducha, porta_wc, *flames):
    if ob is None:
        continue
    ad = ob.animation_data
    if not ad or not ad.action:
        continue
    for fc in ad.action.fcurves:
        const = fc.data_path.endswith(("hide_render", "hide_viewport"))
        for kp in fc.keyframe_points:
            if const:
                kp.interpolation = 'CONSTANT'
            else:
                kp.interpolation = 'BEZIER'
                kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'

# ---------------------------------------------------------------------------
# Render: frames PNG (retomavel) -> encode MP4 pelo sequencer.
#   WALK_QUALITY=draft  -> 854x480,  16 spp + denoise -> passeio_quiosque_rascunho.mp4
#   WALK_QUALITY=final  -> 1280x720, 28 spp + denoise -> passeio_quiosque.mp4 (padrao)
# Precisa de um Blender COM OpenImageDenoiser (o 4.0.2 do sistema NAO tem;
# usar o 4.2 LTS oficial em ~/opt). Se o denoiser nao existir, cai no
# fallback de mais amostras.
# ---------------------------------------------------------------------------
QUALITY = os.environ.get("WALK_QUALITY", "final").lower()
if QUALITY == "draft":
    RES_X, RES_Y, SAMPLES, ADAPT, ADAPT_MIN = 854, 480, 16, 0.1, 8
    frames_sub, mp4_name = "passeio_frames_draft", "passeio_quiosque_rascunho.mp4"
else:
    RES_X, RES_Y, SAMPLES, ADAPT, ADAPT_MIN = 1280, 720, 28, 0.06, 12
    frames_sub, mp4_name = "passeio_frames", "passeio_quiosque.mp4"

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES
scene.render.fps = FPS
scene.view_settings.view_transform = 'AgX'
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'

_has_oidn = False
try:
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    _has_oidn = True
except TypeError:
    pass

if _has_oidn:
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        scene.cycles.denoising_prefilter = 'ACCURATE'
    except (AttributeError, TypeError):
        pass
else:
    # sem denoiser -> precisa de MUITO mais amostras
    SAMPLES = 96 if QUALITY == "draft" else 200
    ADAPT = 0.04
    scene.cycles.use_denoising = False

scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = ADAPT
scene.cycles.adaptive_min_samples = ADAPT_MIN
scene.cycles.use_light_tree = True
scene.cycles.max_bounces = 6
scene.cycles.diffuse_bounces = 3
scene.cycles.glossy_bounces = 3
scene.cycles.transmission_bounces = 5
scene.cycles.volumes_bounces = 0
scene.cycles.caustics_reflective = False
scene.cycles.caustics_refractive = False
scene.render.resolution_x = RES_X
scene.render.resolution_y = RES_Y
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
prefs = bpy.context.preferences.addons.get('cycles')
if prefs:
    prefs.preferences.compute_device_type = 'NONE'

renders_dir = os.path.join(scriptdir, "renders")
os.makedirs(renders_dir, exist_ok=True)
frames_dir = os.path.join(renders_dir, frames_sub)
os.makedirs(frames_dir, exist_ok=True)

scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.use_sequencer = False
scene.render.use_compositing = False

print(f"WALKTHROUGH TOTAL_FRAMES={TOTAL_FRAMES} FPS={FPS} dur={TOTAL_FRAMES/FPS:.1f}s")
_only = os.environ.get("WALK_ONLY_FRAMES", "")
_frames = [int(x) for x in _only.split(",") if x.strip()] if _only else range(1, TOTAL_FRAMES + 1)
for fr in _frames:
    out_png = os.path.join(frames_dir, f"f_{fr:04d}.png")
    if os.path.exists(out_png) and os.path.getsize(out_png) > 2000:
        continue
    scene.frame_set(fr)
    scene.render.filepath = os.path.join(frames_dir, f"f_{fr:04d}")
    bpy.ops.render.render(write_still=True)
    print(f"  frame {fr}/{TOTAL_FRAMES}")

_missing = [fr for fr in range(1, TOTAL_FRAMES + 1)
            if not os.path.exists(os.path.join(frames_dir, f"f_{fr:04d}.png"))]
if _only or _missing:
    print(f"ENCODE SKIP: only={_only!r} missing={len(_missing)}")
    raise SystemExit(0)

if scene.sequence_editor:
    scene.sequence_editor_clear()
se = scene.sequence_editor_create()
strip = se.sequences.new_image(name="passeio",
                               filepath=os.path.join(frames_dir, "f_0001.png"),
                               channel=1, frame_start=1)
for fr in range(2, TOTAL_FRAMES + 1):
    strip.elements.append(f"f_{fr:04d}.png")

scene.render.use_sequencer = True
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'HIGH'
scene.render.ffmpeg.gopsize = 18
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = os.path.join(renders_dir, mp4_name)
bpy.ops.render.render(animation=True)
print("WALKTHROUGH_OK:", scene.render.filepath)
