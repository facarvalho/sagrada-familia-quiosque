"""
V3 - "Quiosque com fundo para a casa da mãe"

Substitui a versão antiga (posição sintética na quina nordeste + cálculo
solar simplificado com coordenadas de São Paulo) por posição REAL: o
usuário deu o ponto GPS real de referência do pilar P9 nesta posição
(-21.352973052981856, -45.99008896729865), convertido para o referencial
do projeto com a mesma calibração de nucleo/sun_geo.py (âncora P1/P9, rotação
133,7°) -> (-8,0318 ; -7,9191).

Mesma lógica de V6 ("cerca do Fernando") e V4 ("milho/abóbora"): gira o
quiosque -90° em Z em torno do pilar P9 original e ancora no ponto real.
Inclui o entorno real (cerca/café/terreno, arquitetonico/contexto_externo.py) e a
prova de sol real (NOAA, nucleo/sun_geo.py) às 15h/16h/17h/18h/19h, verão e
inverno.

Câmera customizada (diferente do offset genérico das outras visões): a
casa da mãe tem posição real conhecida (3 pontos do projeto de fibra
óptica — roteador "MÃE" + câmeras "Mãe Cozinha"/"Mãe Varanda",
convertidos pra XY do projeto, ver arquitetonico/contexto_externo.py) a
~28 m daqui, direção ~184° (quase -X). A câmera fica do lado OPOSTO da
casa (a ~3,5°, "atrás" do quiosque em relação à casa) olhando de volta
pro quiosque, pra casa aparecer ao fundo, atrás do quiosque, como pedido.

Uso:
  BL=~/opt/blender-4.2.23-linux-x64/blender
  $BL --background --factory-startup \
      --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
      --python visao-casa-da-mae/render_v3_sol.py
"""
import os
import sys

scriptdir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(scriptdir)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import nucleo.variant_sol_common as common

TARGET = (-8.031770738245125, -7.919110538381107)
OUT_DIR = os.path.join(scriptdir, "renders")

# Câmera do lado oposto da casa (ver docstring): casa real a ~184° daqui,
# então a câmera fica a ~3,5°, olhando de volta pro quiosque com a casa
# aparecendo atrás dele.
import math as _math
_ang = _math.radians(3.5)
_dist = 32.0
CAM_OFFSET = (_dist * _math.cos(_ang), _dist * _math.sin(_ang), 15.0)

common.build_and_render(TARGET, OUT_DIR, "V3 - Quiosque com fundo para a casa da mãe",
                         cam_offset=CAM_OFFSET)
