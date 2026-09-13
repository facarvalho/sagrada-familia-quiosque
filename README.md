# Quiosque da Piscina Esmeralda

Projeto executivo do quiosque ao lado da piscina — Sítio Sagrada Família, Alfenas-MG.
Modelo 3D em Blender/Python, plantas técnicas, passeio em vídeo e
levantamento de materiais por fase de obra.

**Site publicado:** https://facarvalho.github.io/sagrada-familia-quiosque/
(GitHub Pages — Settings → Pages → Deploy from branch → `main` → `/(root)`)

## Estrutura do repositório

- **`site/`** — o site publicado (`index.html`, `galeria.html`, `video.html`,
  `caderno*.html`, `orcamento.html`). Referencia as imagens/vídeo direto em
  `V1/renders/`, `visao-*/renders/` — nada é duplicado.
- **`V1/`** — projeto atual/real (fonte da verdade): scripts Blender/Python
  (`projeto.py`, `roof_frame.py`, `calcadas.py`, `wall.py`, `bathroom.py`,
  `counter.py`, ...), renders em `V1/renders/`, o `Caderno_de_Obra.pdf` e o
  `orcamento_quiosque.md` (histórico — ver `site/orcamento.html` para o
  levantamento atual). `V1/comeco/` é a versão "esqueleto" (fase de obra,
  sem acabamento). `V1/contexto_externo.py` modela a cerca/café/terreno
  reais da propriedade (dados do projeto `sagrada-familia-infra`).
  **Reorganização em andamento**: o conteúdo do `V1/` está sendo
  redistribuído em pastas por disciplina (`arquitetonico/`, `estrutural/`,
  `hidrossanitario/`, `orcamento/`, `renders/`) — ver
  `piscina-reorg-aec-plano` na memória do projeto.
- **`visao-casa-da-mae/`, `visao-milho-abobora/`, `visao-cerca-fernando/`**
  — três posições reais alternativas do quiosque ao redor da laje da
  piscina (não são o projeto real — são provas de conceito de
  posicionamento), todas com a mesma metodologia (`V1/variant_sol_common.py`):
  ponto GPS real do pilar P9 (dado pelo usuário) → giro −90° em Z a partir
  do projeto original → prova de sol real (algoritmo NOAA, coordenadas
  reais de Alfenas-MG) às 15h/16h/17h/18h/19h em verão e inverno → entorno
  real (cerca/café/terreno do projeto de fibra óptica
  `sagrada-familia-infra`, via `V1/contexto_externo.py`). Nomeadas pelo que
  fica atrás do quiosque em cada uma. Eram `V3/`, `V4/` e `V6/` — a antiga
  `V5/` usava posição/cálculo placeholder e foi removida do repositório.
- **`regerar_tudo.sh`** — regenera todos os renders/plantas/PDF do V1 e das
  visões. Retomável (`--resume`). Ver bootstrap de import nos comentários
  do script.

## Como rodar os scripts Blender

```bash
blender --background --factory-startup \
  --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
  --python V1/render_projeto.py
```

Os desenhos técnicos 2D (`render_piso_medidas.py`, `render_banheiro_medidas.py`,
`render_telhado_medidas.py`, `render_esgoto_medidas.py`) rodam direto com
`python3`, sem Blender.
