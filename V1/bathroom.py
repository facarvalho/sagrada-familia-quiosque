"""
Banheiros no vao entre os pilares 6, 7, 8 e 9 do quiosque (a "ala" da
planta em L, y de 9.5 a 12.0; borda leste alinhada com P9-P6 em x=0,40).

Layout sem corredor interno, ACABAMENTO RUSTICO: paredes em MURO TENDINOSO
(malla + varão tensionados entre os pilares e rebocados com argamassa nas
duas faces -> parede fina ~8 cm, monolítica e rústica), chao de brita
solta. 4 cabines - 2 duchas quentes (lado oeste, porta p/ a piscina) e 2
sanitarios (lado leste, so o vaso, sem pia). Portas de 0,60 m.
O lava-maos e uma PIA COMUNITARIA rustica fixada na parede P8-P9 (face sul),
funda, com saboneteira e papeleira.

As paredes tem 2,50 m de altura, MAS param ~3 cm abaixo da face inferior do
telhado onde ele desce (lado oeste da ala) -> sempre sobra um respiro entre
a parede e a cobertura. Acima de cada porta ha uma verga ate o topo da
parede.
"""
import bpy
import math

import V1.roof_frame as roof_frame


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

    # Acabamento RUSTICO: paredes em MURO TENDINOSO (reboco rústico nas duas
    # faces sobre malla tensionada), chao de brita solta.
    mat_parede = _mat("Material_Muro_Tendinoso", (0.80, 0.78, 0.72, 1.0), roughness=0.97)
    mat_porta = _mat("Material_Banheiro_Porta", (0.34, 0.24, 0.15, 1.0), roughness=0.8)
    mat_brita = _mat("Material_Banheiro_Brita", (0.46, 0.45, 0.42, 1.0), roughness=1.0)
    mat_louca = _mat("Material_Banheiro_Louca", (0.90, 0.89, 0.86, 1.0), roughness=0.35)
    mat_metal = _mat("Material_Banheiro_Metal", (0.62, 0.63, 0.64, 1.0), roughness=0.35, metallic=0.85)
    mat_chuveiro_box = _mat("Material_Chuveiro_Eletrico", (0.90, 0.88, 0.82, 1.0), roughness=0.4)
    mat_rustico = _mat("Material_Pia_Rustica", (0.52, 0.49, 0.45, 1.0), roughness=0.95)

    # Footprint: a ala cresceu 0,40 m para o LESTE para alinhar com a nova
    # posicao de P9-P6 (fileira oeste recuada). Borda leste = x de P9/P6.
    X0, X1 = min(p7[0], p8[0]) + 0.05, max(p6[0], p9[0])
    Y0, Y1 = min(p8[1], p9[1]) + 0.10, max(p6[1], p7[1]) - 0.10

    WT = 0.08                       # espessura das paredes/divisorias
    WALL_Z0 = altura_piso
    WALL_H = 2.5                    # altura alvo das paredes do banheiro
    DOOR_W = 0.6                    # vao de porta = 0,60 m nas 4 cabines
    DOOR_H = 1.9

    XM = (X0 + X1) / 2.0            # parede central: duchas (oeste) | lavabos (leste)
    YM = (Y0 + Y1) / 2.0            # divisao entre cabine 1 (sul) e cabine 2 (norte)

    def _teto(x):                  # face inferior do telhado inclinado
        return roof_frame.roof_underside_z(ns, x)

    def _top(x0, x1):
        # 2,50 m, mas nunca a menos de 3 cm do telhado (que desce a oeste)
        return min(WALL_Z0 + WALL_H, _teto(x0) - 0.03, _teto(x1) - 0.03)

    def wall(name, x0, x1, y0, y1, z_base=None):
        zb = WALL_Z0 if z_base is None else z_base
        z1 = _top(x0, x1)
        cz = (zb + z1) / 2.0
        _box(name, (x0 + x1) / 2.0, (y0 + y1) / 2.0, cz,
             max(x1 - x0, 0.001), max(y1 - y0, 0.001), max(z1 - zb, 0.02), mat_parede)

    def door_in_x_wall(name, x_fixed, y0, y1):
        """Porta numa parede vertical (perpendicular a X), vao entre y0 e y1."""
        cz = WALL_Z0 + DOOR_H / 2.0
        _box(name, x_fixed, (y0 + y1) / 2.0, cz, 0.04, y1 - y0, DOOR_H, mat_porta)

    def perimeter_wall_with_doors(name_prefix, x_fixed):
        """Parede externa (oeste ou leste) com 2 vaos de porta, um por cabine.
        Acima de cada porta, uma verga fecha o vao ate o teto."""
        rows = [(Y0, YM), (YM, Y1)]
        for i, (ry0, ry1) in enumerate(rows, start=1):
            center = (ry0 + ry1) / 2.0
            d0, d1 = center - DOOR_W / 2.0, center + DOOR_W / 2.0
            if d0 - ry0 > 0.02:
                wall(f"{name_prefix}_{i}_a", x_fixed - WT / 2, x_fixed + WT / 2, ry0, d0)
            if ry1 - d1 > 0.02:
                wall(f"{name_prefix}_{i}_b", x_fixed - WT / 2, x_fixed + WT / 2, d1, ry1)
            wall(f"{name_prefix}_{i}_Verga", x_fixed - WT / 2, x_fixed + WT / 2, d0, d1,
                 z_base=WALL_Z0 + DOOR_H)
            door_in_x_wall(f"{name_prefix}_{i}_Porta", x_fixed, d0, d1)

    # --- Perimetro -------------------------------------------------------
    # Oeste: portas das duchas, voltadas para fora (lado da piscina).
    perimeter_wall_with_doors("Banheiro_Parede_Oeste", X0)
    # Leste: portas dos sanitarios, voltadas para fora (corredor do quiosque).
    perimeter_wall_with_doors("Banheiro_Parede_Leste", X1)
    # Norte e sul: paredes cegas, sem porta.
    wall("Banheiro_Parede_Norte", X0, X1, Y1 - WT / 2, Y1 + WT / 2)
    wall("Banheiro_Parede_Sul", X0, X1, Y0 - WT / 2, Y0 + WT / 2)

    # --- Parede central (duchas | lavabos) e divisorias internas ---------
    wall("Banheiro_Parede_Central", XM - WT / 2, XM + WT / 2, Y0, Y1)
    wall("Banheiro_Particao_Ducha", X0, XM, YM - WT / 2, YM + WT / 2)
    wall("Banheiro_Particao_Lavabo", XM, X1, YM - WT / 2, YM + WT / 2)

    # --- CAIXA DE BRITA: o piso da ala e uma caixa (tabuleiro rebaixado)
    #     cheia de brita solta, contida por um meio-fio. A agua das duchas
    #     percola pela brita ate o dreno; a brita fica ~1 cm abaixo do nivel
    #     do quiosque e o meio-fio sobe ~9 cm, inclusive nas soleiras das
    #     portas, para a brita nao escapar.
    CAIXA_FUNDO = altura_piso - 0.14      # fundo da caixa (escavado)
    CAIXA_TOPO_BRITA = altura_piso - 0.01 # topo da brita, logo abaixo do piso
    MEIO_FIO_H = 0.09                     # meio-fio acima do piso
    MEIO_FIO_W = 0.06
    ix0, ix1 = X0 + WT / 2.0, X1 - WT / 2.0
    iy0, iy1 = Y0 + WT / 2.0, Y1 - WT / 2.0
    # laje de fundo da caixa
    _box("Banheiro_Caixa_Brita_Fundo", (X0 + X1) / 2.0, (Y0 + Y1) / 2.0,
         CAIXA_FUNDO - 0.03, X1 - X0, Y1 - Y0, 0.06, mat_parede)
    # recheio de brita solta
    _box("Banheiro_Caixa_Brita_Recheio", (X0 + X1) / 2.0, (Y0 + Y1) / 2.0,
         (CAIXA_FUNDO + CAIXA_TOPO_BRITA) / 2.0,
         ix1 - ix0, iy1 - iy0, CAIXA_TOPO_BRITA - CAIXA_FUNDO, mat_brita)
    # meio-fio: moldura continua da caixa (borda interna das 4 paredes),
    # subindo acima do piso para conter a brita
    _mf_cz = altura_piso + MEIO_FIO_H / 2.0
    for _n, _cx, _cy, _sx, _sy in [
        ("Sul",   (ix0 + ix1) / 2.0, iy0 + MEIO_FIO_W / 2.0, ix1 - ix0, MEIO_FIO_W),
        ("Norte", (ix0 + ix1) / 2.0, iy1 - MEIO_FIO_W / 2.0, ix1 - ix0, MEIO_FIO_W),
        ("Oeste", ix0 + MEIO_FIO_W / 2.0, (iy0 + iy1) / 2.0, MEIO_FIO_W, iy1 - iy0),
        ("Leste", ix1 - MEIO_FIO_W / 2.0, (iy0 + iy1) / 2.0, MEIO_FIO_W, iy1 - iy0),
    ]:
        _box(f"Banheiro_Caixa_Brita_MeioFio_{_n}", _cx, _cy, _mf_cz,
             _sx, _sy, MEIO_FIO_H, mat_rustico)
    # meio-fio da parede central tambem (separa caixa duchas | caixa lavabos)
    _box("Banheiro_Caixa_Brita_MeioFio_Central", XM, (iy0 + iy1) / 2.0, _mf_cz,
         MEIO_FIO_W, iy1 - iy0, MEIO_FIO_H, mat_rustico)

    # --- Fixtures: 2 duchas (coluna oeste, porta no lado oeste) -----------
    shower_rows = [(Y0, YM), (YM, Y1)]
    for i, (ry0, ry1) in enumerate(shower_rows, start=1):
        cy = (ry0 + ry1) / 2.0
        wall_x = XM - WT / 2.0  # fixtures na parede central (oposta a porta)
        _box(f"Ducha_{i}_Base", wall_x - 0.35, cy, altura_piso - 0.005,
             0.7, (ry1 - ry0) - 0.15, 0.03, mat_louca)
        # coluna/haste da valvula ate o chuveiro (z 1,05 -> 2,05)
        _cyl(f"Ducha_{i}_Coluna", wall_x - 0.03, cy, altura_piso + 1.55,
             0.013, 1.0, mat_metal)
        # chuveiro eletrico no alto
        _box(f"Ducha_{i}_Eletrico", wall_x - 0.07, cy, altura_piso + 2.00,
             0.11, 0.10, 0.17, mat_chuveiro_box)
        # crivo (cabeca do chuveiro) apontando para baixo
        _cyl(f"Ducha_{i}_Crivo", wall_x - 0.15, cy, altura_piso + 1.88,
             0.055, 0.035, mat_metal)
        # braco do crivo ate a coluna
        _cyl(f"Ducha_{i}_Braco", wall_x - 0.09, cy, altura_piso + 1.90,
             0.012, 0.14, mat_metal, rotation=(0.0, math.radians(90), 0.0))
        # registro (valvula) na altura da mao
        _cyl(f"Ducha_{i}_Registro", wall_x - 0.05, cy, altura_piso + 1.05,
             0.022, 0.06, mat_metal, rotation=(0.0, math.radians(90), 0.0))

    # --- Fixtures: 2 sanitarios (SO o vaso, sem pia) ---------------------
    # As pias saem das cabines; o lava-maos passa a ser a pia comunitaria
    # na parede P8-P9 (abaixo).
    vaso_rows = [(Y0, YM), (YM, Y1)]
    for i, (ry0, ry1) in enumerate(vaso_rows, start=1):
        cy = (ry0 + ry1) / 2.0
        wall_x = XM + WT / 2.0  # vaso encostado na parede central (oposta a porta)
        toilet_cy = cy
        _box(f"Vaso_{i}_Caixa", wall_x + 0.10, toilet_cy, altura_piso + 0.62,
             0.16, 0.38, 0.30, mat_louca)
        bowl = _cyl(f"Vaso_{i}_Bacia", wall_x + 0.27, toilet_cy, altura_piso + 0.20,
                    0.19, 0.40, mat_louca)
        bowl.scale = (1.35, 1.0, 1.0)
        _box(f"Vaso_{i}_Assento", wall_x + 0.27, toilet_cy, altura_piso + 0.41,
             0.34, 0.30, 0.03, mat_louca)

    # --- Pia comunitaria (lava-maos), fixada na face SUL da parede P8-P9 --
    # Rustica, funda, com saboneteira e papeleira. Fica sob o beiral da ala.
    y_wall_sul = Y0 - WT / 2.0
    pia_cx = (X0 + X1) / 2.0
    pia_len = min(1.8, (X1 - X0) - 0.6)
    pia_top = altura_piso + 0.90
    pia_cy = y_wall_sul - 0.24              # projeta ~0,44 m para o sul
    _box("Pia_Comunitaria_Corpo", pia_cx, pia_cy, altura_piso + (pia_top - altura_piso) / 2.0,
         pia_len, 0.44, pia_top - altura_piso, mat_rustico)
    # cuba funda (rebaixo escuro no tampo)
    _box("Pia_Comunitaria_Cuba", pia_cx, pia_cy + 0.02, pia_top - 0.13,
         pia_len - 0.34, 0.30, 0.24, mat_louca)
    # bicas/torneiras comunitarias
    n_tap = 3
    for k in range(n_tap):
        tx = pia_cx + (k - (n_tap - 1) / 2.0) * (pia_len / n_tap)
        _cyl(f"Pia_Comunitaria_Torneira_{k+1}", tx, y_wall_sul - 0.05, pia_top + 0.13,
             0.014, 0.30, mat_metal)
        _cyl(f"Pia_Comunitaria_Bica_{k+1}", tx, y_wall_sul - 0.14, pia_top + 0.22,
             0.011, 0.16, mat_metal, rotation=(math.radians(55), 0.0, 0.0))
    # saboneteira (lado esquerdo, na parede acima do tampo)
    _box("Pia_Comunitaria_Saboneteira", pia_cx - pia_len / 2.0 + 0.12, y_wall_sul - 0.06,
         pia_top + 0.16, 0.16, 0.11, 0.04, mat_rustico)
    # papeleira / toalheiro de papel (lado direito, na parede)
    _box("Pia_Comunitaria_Papeleira", pia_cx + pia_len / 2.0 - 0.12, y_wall_sul - 0.08,
         pia_top + 0.24, 0.17, 0.15, 0.26, mat_rustico)

    return {
        "bounds": (X0, X1, Y0, Y1),
        "center_wall_x": XM,
        "row_split": YM,
        "pia_comunitaria": (pia_cx, pia_cy, pia_top),
    }
