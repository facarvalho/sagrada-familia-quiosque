# Modelo 3D do quiosque para o Google Earth

Gerado por `nucleo/export_google_earth.py` a partir do mesmo modelo 3D do
projeto (`arquitetonico/projeto.py` + `extras.py` + `fixes.py`) — posição
real (projeto atual, sem girar/mover), na coordenada GPS real e com a
orientação (heading) calculada a partir do mesmo norte verdadeiro
(133,7°) usado no resto do projeto (`nucleo/sun_geo.py`).

## Como importar

**Arquivo único (mais fácil):** `quiosque_piscina.kmz`

- **Google Earth Web** (earth.google.com): abra "Projetos" → "Novo projeto"
  → "Importar arquivo KML" → selecione `quiosque_piscina.kmz`.
- **Google Earth Pro** (desktop): Arquivo → Abrir → selecione o `.kmz`,
  ou simplesmente arraste o arquivo pra dentro da janela do programa.

Os outros dois arquivos (`quiosque_piscina.kml` + `quiosque_piscina.dae`)
são os mesmos dados sem compactar — o `.kmz` é só os dois zipados junto,
não precisa deles separados a menos que quera editar o KML manualmente.

## Se a orientação parecer errada

O `heading` (133,7°) já reflete o norte verdadeiro medido nesta sessão
(validado por 3 métodos independentes — ver memória
`piscina-georreferenciamento`), mas a convenção de eixo "norte" de um
Model KML depende de como o leitor interpreta o COLLADA exportado. Se ao
abrir o modelo ficar girado (90°, 180° etc. errado), abra o
`quiosque_piscina.kml` num editor de texto e ajuste só o valor dentro de
`<heading>...</heading>` (linha ~20) — não precisa reexportar o `.dae`.

## Escopo do modelo

Inclui todo o projeto atual: piso em L, pilares, telhado, paredes (muro
tendinoso), banheiros, área gourmet (bancada de alvenaria, fogão,
geladeira), sala de estar, mesas de bar, TV — e a piscina (já existente,
incluída só como referência visual de posição, não faz parte do escopo
da obra).

## Regerar

```bash
BL=~/opt/blender-4.2.23-linux-x64/blender   # precisa dessa build (a do
                                              # sistema não tem o exportador COLLADA)
$BL --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python nucleo/export_google_earth.py
```
