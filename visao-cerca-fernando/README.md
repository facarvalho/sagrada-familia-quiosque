# Visão: Cerca do Fernando

Nome dado pelo usuário: o fundo do quiosque nesta posição fica voltado para
a cerca que divide a propriedade do vizinho Fernando. Esta variante
**substitui uma tentativa anterior** (mesma posição real, que antes só
existia com coordenadas/cálculo solar placeholder, depois removida do
repo) e foi a primeira a usar dado 100% real.

Variante de posicionamento pedida pelo usuário ("fazer o quiosque em outro
canto da piscina"), com **prova de incidência de sol real** (verão e
inverno) — diferente das tentativas antigas (já removidas), que usavam um
azimute/elevação solar simplificado e coordenadas de São Paulo
(placeholder). Esta visão usa o mesmo algoritmo NOAA e as mesmas
coordenadas geográficas reais do terreno (Alfenas-MG) de
`renders/scripts/render_sun_study.py` / `nucleo/sun_geo.py`.

## De onde veio a posição

O usuário marcou 3 pontos de referência num KML novo
(`nucleo/divisa-propriedade-fibra.kml`): `p1`, `P8`, `p9` — mesmos
nomes de pilares do projeto original, num lugar diferente do terreno.

Esses pontos foram convertidos de GPS para o referencial do projeto com a
mesma calibração já validada (âncora em P9, rotação 133,7°, escala derivada
do par P1↔P9 original — ver `nucleo/sun_geo.py` e a memória
`piscina-georreferenciamento`). Um ajuste de Procrustes 2D (rotação +
translação, sem distorcer escala) usando os 3 pontos correspondentes
(P1/P8/P9 do projeto ↔ p1/P8/p9 novos) deu rotação ótima de **−87,5°** com
erro RMS de **~1,8 m** — esperado, já que são cliques aproximados sobre
imagem de satélite (não um levantamento GPS preciso como o par P1/P9
original, que tem ~3 cm de erro conhecido). P8 e P9 (mais próximos entre
si) bateram bem (~1–1,3 m de erro); P1 teve o pior ajuste (~2,5 m).

Em vez de aplicar o ajuste ruidoso ponto a ponto, foi adotada a leitura
geométrica limpa que os 3 pontos indicam: **girar o quiosque −90° em Z e
ancorar o pilar P9 (canto reentrante do "L") exatamente na quina SUDESTE**
da laje da piscina (`Piso_Area_Piscina`, x∈[−9,0], y∈[−7,9.5] → quina SE =
(0,−7)) — o mesmo tipo de ancoragem "canto reentrante = quina da laje" que
já existe no projeto original (P9 casa com a quina NORDESTE). O lado
aberto do quiosque passa a apontar para o **norte** (de volta para a
laje/piscina), em vez de para oeste.

```
novo_ponto = Rot(−90°, Z) aplicado a (ponto − P9_original) + quina_SE
P9_original = (0.4, 9.5, 0)  ;  quina_SE = (0.0, −7.0, 0)
```

Aplicado a todos os objetos do quiosque (pilares, piso, telhado, paredes,
móveis) via `obj.matrix_world = transform @ obj.matrix_world` — a piscina e
o deck de concreto (já existentes) não são tocados.

## Câmera

Ponto de vista pedido pelo usuário: lat/lon reais (`-21.3530973,
-45.9900076`), convertidos com a mesma calibração → projeto (−3,93 ; 7,63),
na borda norte do deck, altura de olho humano (1,6 m), olhando para o
centro do quiosque na nova posição — a piscina fica em primeiro plano, o
quiosque ao fundo.

## Estudo solar

10 imagens: verão (solstício 21/12) e inverno (solstício 21/06), às
**15h, 16h, 17h, 18h e 19h** (horário de Brasília), sol na posição real do
céu (algoritmo NOAA, mesmas lat/lon do terreno). Saídas em
`visao-cerca-fernando/renders/sol_{estacao}_{h}h.png`, com legenda (`_anotado.png`) via
`visao-cerca-fernando/annotate_sun_study.py`.

## Como gerar

```bash
BL=~/opt/blender-4.2.23-linux-x64/blender
$BL --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python visao-cerca-fernando/render_sol.py
python3 visao-cerca-fernando/annotate_sun_study.py
```

## Contexto externo (cerca, café, terreno)

A pedido do usuário, a cena inclui também `arquitetonico/contexto_externo.py`:
- **Cerca**: postes P7–P13 do projeto de fibra óptica
  (https://facarvalho.github.io/sagrada-familia-infra/mapa.html — o
  usuário confirmou que o caminho da fibra segue a divisa da propriedade)
  + 3 fiadas de arame farpado. Só o trecho mais próximo da piscina/quiosque
  (~15–100 m) foi modelado; P1–P6 e P14–P20 ficam fora do alcance de
  qualquer câmera enquadrando o quiosque.
- **Café**: faixa representativa de pés (não é um mapa 1:1 da plantação —
  seriam milhares de pés em ~300 m) no trecho P9→P12, que o usuário
  confirmou ser cafezal ("pomar e piscina do P9-P17 é café").
- **Terreno**: chão de terra cobrindo a área entre o quiosque/piscina e a
  cerca modelada.

Mesma ressalva de calibração do posicionamento do quiosque (abaixo) se
aplica aqui, com erro potencialmente maior — a cerca mais distante
modelada (P13) fica a ~100 m da âncora original (P1/P9, validada em só
8 m), então qualquer erro residual de rotação/escala tende a compor com a
distância. Tratar como contexto visual, não como levantamento de divisa.

## Ressalva

A posição exata (quina SE) é uma leitura geométrica dos 3 pontos marcados,
não um ajuste milimétrico — os pontos em si têm ~1–2,5 m de imprecisão
(cliques em imagem de satélite). Suficiente para uma prova de incidência
de sol; para posicionamento definitivo de obra, os pilares reais devem ser
levantados com GPS/estação total no local, como foi feito para P1/P9 do
projeto original.
