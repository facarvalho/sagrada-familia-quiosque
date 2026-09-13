# Visão: Casa da Mãe

Nome dado pelo usuário: nesta posição o fundo do quiosque fica voltado
para a casa da mãe. Reescrita em 13/09/2026 para usar dados reais (antes
usava posição sintética + cálculo solar simplificado com coordenadas de
São Paulo) — mesma metodologia da V6 ("cerca do Fernando").

## De onde veio a posição

O usuário deu o ponto GPS real do pilar P9 nesta posição:
`-21.352973052981856, -45.99008896729865`. Convertido para o referencial
do projeto com a mesma calibração de `V1/sun_geo.py` (âncora P1/P9,
rotação 133,7°) → **(−8,03 ; −7,92)**.

## O que muda

`visao-casa-da-mae/render_v3_sol.py` agora só chama `V1/variant_sol_common.py`
(compartilhado com V4 e V6):
1. Constrói o projeto original (`projeto.py` + `extras.py` + `fixes.py`),
   sem alterar nenhum arquivo original.
2. Gira o quiosque **−90° em Z em torno do pilar P9 original** (0,4 ; 9,5)
   e translada até o ponto real acima.
3. Adiciona o entorno real — cerca, café e terreno
   (`V1/contexto_externo.py`, dados do projeto de fibra óptica
   `sagrada-familia-infra`) — **sem** girar/mover esses objetos junto (eles
   já estão nas coordenadas reais certas).
4. Câmera enquadrando quiosque + piscina (lente 20 mm).

## Estudo solar

10 imagens: verão (solstício 21/12) e inverno (solstício 21/06), às
**15h, 16h, 17h, 18h e 19h** (horário de Brasília), sol na posição real do
céu (algoritmo NOAA, `V1/sun_geo.py`, coordenadas reais de Alfenas-MG).
Saídas em `visao-casa-da-mae/renders/sol_{estacao}_{h}h.png`, com legenda
(`_anotado.png`) via `visao-casa-da-mae/annotate_sun_study.py`.

## Como gerar

```bash
BL=~/opt/blender-4.2.23-linux-x64/blender
$BL --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python visao-casa-da-mae/render_v3_sol.py
python3 visao-casa-da-mae/annotate_sun_study.py
```

## Ressalva

Só um ponto (P9) foi dado nesta posição — a rotação de −90° foi assumida
por analogia com a V6 (mesma faixa sul da propriedade), não derivada de
múltiplos pontos como na V6. Suficiente para uma prova de incidência de
sol; para posicionamento definitivo de obra, medir mais pontos no local.
