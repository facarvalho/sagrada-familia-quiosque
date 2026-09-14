"""
V4 - "Quiosque com fundo para a área de plantio de milho/abóbora"

Substitui a versão antiga (espelhamento sintético + cálculo solar
simplificado com coordenadas de São Paulo) por posição REAL: o usuário deu
o ponto GPS real de referência do pilar P9 nesta posição
(-21.353027909607615, -45.990141938058045), convertido para o
referencial do projeto com a mesma calibração de nucleo/sun_geo.py (âncora
P1/P9, rotação 133,7°) -> (0,1251 ; -7,6966).

Mesma lógica de V6 ("cerca do Fernando"): gira o quiosque -90° em Z em
torno do pilar P9 original e ancora no ponto real. Inclui o entorno real
(cerca/café/terreno, arquitetonico/contexto_externo.py) e a prova de sol real (NOAA,
nucleo/sun_geo.py) às 15h/16h/17h/18h/19h, verão e inverno.

PENDÊNCIA: ao contrário de V3 (casa da mãe, câmera reorientada pra mostrar
a casa real ao fundo) e V6 (câmera real dada pelo usuário), esta posição
NÃO tem, nos dados do projeto de fibra óptica
(sagrada-familia-infra/mapa.html), nenhum ponto nomeado de referência
para "milho/abóbora" — os pontos nomeados lá são CTO, Motor, Rancho,
Porteira, Pomar, Sede, Mãe e Lazer, nenhum deles descrito como a
plantação de milho/abóbora. Esta posição fica a só ~13-24 m dos postes
P9-P11 da cerca (por isso café/cerca aparecem tão perto no fundo — é
geograficamente real, não um bug de renderização). Câmera ainda genérica
(cam_offset padrão) até o usuário indicar a direção/distância real da
plantação a partir do P9 desta posição.

Uso:
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python visao-milho-abobora/render_v4_sol.py
"""
import os
import sys

scriptdir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(scriptdir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import nucleo.variant_sol_common as common

TARGET = (0.12513613847001953, -7.696593669216613)
OUT_DIR = os.path.join(scriptdir, "renders")

common.build_and_render(TARGET, OUT_DIR, "V4 - Quiosque com fundo para milho/abóbora")
