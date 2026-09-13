# Quiosque da Piscina Esmeralda

Projeto executivo do quiosque ao lado da piscina — Sítio Harmonia, Alfenas-MG.
Modelo 3D em Blender/Python, plantas técnicas, passeio em vídeo e
levantamento de materiais por fase de obra.

**Site publicado:** https://facarvalho.github.io/sagrada-familia-quiosque/
(GitHub Pages — Settings → Pages → Deploy from branch → `main` → `/(root)`)

## Estrutura do repositório

- **`site/`** — o site publicado (`index.html`, `galeria.html`, `video.html`,
  `caderno*.html`, `orcamento.html`). Referencia as imagens/vídeo direto em
  `V1/renders/`, `V3/renders/`, `V4/renders/`, `V6/renders/` — nada é
  duplicado.
- **`V1/`** — projeto atual (fonte da verdade): scripts Blender/Python
  (`projeto.py`, `roof_frame.py`, `calcadas.py`, `wall.py`, `bathroom.py`,
  `counter.py`, ...), renders em `V1/renders/`, o `Caderno_de_Obra.pdf` e o
  `orcamento_quiosque.md` (histórico — ver `site/orcamento.html` para o
  levantamento atual). `V1/comeco/` é a versão "esqueleto" (fase de obra,
  sem acabamento). `V1/contexto_externo.py` modela a cerca/café/terreno
  reais da propriedade (dados do projeto `sagrada-familia-infra`).
- **`V3/`** — "Quiosque com fundo para a casa da mãe": estudo de
  insolação com o quiosque na quina nordeste da laje, cálculo solar
  simplificado, coordenadas de São Paulo (placeholder).
- **`V4/`** — "Quiosque com fundo para a área de plantio de milho/abóbora":
  variante espelhada (quina noroeste), mesmo cálculo simplificado de V3.
- **`V6/`** — "Quiosque com fundo para a cerca do Fernando": posição vinda
  de pontos GPS reais marcados pelo usuário, com prova de sol real
  (algoritmo NOAA, coordenadas reais de Alfenas-MG), câmera num ponto de
  vista real da propriedade, e cerca/café/terreno reais ao redor. Substitui
  a antiga `V5/` (mesma posição, com dados reais em vez de placeholder) —
  a V5 foi removida do repositório.
- **Não existe `V2`** — a numeração pulou de V1 direto para V3 na sessão em
  que os estudos de posicionamento foram feitos.
- **`regerar_tudo.sh`** — regenera todos os renders/plantas/PDF do V1 (e as
  variantes). Retomável (`--resume`). Ver bootstrap de import nos
  comentários do script.

## Como rodar os scripts Blender

```bash
blender --background --factory-startup \
  --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
  --python V1/render_projeto.py
```

Os desenhos técnicos 2D (`render_piso_medidas.py`, `render_banheiro_medidas.py`,
`render_telhado_medidas.py`, `render_esgoto_medidas.py`) rodam direto com
`python3`, sem Blender.
