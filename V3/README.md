# V3 — Quiosque atravessado no pé da piscina + estudo de insolação

Variante do projeto para avaliar a **incidência de sol** com o quiosque
**girado 90° e atravessado na extremidade rasa (sul) da piscina**, com o
lado aberto voltado para a água.

## O que muda

- O quiosque inteiro (pilares, piso em L, telhado meia-água, estrutura de
  vigas e todos os módulos de `extras.py`) é **rotacionado −90° em Z** e
  transladado para:
  - centralizar o trecho de 12 m no eixo da piscina (`x = -4,5`);
  - encostar o lado aberto logo ao sul da extremidade rasa (`y ≈ -5`).
- A **piscina e o piso de concreto** ao redor permanecem no lugar.
- Um **terreno (gramado)** é adicionado sob a área para o quiosque não
  flutuar e para receber as sombras (recebe o mesmo recorte booleano da
  piscina).
- Nenhum arquivo do projeto original é alterado — `render_v3_sol.py`
  executa `projeto.py` + `extras.py` + `fixes.py` e aplica a transformação
  na cena já montada.
- Câmera posicionada do lado da piscina (norte), olhando para o quiosque.

## Estudo solar

Gera **somente** a vista `projeto_render`, uma imagem por hora cheia das
**10h às 19h**, com o Sol na posição real do céu (algoritmo NOAA).

Local/data assumidos (edite as constantes no topo de `render_v3_sol.py` se
o terreno for em outra cidade):

| Parâmetro | Valor |
|---|---|
| Latitude | −23,55° (São Paulo/SP) |
| Longitude | −46,63° |
| Fuso | −3 (Brasília) |
| Data | 2026-08-31 |

Após o pôr do sol (18h/19h nesta data) o Sol fica abaixo do horizonte: a
luz direta é desligada e a cena aparece em penumbra.

Como o Sol no hemisfério sul cruza o céu pelo **norte**, e o quiosque
fica ao **sul** da piscina, a sombra do quiosque cai para longe da água —
a piscina recebe sol praticamente o dia todo nesta configuração.

## Como gerar

```bash
blender --background --factory-startup --python V3/render_v3_sol.py
```

Saídas em `V3/renders/projeto_render_10h.png` … `projeto_render_19h.png`.
