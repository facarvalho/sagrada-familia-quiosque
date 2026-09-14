"""
Calcadas de concreto ao redor do quiosque + calha no beiral oeste +
drenagem pluvial.

Pedido do cliente (07/09/2026):
  - Sul (P1-P2):     faixa de 0,50 m para fora
  - Banheiro (ala): faixa de 1,00 m só nos lados OESTE e NORTE. O lado sul
    da ala (y < 9,5) NÃO leva calçada nova — ali já existe o piso de
    concreto da área da piscina (`Piso_Area_Piscina`, que vai até y=9,5).
  - Norte (P7-P5):   faixa de 1,00 m para fora
  - Calha (meia-cana) sob o beiral oeste do corpo principal, que ganhou
    0,40 m de balanco com o recuo da fileira de pilares oeste.
  - DRENAGEM PLUVIAL: no chão da piscina, seguindo o alinhamento da calha,
    uma canaleta com grelha (trecho aparente) que despeja num cano de
    esgoto Ø100 mm. O cano segue enterrado e ATRAVESSA O BANHEIRO (ala)
    como subterrâneo, saindo ao norte numa caixa de inspeção.
"""
import bpy
import math


def _mat(name, color, roughness=0.6, metallic=0.0):
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _slab(name, x0, x1, y0, y1, mat, z_top=0.0, esp=0.10):
    # z_top = cota do topo da calcada; por padrao no nivel do deck da
    # piscina (0). A laje e escavada para baixo (esp).
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, z_top - esp / 2.0))
    o = bpy.context.active_object
    o.name = name
    o.scale = (max(x1 - x0, 0.01), max(y1 - y0, 0.01), esp)
    o.data.materials.append(mat)
    return o


def build(ns):
    mat_calcada = bpy.data.materials.get("Material_Concreto_Area") or _mat(
        "Material_Concreto_Area", (0.7, 0.68, 0.62, 1.0), roughness=0.5
    )
    mat_calha = _mat("Material_Calha", (0.72, 0.74, 0.76, 1.0), roughness=0.3, metallic=0.8)

    altura_pilar = ns.get("altura_pilar", 2.5)
    nivel = ns.get("nivel_piscina", 0.0)
    # Topo das calcadas 1 cm ACIMA do deck da piscina: fica visualmente
    # rente, mas evita z-fighting (faces coplanares -> pretas) com o
    # `Piso_Area_Piscina` e entre as próprias placas.
    z = nivel + 0.01

    # --- Calcada Sul (P1-P2), 0,50 m para fora (y de 1,0 a 1,5) -----------
    _slab("Calcada_Sul", 0.0, 4.0, 1.0, 1.5, mat_calcada, z_top=z)

    # --- Calcada da ala: só OESTE e NORTE -------------------------------
    # Bloco do banheiro: x -2,25..0,40 ; y 9,5..12,0. Faixa de 1,00 m nos
    # lados oeste (y 9,5..13,0, pega o canto NO) e norte. O lado SUL da ala
    # (y < 9,5) não leva calçada: ali já existe o `Piso_Area_Piscina`.
    _slab("Calcada_Ala_Oeste", -3.25, -2.25, 9.5, 13.0, mat_calcada, z_top=z)

    # --- Calcada Norte (P6-P5 + canto NO da ala), 1,00 m para fora -------
    _slab("Calcada_Norte", -2.25, 4.0, 12.0, 13.0, mat_calcada, z_top=z)

    # --- Calha sob o beiral oeste do corpo principal --------------------
    # beiral oeste da telha em x = 0; a calha corre em y de ~1,1 ate ~9,5,
    # pendurada rente a ponta do beiral (telhado ja reposicionado ~+0,23 m
    # sobre as tercas -> ver roof_frame.roof_raise).
    cy0, cy1 = 1.1, 9.5
    cx = -0.02
    z_calha = altura_pilar + 0.22 - 0.06              # rente a ponta do beiral baixo
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.06, depth=(cy1 - cy0), vertices=16,
        location=(cx, (cy0 + cy1) / 2.0, z_calha),
    )
    o = bpy.context.active_object
    o.name = "Calha_Beiral_Oeste"
    o.rotation_euler = (math.radians(90), 0.0, 0.0)
    o.data.materials.append(mat_calha)

    dren = _drenagem_pluvial(ns, nivel, z_calha, cy0)

    return {
        "calcadas": ["Calcada_Sul", "Calcada_Ala_Oeste", "Calcada_Norte"],
        "calha": "Calha_Beiral_Oeste",
        "drenagem": dren,
    }


def _drenagem_pluvial(ns, nivel, z_calha, y_calha_sul):
    """Canaleta com grelha no chão da piscina (alinhada com a calha) que
    escoa para um cano de esgoto Ø100 mm. O cano segue enterrado e cruza
    o banheiro (ala, y 9,5..12,0) como subterrâneo, saindo ao norte."""
    mat_canal = _mat("Material_Canaleta", (0.30, 0.30, 0.32, 1.0), roughness=0.9)
    mat_grelha = _mat("Material_Grelha_Ferro", (0.28, 0.29, 0.30, 1.0),
                      roughness=0.45, metallic=0.9)
    mat_cano = _mat("Material_Cano_PVC", (0.86, 0.86, 0.84, 1.0), roughness=0.35)

    X = -0.10                       # eixo da drenagem (alinhado com a calha ~x=0)
    LARG = 0.18                     # largura da canaleta
    DIAM = 0.10                     # cano Ø100 mm
    y_sul, y_ala0, y_ala1, y_norte = 1.0, 9.5, 12.0, 13.3

    # --- Canaleta aberta (trecho aparente: y_sul -> y_ala0) --------------
    # corpo/void escuro, rebaixado; topo ~3 cm abaixo do deck.
    cx, cy = X, (y_sul + y_ala0) / 2.0
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, nivel - 0.13))
    canal = bpy.context.active_object
    canal.name = "Canaleta_Pluvial"
    canal.scale = (LARG, y_ala0 - y_sul, 0.22)
    canal.data.materials.append(mat_canal)

    # grelha (chapa perfurada) rente ao deck
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, nivel - 0.015))
    grelha = bpy.context.active_object
    grelha.name = "Canaleta_Grelha"
    grelha.scale = (LARG - 0.03, y_ala0 - y_sul, 0.02)
    grelha.data.materials.append(mat_grelha)

    # --- Tubo de queda: da calha (topo) até a canaleta -----------------
    h = z_calha - (nivel - 0.05)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.038, depth=h, vertices=16,
        location=(0.0, y_calha_sul + 0.15, (z_calha + nivel - 0.05) / 2.0),
    )
    tq = bpy.context.active_object
    tq.name = "Tubo_Queda_Calha"
    tq.data.materials.append(mat_cano)

    # --- Cano de esgoto Ø100 enterrado (y_sul -> y_norte), cruza a ala --
    z_cano = nivel - 0.30
    bpy.ops.mesh.primitive_cylinder_add(
        radius=DIAM / 2.0, depth=(y_norte - y_sul), vertices=20,
        location=(X, (y_sul + y_norte) / 2.0, z_cano),
    )
    cano = bpy.context.active_object
    cano.name = "Cano_Drenagem_Pluvial_100"
    cano.rotation_euler = (math.radians(90), 0.0, 0.0)
    cano.data.materials.append(mat_cano)

    # --- Caixa de inspeção no fim (norte, além da calçada) -------------
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(X, y_norte - 0.2, nivel - 0.25))
    caixa = bpy.context.active_object
    caixa.name = "Caixa_Inspecao_Pluvial"
    caixa.scale = (0.45, 0.45, 0.55)
    caixa.data.materials.append(mat_canal)

    return {
        "eixo_x": X,
        "canaleta": [y_sul, y_ala0],       # trecho com grelha (aparente)
        "cano": [y_sul, y_norte],          # cano Ø100 (enterrado)
        "sob_banheiro": [y_ala0, y_ala1],  # trecho subterrâneo sob a ala
        "caixa_y": y_norte - 0.2,
        "diam_mm": int(DIAM * 1000),
    }
