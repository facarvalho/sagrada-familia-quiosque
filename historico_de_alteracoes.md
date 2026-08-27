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

## Pendências / problemas conhecidos

- **Pequeno artefato preto** no encontro em L do piso do quiosque (perto dos
  pilares 6/9): o piso principal e a ala são dois blocos sólidos
  independentes que se sobrepõem sem compartilhar vértices — não é um
  problema de solda (já tentado via `remove_doubles`, sem efeito), e sim uma
  face interna soterrada entre os dois sólidos, exposta por uma fresta
  triangular no ângulo de visão. Corrigir de verdade exigiria cortar essa
  face manualmente via bmesh (mais invasivo) — deixado como pendência dado
  o tamanho (poucos cm², numa área com pouca luz).
