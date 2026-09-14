"""
Estrutura da cobertura em meia-água (caimento de 15% escoando para OESTE,
x=0 - em direção à piscina). Lado alto: leste (x=4).

Estrutura enxuta (a telha de 1,00 x 4,50 m vence até 2,50 m de vão livre):

  1. Montantes curtos sobre os 4 pilares da fileira leste (x=4), para
     levantar esse lado e formar o caimento de 15%.
  2. Vigas transversais V1..V6 (sentido X), pilar a pilar.
  3. Terças T1..T4 (sentido Y) sobre as transversais: T1 x=0,40 (fileira
     recuada) / T2 no eixo entre T1 e T3 (x=2,20) / T3 x=4,0 + T4 na ala
     (x=-2,25). As 4 terças terminam na mesma linha norte (y=12,50 = beiral
     de 0,50 m). T1-T3 tem 11,0 m (ponta sul em y=1,50); T4 tem 3,50 m,
     centrada no vão P8-P7 (mid y=10,75).

A telha assenta direto nas terças (cantilever nas pontas = beiral). O
objeto Telhado_Zinco_L (plano já inclinado, criado em projeto.py) é
transladado no eixo Z para descansar sobre as terças.

`build()` retorna, em result["schedule"], a numeração e o comprimento de
todas as terças e vigas transversais (usado pela planta anotada).

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


def roof_underside_z(ns, x):
    """Cota da face inferior do telhado (já com o roof_raise aplicado) em
    função de x. As paredes de muro tendinoso (wall.py / bathroom.py) sobem
    até aqui para ficarem "até o topo", sem vão de ventilação."""
    altura_pilar = ns["altura_pilar"]
    caimento = ns.get("caimento_telhado", 0.15)
    x_baixo = ns.get("x_beiral_baixo", 0.0)
    R = 0.065
    z_transv_baixo = altura_pilar + R                 # z_transv(x_baixo)
    target_low = z_transv_baixo + 2 * R + R + 0.02    # = base da telha no beiral baixo
    return target_low + caimento * (x - x_baixo)


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

    recuo_oeste = ns.get("recuo_oeste", 0.0)
    _beiral_ala = ns.get("beiral_ala", 0.7)

    # --- 1. Montantes sobre a fileira leste (lado alto) ------------------
    for name, pt in [("Montante_P2", p[2]), ("Montante_P3", p[3]),
                     ("Montante_P4", p[4]), ("Montante_P5", p[5])]:
        z0 = altura_pilar
        z1 = z_transv(pt[0]) - R          # topo do montante = base da transversal
        if z1 - z0 > 0.02:
            _beam(name, (pt[0], pt[1], z0), (pt[0], pt[1], z1), R, mat_viga)

    # --- 2. Vigas transversais (sentido X), pilar a pilar --------------
    # Numeradas V1..V6 (sul -> norte). Comprimento medido entre eixos de
    # pilares (3,60 m nas do corpo, fileira oeste recuada 0,40 m). EXCEÇÃO:
    # V1 e V2 avançam 0,40 m a oeste, até a linha do beiral/calha (x=0),
    # para APOIAR A CALHA -> ficam com 4,00 m.
    x_calha = ns.get("x_beiral_oeste", 0.0)
    v1_oeste = (x_calha, p[1][1], p[1][2])
    v2_oeste = (x_calha, p[10][1], p[10][2])
    transversais = [
        ("V1", "Viga_Transv_V1", v1_oeste, p[2]),  # x=0 -> P2   (y=1,5)  L=4,00
        ("V2", "Viga_Transv_V2", v2_oeste, p[3]),  # x=0 -> P3   (y=5,5)  L=4,00
        ("V3", "Viga_Transv_V3", p[9],  p[4]),   # P9-P4   (y=9,5)
        ("V4", "Viga_Transv_V4", p[6],  p[5]),   # P6-P5   (y=12)
        ("V5", "Viga_Transv_V5_Ala", p[8], p[9]),  # P8-P9  (y=9,5, ala)
        ("V6", "Viga_Transv_V6_Ala", p[7], p[6]),  # P7-P6  (y=12,  ala)
    ]
    schedule = {"transversais": [], "tercas": []}
    for num, name, a, b in transversais:
        _beam(name, (a[0], a[1], z_transv(a[0])), (b[0], b[1], z_transv(b[0])),
              R, mat_viga)
        comp = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
        schedule["transversais"].append({
            "n": num, "nome": name, "eixo": "X", "y": round(a[1], 2),
            "p1": [round(a[0], 2), round(a[1], 2)],
            "p2": [round(b[0], 2), round(b[1], 2)],
            "comprimento": round(comp, 2),
        })

    # --- 3. Terças (sentido Y), sobre as transversais -----------------
    # Numeradas T1..T4 (oeste -> leste, + a da ala). Todas as quatro terças
    # terminam na MESMA linha ao norte (y = 12,50), formando um beiral
    # contínuo de 0,50 m além da fileira de pilares norte (y = 12,0).
    #  - T1..T3: L = 11,00 m -> ponta sul em y = 1,50 (na linha de P1/P2).
    #    T2 fica exatamente no eixo entre T1 (x=recuo_oeste) e T3 (x=4,0).
    #  - T4 (ala): L = 3,50 m -> ponta sul em y = 9,00; segue centrada no
    #    vão P8-P7 (y 9,5..12,0 -> mid 10,75).
    z_terca_off = 2 * R

    y_beiral_norte = 12.5                 # ponta norte comum a T1..T4
    x_t2 = (recuo_oeste + 4.0) / 2.0

    comp_corpo = 11.0
    y1_corpo = y_beiral_norte
    y0_corpo = y1_corpo - comp_corpo

    comp_ala = 3.5
    y1_ala = y_beiral_norte
    y0_ala = y1_ala - comp_ala

    tercas = [
        ("T1", "Terca_T1_Oeste",   recuo_oeste, y0_corpo, y1_corpo),  # sobre P1-P10-P9-P6
        ("T2", "Terca_T2_Central", x_t2,        y0_corpo, y1_corpo),  # eixo entre T1 e T3
        ("T3", "Terca_T3_Leste",   4.0,         y0_corpo, y1_corpo),  # sobre P2-P3-P4-P5
        ("T4", "Terca_T4_Ala",    -2.25,        y0_ala,   y1_ala),    # centrada em P8-P7
    ]
    for num, name, x, y0, y1 in tercas:
        z = z_transv(x) + z_terca_off
        _beam(name, (x, y0, z), (x, y1, z), R, mat_viga)
        schedule["tercas"].append({
            "n": num, "nome": name, "eixo": "Y", "x": round(x, 2),
            "y0": round(y0, 2), "y1": round(y1, 2),
            "comprimento": round(y1 - y0, 2),
        })

    # --- 4. Reposiciona o telhado sobre as terças --------------------
    telhado = bpy.data.objects.get("Telhado_Zinco_L")
    roof_raise = 0.0
    if telhado:
        original_low = altura_pilar + 0.05             # z_telhado(x_baixo)
        roof_raise = roof_underside_z(ns, x_baixo) - original_low
        telhado.location.z += roof_raise

    return {"roof_raise": roof_raise, "z_transv_x4": z_transv(4.0),
            "schedule": schedule, "R": R, "beiral_ala": _beiral_ala}
