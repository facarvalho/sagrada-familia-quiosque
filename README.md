# Quiosque da Piscina Esmeralda

Projeto executivo do quiosque ao lado da piscina — Sítio Harmonia, Alfenas-MG.
Modelo 3D em Blender/Python, plantas técnicas, passeio em vídeo e
levantamento de materiais por fase de obra.

**Site publicado:** https://facarvalho.github.io/sagrada-familia-quiosque/
(GitHub Pages — Settings → Pages → Deploy from branch → `main` → `/(root)`)

## Estrutura do repositório

- **`site/`** — o site publicado (`index.html`, `galeria.html`, `video.html`,
  `caderno.html`, `orcamento.html`). Referencia as imagens/vídeo direto em
  `V1/renders/`, `V3/renders/`, `V4/renders/`, `V5/renders/` — nada é
  duplicado.
- **`V1/`** — projeto atual (fonte da verdade): scripts Blender/Python
  (`projeto.py`, `roof_frame.py`, `calcadas.py`, `wall.py`, `bathroom.py`,
  `counter.py`, ...), renders em `V1/renders/`, o `Caderno_de_Obra.pdf` e o
  `orcamento_quiosque.md` (histórico — ver `site/orcamento.html` para o
  levantamento atual). `V1/comeco/` é a versão "esqueleto" (fase de obra,
  sem acabamento).
- **`V3/`, `V4/`** — estudos de insolação com o quiosque em outras posições
  ao redor da laje da piscina (quina nordeste e noroeste). Cada um tem seu
  próprio `README.md`.
- **`V5/`** — variante adicional (V4 girada 90°, abraçando a borda norte da
  laje).
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
