# Quiosque da Piscina Esmeralda

Projeto executivo do quiosque ao lado da piscina — Sítio Sagrada Família, Alfenas-MG.
Modelo 3D em Blender/Python, plantas técnicas, passeio em vídeo e
levantamento de materiais por fase de obra.

**Site publicado:** https://facarvalho.github.io/sagrada-familia-quiosque/
(GitHub Pages — Settings → Pages → Deploy from branch → `main` → `/(root)`)

## Estrutura do repositório

Organizado por disciplina (o `V1/` que existia até 13/09/2026 não existe
mais — era o projeto real, e foi redistribuído nas pastas abaixo; só as
visões de posicionamento continuam com nome de pasta próprio, por serem
provas de conceito, não o projeto real):

- **`arquitetonico/`** — piso, pilares (geometria), telhado (forma),
  paredes (muro tendinoso), banheiros, bancada/cozinha, sala de estar,
  mesas de bar, TV, calçadas, entorno real (`contexto_externo.py`), e os
  scripts de planta/render ligados a isso (`render_floorplan.py`,
  `render_piso_medidas.py`, `render_banheiro_medidas.py`, etc).
  `projeto.py` é o arquivo-base: gera a cena (piscina, quiosque em L,
  pilares, telhado) e define os parâmetros usados por todos os outros
  módulos.
- **`estrutural/`** — vigas transversais e terças (`roof_frame.py`) e a
  planta cotada do telhado.
- **`hidrossanitario/`** — planta da rede de água fria/esgoto/represa.
- **`orcamento/`** — levantamento de materiais histórico (28/08/2026,
  superado — ver `site/orcamento.html` para o atual).
- **`documentacao/`** — gerador do Caderno de Obra em PDF
  (`gerar_pdf.py`, `pdf_lib.py`), o PDF em si (22 páginas) e o histórico
  de alterações do projeto.
- **`nucleo/`** — infraestrutura compartilhada entre disciplinas e
  visões: georreferenciamento real + posição solar (`sun_geo.py`), a
  lógica comum das visões (`variant_sol_common.py`) e os KML de
  referência GPS.
- **`renders/`** — todas as imagens/vídeo gerados (`.png`/`.mp4`/`.json`)
  + `renders/scripts/`, os scripts de render que não são específicos de
  uma disciplina (vistas 3D gerais, passeio em vídeo, estudo de sol da
  posição real).
- **`visao-casa-da-mae/`, `visao-milho-abobora/`, `visao-cerca-fernando/`**
  — três posições reais alternativas do quiosque ao redor da laje da
  piscina (não são o projeto real — são provas de conceito de
  posicionamento), todas com a mesma metodologia
  (`nucleo/variant_sol_common.py`): ponto GPS real do pilar P9 (dado pelo
  usuário) → giro −90° em Z a partir do projeto original → prova de sol
  real (algoritmo NOAA, coordenadas reais de Alfenas-MG) às
  15h/16h/17h/18h/19h em verão e inverno → entorno real (cerca/café/terreno
  do projeto de fibra óptica `sagrada-familia-infra`, via
  `arquitetonico/contexto_externo.py`). Nomeadas pelo que fica atrás do
  quiosque em cada uma. Eram `V3/`, `V4/` e `V6/` — a antiga `V5/` usava
  posição/cálculo placeholder e foi removida do repositório.
- **`visoes/fase-obra-comeco/`** — versão "esqueleto" da obra (só piso,
  calçada, pilares, vigas, terças e telhado, sem acabamento).
- **`regerar_tudo.sh`** — regenera todos os renders/plantas/PDF (projeto
  real + as 3 visões). Retomável (`--resume`). Ver bootstrap de import nos
  comentários do script.

## Como rodar os scripts Blender

```bash
blender --background --factory-startup \
  --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
  --python renders/scripts/render_projeto.py
```

Os desenhos técnicos 2D (`render_piso_medidas.py`, `render_banheiro_medidas.py`,
`render_telhado_medidas.py`, `render_esgoto_medidas.py`) rodam direto com
`python3`, sem Blender.
