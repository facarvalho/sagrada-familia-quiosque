"""
Construtor da cena "esqueleto" - fase de obra sem acabamentos.

Monta só: piso do quiosque + piscina/deck (projeto.py), calçadas +
drenagem (calcadas.py) e a estrutura do telhado - vigas transversais,
terças, telhado reposicionado (roof_frame.py).

NÃO monta (ao contrário de V1/extras.py): paredes (wall.py/bathroom.py),
bancada/pia comunitária (counter.py), sala de estar (lounge.py), mesas de
bar (bartables.py), eletrodomésticos (appliances.py), TV (tv.py).

Os render_*.py desta pasta (V1/comeco/) chamam build() no lugar de
V1.extras.build_all.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import V1.calcadas as calcadas
import V1.roof_frame as roof_frame
import V1.fixes as fixes


def build():
    projeto_path = os.path.join(REPO_ROOT, "V1", "projeto.py")
    with open(projeto_path, "r", encoding="utf-8") as f:
        ns = {"__name__": "__main__"}
        exec(compile(f.read(), projeto_path, "exec"), ns)

    info = {}
    info["calcadas"] = calcadas.build(ns)
    info["roof_frame"] = roof_frame.build(ns)

    # fix_pool_boolean (piscina/deck) e fix_piso_quiosque_seam (piso em L)
    # só tocam objetos criados em projeto.py - seguem válidas aqui.
    fixes.apply_all()

    return ns, info
