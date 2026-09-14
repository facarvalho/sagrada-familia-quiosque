# Modelo 3D do quiosque para o Google Earth

Duas versões, dependendo de onde você vai abrir:

| Arquivo | Onde funciona | O que tem |
|---|---|---|
| `quiosque_piscina_web.kml` | **Google Earth Web** (navegador) e Google Earth Pro | Massa simplificada: piso, 10 pilares, paredes, telhado inclinado (poligonos KML nativos, sem modelo importado) |
| `quiosque_piscina.kmz` | **Só Google Earth Pro** (desktop) | Modelo completo: todos os móveis, banheiros, área gourmet, TV etc. (modelo 3D COLLADA) |

O Google Earth Web **não suporta** modelo 3D importado (`<Model>`/COLLADA)
— só o Google Earth Pro (app desktop) suporta. Por isso existem as duas
versões.

## Como importar

**`quiosque_piscina_web.kml`** (recomendado pra abrir no navegador):
- Google Earth Web (earth.google.com): "Projetos" → "Novo projeto" →
  "Importar arquivo KML" → selecione o arquivo.
- Google Earth Pro: Arquivo → Abrir, ou arraste o arquivo pra janela.

**`quiosque_piscina.kmz`** (só funciona no Google Earth Pro, desktop —
grátis em earth.google.com/download-earth-pro): mesmo processo de
importação, mas dá erro "Unsupported element: Model" se tentar no navegador.

## Posição e orientação

Ambas as versões usam a mesma calibração: coordenada GPS real (a partir
do contorno real do piso da piscina desenhado no Google Earth) e
orientação pro norte verdadeiro (heading/rotação 133,7°, `nucleo/sun_geo.py`).

Na versão `.kmz` (modelo COLLADA), se a orientação vier girada errada ao
abrir no Google Earth Pro, abra o `quiosque_piscina.kml` (dentro do kmz,
ou o arquivo solto) num editor de texto e ajuste só o valor dentro de
`<heading>...</heading>` — não precisa reexportar o `.dae`.

## Escopo de cada versão

**`_web.kml`** (poligonos nativos): piso em L, 10 pilares (extrudados),
7 segmentos de parede (extrudados), telhado inclinado (um plano só,
seguindo o caimento real de 15%), deck e piscina (referência visual).
Pilares aparecem como postes quadrados (a extrusão KML não faz cilindro),
não é uma réplica exata — é a massa/volumetria do projeto.

**`.kmz`** (modelo COLLADA): tudo que o `_web.kml` tem, mais todos os
móveis, banheiros, área gourmet completa (bancada de alvenaria, fogão,
geladeira), sala de estar, mesas de bar, TV — o modelo 3D completo do
projeto, com a geometria exata (pilares cilíndricos de verdade, etc).

## Regerar

```bash
# versão completa (precisa do Blender 4.2 LTS - o do sistema não tem
# o exportador COLLADA):
~/opt/blender-4.2.23-linux-x64/blender --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python nucleo/export_google_earth.py

# versão web (poligonos nativos, funciona com o Blender do sistema):
blender --background --factory-startup \
    --python-expr "__import__('sys').path.insert(0,'/home/fac/piscina')" \
    --python nucleo/export_google_earth_web.py
```
