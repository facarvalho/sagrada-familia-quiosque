"""
Área gourmet. Layout (pedido do usuário, reorganizado 14/09/2026):
- Parede SUL (P1-P2, x 0,4-4,0): bancada de ALVENARIA em peça única
  (Bancada_Sul_Alvenaria + Bancada_Sul_Tampo), ocupando o vão entre os
  pilares (com folga pros pedestais) - pia embutida sob a janela
  (wall.py) e churrasqueira embutida do lado do Pilar 2.
- Parede LESTE (P2-P3, x=4,0): fogão e geladeira (ver appliances.py) -
  saíram da parede sul pra dar lugar à churrasqueira.
Mesa rústica de 8 lugares com bancos no meio do quiosque, independente
dessas duas paredes.
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

    mat_alvenaria = _mat("Material_Bancada_Alvenaria", (0.84, 0.81, 0.75, 1.0), roughness=0.88)
    mat_tampo = _mat("Material_Bancada_Tampo_Rustico", (0.47, 0.45, 0.42, 1.0), roughness=0.75)
    mat_metal = _mat("Material_Bancada_Metal", (0.75, 0.76, 0.78, 1.0), roughness=0.2, metallic=0.9)
    mat_grelha = _mat("Material_Churrasqueira_Grelha", (0.08, 0.08, 0.08, 1.0), roughness=0.35, metallic=0.6)
    mat_brasa = _mat("Material_Churrasqueira_Brasa", (0.9, 0.25, 0.05, 1.0), roughness=0.6)
    bsdf_brasa = mat_brasa.node_tree.nodes.get("Principled BSDF")
    if bsdf_brasa:
        bsdf_brasa.inputs["Emission Color"].default_value = (1.0, 0.3, 0.05, 1.0)
        bsdf_brasa.inputs["Emission Strength"].default_value = 1.5
    mat_madeira_mesa = _mat("Material_Mesa_Rustica", (0.34, 0.22, 0.13, 1.0), roughness=0.8)

    # --- Parede LESTE (x=4), entre Pilar 2 (4; 1,5) e Pilar 3 (4; 5,5) -----
    # Geladeira e fogão ficam aqui agora (ver appliances.py) - usuário pediu
    # pra trocar: fogão/geladeira foram pra esta parede, churrasqueira foi
    # pra parede sul junto com a pia. Sem bancada própria aqui (os dois
    # ficam encostados na parede, como já era o padrão da pia/fogão antes).
    # Constantes mantidas (sem bancada física) só pra compatibilizar com
    # scripts de render que ainda usam esses valores pra enquadrar a câmera.
    Y0, Y1 = 2.1, 5.1
    DEPTH = 0.65
    X_WALL = 4.0
    X_FRONT = X_WALL - DEPTH
    H_TOP = altura_piso + 0.90
    BASE_H = H_TOP - 0.05

    cx, cy = (X_FRONT + X_WALL) / 2.0, (Y0 + Y1) / 2.0

    # --- Bancada de alvenaria única, na parede SUL (entre P1 e P2), com pia
    #     + churrasqueira - usuário pediu pra virar UMA PEÇA SÓ, em alvenaria
    #     (não madeira), ocupando o vão entre os pilares (com folga pros
    #     pedestais). Pia sob a janela (wall.py); churrasqueira do lado do
    #     Pilar 2. Geladeira/fogão saíram daqui - foram pra parede leste
    #     (appliances.py).
    PIA_SUL_Y_WALL = 1.53   # face interna da parede sul (mesma cota de appliances.py)
    pia_sul_depth = 0.55
    pia_sul_top = altura_piso + 0.90
    BANC_SUL_X0, BANC_SUL_X1 = 0.75, 3.75   # folga de ~0,35 m dos pilares P1/P2
    banc_sul_cx = (BANC_SUL_X0 + BANC_SUL_X1) / 2.0
    banc_sul_width = BANC_SUL_X1 - BANC_SUL_X0
    banc_sul_base_h = pia_sul_top - 0.05
    pia_cy = PIA_SUL_Y_WALL + pia_sul_depth / 2.0

    _box("Bancada_Sul_Alvenaria", banc_sul_cx, pia_cy, altura_piso + (banc_sul_base_h - altura_piso) / 2.0,
         banc_sul_width, pia_sul_depth, banc_sul_base_h - altura_piso, mat_alvenaria)
    _box("Bancada_Sul_Tampo", banc_sul_cx, pia_cy, pia_sul_top - 0.02,
         banc_sul_width + 0.06, pia_sul_depth + 0.06, 0.04, mat_tampo)

    # --- Pia, embutida na bancada, sob a janela ----------------------------
    PIA_SUL_CX = 2.2
    pia_sul_w = 0.75
    _box("Pia_Sul_Cuba", PIA_SUL_CX, pia_cy, pia_sul_top - 0.075,
         pia_sul_w - 0.15, pia_sul_depth - 0.10, 0.09, mat_metal)
    _cyl("Pia_Sul_Coluna_Torneira", PIA_SUL_CX, PIA_SUL_Y_WALL + 0.06, pia_sul_top + 0.02,
         0.015, 0.30, mat_metal)
    _cyl("Pia_Sul_Bico_Torneira", PIA_SUL_CX, PIA_SUL_Y_WALL + 0.06 + 0.13, pia_sul_top + 0.16,
         0.013, 0.22, mat_metal, rotation=(math.radians(90), 0.0, 0.0))

    # --- Churrasqueira, embutida na mesma bancada, do lado do Pilar 2 ------
    CHUR_CX = 3.15
    chur_top = pia_sul_top
    bbq_cx, bbq_cy = CHUR_CX, pia_cy
    _box("Churrasqueira_Corpo", bbq_cx, bbq_cy, chur_top - 0.06,
         0.62, 0.46, 0.14, mat_grelha)
    n_bars = 6
    for i in range(n_bars):
        t = (i + 0.5) / n_bars - 0.5
        _cyl(f"Churrasqueira_Barra_{i+1}", bbq_cx + t * 0.5, bbq_cy, chur_top - 0.01,
             0.012, 0.40, mat_grelha, rotation=(math.radians(90), 0.0, 0.0))
    _box("Churrasqueira_Brasa", bbq_cx, bbq_cy, chur_top - 0.09,
         0.5, 0.36, 0.02, mat_brasa)
    _cyl("Churrasqueira_Chamine", bbq_cx + 0.20, PIA_SUL_Y_WALL + 0.05, chur_top + 0.30,
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
        "pia_sul_cy": pia_cy,
        "pia_sul_top": pia_sul_top,
        "pia_sul_y_wall": PIA_SUL_Y_WALL,
    }
