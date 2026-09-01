"""
Estrutura da cobertura em meia-água (caimento de 15% escoando para OESTE,
x=0 - em direção à piscina). Lado alto: leste (x=4).

Estrutura enxuta (a telha de 1,00 x 4,50 m vence até 2,50 m de vão livre):

  1. Montantes curtos sobre os 4 pilares da fileira leste (x=4), para
     levantar esse lado e formar o caimento de 15%.
  2. Vigas transversais (sentido X) sobre os pares de pilares, acompanhando
     o caimento.
  3. Terças (sentido Y) sobre as transversais, em x = 0 / 2 / 4 (espaçamento
     ~2,0 m <= 2,5 m) + uma terça na ala (x = -2.25).

A telha assenta direto nas terças. O objeto Telhado_Zinco_L (plano já
inclinado, criado em projeto.py) é transladado no eixo Z para descansar
sobre as terças.

Bitola de todas as peças: eucalipto roliço 12/14 (raio 0.065 m); as terças
poderiam ser 8/10, mas o vão entre transversais favorece manter 12/14.
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


def _beam(name, p1, p2, radius, mat):
    """Viga cilíndrica entre dois pontos 3D quaisquer (aceita inclinação)."""
    a = mathutils.Vector((p1[0], p1[1], p1[2]))
    b = mathutils.Vector((p2[0], p2[1], p2[2]))
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
    altura_pilar = ns["altura_pilar"]                 # topo dos pilares (2.5)
    caimento = ns.get("caimento_telhado", 0.15)
    x_baixo = ns.get("x_beiral_baixo", 0.0)           # lado baixo = oeste

    mat_viga = bpy.data.materials.get("Material_Eucalipto") or _mat(
        "Material_Eucalipto", (0.35, 0.22, 0.12, 1.0), roughness=0.8
    )

    p = {i + 1: pilares_coords[i] for i in range(10)}
    R = 0.065          # eucalipto 12/14

    # Cota do eixo das vigas transversais em função de x. No lado baixo
    # (x=0) elas apoiam direto no topo dos pilares.
    def z_transv(x):
        return altura_pilar + R + caimento * (x - x_baixo)

    # --- 1. Montantes sobre a fileira leste (lado alto) ------------------
    for name, pt in [("Montante_P2", p[2]), ("Montante_P3", p[3]),
                     ("Montante_P4", p[4]), ("Montante_P5", p[5])]:
        z0 = altura_pilar
        z1 = z_transv(pt[0]) - R          # topo do montante = base da transversal
        if z1 - z0 > 0.02:
            _beam(name, (pt[0], pt[1], z0), (pt[0], pt[1], z1), R, mat_viga)

    # --- 2. Vigas transversais (sentido X), acompanham o caimento -------
    transversais = [
        ("Viga_Transv_Y0",       p[1],  p[2]),   # (0,0)-(4,0)
        ("Viga_Transv_Y4",       p[10], p[3]),   # (0,4)-(4,4)
        ("Viga_Transv_P9_P4",    p[9],  p[4]),   # (0,9.5)-(4,8)
        ("Viga_Transv_Y12",      p[6],  p[5]),   # (0,12)-(4,12)
        ("Viga_Transv_Ala_Y9_5", p[8],  p[9]),   # (-2.25,9.5)-(0,9.5)
        ("Viga_Transv_Ala_Y12",  p[7],  p[6]),   # (-2.25,12)-(0,12)
    ]
    for name, a, b in transversais:
        _beam(name,
              (a[0], a[1], z_transv(a[0])),
              (b[0], b[1], z_transv(b[0])),
              R, mat_viga)

    # --- 3. Terças (sentido Y), sobre as transversais ------------------
    z_terca_off = 2 * R
    tercas = [
        ("Terca_Oeste_X0",   0.0,   0.0,  12.0),
        ("Terca_Central_X2", 2.0,   0.0,  12.0),
        ("Terca_Leste_X4",   4.0,   0.0,  12.0),
        ("Terca_Ala_Xm225", -2.25,  9.25, 12.0),
    ]
    for name, x, y0, y1 in tercas:
        z = z_transv(x) + z_terca_off
        _beam(name, (x, y0, z), (x, y1, z), R, mat_viga)

    # --- 4. Reposiciona o telhado sobre as terças ---------------------
    telhado = bpy.data.objects.get("Telhado_Zinco_L")
    roof_raise = 0.0
    if telhado:
        original_low = altura_pilar + 0.05             # z_telhado(x_baixo)
        target_low = z_transv(x_baixo) + z_terca_off + R + 0.02
        roof_raise = target_low - original_low
        telhado.location.z += roof_raise

    return {"roof_raise": roof_raise, "z_transv_x4": z_transv(4.0)}
