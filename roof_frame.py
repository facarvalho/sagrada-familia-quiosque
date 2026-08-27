"""
Estrutura de vigas de eucalipto para apoiar o telhado (vão livre máximo de
3m das telhas). Duas camadas:

  Camada 1 (travamento entre pilares, apoiada no topo dos pilares):
    Pilar1-Pilar2, Pilar10-Pilar3, Pilar6-Pilar5, Pilar9-Pilar4,
    Pilar7-Pilar6, Pilar8-Pilar9

  Camada 2 (apoiada sobre a camada 1):
    Pilar2-Pilar5 (lado leste), Pilar1-Pilar6 (lado oeste), uma viga
    central entre elas (sem pilar embaixo), e Pilar7-Pilar8 (que fica em
    cima das vigas Pilar7-Pilar6 e Pilar8-Pilar9)

O telhado (Telhado_Zinco_L) é então reposicionado para descansar sobre o
topo da camada 2, em vez de flutuar 5cm acima do topo dos pilares como no
projeto original.
"""
import bpy
import mathutils


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


def _beam(name, p1, p2, z, radius, mat):
    a = mathutils.Vector((p1[0], p1[1], z))
    b = mathutils.Vector((p2[0], p2[1], z))
    direction = b - a
    length = direction.length
    mid = (a + b) / 2.0

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    if mat:
        obj.data.materials.append(mat)
    return obj


def build(ns):
    pilares_coords = ns["pilares_coords"]
    altura_pilar = ns["altura_pilar"]

    mat_viga = bpy.data.materials.get("Material_Eucalipto") or _mat(
        "Material_Eucalipto", (0.35, 0.22, 0.12, 1.0), roughness=0.8
    )

    p = {i + 1: pilares_coords[i] for i in range(10)}
    VIGA_R = 0.07

    z1 = altura_pilar + VIGA_R           # centro da camada 1 (apoiada no topo dos pilares)
    z1_top = altura_pilar + 2 * VIGA_R
    z2 = z1_top + VIGA_R                 # centro da camada 2 (apoiada sobre a camada 1)
    z2_top = z1_top + 2 * VIGA_R

    # --- Camada 1: travamentos entre pilares -----------------------------
    camada1 = [
        ("Viga_P1_P2", p[1], p[2]),
        ("Viga_P10_P3", p[10], p[3]),
        ("Viga_P6_P5", p[6], p[5]),
        ("Viga_P9_P4", p[9], p[4]),
        ("Viga_P7_P6", p[7], p[6]),
        ("Viga_P8_P9", p[8], p[9]),
    ]
    for name, a, b in camada1:
        _beam(name, a, b, z1, VIGA_R, mat_viga)

    # --- Camada 2: vigas longitudinais (leste, oeste, central) + a viga
    # Pilar7-Pilar8, que fica em cima das vigas Pilar7-Pilar6 e Pilar8-Pilar9 --
    y_min = min(pt[1] for pt in pilares_coords if pt[0] in (0.0,)) if False else 0.0
    y_max = 12.0
    camada2 = [
        ("Viga_Longitudinal_Leste", p[2], p[5]),
        ("Viga_Longitudinal_Oeste", p[1], p[6]),
        ("Viga_Longitudinal_Central", (2.0, y_min, 0.0), (2.0, y_max, 0.0)),
        ("Viga_P7_P8", p[7], p[8]),
    ]
    for name, a, b in camada2:
        _beam(name, a, b, z2, VIGA_R, mat_viga)

    # --- Reposiciona o telhado para descansar sobre a camada 2 ------------
    telhado = bpy.data.objects.get("Telhado_Zinco_L")
    roof_raise = 0.0
    if telhado:
        original_roof_z = altura_pilar + 0.05  # fórmula usada no projeto.py
        target_roof_z = z2_top + 0.02
        roof_raise = target_roof_z - original_roof_z
        telhado.location.z += roof_raise

    return {"z1_top": z1_top, "z2_top": z2_top, "roof_raise": roof_raise}
