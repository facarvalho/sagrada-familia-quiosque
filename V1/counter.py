"""
Área gourmet rústica encostada na parede leste, entre os pilares 2 e 3
(x=4, y de 0 a 4 - lado oposto aos banheiros/ala). Inclui bancada com
churrasqueira de bancada embutida (acabamento rústico: base de madeira e
tampo em concreto/pedra bruta) e uma mesa rústica de 8 lugares com bancos.

A pia trocou de lugar com a geladeira/fogão (ver appliances.py): agora fica
na parede SUL, entre os pilares 1 e 2, com uma janela acima (wall.py) -
não faz mais parte desta bancada leste, que ficou só com a churrasqueira.
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

    # --- Bancada encostada na parede leste (x=4), entre Pilar 2 (4; 1,5) e
    # Pilar 3 (4; 5,5) - vao de 4,0 m ----------------------------------
    # Geladeira/fogão saíram desta parede (foram pra parede sul, ao lado da
    # pia - ver appliances.py), então a bancada voltou ao comprimento
    # cheio; ficou só com a churrasqueira, na ponta norte.
    Y0, Y1 = 2.1, 5.1
    DEPTH = 0.65
    X_WALL = 4.0
    X_FRONT = X_WALL - DEPTH
    H_TOP = altura_piso + 0.90
    BASE_H = H_TOP - 0.05

    cx, cy = (X_FRONT + X_WALL) / 2.0, (Y0 + Y1) / 2.0
    length = Y1 - Y0

    _box("Bancada_Base", cx, cy, (altura_piso + BASE_H) / 2.0,
         DEPTH, length, BASE_H - altura_piso, mat_base)

    # --- Tampo contínuo (a pia saiu daqui - foi para a parede sul) ---------
    _box("Bancada_Tampo", cx, cy, H_TOP - 0.02,
         DEPTH + 0.06, length + 0.06, 0.04, mat_tampo)

    # --- Pia nova, na parede SUL (entre P1 e P2), onde antes ficava a
    #     geladeira/fogão - ver appliances.py. Janela acima dela: wall.py.
    PIA_SUL_CX = 2.2
    PIA_SUL_Y_WALL = 1.53   # face interna da parede sul (mesma cota de appliances.py)
    pia_sul_depth = 0.55
    pia_sul_w = 0.75
    pia_sul_top = altura_piso + 0.90
    pia_cy = PIA_SUL_Y_WALL + pia_sul_depth / 2.0
    _box("Pia_Sul_Base", PIA_SUL_CX, pia_cy, altura_piso + (pia_sul_top - 0.05 - altura_piso) / 2.0,
         pia_sul_depth, pia_sul_w, (pia_sul_top - 0.05) - altura_piso, mat_base)
    _box("Pia_Sul_Tampo", PIA_SUL_CX, pia_cy, pia_sul_top - 0.02,
         pia_sul_depth + 0.06, pia_sul_w + 0.06, 0.04, mat_tampo)
    _box("Pia_Sul_Cuba", PIA_SUL_CX, pia_cy, pia_sul_top - 0.075,
         pia_sul_depth - 0.10, pia_sul_w - 0.15, 0.09, mat_metal)
    _cyl("Pia_Sul_Coluna_Torneira", PIA_SUL_CX, PIA_SUL_Y_WALL + 0.06, pia_sul_top + 0.02,
         0.015, 0.30, mat_metal)
    _cyl("Pia_Sul_Bico_Torneira", PIA_SUL_CX, PIA_SUL_Y_WALL + 0.06 + 0.13, pia_sul_top + 0.16,
         0.013, 0.22, mat_metal, rotation=(math.radians(90), 0.0, 0.0))

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
    TABLE_CX, TABLE_CY = 2.15, 3.55
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
        "pia_sul_cx": PIA_SUL_CX,
    }
