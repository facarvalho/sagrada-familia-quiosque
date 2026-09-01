"""
Área gourmet rústica encostada na parede leste, entre os pilares 2 e 3
(x=4, y de 0 a 4 - lado oposto aos banheiros/ala). Inclui bancada com pia e
churrasqueira de bancada embutida (acabamento rústico: base de madeira e
tampo em concreto/pedra bruta) e uma mesa rústica de 8 lugares com bancos.
"""
import bpy
import math


def _mat(name, color, roughness=0.5, metallic=0.0):
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _box(name, cx, cy, cz, sx, sy, sz, mat):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (sx, sy, sz)
    if mat:
        obj.data.materials.append(mat)
    return obj


def _cyl(name, cx, cy, cz, radius, depth, mat, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    if mat:
        obj.data.materials.append(mat)
    return obj


def build(ns):
    altura_piso = ns["altura_piso"]

    mat_base = _mat("Material_Bancada_Base_Rustica", (0.30, 0.20, 0.12, 1.0), roughness=0.85)
    mat_tampo = _mat("Material_Bancada_Tampo_Rustico", (0.47, 0.45, 0.42, 1.0), roughness=0.75)
    mat_metal = _mat("Material_Bancada_Metal", (0.75, 0.76, 0.78, 1.0), roughness=0.2, metallic=0.9)
    mat_grelha = _mat("Material_Churrasqueira_Grelha", (0.08, 0.08, 0.08, 1.0), roughness=0.35, metallic=0.6)
    mat_brasa = _mat("Material_Churrasqueira_Brasa", (0.9, 0.25, 0.05, 1.0), roughness=0.6)
    bsdf_brasa = mat_brasa.node_tree.nodes.get("Principled BSDF")
    if bsdf_brasa:
        bsdf_brasa.inputs["Emission Color"].default_value = (1.0, 0.3, 0.05, 1.0)
        bsdf_brasa.inputs["Emission Strength"].default_value = 1.5
    mat_madeira_mesa = _mat("Material_Mesa_Rustica", (0.34, 0.22, 0.13, 1.0), roughness=0.8)

    # --- Bancada encostada na parede leste (x=4), entre Pilar 2 (4,0) e
    # Pilar 3 (4,4) -----------------------------------------------------
    Y0, Y1 = 0.6, 3.6           # comprimento da bancada (3.0m)
    DEPTH = 0.65
    X_WALL = 4.0
    X_FRONT = X_WALL - DEPTH
    H_TOP = altura_piso + 0.90
    BASE_H = H_TOP - 0.05

    cx, cy = (X_FRONT + X_WALL) / 2.0, (Y0 + Y1) / 2.0
    length = Y1 - Y0

    _box("Bancada_Base", cx, cy, (altura_piso + BASE_H) / 2.0,
         DEPTH, length, BASE_H - altura_piso, mat_base)

    # --- Pia, extremidade sul da bancada (perto do Pilar 2) -----------------
    sink_cy = Y0 + 0.55
    SINK_W = 0.42
    gap0, gap1 = sink_cy - SINK_W / 2.0, sink_cy + SINK_W / 2.0

    _box("Bancada_Tampo_Sul", cx, (Y0 - 0.03 + gap0) / 2.0, H_TOP - 0.02,
         DEPTH + 0.06, gap0 - (Y0 - 0.03), 0.04, mat_tampo)
    _box("Bancada_Tampo_Norte", cx, (gap1 + Y1 + 0.03) / 2.0, H_TOP - 0.02,
         DEPTH + 0.06, (Y1 + 0.03) - gap1, 0.04, mat_tampo)

    _box("Bancada_Pia_Cuba", cx, sink_cy, H_TOP - 0.075,
         DEPTH - 0.02, SINK_W, 0.09, mat_metal)
    _cyl("Bancada_Pia_Coluna_Torneira", X_WALL - 0.08, sink_cy, H_TOP + 0.02,
         0.015, 0.30, mat_metal)
    _cyl("Bancada_Pia_Bico_Torneira", X_WALL - 0.08 - 0.13, sink_cy, H_TOP + 0.16,
         0.013, 0.22, mat_metal, rotation=(0.0, math.radians(90), 0.0))

    # --- Churrasqueira de bancada, extremidade norte (perto do Pilar 3) -----
    bbq_cy = Y1 - 0.65
    bbq_cx = cx
    _box("Churrasqueira_Corpo", bbq_cx, bbq_cy, H_TOP - 0.06,
         0.46, 0.62, 0.14, mat_grelha)
    n_bars = 6
    for i in range(n_bars):
        t = (i + 0.5) / n_bars - 0.5
        _cyl(f"Churrasqueira_Barra_{i+1}", bbq_cx, bbq_cy + t * 0.5, H_TOP - 0.01,
             0.012, 0.40, mat_grelha, rotation=(0.0, math.radians(90), 0.0))
    _box("Churrasqueira_Brasa", bbq_cx, bbq_cy, H_TOP - 0.09,
         0.36, 0.5, 0.02, mat_brasa)
    _cyl("Churrasqueira_Chamine", X_WALL - 0.05, bbq_cy + 0.20, H_TOP + 0.30,
         0.05, 0.55, mat_metal)

    # ---------------------------------------------------------------------
    # Mesa rústica para 8 pessoas (2 bancos corridos), em frente à bancada
    # ---------------------------------------------------------------------
    TABLE_CX, TABLE_CY = 2.15, 2.05
    TABLE_LEN, TABLE_W = 2.4, 0.9
    TABLE_TOP_H = altura_piso + 0.75
    LEG_R = 0.05

    _box("Mesa_Tampo", TABLE_CX, TABLE_CY, TABLE_TOP_H,
         TABLE_W, TABLE_LEN, 0.06, mat_madeira_mesa)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _box(f"Mesa_Pe_{sx}_{sy}",
                 TABLE_CX + sx * (TABLE_W / 2 - 0.08),
                 TABLE_CY + sy * (TABLE_LEN / 2 - 0.15),
                 (altura_piso + TABLE_TOP_H - 0.03) / 2.0,
                 0.08, 0.08, (TABLE_TOP_H - 0.03) - altura_piso, mat_madeira_mesa)

    BENCH_H = altura_piso + 0.45
    BENCH_LEN = TABLE_LEN - 0.2
    for sx, side in ((-1, "Oeste"), (1, "Leste")):
        bx = TABLE_CX + sx * (TABLE_W / 2 + 0.30)
        _box(f"Banco_{side}_Assento", bx, TABLE_CY, BENCH_H,
             0.30, BENCH_LEN, 0.05, mat_madeira_mesa)
        for sy in (-1, 1):
            _box(f"Banco_{side}_Pe_{sy}", bx, TABLE_CY + sy * (BENCH_LEN / 2 - 0.12),
                 (altura_piso + BENCH_H - 0.025) / 2.0,
                 0.06, 0.06, (BENCH_H - 0.025) - altura_piso, mat_madeira_mesa)

    return {
        "bounds": (X_FRONT, X_WALL, Y0, Y1),
        "top_z": H_TOP,
        "table_center": (TABLE_CX, TABLE_CY),
    }
