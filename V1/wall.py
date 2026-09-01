"""
Parede de fechamento em placa cimentícia ao longo dos pilares 1-2-3-4-5
(lado sul + lado leste do corredor principal), fechando esse lado do
quiosque e mantendo o lado oeste (voltado para a piscina) aberto.
"""
import bpy


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


def build(ns):
    pilares_coords = ns["pilares_coords"]
    altura_piso = ns["altura_piso"]

    mat_placa = _mat("Material_Placa_Cimenticia", (0.72, 0.71, 0.68, 1.0), roughness=0.8)

    p1 = pilares_coords[0]   # (0, 0)
    p2 = pilares_coords[1]   # (4, 0)
    p3 = pilares_coords[2]   # (4, 4)
    p4 = pilares_coords[3]   # (4, 8)
    p5 = pilares_coords[4]   # (4, 12)

    WT = 0.06
    Z0 = altura_piso
    # Lado leste (x=4) e o beiral baixo da meia-agua (~2.5 m). Parede em
    # 2.0 m deixa um vao de ventilacao ate o telhado em todo o trecho.
    Z1 = altura_piso + 2.0

    def wall_segment(name, a, b):
        x0, x1 = min(a[0], b[0]), max(a[0], b[0])
        y0, y1 = min(a[1], b[1]), max(a[1], b[1])
        if x1 - x0 < 0.01:  # segmento vertical (varia em Y, parede ao longo de X fixo)
            x0, x1 = a[0] - WT / 2, a[0] + WT / 2
        else:  # segmento horizontal (varia em X, parede ao longo de Y fixo)
            y0, y1 = a[1] - WT / 2, a[1] + WT / 2
        cx, cy, cz = (x0 + x1) / 2.0, (y0 + y1) / 2.0, (Z0 + Z1) / 2.0
        _box(name, cx, cy, cz, max(x1 - x0, WT), max(y1 - y0, WT), Z1 - Z0, mat_placa)

    wall_segment("Parede_Sul_1_2", p1, p2)
    wall_segment("Parede_Leste_2_3", p2, p3)
    wall_segment("Parede_Leste_3_4", p3, p4)
    wall_segment("Parede_Leste_4_5", p4, p5)

    return {"top_z": Z1}
