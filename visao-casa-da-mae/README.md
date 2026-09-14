# Visão: Casa da Mãe

Nome dado pelo usuário: nesta posição o fundo do quiosque fica voltado
para a casa da mãe. Reescrita em 13/09/2026 para usar dados reais (antes
usava posição sintética + cálculo solar simplificado com coordenadas de
São Paulo) — mesma metodologia da visão "cerca do Fernando".

## De onde vieram orientação e posição

O usuário deu 3 pontos GPS reais nesta posição (P9, P1) e o contorno real
do "piso piscina" (4 vértices, usado como recalibração local — ver
`arquitetonico/contexto_externo.py`). Eles servem pra coisas DIFERENTES:

- **Orientação**: comparando o vetor real P1→P9 com o vetor do projeto
  original (P1→P9 = −90°), a rotação implícita ficou em ~181° — ou seja,
  o quiosque fica praticamente **espelhado (180°)**, não girado 90° como
  na visão "cerca do Fernando" (que usa −90°).
- **Posição**: o P9 convertido caiu a só 0,73 m do canto SO do deck real
  da piscina (`Piso_Area_Piscina`, projeto.py: 9x16,5 m, cantos
  (−9,−7)/(−9,9.5)/(0,−7)/(0,9.5)) — não é coincidência: a piscina é real
  e fixa (já construída), é o quiosque que muda de canto/orientação em
  cada visão. `TARGET` usa o canto exato **(−9, −7)**, não o ponto GPS
  aproximado, pra não deixar gap/overlap visível com o deck no render.

## O que muda

`visao-casa-da-mae/render_sol.py` chama `nucleo/variant_sol_common.py`
(compartilhado com a visão "cerca do Fernando"):
1. Constrói o projeto original (`projeto.py` + `extras.py` + `fixes.py`),
   sem alterar nenhum arquivo original.
2. Gira o quiosque **180° em Z em torno do pilar P9 original** (0,4 ; 9,5)
   e translada até o canto SO do deck real, (−9, −7).
3. Adiciona o entorno real — cerca, café, terreno e a **casa da mãe**
   (pegada real de 8 vértices desenhada pelo usuário no Google Earth,
   `CASA_MAE_POLIGONO` em `arquitetonico/contexto_externo.py`) — **sem**
   girar/mover esses objetos junto (já estão nas coordenadas reais certas).
4. Câmera do lado OPOSTO da casa (~345°), olhando de volta pro quiosque
   com a casa aparecendo ao fundo, atrás dele.

## Estudo solar

10 imagens: verão (solstício 21/12) e inverno (solstício 21/06), às
**15h, 16h, 17h, 18h e 19h** (horário de Brasília), sol na posição real do
céu (algoritmo NOAA, `nucleo/sun_geo.py`, coordenadas reais de Alfenas-MG).
Saídas em `visao-casa-da-mae/renders/sol_{estacao}_{h}h.png`, com legenda
(`_anotado.png`) via `visao-casa-da-mae/annotate_sun_study.py`.

## Como gerar

```bash
BL=~/opt/blender-4.2.23-linux-x64/blender
$BL --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python visao-casa-da-mae/render_sol.py
python3 visao-casa-da-mae/annotate_sun_study.py
```

## Ressalva

Os pontos GPS (P1, P9, piso da piscina) foram desenhados/clicados no
Google Earth pelo usuário — têm a imprecisão normal desse tipo de
levantamento (a orientação bateu bem, ~1°; os pontos individuais têm
erro de ~1-2 m). Suficiente para uma prova de incidência de sol e estudo
de posicionamento; para obra definitiva, medir no local.
