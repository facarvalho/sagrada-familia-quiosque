"""
Mesas de bar altas espalhadas entre os pilares 3 (4,4) e 4 (4,8), cada uma
com 2 banquetas.
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


def _cyl(name, cx, cy, cz, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj


def _bar_table(prefix, cx, cy, altura_piso, mat_madeira, mat_metal):
    top_h = altura_piso + 1.10
    _cyl(f"{prefix}_Tampo", cx, cy, top_h, 0.32, 0.04, mat_madeira)
    _cyl(f"{prefix}_Coluna", cx, cy, (altura_piso + top_h - 0.02) / 2.0,
         0.04, (top_h - 0.02) - altura_piso, mat_metal)
    _cyl(f"{prefix}_Base", cx, cy, altura_piso + 0.02, 0.22, 0.04, mat_metal)

    stool_h = altura_piso + 0.75
    for i, ang in enumerate((60, 240)):
        rad = math.radians(ang)
        sx, sy = cx + 0.55 * math.cos(rad), cy + 0.55 * math.sin(rad)
        _cyl(f"{prefix}_Banqueta_{i+1}_Assento", sx, sy, stool_h, 0.16, 0.04, mat_madeira)
        _cyl(f"{prefix}_Banqueta_{i+1}_Coluna", sx, sy, (altura_piso + stool_h - 0.02) / 2.0,
             0.03, (stool_h - 0.02) - altura_piso, mat_metal)
        _cyl(f"{prefix}_Banqueta_{i+1}_Base", sx, sy, altura_piso + 0.015, 0.14, 0.03, mat_metal)


def build(ns):
    altura_piso = ns["altura_piso"]

    mat_madeira = _mat("Material_MesaBar_Madeira", (0.36, 0.24, 0.14, 1.0), roughness=0.7)
    mat_metal = _mat("Material_MesaBar_Metal", (0.15, 0.15, 0.16, 1.0), roughness=0.35, metallic=0.85)

    # Entre Pilar 3 (4,4) e Pilar 4 (4,8): 2 mesas espalhadas.
    positions = [(2.6, 5.1), (1.6, 6.9)]
    for i, (x, y) in enumerate(positions, start=1):
        _bar_table(f"MesaBar_{i}", x, y, altura_piso, mat_madeira, mat_metal)

    return {"positions": positions}
