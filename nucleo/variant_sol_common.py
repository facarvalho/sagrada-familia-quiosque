"""
Lógica compartilhada pelas variantes de posicionamento "com fundo para X"
que usam dado real (GPS do usuário + posição solar NOAA + entorno real) -
"cerca do Fernando" foi a primeira; esta função generaliza pra "casa da
mãe", que usa a mesma lógica de transformação (giro em Z, ancorado no
pilar P9, sempre alinhado a um canto real do deck da piscina), só que com
ângulo e canto diferentes por posição.

Cada variante:
  1. Constrói o projeto original (projeto.py + extras.py + fixes.py).
  2. Gira o quiosque em Z (rotation_deg) em torno de P9 original (0.4, 9.5)
     e translada até o canto do deck informado (target_xy).
  3. Adiciona o contexto externo (cerca/café/terreno reais,
     arquitetonico/contexto_externo.py).
  4. Câmera enquadrando quiosque + piscina (lente larga).
  5. 10 renders: verão/inverno x 15h/16h/17h/18h/19h, sol na posição real
     (nucleo/sun_geo.py, NOAA), com legenda via annotate_sun_study (mesmo
     padrão de visao-cerca-fernando/annotate_sun_study.py, mas parametrizável por pasta).
"""
import bpy
import os
import sys
import math
import json
import mathutils


def build_and_render(target_xy, out_dir, titulo_curto, cam_offset=(-23.0, -27.0, 15.0),
                      cam_target_offset=(-2.5, -0.5, 0.8), lens=20, rotation_deg=-90.0):
    scriptdir = os.path.dirname(os.path.abspath(out_dir))
    repo_root = "/home/fac/piscina"
    arq_dir = os.path.join(repo_root, "arquitetonico")
    for p in (arq_dir, repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)

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

    # --- transformação: -90 graus em Z, P9 original -> target_xy ---------
    _manter = {"Piso_Area_Piscina", "Piscina_Cortador_Boolean"}

    def _e_piscina(nome):
        return nome in _manter or nome.startswith("Piscina_")

    _quiosque = [o for o in bpy.data.objects
                 if o.type in {"MESH", "EMPTY"} and not _e_piscina(o.name)
                 and not o.name.startswith(("Cerca_", "Cafe_", "Terreno_", "CasaMae_"))]

    _pivot = mathutils.Vector((0.4, 9.5, 0.0))
    _target = mathutils.Vector((target_xy[0], target_xy[1], 0.0))
    _Rz = mathutils.Matrix.Rotation(math.radians(rotation_deg), 4, 'Z')
    _transform = mathutils.Matrix.Translation(_target) @ _Rz @ mathutils.Matrix.Translation(-_pivot)

    for obj in _quiosque:
        obj.matrix_world = _transform @ obj.matrix_world
    bpy.context.view_layer.update()

    # --- seta de norte -----------------------------------------------------
    nx, ny = sun_geo.true_north_vector_project_xy()
    arrow_origin = mathutils.Vector((target_xy[0] + 5.0, target_xy[1] + 1.5, 0.03))
    arrow_len = 2.2
    arrow_tip = arrow_origin + mathutils.Vector((nx, ny, 0.0)) * arrow_len
    mesh_arrow = bpy.data.meshes.new("Mesh_Seta_Norte")
    obj_arrow = bpy.data.objects.new("Seta_Norte_Verdadeiro", mesh_arrow)
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
    mat_norte = bpy.data.materials.new("Material_Seta_Norte")
    mat_norte.use_nodes = True
    mat_norte.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.05, 0.05, 1.0)
    mat_norte.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
    obj_arrow.data.materials.append(mat_norte)

    # --- camera --------------------------------------------------------
    cam_data = bpy.data.cameras.new("Camera_Render")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("Camera_Render", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_target = mathutils.Vector((target_xy[0] + cam_target_offset[0],
                                    target_xy[1] + cam_target_offset[1], cam_target_offset[2]))
    cam_location = cam_target + mathutils.Vector(cam_offset)
    cam_obj.location = cam_location
    direction = cam_target - cam_location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam_obj

    # --- mundo -----------------------------------------------------------
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

    # --- render config -----------------------------------------------------
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
    try:
        scene.cycles.denoiser = 'OPENIMAGEDENOISE'
        scene.cycles.use_denoising = True
        scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        scene.cycles.denoising_prefilter = 'ACCURATE'
        scene.cycles.samples = 96
    except TypeError:
        scene.cycles.use_denoising = False
        scene.cycles.samples = 300

    sun_data = bpy.data.lights.new("Sol", type='SUN')
    sun_data.angle = math.radians(3.0)
    sun_obj = bpy.data.objects.new("Sol", sun_data)
    bpy.context.collection.objects.link(sun_obj)

    HORAS = [15, 16, 17, 18, 19]
    CENAS = [("verao", 2026, 12, 21, h, 0) for h in HORAS] \
        + [("inverno", 2026, 6, 21, h, 0) for h in HORAS]

    os.makedirs(out_dir, exist_ok=True)
    region = bpy.context.scene.render
    from bpy_extras.object_utils import world_to_camera_view
    co2d = world_to_camera_view(bpy.context.scene, cam_obj, arrow_tip)
    arrow_tip_px = (co2d.x * region.resolution_x, (1 - co2d.y) * region.resolution_y)

    meta = {"cenas": [], "posicao": titulo_curto}
    for estacao, y, m, d, h, mi in CENAS:
        azimuth, elevation = sun_geo.solar_position(y, m, d, h, mi)
        dx, dy, dz = sun_geo.sun_direction_project_xyz(azimuth, elevation)
        travel_dir = mathutils.Vector((-dx, -dy, -dz))
        sun_obj.rotation_euler = travel_dir.to_track_quat('-Z', 'Y').to_euler()
        if elevation <= 0.0:
            sun_data.energy = 0.0
            bg_node.inputs["Strength"].default_value = 0.05
            bg_node.inputs["Color"].default_value = (0.05, 0.06, 0.09, 1.0)
        else:
            t = max(0.0, min(1.0, elevation / 70.0))
            sun_data.energy = 5.0 + 3.0 * t
            sun_data.color = (1.0, 0.55 + 0.35 * t, 0.35 + 0.45 * t)
            bg_node.inputs["Strength"].default_value = 0.3
            bg_node.inputs["Color"].default_value = (0.55, 0.62, 0.72, 1.0)

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

    print("ALLDONE_SUN_STUDY:", titulo_curto)
