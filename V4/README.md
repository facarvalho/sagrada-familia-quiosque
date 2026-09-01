# V4 — Quiosque na quina noroeste da laje ("outra perna do X")

Variante para avaliar a **incidência de sol** com o quiosque na **quina
noroeste** da laje de concreto da piscina — a "outra perna do X" em
relação à V3 (que abraça a quina nordeste).

## O que muda

- O quiosque é **espelhado em torno do eixo vertical (N–S) da laje**
  (`x = centro da laje`). Como no projeto original o canto reentrante do
  "L" já coincidia com a quina NE, ele passa a coincidir **exatamente**
  com a quina NW.
- A perna principal do "L" fica **paralela à da V3**, só que ao longo da
  borda **oeste** da laje; o lado aberto continua voltado para a piscina
  (agora para leste).
- Piscina e piso de concreto permanecem no lugar. Um terreno (gramado) é
  adicionado para receber as sombras.
- Nenhum arquivo do projeto original é alterado.

## Estudo solar

Vista `projeto_render`, uma imagem por hora cheia das **07h às 18h**, com
o Sol na posição real do céu (algoritmo NOAA).

| Parâmetro | Valor |
|---|---|
| Latitude | −23,55° (São Paulo/SP) |
| Longitude | −46,63° |
| Fuso | −3 (Brasília) |
| Data | 2026-08-31 |

Saídas: `V4/renders/projeto_render_7h.png` … `projeto_render_18h.png`.

## Leitura da insolação (V4 × V3)

Com o quiosque a **oeste** da piscina:
- **Manhã (07h–12h):** sol nasce a leste/nordeste, entra pelo lado aberto
  e ilumina o interior; a sombra do quiosque cai para oeste, **fora da
  água** → piscina ensolarada.
- **Tarde (a partir de ~14h):** o sol vai para oeste, passa **atrás** do
  quiosque e a sombra da cobertura/pilares avança **sobre a piscina**,
  cobrindo a parte oeste da lâmina d'água já às 15h–16h e quase toda ela
  às 17h.
- **18h:** sol abaixo do horizonte (penumbra).

É o inverso da V3 (quina NE), em que a piscina fica no sol à tarde e a
sombra só a alcança de manhã cedo.

## Como gerar

```bash
blender --background --factory-startup --python V4/render_v4_sol.py
```
