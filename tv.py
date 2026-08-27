"""
TV montada na parede leste, entre os pilares 4 (4,8) e 5 (4,12), voltada
para a sala de estar (entre pilares 4, 5 e 6).
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
    altura_piso = ns["altura_piso"]

    mat_tela = _mat("Material_TV_Tela", (0.02, 0.02, 0.03, 1.0), roughness=0.15, metallic=0.2)
    mat_moldura = _mat("Material_TV_Moldura", (0.08, 0.08, 0.08, 1.0), roughness=0.4)

    WALL_X = 4.0
    TV_CX = WALL_X - 0.035
    TV_CY = 10.0
    TV_CZ = altura_piso + 1.55
    TV_W, TV_H = 1.25, 0.72

    _box("TV_Suporte", WALL_X - 0.02, TV_CY, TV_CZ, 0.04, 0.30, 0.10, mat_moldura)
    _box("TV_Moldura", TV_CX, TV_CY, TV_CZ, 0.035, TV_W + 0.04, TV_H + 0.04, mat_moldura)
    _box("TV_Tela", TV_CX - 0.01, TV_CY, TV_CZ, 0.015, TV_W, TV_H, mat_tela)

    return {"position": (TV_CX, TV_CY, TV_CZ)}
