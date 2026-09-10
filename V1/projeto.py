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
# Piso do quiosque NO MESMO NIVEL do deck da piscina (sem degrau): o topo
# da laje fica em z = nivel_piscina (0). `altura_piso` = cota do topo do
# piso, usada como referencia pelos modulos de extras.py (moveis, paredes)
# -> agora 0. A espessura da laje e `esp_piso`, escavada para baixo.
esp_piso = 0.10
altura_piso = 0.0

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
# Quiosque encurtado de 12,0 m -> 10,5 m: a reducao (1,5 m) sai do lado
# sul. P1 e P2 recuados para y=1,5. Fileiras leste e oeste alinhadas em
# y = 1,5 / 5,5 / 9,5 / 12 (vaos 4,0 / 4,0 / 2,5 m):
#   P10 e P3 centrados entre P1 e P9 -> y=5,5
#   P4 alinhado com P9 -> y=9,5
# Medidas: P9->P1 = 8,0 m, P9->P6 = 2,5 m, total P1->P6 = 10,5 m.
#
# Fileira OESTE (P1, P10, P9, P6) recuada 0,40 m para dentro (x = 0 -> 0,40):
# o piso e a cobertura continuam com 4,0 m (borda oeste em x=0); o recuo
# cria um beiral de 0,40 m de telha alem dos pilares no lado da piscina,
# onde corre a calha (ver calcadas.py). A terca T1 (viga longitudinal oeste
# que liga P1-P10-P9-P6) fica sobre os pilares, em x=0,40.
recuo_oeste = 0.4
pilares_coords = [
    (recuo_oeste, 1.5, 0.0),  (4.0, 1.5, 0.0),        (4.0, 5.5, 0.0),   (4.0, 9.5, 0.0),
    (4.0, 12.0, 0.0),         (recuo_oeste, 12.0, 0.0), (-2.25, 12.0, 0.0), (-2.25, 9.5, 0.0),
    (recuo_oeste, 9.5, 0.0),  (recuo_oeste, 5.5, 0.0)
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

    # Tora de eucalipto, apoiada no topo do pedestal.
    #  - Pilares 7 e 8 (ala): encurtados p/ o topo seguir o caimento p/ oeste.
    #  - Pilares 1, 10, 9 e 6 (fileira oeste recuada 0,40 m): ALONGADOS
    #    (+caimento*recuo_oeste = +0,06 m) para o topo alcançar a face
    #    inferior das transversais/terça T1 nessa posição (senão T1 fica
    #    "flutuando" acima desses pilares).
    tora_i = altura_tora - (rebaixo_ala if (i + 1) in (7, 8) else 0.0)
    if (i + 1) in (1, 6, 9, 10):
        tora_i += caimento_telhado * recuo_oeste
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
z_piso_superior = nivel_quiosque          # topo da laje = nivel do deck da piscina
z_piso_inferior = nivel_quiosque - esp_piso

mesh_piso = bpy.data.meshes.new("Mesh_Piso_Quiosque_L")
obj_piso = bpy.data.objects.new("Piso_Quiosque_L", mesh_piso)
collection.objects.link(obj_piso)

bpy.context.view_layer.objects.active = obj_piso
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh_piso)

# Piso em "L" num unico solido estanque (sem dois blocos sobrepostos, que
# antes deixavam uma face interna exposta no canto reentrante perto de P6/P9).
# Contorno do L, no sentido anti-horario visto de cima:
#   corpo principal x[0..4] y[1,5..12] + ala x[-2,25..0] y[9,5..12].
_piso_outline = [
    (0.0,   1.5),    # a - sudoeste do corpo
    (4.0,   1.5),    # b - sudeste
    (4.0,   12.0),   # c - nordeste
    (-2.25, 12.0),   # d - noroeste da ala
    (-2.25, 9.5),    # e - sudoeste da ala
    (0.0,   9.5),    # f - canto reentrante do L
]
_pb = [bm.verts.new((x, y, z_piso_inferior)) for (x, y) in _piso_outline]
_pt = [bm.verts.new((x, y, z_piso_superior)) for (x, y) in _piso_outline]
bm.faces.new(_pt)                       # face superior (n-gon)
bm.faces.new(list(reversed(_pb)))       # face inferior
_n = len(_piso_outline)
for _i in range(_n):
    _j = (_i + 1) % _n
    bm.faces.new([_pb[_i], _pb[_j], _pt[_j], _pt[_i]])

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

# Contorno em "L". No lado LESTE o telhado MORRE NA TERÇA T3 (x=4,0) - sem
# beiral alem de T3 (lado alto do caimento). Beiral de 0,40 m so no SUL. No
# lado OESTE (piscina) a telha vai ate x=0 (borda do piso) - como os pilares
# oeste recuaram para x=0,40, isso ja da 0,40 m de beiral alem dos pilares,
# onde corre a calha. z varia só com x, o plano permanece plano mesmo inclinado.
# Tamanhos de beiral (telha alem do eixo dos pilares / borda do piso):
#   leste (corpo principal) ......... 0,00 m  (telhado termina em T3, x=4,0)
#   sul (corpo principal) ........... 0,40 m
#   oeste (lado da piscina) ......... 0,40 m de telha alem dos pilares
#                                     (pilares recuados 0,40 -> telha ate x=0)
#   norte (P6-P5) ................... 0,50 m
#   ala (P7-P8): oeste, sul e norte . 0,70 m, igual nos tres lados livres
beiral_telhado = 0.4
beiral_norte = 0.5
beiral_ala = 0.7
x_telhado_leste = 4.0      # borda leste da telha = eixo da terça T3 (sem beiral)
x_beiral_oeste = 0.0        # borda oeste da telha do corpo principal = borda do piso
_contorno_telhado = [
    (x_telhado_leste,           12.0 + beiral_norte),   # nordeste (em T3)
    (x_telhado_leste,           1.5 - beiral_telhado),  # sudeste (em T3)
    (x_beiral_oeste,             1.5 - beiral_telhado),  # sudoeste (corpo principal)
    (x_beiral_oeste,             9.5 - beiral_ala),       # canto reentrante do L
    (-2.25 - beiral_ala,         9.5 - beiral_ala),      # sudoeste da ala (beiral 0,70)
    (-2.25 - beiral_ala,         12.0 + beiral_ala),     # noroeste da ala (beiral 0,70)
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