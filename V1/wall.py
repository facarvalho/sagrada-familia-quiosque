"""
Fechamento em MURO TENDINOSO ao longo dos pilares 1-2-3-4-5 (lado sul +
lado leste do corredor principal), fechando esse lado do quiosque e
mantendo o lado oeste (voltado para a piscina) aberto.

Muro tendinoso: malla de vena + varão de 1/4" tensionados entre os pilares
de eucalipto e revestidos com argamassa nas duas faces -> parede fina
(~5 cm), monolítica, de reboco rústico. Aqui as paredes sobem ATÉ O TOPO
(face inferior do telhado), sem vão de ventilação.
"""
import bpy
import bmesh

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


def _panel(name, a, b, z0, zta, ztb, wt, mat):
    """Painel fino de parede entre A e B, base plana em z0 e topo indo de
    zta (em A) a ztb (em B) -> acompanha a inclinação do telhado."""
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    if abs(bx - ax) < 1e-6:            # parede ao longo de Y (x fixo)
        ox, oy = wt / 2.0, 0.0
    else:                             # parede ao longo de X (y fixo)
        ox, oy = 0.0, wt / 2.0

    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    v = [
        bm.verts.new((ax - ox, ay - oy, z0)),
        bm.verts.new((bx - ox, by - oy, z0)),
        bm.verts.new((bx - ox, by - oy, ztb)),
        bm.verts.new((ax - ox, ay - oy, zta)),
        bm.verts.new((ax + ox, ay + oy, z0)),
        bm.verts.new((bx + ox, by + oy, z0)),
        bm.verts.new((bx + ox, by + oy, ztb)),
        bm.verts.new((ax + ox, ay + oy, zta)),
    ]
    for f in ([0, 1, 2, 3], [7, 6, 5, 4], [4, 5, 1, 0],
              [3, 2, 6, 7], [4, 0, 3, 7], [1, 5, 6, 2]):
        bm.faces.new([v[i] for i in f])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        obj.data.materials.append(mat)
    return obj


def build(ns):
    pilares_coords = ns["pilares_coords"]
    altura_piso = ns["altura_piso"]

    mat_muro = _mat("Material_Muro_Tendinoso", (0.80, 0.78, 0.72, 1.0), roughness=0.97)
    mat_vidro = _mat("Material_Janela_Vidro", (0.75, 0.85, 0.88, 0.35), roughness=0.05, metallic=0.0)
    mat_caixilho = _mat("Material_Janela_Caixilho", (0.18, 0.18, 0.19, 1.0), roughness=0.4, metallic=0.6)

    p1 = pilares_coords[0]
    p2 = pilares_coords[1]
    p3 = pilares_coords[2]
    p4 = pilares_coords[3]
    p5 = pilares_coords[4]

    WT = 0.05                          # muro tendinoso ~5 cm
    Z0 = altura_piso

    def zt(x):
        return roof_frame.roof_underside_z(ns, x)

    def wall_segment(name, a, b):
        _panel(name, a, b, Z0, zt(a[0]), zt(b[0]), WT, mat_muro)

    # --- Parede sul (P1-P2), com janela sobre a pia nova (ver counter.py) --
    # Pia na parede sul centrada em x=2,2 (mesma posição em counter.py) -
    # janela de 1,10 m de largura, peitoril a 1,00 m, verga a 2,00 m.
    WIN_CX = 2.2
    WIN_W = 1.10
    WIN_X0, WIN_X1 = WIN_CX - WIN_W / 2.0, WIN_CX + WIN_W / 2.0
    WIN_SILL = Z0 + 1.00
    WIN_TOP = Z0 + 2.00
    y_sul = p1[1]

    wall_segment("Parede_Sul_1_Janela", p1, (WIN_X0, y_sul, 0.0))
    wall_segment("Parede_Sul_Janela_2", (WIN_X1, y_sul, 0.0), p2)
    _panel("Parede_Sul_Peitoril", (WIN_X0, y_sul, 0.0), (WIN_X1, y_sul, 0.0),
           Z0, WIN_SILL, WIN_SILL, WT, mat_muro)
    _panel("Parede_Sul_Verga", (WIN_X0, y_sul, 0.0), (WIN_X1, y_sul, 0.0),
           WIN_TOP, zt(WIN_X0), zt(WIN_X1), WT, mat_muro)

    # vidro + caixilho da janela
    win_cz = (WIN_SILL + WIN_TOP) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(WIN_CX, y_sul, win_cz))
    obj_vidro = bpy.context.active_object
    obj_vidro.name = "Janela_Sul_Vidro"
    obj_vidro.scale = (WIN_W - 0.06, WT + 0.02, WIN_TOP - WIN_SILL - 0.06)
    obj_vidro.data.materials.append(mat_vidro)

    frame_t = 0.04
    for name, cx, cy, cz, sx, sy, sz in [
        ("Janela_Sul_Caixilho_Sup", WIN_CX, y_sul, WIN_TOP - 0.03, WIN_W, WT + 0.03, frame_t),
        ("Janela_Sul_Caixilho_Inf", WIN_CX, y_sul, WIN_SILL + 0.03, WIN_W, WT + 0.03, frame_t),
        ("Janela_Sul_Caixilho_Esq", WIN_X0 + 0.03, y_sul, win_cz, frame_t, WT + 0.03, WIN_TOP - WIN_SILL),
        ("Janela_Sul_Caixilho_Dir", WIN_X1 - 0.03, y_sul, win_cz, frame_t, WT + 0.03, WIN_TOP - WIN_SILL),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
        o = bpy.context.active_object
        o.name = name
        o.scale = (sx, sy, sz)
        o.data.materials.append(mat_caixilho)

    wall_segment("Parede_Leste_2_3", p2, p3)
    wall_segment("Parede_Leste_3_4", p3, p4)
    wall_segment("Parede_Leste_4_5", p4, p5)

    return {"top_z": zt(4.0), "janela_sul": {"cx": WIN_CX, "sill": WIN_SILL, "top": WIN_TOP}}
