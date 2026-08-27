"""
Sala de estar externa entre os pilares 4, 5 e 6 (canto nordeste do
corredor principal / transição para a ala). Dois sofás de frente um para o
outro com mesa de centro entre eles, sobre um tapete.
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


def _cyl(name, cx, cy, cz, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj


def _sofa(prefix, cx, cy, facing, mat_estrutura, mat_almofada, altura_piso,
          length=2.0, depth=0.85):
    """facing: 'north' o sofa fica ao sul olhando p/ +Y, 'south' fica ao
    norte olhando p/ -Y (encosto do lado oposto ao 'facing')."""
    seat_h = altura_piso + 0.42
    back_h = altura_piso + 0.80
    sign = 1.0 if facing == "north" else -1.0

    if True:
        # comprimento ao longo de X, profundidade ao longo de Y
        _box(f"{prefix}_Assento", cx, cy, seat_h, length, depth, 0.14, mat_almofada)
        _box(f"{prefix}_Encosto", cx, cy - sign * (depth / 2 - 0.06), (seat_h + back_h) / 2.0,
             length, 0.12, back_h - seat_h, mat_almofada)
        for sx in (-1, 1):
            _box(f"{prefix}_Braco_{sx}", cx + sx * (length / 2 - 0.06), cy, (altura_piso + back_h) / 2.0 - 0.05,
                 0.12, depth, back_h - altura_piso - 0.15, mat_estrutura)
        for i, sx in enumerate((-1, 1)):
            for sy in (-1, 1):
                _box(f"{prefix}_Pe_{i}_{sy}", cx + sx * (length / 2 - 0.15), cy + sy * (depth / 2 - 0.1),
                     (altura_piso + 0.12) / 2.0, 0.06, 0.06, 0.12, mat_estrutura)


def build(ns):
    altura_piso = ns["altura_piso"]

    mat_estrutura = _mat("Material_Sofa_Estrutura", (0.28, 0.18, 0.11, 1.0), roughness=0.75)
    mat_almofada = _mat("Material_Sofa_Almofada", (0.55, 0.52, 0.46, 1.0), roughness=0.9)
    mat_mesa = _mat("Material_Mesa_Centro", (0.30, 0.20, 0.12, 1.0), roughness=0.6)
    mat_tapete = _mat("Material_Tapete", (0.62, 0.35, 0.25, 1.0), roughness=0.95)

    # Área aproximada entre pilares 4 (4,8), 5 (4,12) e 6 (0.75,12).
    CX, CY = 2.3, 9.7

    _box("Sala_Tapete", CX, CY, altura_piso + 0.005, 2.6, 3.0, 0.01, mat_tapete)

    _sofa("Sofa_Sul", CX, CY - 0.85, "north", mat_estrutura, mat_almofada, altura_piso)
    _sofa("Sofa_Norte", CX, CY + 0.85, "south", mat_estrutura, mat_almofada, altura_piso)

    table_h = altura_piso + 0.35
    _box("Mesa_Centro_Tampo", CX, CY, table_h, 1.0, 0.55, 0.05, mat_mesa)
    for sx in (-1, 1):
        for sy in (-1, 1):
            _cyl(f"Mesa_Centro_Pe_{sx}_{sy}", CX + sx * 0.42, CY + sy * 0.20,
                 (altura_piso + table_h - 0.03) / 2.0, 0.025, (table_h - 0.03) - altura_piso, mat_mesa)

    return {"center": (CX, CY)}
