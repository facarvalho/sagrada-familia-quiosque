"""
V4 - "Quiosque com fundo para a área de plantio de milho/abóbora"

Substitui a versão antiga (espelhamento sintético + cálculo solar
simplificado com coordenadas de São Paulo) por posição REAL: o usuário deu
o ponto GPS real de referência do pilar P9 nesta posição
(-21.353027909607615, -45.990141938058045), convertido para o
referencial do projeto com a mesma calibração de V1/sun_geo.py (âncora
P1/P9, rotação 133,7°) -> (0,4525 ; -7,6966).

Mesma lógica de V6 ("cerca do Fernando"): gira o quiosque -90° em Z em
torno do pilar P9 original e ancora no ponto real. Inclui o entorno real
(cerca/café/terreno, V1/contexto_externo.py) e a prova de sol real (NOAA,
V1/sun_geo.py) às 15h/16h/17h/18h/19h, verão e inverno.

Uso:
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python V4/render_v4_sol.py
"""
import os
import sys

scriptdir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(scriptdir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import V1.variant_sol_common as common

TARGET = (0.12513613847001953, -7.696593669216613)
OUT_DIR = os.path.join(scriptdir, "renders")

common.build_and_render(TARGET, OUT_DIR, "V4 - Quiosque com fundo para milho/abóbora")
