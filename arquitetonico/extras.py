"""
Agrega todos os módulos de adições solicitadas pelo usuário (não fazem
parte do projeto.py original): banheiros, área gourmet/bancada, parede de
fechamento, sala de estar, mesas de bar, eletrodomésticos, TV e a estrutura
de vigas do telhado.

Ordem importa: roof_frame precisa rodar por último, pois reposiciona o
telhado (Telhado_Zinco_L) com base na altura da nova estrutura de vigas.
"""
import arquitetonico.bathroom as bathroom
import arquitetonico.counter as counter
import arquitetonico.wall as wall
import arquitetonico.lounge as lounge
import arquitetonico.bartables as bartables
import arquitetonico.appliances as appliances
import arquitetonico.tv as tv
import arquitetonico.calcadas as calcadas
import estrutural.roof_frame as roof_frame


def build_all(ns):
    result = {}
    result["bathroom"] = bathroom.build(ns)
    result["counter"] = counter.build(ns)
    result["wall"] = wall.build(ns)
    result["lounge"] = lounge.build(ns)
    result["bartables"] = bartables.build(ns)
    result["appliances"] = appliances.build(ns)
    result["tv"] = tv.build(ns)
    result["calcadas"] = calcadas.build(ns)
    result["roof_frame"] = roof_frame.build(ns)
    return result
