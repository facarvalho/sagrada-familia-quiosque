"""
Geladeira e fogão encostados na parede sul, entre os pilares 1 (0,0) e
2 (4,0) - completando a área gourmet (bancada com pia/churrasqueira fica
na parede leste, entre pilares 2 e 3).
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


def _cyl(name, cx, cy, cz, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(cx, cy, cz))
    obj = bpy.context.active_object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj


def build(ns):
    altura_piso = ns["altura_piso"]

    mat_inox = _mat("Material_Eletro_Inox", (0.72, 0.73, 0.75, 1.0), roughness=0.3, metallic=0.85)
    mat_preto = _mat("Material_Eletro_Preto", (0.05, 0.05, 0.05, 1.0), roughness=0.4)

    Y_WALL = 0.03  # face interna da parede sul (y=0 +- espessura/2)

    # --- Geladeira (perto do Pilar 2, ao lado da área gourmet) --------------
    fr_w, fr_d, fr_h = 0.68, 0.65, 1.80
    fr_cx, fr_cy = 2.85, Y_WALL + fr_d / 2.0
    _box("Geladeira_Corpo", fr_cx, fr_cy, altura_piso + fr_h / 2.0, fr_w, fr_d, fr_h, mat_inox)
    _box("Geladeira_Linha_Divisoria", fr_cx, fr_cy - fr_d / 2.0 - 0.005, altura_piso + fr_h * 0.62,
         fr_w - 0.04, 0.01, 0.02, mat_preto)
    _box("Geladeira_Puxador_1", fr_cx + fr_w / 2.0 - 0.04, fr_cy - fr_d / 2.0 - 0.02,
         altura_piso + fr_h * 0.8, 0.03, 0.03, 0.35, mat_preto)
    _box("Geladeira_Puxador_2", fr_cx + fr_w / 2.0 - 0.04, fr_cy - fr_d / 2.0 - 0.02,
         altura_piso + fr_h * 0.35, 0.03, 0.03, 0.30, mat_preto)

    # --- Fogão (entre a geladeira e o Pilar 1) ------------------------------
    st_w, st_d, st_h = 0.60, 0.60, 0.90
    st_cx, st_cy = 1.6, Y_WALL + st_d / 2.0
    _box("Fogao_Corpo", st_cx, st_cy, altura_piso + st_h / 2.0, st_w, st_d, st_h, mat_inox)
    _box("Fogao_Cooktop", st_cx, st_cy, altura_piso + st_h + 0.01, st_w - 0.02, st_d - 0.02, 0.02, mat_preto)
    for i, sx in enumerate((-1, 1)):
        for j, sy in enumerate((-1, 1)):
            _cyl(f"Fogao_Boca_{i}_{j}", st_cx + sx * st_w * 0.22, st_cy + sy * st_d * 0.22,
                 altura_piso + st_h + 0.02, 0.06, 0.01, mat_preto)
    _box("Fogao_Forno_Porta", st_cx, st_cy - st_d / 2.0 - 0.005, altura_piso + st_h * 0.35,
         st_w - 0.06, 0.01, st_h * 0.55, mat_preto)

    return {"fridge_pos": (fr_cx, fr_cy), "stove_pos": (st_cx, st_cy)}
