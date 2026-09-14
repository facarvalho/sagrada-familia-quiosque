"""
Visão "Quiosque com fundo para a casa da mãe"

Substitui a versão antiga (posição sintética na quina nordeste + cálculo
solar simplificado com coordenadas de São Paulo) por posição REAL: o
usuário deu o ponto GPS real de referência do pilar P9 nesta posição
(-21.352973052981856, -45.99008896729865).

RECALIBRAÇÃO (13/09/2026, ver arquitetonico/contexto_externo.py): o
usuário desenhou no Google Earth o contorno real do piso da piscina (4
vértices) — comparado com o retângulo conhecido do deck em projeto.py,
um ajuste de 4 pontos dá rotação 132,94°/escala 0,976 (erro médio 0,6 m),
mais preciso que o ajuste anterior de 2 pontos.

CORREÇÃO IMPORTANTE (rotação): a rotação do QUIOSQUE aqui não é -90°
como na visão "cerca do Fernando" — o usuário deu também P1 desta posição
(-21.35302074053984, -45.99003371422486); comparando P1-P9 real
(ângulo 91,2°) com P1-P9 do projeto original (-90°), a rotação
implícita é ~181° (praticamente um espelhamento), não -90°.
`rotation_deg=180.0` é passado explicitamente pra
`common.build_and_render` por isso (a visão "cerca do Fernando" continua com o -90° padrão,
sem dado real pra questionar). O usuário confirmou que essa orientação
ficou correta.

CORREÇÃO IMPORTANTE (posição): P1/P9 dados pelo usuário são só
REFERÊNCIA DE ORIENTAÇÃO, não a posição final — o quiosque precisa ficar
ALINHADO ao piso da piscina real (Piso_Area_Piscina, projeto.py: deck
9x16,5m, cantos (-9,-7)/(-9,9.5)/(0,-7)/(0,9.5); a piscina é fixa, é o
quiosque que muda de canto/orientação em cada visão). O ponto GPS de P9
convertido (-8,45 ; -7,48) caiu a só 0,73 m do canto SO do deck (-9,-7)
— confirma que essa é a quina pretendida. `TARGET` usa o canto exato,
não o ponto GPS aproximado (evita um gap/desalinhamento visível entre o
quiosque e o deck no render). Ver [[piscina-visoes-fundo-real]].

Inclui o entorno real (cerca/café/terreno, arquitetonico/contexto_externo.py) e a
prova de sol real (NOAA, nucleo/sun_geo.py) às 15h/16h/17h/18h/19h, verão e
inverno.

Câmera customizada (diferente do offset genérico das outras visões): a
casa da mãe tem pegada REAL (polígono de 8 vértices desenhado pelo
usuário, ver CASA_MAE_POLIGONO em arquitetonico/contexto_externo.py),
centroide a ~17,2 m do canto SO do deck, direção ~165° (SE). A câmera
fica do lado OPOSTO da casa (a ~345°) olhando de volta pro quiosque, pra
casa aparecer ao fundo, atrás do quiosque, como pedido.

Uso:
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python visao-casa-da-mae/render_sol.py
"""
import os
import sys

scriptdir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(scriptdir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import nucleo.variant_sol_common as common

TARGET = (-9.0, -7.0)  # canto SO do deck da piscina (Piso_Area_Piscina) — não o ponto GPS aproximado
OUT_DIR = os.path.join(scriptdir, "renders")

# Câmera do lado oposto da casa (ver docstring): casa real a ~165° daqui,
# então a câmera fica a ~345°, olhando de volta pro quiosque com a casa
# aparecendo atrás dele.
import math as _math
_ang = _math.radians(345.3763090526943)
_dist = 32.0
CAM_OFFSET = (_dist * _math.cos(_ang), _dist * _math.sin(_ang), 15.0)

common.build_and_render(TARGET, OUT_DIR, "Quiosque com fundo para a casa da mãe",
                         cam_offset=CAM_OFFSET, rotation_deg=180.0)
