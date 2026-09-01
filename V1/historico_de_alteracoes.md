# Histórico de Alterações

Registro das mudanças pedidas pelo cliente, na ordem em que foram feitas.

1. **Render realista inicial** a partir do `projeto.py` original. Corrigido
   (só no wrapper de render, não no arquivo original) um bug de booleano
   coplanar que deixava a piscina toda preta.
2. **Planta anotada** com nomes e medidas dos elementos principais.
3. **Iluminação de fim de tarde**: sol reposicionado para o lado direito da
   imagem, calculado a partir do vetor "direita" da câmera; antes o sol não
   iluminava o interior do quiosque.
4. **Banheiros** criados na ala entre os pilares 6-7-8-9 (2 lavabos + 2
   duchas quentes).
5. **Banheiros otimizados**: removido o corredor interno, cabines maiores,
   portas viradas para o lado externo (duchas → lado da piscina, lavabos →
   lado do corredor do quiosque).
6. **Planta técnica completa do quiosque**: nome e coordenadas dos 10
   pilares, cotas de distância entre pilares consecutivos, ficha técnica do
   piso.
7. **Vídeo de caminhada** (walkthrough) por toda a propriedade.
8. **Mais fotos** de outros ângulos + interior dos banheiros.
9. **Bancada com pia e churrasqueira** no canto do quiosque perto do
   Pilar 5 (posição inicial).
10. **Piscina deslocada 1m** (`centro_y_piscina` 1.25 → 0.25) para reduzir
    sombra do quiosque sobre a água.
11. **Reorganização completa do quiosque**:
    - Bancada movida para o lado oposto (pilares 1-2-3), estilo rústico,
      + mesa para 8 pessoas com bancos.
    - Parede de fechamento em placa cimentícia ao longo dos pilares
      1-2-3-4-5 (lados sul e leste).
    - Sala de estar entre pilares 4-5-6.
    - Mesas de bar entre pilares 3-4.
12. **Pilares e estrutura do telhado**:
    - Espessura dos pilares reduzida em 50% (`raio_pilar` 0.15 → 0.075).
    - Pilares 6 e 9 realinhados para x=0 (mesmo alinhamento dos pilares 1
      e 10).
    - Estrutura de vigas de eucalipto em 2 camadas (`roof_frame.py`) para
      respeitar o vão livre máximo de 3m das telhas; telhado reposicionado
      sobre a nova estrutura.
    - Geladeira e fogão entre pilares 1-2.
    - TV de parede entre pilares 4-5.

13. **Revisão dos pilares e do telhado** (28/08/2026):
    - Pilares agora são **tora de eucalipto 12/14** (`raio_pilar` 0.075 → 0.065),
      **2,00 m** de madeira sobre um **pedestal de concreto** cilíndrico
      (Ø 0.30 m, de -0.30 m a +0.50 m do piso) para tirar a madeira do
      contato com o piso — objeto `Pedestal_Concreto_{n}` por pilar.
    - `altura_pilar` passou a significar o **topo dos pilares = 2,50 m**
      (era 2,80 m); novas variáveis `altura_tora`, `altura_pedestal`,
      `prof_pedestal`, `raio_pedestal`.
    - Telhado agora é **meia-água com caimento de 15%** escoando para
      **leste (x=4), lado oposto à piscina**; lado alto = x=0 e a ala.
      O telhado (`Telhado_Zinco_L`) virou um plano inclinado com beiral
      de 0,40 m.
    - `roof_frame.py` reescrito: montantes sobre as fileiras altas +
      vigas transversais/frechais 12/14 + caibros 8/10 a cada 0,50 m.
    - Parede de fechamento (`wall.py`) baixada de 2,50 m → 2,00 m para não
      encostar no beiral baixo.
    - `render_labels.py`, `render_floorplan.py`, `annotate_floorplan.py` e
      `gerar_pdf.py` atualizados com as novas medidas.
    - Levantamento de materiais para orçamento em `orcamento_quiosque.md`.

14. **Caimento invertido e estrutura enxuta** (28/08/2026):
    - Telhado agora escoa para **oeste (x=0), em direção à piscina**; lado
      alto passou a ser o leste (x=4). Montantes agora só na fileira leste.
    - Estrutura reduzida: removidos os 25 caibros. Passou a ser
      4 montantes + 6 vigas transversais 12/14 + 4 terças 12/14
      (x = 0 / 2 / 4 e a da ala). A telha (informada pelo cliente:
      **1,00 × 4,50 m, vão livre ≤ 2,50 m**) assenta direto nas terças,
      que ficam a ~2,0 m entre si.
    - Pilares 7 e 8 (ala) encurtados (~2,16 m de topo) para acompanhar o
      plano do telhado, que é mais baixo desse lado.
    - `orcamento_quiosque.md` e docs atualizados.

## Pendências / problemas conhecidos

- **Pequeno artefato preto** no encontro em L do piso do quiosque (perto dos
  pilares 6/9): o piso principal e a ala são dois blocos sólidos
  independentes que se sobrepõem sem compartilhar vértices — não é um
  problema de solda (já tentado via `remove_doubles`, sem efeito), e sim uma
  face interna soterrada entre os dois sólidos, exposta por uma fresta
  triangular no ângulo de visão. Corrigir de verdade exigiria cortar essa
  face manualmente via bmesh (mais invasivo) — deixado como pendência dado
  o tamanho (poucos cm², numa área com pouca luz).
