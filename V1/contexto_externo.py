"""
Contexto externo da propriedade: cerca (divisa real, postes do projeto de
fibra óptica), terreno ("terra") e uma faixa de cafezal — para dar contexto
rural aos renders do quiosque/piscina, a pedido do usuário.

--- Origem dos dados ------------------------------------------------------
Postes P1..P20 + pontos nomeados (Rancho, Sede, Mãe, Lazer) vêm de
https://facarvalho.github.io/sagrada-familia-infra/mapa.html (projeto de
infraestrutura de fibra óptica da mesma propriedade). O usuário confirmou:
"onde passa cabo de fibra é divisa da propriedade" — os postes marcam a
cerca. Café: usuário confirmou que a faixa entre os postes P9 e P17 é
cafezal ("pomar e piscina do P9-P17 é café").

Conversão GPS -> projeto: mesma calibração de V1/sun_geo.py (âncora P9,
rotação 133,7°, validada com ~3 cm de erro na âncora e ~4 cm no centro da
piscina). Aqui a calibração é extrapolada por até ~300 m (a cerca mais
distante) — a aproximação plana (equirretangular) e qualquer erro residual
de rotação/escala tendem a compor com a distância; tratar como contexto
visual aproximado, não como levantamento de divisa para fins legais/registro.

--- Escopo modelado --------------------------------------------------------
Cerca: postes P7..P13 (o trecho mais próximo da piscina/quiosque, ~15-100 m
de distância — os postes mais distantes, P1-P6 e P14-P20, ficam fora do
alcance visual de qualquer câmera enquadrando o quiosque e não foram
modelados) + arame farpado (3 fiadas).
Café: faixa representativa (NÃO é um mapa bush-a-bush real — seria
milhares de pés ao longo de ~300 m) de algumas fileiras curtas, só no
trecho P9-P12 (o que realmente pode aparecer num enquadramento próximo da
piscina); indica "aqui começa o cafezal", não a plantação inteira.
Terreno: chão de terra/grama cobrindo a área entre o quiosque/piscina e a
cerca modelada.
"""
import bpy
import bmesh
import math
import random

# --- Postes da cerca (projeto.py XY, metros), convertidos do KML real ----
POSTES = {
    "P7":  (-63.09, 59.35),
    "P8":  (-51.03, 16.17),
    "P9":  (-44.36, -18.47),   # CTO
    "P10": (-11.48, -14.45),
    "P11": (23.57, -9.35),
    "P12": (40.81, 33.53),     # ligação Piscina
    "P13": (58.69, 79.35),
}
CERCA_ORDEM = ["P7", "P8", "P9", "P10", "P11", "P12", "P13"]

# trecho de café confirmado pelo usuário (P9 -> P17); só modelamos a parte
# visível perto da piscina (P9->P12) — ver docstring.
CAFE_ORDEM = ["P9", "P10", "P11", "P12"]


def _mat(name, color, roughness=0.9, metallic=0.0):
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


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def build(ns=None):
    mat_madeira_poste = _mat("Material_Poste_Cerca", (0.30, 0.20, 0.12, 1.0), roughness=0.95)
    mat_arame = _mat("Material_Arame_Farpado", (0.35, 0.34, 0.32, 1.0), roughness=0.5, metallic=0.7)
    mat_terra = _mat("Material_Terra_Roxa", (0.32, 0.16, 0.11, 1.0), roughness=1.0)
    mat_cafe_folha = _mat("Material_Cafe_Folha", (0.09, 0.22, 0.08, 1.0), roughness=0.85)
    mat_cafe_tronco = _mat("Material_Cafe_Tronco", (0.22, 0.15, 0.09, 1.0), roughness=0.9)

    result = {"postes": {}, "cerca": [], "cafe": [], "terreno": None}

    # --- Terreno de terra, cobrindo a área da cerca modelada -------------
    xs = [p[0] for p in POSTES.values()]
    ys = [p[1] for p in POSTES.values()]
    cx, cy = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    size = max(max(xs) - min(xs), max(ys) - min(ys)) + 40.0
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(cx, cy, -0.03))
    terreno = bpy.context.active_object
    terreno.name = "Terreno_Propriedade"
    terreno.scale = (size, size, 1.0)
    terreno.data.materials.append(mat_terra)
    cutter = bpy.data.objects.get("Piscina_Cortador_Boolean")
    if cutter:
        mb = terreno.modifiers.new(name="Corte_Piscina", type="BOOLEAN")
        mb.operation = "DIFFERENCE"
        mb.object = cutter
    result["terreno"] = terreno.name

    # --- Postes da cerca ---------------------------------------------------
    POST_H = 1.3
    POST_R = 0.06
    for nome, (x, y) in POSTES.items():
        bpy.ops.mesh.primitive_cylinder_add(radius=POST_R, depth=POST_H, location=(x, y, POST_H / 2.0))
        obj = bpy.context.active_object
        obj.name = f"Cerca_Poste_{nome}"
        obj.data.materials.append(mat_madeira_poste)
        result["postes"][nome] = obj.name

    # --- Arame farpado (3 fiadas) entre postes consecutivos ---------------
    alturas = [0.45, 0.80, 1.15]
    for i in range(len(CERCA_ORDEM) - 1):
        a = POSTES[CERCA_ORDEM[i]]
        b = POSTES[CERCA_ORDEM[i + 1]]
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for h in alturas:
            mx, my = (a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0
            bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=dist, location=(mx, my, h))
            wire = bpy.context.active_object
            wire.name = f"Cerca_Arame_{CERCA_ORDEM[i]}_{CERCA_ORDEM[i+1]}_{int(h*100)}"
            wire.rotation_euler = (math.radians(90), 0.0, ang - math.radians(90))
            wire.data.materials.append(mat_arame)
            result["cerca"].append(wire.name)

    # --- Faixa de café (representativa, só P9->P12) ------------------------
    random.seed(42)
    ROW_OFFSETS = [4.0, 8.0, 12.0]     # fileiras, deslocadas p/ dentro da propriedade
    BUSH_STEP = 2.2                     # espaçamento entre pés na fileira
    BUSH_R = 0.45
    for i in range(len(CAFE_ORDEM) - 1):
        a = POSTES[CAFE_ORDEM[i]]
        b = POSTES[CAFE_ORDEM[i + 1]]
        seg_len = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        # normal apontando "para dentro" (lado da piscina, x crescente aprox.)
        nrm = (math.sin(ang), -math.cos(ang))
        n_bushes = max(1, int(seg_len / BUSH_STEP))
        for row_off in ROW_OFFSETS:
            for k in range(n_bushes):
                t = (k + 0.5) / n_bushes
                px, py = _lerp(a, b, t)
                px += nrm[0] * row_off + random.uniform(-0.3, 0.3)
                py += nrm[1] * row_off + random.uniform(-0.3, 0.3)
                h = random.uniform(1.1, 1.5)
                bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=h * 0.5, location=(px, py, h * 0.25))
                tronco = bpy.context.active_object
                tronco.name = f"Cafe_Tronco_{i}_{row_off}_{k}"
                tronco.data.materials.append(mat_cafe_tronco)
                bpy.ops.mesh.primitive_ico_sphere_add(radius=BUSH_R, subdivisions=1, location=(px, py, h * 0.5 + BUSH_R * 0.6))
                copa = bpy.context.active_object
                copa.name = f"Cafe_Copa_{i}_{row_off}_{k}"
                copa.scale = (1.0, 1.0, 1.25)
                copa.data.materials.append(mat_cafe_folha)
                result["cafe"].append((tronco.name, copa.name))

    return result


if __name__ == "__main__":
    # permite testar isolado: builda o projeto base + este contexto
    import os
    import sys
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(scriptdir)
    for p in (scriptdir, repo_root):
        if p not in sys.path:
            sys.path.insert(0, p)
    projeto_path = os.path.join(scriptdir, "projeto.py")
    with open(projeto_path, "r", encoding="utf-8") as f:
        _ns = {"__name__": "__main__"}
        exec(compile(f.read(), projeto_path, "exec"), _ns)
    import V1.extras as extras
    extras.build_all(_ns)
    import V1.fixes as fixes
    fixes.apply_all()
    build(_ns)
    print("CONTEXTO_EXTERNO_OK (standalone)")
