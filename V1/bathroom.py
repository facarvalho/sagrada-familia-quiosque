"""
Banheiros no vao entre os pilares 6, 7, 8 e 9 do quiosque (a "ala" da
planta em L: x de -2.25 a 0.75, y de 9.5 a 12.0).

Layout sem corredor interno: o espaco e dividido ao meio (parede central)
em 2 duchas quentes (lado oeste, porta voltada para fora/lado da piscina) e
2 lavabos (lado leste, porta voltada para fora/lado do corredor principal do
quiosque). Cada cabine tem porta direta para o lado de fora, sem circulacao
interna - isso maximiza a area util de cada cabine (~1.35 x 1.1m).
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
    """ns: namespace dict resultante de exec(projeto.py) - fornece
    pilares_coords, altura_piso, altura_pilar."""
    pilares_coords = ns["pilares_coords"]
    altura_piso = ns["altura_piso"]

    # Pilares 6,7,8,9 (1-indexados) -> indices 5,6,7,8 na lista.
    p6 = pilares_coords[5]   # (0.75, 12.0)
    p7 = pilares_coords[6]   # (-2.25, 12.0)
    p8 = pilares_coords[7]   # (-2.25, 9.5)
    p9 = pilares_coords[8]   # (0.25, 9.5)

    mat_parede = _mat("Material_Banheiro_Parede", (0.92, 0.92, 0.90, 1.0), roughness=0.45)
    mat_porta = _mat("Material_Banheiro_Porta", (0.55, 0.58, 0.60, 1.0), roughness=0.4)
    mat_louca = _mat("Material_Banheiro_Louca", (0.96, 0.96, 0.96, 1.0), roughness=0.15)
    mat_metal = _mat("Material_Banheiro_Metal", (0.8, 0.82, 0.85, 1.0), roughness=0.15, metallic=0.9)
    mat_chuveiro_box = _mat("Material_Chuveiro_Eletrico", (0.93, 0.9, 0.82, 1.0), roughness=0.3)

    # Footprint retangular simplificado, com margem de seguranca em relacao
    # aos pilares (que ficam nos cantos do trapezio real da ala).
    X0, X1 = min(p7[0], p8[0]) + 0.05, max(p6[0], p9[0]) - 0.05
    Y0, Y1 = min(p8[1], p9[1]) + 0.10, max(p6[1], p7[1]) - 0.10

    WT = 0.08                       # espessura das paredes/divisorias
    WALL_Z0 = altura_piso
    WALL_Z1 = altura_piso + 2.0     # paredes de 2.0m (nao sobem ate o telhado)
    DOOR_W = 0.7
    DOOR_H = 1.9

    XM = (X0 + X1) / 2.0            # parede central: duchas (oeste) | lavabos (leste)
    YM = (Y0 + Y1) / 2.0            # divisao entre cabine 1 (sul) e cabine 2 (norte)

    def wall(name, x0, x1, y0, y1):
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        cz = (WALL_Z0 + WALL_Z1) / 2.0
        sx, sy, sz = max(x1 - x0, 0.001), max(y1 - y0, 0.001), WALL_Z1 - WALL_Z0
        return _box(name, cx, cy, cz, sx, sy, sz, mat_parede)

    def door_in_x_wall(name, x_fixed, y0, y1):
        """Porta numa parede vertical (perpendicular a X), vao entre y0 e y1."""
        cz = WALL_Z0 + DOOR_H / 2.0
        _box(name, x_fixed, (y0 + y1) / 2.0, cz, 0.04, y1 - y0, DOOR_H, mat_porta)

    def perimeter_wall_with_doors(name_prefix, x_fixed):
        """Parede externa (oeste ou leste) com 2 vaos de porta, um por cabine."""
        rows = [(Y0, YM), (YM, Y1)]
        for i, (ry0, ry1) in enumerate(rows, start=1):
            center = (ry0 + ry1) / 2.0
            d0, d1 = center - DOOR_W / 2.0, center + DOOR_W / 2.0
            if d0 - ry0 > 0.02:
                wall(f"{name_prefix}_{i}_a", x_fixed - WT / 2, x_fixed + WT / 2, ry0, d0)
            if ry1 - d1 > 0.02:
                wall(f"{name_prefix}_{i}_b", x_fixed - WT / 2, x_fixed + WT / 2, d1, ry1)
            door_in_x_wall(f"{name_prefix}_{i}_Porta", x_fixed, d0, d1)

    # --- Perimetro -------------------------------------------------------
    # Oeste: portas das duchas, voltadas para fora (lado da piscina).
    perimeter_wall_with_doors("Banheiro_Parede_Oeste", X0)
    # Leste: portas dos lavabos, voltadas para fora (lado do corredor do quiosque).
    perimeter_wall_with_doors("Banheiro_Parede_Leste", X1)
    # Norte e sul: paredes cegas, sem porta.
    wall("Banheiro_Parede_Norte", X0, X1, Y1 - WT / 2, Y1 + WT / 2)
    wall("Banheiro_Parede_Sul", X0, X1, Y0 - WT / 2, Y0 + WT / 2)

    # --- Parede central (duchas | lavabos) e divisorias internas ---------
    wall("Banheiro_Parede_Central", XM - WT / 2, XM + WT / 2, Y0, Y1)
    wall("Banheiro_Particao_Ducha", X0, XM, YM - WT / 2, YM + WT / 2)
    wall("Banheiro_Particao_Lavabo", XM, X1, YM - WT / 2, YM + WT / 2)

    # --- Piso (ladrilho, cobrindo toda a ala) -----------------------------
    _box(
        "Banheiro_Piso",
        (X0 + X1) / 2.0, (Y0 + Y1) / 2.0, altura_piso + 0.005,
        X1 - X0, Y1 - Y0, 0.01,
        mat_louca,
    )

    # --- Fixtures: 2 duchas (coluna oeste, porta no lado oeste) -----------
    shower_rows = [(Y0, YM), (YM, Y1)]
    for i, (ry0, ry1) in enumerate(shower_rows, start=1):
        cy = (ry0 + ry1) / 2.0
        wall_x = XM - WT / 2.0  # fixtures na parede central (oposta a porta)
        _box(f"Ducha_{i}_Base", wall_x - 0.35, cy, altura_piso + 0.02,
             0.7, (ry1 - ry0) - 0.15, 0.03, mat_louca)
        _cyl(f"Ducha_{i}_Coluna", wall_x - 0.02, cy, altura_piso + 1.0,
             0.012, 1.6, mat_metal)
        _box(f"Ducha_{i}_Eletrico", wall_x - 0.06, cy, altura_piso + 1.85,
             0.1, 0.09, 0.16, mat_chuveiro_box)
        _cyl(f"Ducha_{i}_Registro", wall_x - 0.05, cy, altura_piso + 1.1,
             0.02, 0.05, mat_metal, rotation=(0.0, math.radians(90), 0.0))

    # --- Fixtures: 2 lavabos (coluna leste, porta no lado leste) ----------
    lavabo_rows = [(Y0, YM), (YM, Y1)]
    for i, (ry0, ry1) in enumerate(lavabo_rows, start=1):
        cy = (ry0 + ry1) / 2.0
        wall_x = XM + WT / 2.0  # vaso encostado na parede central (oposta a porta)

        toilet_cy = cy - (ry1 - ry0) * 0.18
        _box(f"Lavabo_{i}_Caixa", wall_x + 0.10, toilet_cy, altura_piso + 0.62,
             0.16, 0.38, 0.30, mat_louca)
        bowl = _cyl(f"Lavabo_{i}_Bacia", wall_x + 0.27, toilet_cy, altura_piso + 0.20,
                    0.19, 0.40, mat_louca)
        bowl.scale = (1.35, 1.0, 1.0)
        _box(f"Lavabo_{i}_Assento", wall_x + 0.27, toilet_cy, altura_piso + 0.41,
             0.34, 0.30, 0.03, mat_louca)

        # pia compacta de canto, perto da porta (lado leste)
        sink_cy = cy + (ry1 - ry0) * 0.32
        _box(f"Lavabo_{i}_Pia", X1 - WT / 2.0 - 0.16, sink_cy, altura_piso + 0.80,
             0.3, 0.22, 0.10, mat_louca)
        _cyl(f"Lavabo_{i}_Torneira", X1 - WT / 2.0 - 0.28, sink_cy, altura_piso + 0.92,
             0.012, 0.14, mat_metal, rotation=(math.radians(90), 0.0, 0.0))

    return {
        "bounds": (X0, X1, Y0, Y1),
        "center_wall_x": XM,
        "row_split": YM,
    }
