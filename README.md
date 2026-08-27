# Projeto Piscina & Quiosque

Modelo 3D (Blender/Python) de uma área de piscina com quiosque, gerado a
partir de `projeto.py` e ampliado com módulos adicionais conforme pedido do
cliente. Todo o trabalho foi feito via scripts headless do Blender (sem
interface gráfica).

## Requisitos

- Blender 4.0+ (`sudo apt install blender`)
- Python 3 com Pillow (`pip install pillow`) — só para os scripts de
  anotação (`annotate*.py`)

## Arquivo original

- **`projeto.py`** — script original do cliente que gera a cena base
  (piscina, quiosque em L, pilares, telhado). Contém os parâmetros de
  posição/dimensão usados por todos os outros módulos (`pilares_coords`,
  `altura_pilar`, `raio_pilar`, `centro_x_piscina`, etc). Foi ajustado
  diretamente (não via wrapper) sempre que o pedido era uma mudança de
  parâmetro do projeto em si (posição da piscina, raio/alinhamento dos
  pilares) — ver `historico_de_alteracoes.md`.

## Módulos de ampliação (`extras.py` agrega todos)

| Módulo | Conteúdo |
|---|---|
| `bathroom.py` | Banheiros na ala entre os pilares 6-7-8-9: 2 duchas + 2 lavabos, sem corredor interno, portas para o lado externo |
| `counter.py` | Área gourmet rústica entre pilares 1-2-3: bancada com pia e churrasqueira de bancada, mesa para 8 pessoas com bancos |
| `appliances.py` | Geladeira e fogão, parede sul entre pilares 1-2 |
| `wall.py` | Fechamento em placa cimentícia ao longo dos pilares 1-2-3-4-5 (lados sul/leste) |
| `lounge.py` | Sala de estar entre pilares 4-5-6 (2 sofás + mesa de centro + tapete) |
| `tv.py` | TV de parede entre pilares 4-5, voltada para a sala de estar |
| `bartables.py` | Mesas de bar altas com banquetas, entre pilares 3-4 |
| `roof_frame.py` | Estrutura de vigas de eucalipto (2 camadas) para vencer o vão livre máx. de 3m das telhas; reposiciona o telhado sobre a nova estrutura |

Cada módulo expõe `build(ns)`, onde `ns` é o namespace resultante de
executar `projeto.py` (dá acesso a `pilares_coords`, `altura_piso` etc. sem
precisar duplicar valores).

## Scripts de render

Todos executam via `blender --background --factory-startup --python <script>`.

- **`render_projeto.py`** — render principal (foto realista, iluminação de
  fim de tarde). Também aplica uma correção não-destrutiva de um bug do
  `projeto.py` original (booleano coplanar da piscina — ver comentário no
  próprio arquivo).
- **`render_labels.py`** + **`annotate.py`** — gera `projeto_render_anotado.png`
  com nomes e medidas dos elementos principais.
- **`render_floorplan.py`** + **`annotate_floorplan.py`** — planta técnica
  de topo do quiosque, com nome/coordenadas dos 10 pilares e cotas de
  distância entre eles (`planta_quiosque_anotada.png`).
- **`render_more_angles.py`** — fotos extras (entrada, aérea, corredor,
  interior dos 2 tipos de cabine do banheiro).
- **`render_walkthrough.py`** — animação de câmera percorrendo toda a
  propriedade, exportada como vídeo MP4 (`renders/passeio_quiosque.mp4`).

## Saídas (`renders/`)

Imagens e vídeo gerados — ver `renders/` para a lista atual. Os arquivos
`*_base.png` são o render sem anotações (usado como camada de fundo pelos
scripts `annotate*.py`); `*.json` guardam as coordenadas de projeção usadas
nas anotações.

## Como regerar tudo do zero

```bash
blender --background --factory-startup --python render_projeto.py
blender --background --factory-startup --python render_labels.py && python3 annotate.py
blender --background --factory-startup --python render_floorplan.py && python3 annotate_floorplan.py
blender --background --factory-startup --python render_more_angles.py
blender --background --factory-startup --python render_walkthrough.py
```
