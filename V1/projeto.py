import bpy
import bmesh

# ---------------------------------------------------------------------------
# 0. LIMPEZA DA CENA
# ---------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

collection = bpy.context.collection

# ---------------------------------------------------------------------------
# 1. VARIÁVEIS GLOBAIS DE POSIÇÃO E CONFIGURAÇÃO
# ---------------------------------------------------------------------------
centro_x_piscina = -4.5
centro_y_piscina = 1.25
# A piscina (casca + água) foi deslocada 1m para reduzir a sombra do
# quiosque sobre a água - mas o piso de concreto ao redor (chao_piscina)
# permanece no centro original, por isso usa uma variável separada.
centro_y_piscina_agua = centro_y_piscina - 1.0

# --- Pilares: tora de eucalipto 12/14 sobre pedestal de concreto ---------
# O pedestal (sapata cilíndrica de concreto) vai de 0,30 m abaixo do piso
# até 0,50 m acima dele, para tirar a madeira do contato com o piso
# molhado. A tora de eucalipto (2,00 m) começa no topo do pedestal; o topo
# dos pilares fica nivelado em +2,50 m do piso (= altura_pilar, referência
# usada pelo telhado e pelos módulos de extras.py).
raio_pilar = 0.065          # eucalipto roliço 12/14 (média ~13 cm)
altura_tora = 2.0           # trecho de madeira, acima do pedestal
altura_pedestal = 0.5       # concreto acima do piso
prof_pedestal = 0.3         # concreto abaixo do piso
raio_pedestal = 0.15        # sapata cilíndrica Ø30 cm
altura_pilar = altura_pedestal + altura_tora   # 2.5 - topo dos pilares
nivel_quiosque = 0.0
nivel_piscina = 0.0

# --- Telhado meia-água ----------------------------------------------------
# Caimento de 15% escoando para OESTE (x baixo = 0), em direção à piscina.
# Lado alto = leste (x = 4). O lado baixo (x=0) fica na cota do topo dos
# pilares; o lado alto sobe sobre montantes curtos. As telhas (1,00 x 4,50 m)
# vencem no máximo 2,50 m de vão livre -> terças a cada ~2 m (x = 0 / 2 / 4).
caimento_telhado = 0.15
x_beiral_baixo = 0.0
# A ala (x = -2.25) fica do lado baixo: os pilares 7 e 8 são encurtados
# para o topo acompanhar o plano inclinado do telhado.
rebaixo_ala = caimento_telhado * 2.25
altura_piso = 0.1

# Dimensões da Piscina Esmeralda (54m³) - Alinhada ao comprimento do piso (Eixo Y)
comprimento_piscina = 10.50  # Eixo Y
largura_piscina = 3.70      # Eixo X
prof_rasa = 1.30
prof_funda = 1.70

# ---------------------------------------------------------------------------
# 2. CRIAÇÃO DE MATERIAIS
# ---------------------------------------------------------------------------
def criar_material(nome, cor, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=nome)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = cor
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

mat_madeira = criar_material("Material_Eucalipto", (0.35, 0.22, 0.12, 1.0), roughness=0.8)
mat_piso_quiosque = criar_material("Material_Piso_Quiosque", (0.6, 0.6, 0.6, 1.0), roughness=0.4)
mat_concreto_geral = criar_material("Material_Concreto_Area", (0.7, 0.68, 0.62, 1.0), roughness=0.5)
mat_agua = criar_material("Material_Agua", (0.1, 0.5, 0.8, 0.8), roughness=0.1)
mat_azulejo_piscina = criar_material("Material_Azulejo_Piscina", (0.15, 0.6, 0.75, 1.0), roughness=0.2)
mat_zinco = criar_material("Material_Zinco", (0.75, 0.78, 0.8, 1.0), roughness=0.25, metallic=0.95)

# ---------------------------------------------------------------------------
# 3. PILARES DE EUCALIPTO (10 Unidades)
# ---------------------------------------------------------------------------
pilares_coords = [
    (0.0, 0.0, 0.0),    (4.0, 0.0, 0.0),    (4.0, 4.0, 0.0),    (4.0, 8.0, 0.0),
    (4.0, 12.0, 0.0),   (0.0, 12.0, 0.0),   (-2.25, 12.0, 0.0), (-2.25, 9.5, 0.0),
    (0.0, 9.5, 0.0),    (0.0, 4.0, 0.0)
]

for i, coord in enumerate(pilares_coords):
    # Pedestal de concreto (sapata cilíndrica): de -prof_pedestal até
    # +altura_pedestal em relação ao piso.
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio_pedestal,
        depth=altura_pedestal + prof_pedestal,
        location=(coord[0], coord[1],
                  nivel_quiosque + (altura_pedestal - prof_pedestal) / 2.0)
    )
    pedestal = bpy.context.active_object
    pedestal.name = f"Pedestal_Concreto_{i+1}"
    pedestal.data.materials.append(mat_concreto_geral)

    # Tora de eucalipto, apoiada no topo do pedestal. Pilares 7 e 8 (ala)
    # são encurtados para o topo seguir o caimento do telhado para oeste.
    tora_i = altura_tora - (rebaixo_ala if (i + 1) in (7, 8) else 0.0)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=raio_pilar,
        depth=tora_i,
        location=(coord[0], coord[1],
                  nivel_quiosque + altura_pedestal + (tora_i / 2.0))
    )
    pilar = bpy.context.active_object
    pilar.name = f"Pilar_Eucalipto_{i+1}"
    pilar.data.materials.append(mat_madeira)

# ---------------------------------------------------------------------------
# 4. PISO DO QUIOSQUE EM "L"
# ---------------------------------------------------------------------------
z_piso_inferior = nivel_quiosque
z_piso_superior = nivel_quiosque + altura_piso

mesh_piso = bpy.data.meshes.new("Mesh_Piso_Quiosque_L")
obj_piso = bpy.data.objects.new("Piso_Quiosque_L", mesh_piso)
collection.objects.link(obj_piso)

bpy.context.view_layer.objects.active = obj_piso
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh_piso)

# Piso Horizontal (4m x 12m)
h1, h2 = bm.verts.new((0.0, 0.0, z_piso_inferior)), bm.verts.new((4.0, 0.0, z_piso_inferior))
h3, h4 = bm.verts.new((4.0, 12.0, z_piso_inferior)), bm.verts.new((0.0, 12.0, z_piso_inferior))
h5, h6 = bm.verts.new((0.0, 0.0, z_piso_superior)), bm.verts.new((4.0, 0.0, z_piso_superior))
h7, h8 = bm.verts.new((4.0, 12.0, z_piso_superior)), bm.verts.new((0.0, 12.0, z_piso_superior))

bm.faces.new([h1, h2, h6, h5]); bm.faces.new([h2, h3, h7, h6])
bm.faces.new([h3, h4, h8, h7]); bm.faces.new([h4, h1, h5, h8])
bm.faces.new([h5, h6, h7, h8])

# Piso Vertical (-2.25m x 2.5m)
v1, v2 = bm.verts.new((-2.25, 9.5, z_piso_inferior)), bm.verts.new((0.25, 9.5, z_piso_inferior))
v3, v4 = bm.verts.new((0.75, 12.0, z_piso_inferior)), bm.verts.new((-2.25, 12.0, z_piso_inferior))
v5, v6 = bm.verts.new((-2.25, 9.5, z_piso_superior)), bm.verts.new((0.25, 9.5, z_piso_superior))
v7, v8 = bm.verts.new((0.75, 12.0, z_piso_superior)), bm.verts.new((-2.25, 12.0, z_piso_superior))

bm.faces.new([v1, v2, v6, v5]); bm.faces.new([v2, v3, v7, v6])
bm.faces.new([v3, v4, v8, v7]); bm.faces.new([v4, v1, v5, v8])
bm.faces.new([v5, v6, v7, v8])

bmesh.update_edit_mesh(mesh_piso)
bpy.ops.object.mode_set(mode='OBJECT')
obj_piso.data.materials.append(mat_piso_quiosque)

# ---------------------------------------------------------------------------
# 5. TELHADO DE ZINCO (MEIA-ÁGUA, CAIMENTO DE 15%)
# ---------------------------------------------------------------------------
# A água escoa para OESTE (x=0), em direção à piscina. Lado alto = leste
# (x=4). Plano único inclinado; roof_frame.py depois o translada para
# descansar sobre as terças. (params caimento_telhado / x_beiral_baixo
# definidos no bloco 1.)
z_telhado_baixo = nivel_quiosque + altura_pilar + 0.05

def z_telhado(x):
    return z_telhado_baixo + caimento_telhado * (x - x_beiral_baixo)

altura_telhado = z_telhado_baixo   # compat.: cota do beiral baixo
mesh_telhado = bpy.data.meshes.new("Mesh_Telhado_L")
obj_telhado = bpy.data.objects.new("Telhado_Zinco_L", mesh_telhado)
collection.objects.link(obj_telhado)

bpy.context.view_layer.objects.active = obj_telhado
bpy.ops.object.mode_set(mode='EDIT')
bm_t = bmesh.from_edit_mesh(mesh_telhado)

# Contorno em "L" com beiral de 0,40 m nas bordas externas. No canto
# reentrante do L (face oeste do corpo principal x face sul da ala) o
# beiral das duas faces se encontra em (0-0.4, 9.5-0.4). z varia só com
# x, então o plano permanece plano mesmo inclinado.
beiral_telhado = 0.4
_contorno_telhado = [
    (4.0 + beiral_telhado,   12.0 + beiral_telhado),   # nordeste
    (4.0 + beiral_telhado,   0.0 - beiral_telhado),    # sudeste
    (0.0 - beiral_telhado,   0.0 - beiral_telhado),    # sudoeste (corpo principal)
    (0.0 - beiral_telhado,   9.5 - beiral_telhado),    # canto reentrante do L
    (-2.25 - beiral_telhado, 9.5 - beiral_telhado),    # sudoeste da ala
    (-2.25 - beiral_telhado, 12.0 + beiral_telhado),   # noroeste da ala
]
verts_telhado = [bm_t.verts.new((x, y, z_telhado(x))) for (x, y) in _contorno_telhado]

bm_t.faces.new(verts_telhado)
bmesh.update_edit_mesh(mesh_telhado)
bpy.ops.object.mode_set(mode='OBJECT')
obj_telhado.data.materials.append(mat_zinco)

# ---------------------------------------------------------------------------
# 6. CONCRETO ENTORNO E PISCINA ESMERALDA (ORIENTADA EM Y)
# ---------------------------------------------------------------------------
# Piso em Concreto da Área Externa (9m x 16.5m)
bpy.ops.mesh.primitive_plane_add(size=1.0, location=(centro_x_piscina, centro_y_piscina, nivel_piscina))
chao_piscina = bpy.context.active_object
chao_piscina.name = "Piso_Area_Piscina"
chao_piscina.scale = (9.0, 16.5, 1.0)
chao_piscina.data.materials.append(mat_concreto_geral)

# Escavação e Casca da Piscina
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(centro_x_piscina, centro_y_piscina_agua, nivel_piscina - (prof_funda / 2))
)
casca_piscina = bpy.context.active_object
casca_piscina.name = "Piscina_Esmeralda_Casca"
casca_piscina.scale = (largura_piscina, comprimento_piscina, prof_funda)

bpy.ops.object.mode_set(mode='EDIT')
bm_piscina = bmesh.from_edit_mesh(casca_piscina.data)
for v in bm_piscina.verts:
    if v.co.z < 0:
        fator_y = (v.co.y + 0.5)
        prof_atual = prof_rasa + (prof_funda - prof_rasa) * fator_y
        v.co.z = -prof_atual / prof_funda

bmesh.update_edit_mesh(casca_piscina.data)
bpy.ops.object.mode_set(mode='OBJECT')
casca_piscina.data.materials.append(mat_azulejo_piscina)

# Recorte Booleano no Piso Externo
mod_bool = chao_piscina.modifiers.new(name="Corte_Piscina", type='BOOLEAN')
mod_bool.operation = 'DIFFERENCE'
mod_bool.object = casca_piscina

# Lâmina d'Água
bpy.ops.mesh.primitive_plane_add(
    size=1.0,
    location=(centro_x_piscina, centro_y_piscina_agua, nivel_piscina - 0.10)
)
agua_piscina = bpy.context.active_object
agua_piscina.name = "Piscina_Esmeralda_Agua"
agua_piscina.scale = (largura_piscina - 0.10, comprimento_piscina - 0.10, 1.0)
agua_piscina.data.materials.append(mat_agua)

print("✅ SCRIPT EXECUTADO COM SUCESSO! CENA 3D COMPLETA E ALINHADA.")