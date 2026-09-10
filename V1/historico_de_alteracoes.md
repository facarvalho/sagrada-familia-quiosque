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

15. **Quiosque encurtado 12,0 m → 10,5 m** (05/09/2026):
    - A redução de 1,5 m sai do **lado sul**. **P1 e P2 recuados de y=0
      para y=1,5**.
    - Fileiras leste e oeste **realinhadas** em `y = 1,5 / 5,5 / 9,5 / 12`
      (vãos 4,0 / 4,0 / 2,5 m): P3 e P10 centrados entre P1 e P9 (y=5,5);
      **P4 alinhado com P9** (y=9,5).
    - Medidas: **P9→P1 = 8,0 m**, **P9→P6 = 2,5 m**, total **P1→P6 = 10,5 m**.
    - Móveis acompanharam: bancada/pia + mesa (`counter.py`) e mesas de bar
      (`bartables.py`) deslocadas +1,5 m; geladeira/fogão na parede sul
      (`appliances.py`); sala de estar comprimida para o vão de 2,5 m
      (sofás mais rasos e juntos, `lounge.py`, `tv.py`). Banheiros intactos.
    - Ajustes: `projeto.py` (pilares, piso em L, contorno do telhado),
      `roof_frame.py` (terças), textos de cota em `render_labels.py`,
      `annotate_floorplan.py`, `gerar_pdf.py` (piso principal 4,00 × 10,50 m).

16. **Beirais, recuo oeste, calçadas e nível único** (07/09/2026 – só V1,
    em validação):
    - **Fileira oeste (P1, P10, P9, P6) recuada 0,40 m** para dentro
      (x = 0 → 0,40). O piso e a cobertura continuam com 4,0 m (borda oeste
      em x=0); o recuo cria um **beiral de 0,40 m** de telha além dos pilares
      no lado da piscina + a **calha** (`Calha_Beiral_Oeste`). A viga
      longitudinal oeste que liga **P1–P10–P9–P6** (`Terca_Oeste`) fica
      **sobre os pilares** (x=0,40). Todas as transversais são pilar-a-pilar
      (as do lado oeste = 3,60 m). Banheiros **não** acompanham o recuo
      (X1 fixo em x=0, `bathroom.py`).
    - **Beiral norte (P7–P5) = 0,50 m** (`beiral_norte`); terças a y=12,5.
    - **Calçadas de concreto** (`calcadas.py`, novo módulo em `extras.py`):
      Sul P1–P2 = 0,50 × 4,0 m; Oeste da ala P7–P8 = **1,00 × 3,00 m**
      (y 10→13, alinhada com a borda externa da calçada norte);
      Norte P7–P5 = 1,00 × 6,25 m.
    - **Piso do quiosque e calçadas no nível do deck da piscina** (sem
      degrau): topo da laje em z=0 (`altura_piso` 0,10 → 0,0 como cota de
      referência; nova `esp_piso = 0,10` para a espessura, escavada para
      baixo). `render_floorplan.py`/`annotate_floorplan.py` atualizados.

17. **Beirais especificados, banheiros rústicos e pia comunitária**
    (07/09/2026 – só V1, em validação):
    - **Tamanhos de beiral** (telha além do eixo dos pilares):
      sul e leste = 0,40 m; oeste (piscina) = 0,40 m de telha além dos
      pilares recuados; norte (P6–P5) = 0,50 m; **ala (P7–P8): 0,70 m
      igual nos três lados livres** (oeste, sul, norte). `beiral_ala = 0,7`
      em `projeto.py`; `Terca_Ala_P7P8` + `Terca_Ala_Beiral` e transversais
      da ala estendidas em `roof_frame.py`.
    - **Banheiros crescem 0,40 m para leste** — borda leste alinhada com
      P9–P6 (x = 0,40).
    - **Acabamento rústico:** paredes em reboco grosso, **chão de brita
      solta** (sem revestimento).
    - **Cabines de vaso: só o vaso, sem pia.** Portas das 4 cabines = **0,60 m**.
    - **Pia comunitária** (lava-mãos) rústica e funda fixada na face sul da
      parede **P8–P9**, com 3 bicas, **saboneteira** e **papeleira**.

18. **Estrutura do telhado enxuta + numeração** (07/09/2026 – só V1):
    - Removida a terça de borda do beiral da ala (`Terca_Ala_Beiral`) e as
      extensões das transversais da ala — **só a ponta da telha** avança
      0,70 m como beiral.
    - **Cada terça morre em cima dos pilares**: T1/T2/T3 de y=1,5 (P1–P2)
      a y=12,0 (P7–P5); T4 (ala) de y=9,5 (P8) a y=12,0 (P7). O beiral é
      sempre cantilever da telha.
    - **Terças T1–T4 e vigas transversais V1–V6 numeradas**, com
      comprimentos, na planta anotada (tags sobre as peças + tabela
      "Terças e Vigas"). `roof_frame.build()` devolve o esquadro em
      `result["schedule"]`.

    | Terça | x (m) | Comprimento |
    |---|---|---|
    | T1 (oeste, sobre P1–P10–P9–P6) | 0,40 | 10,50 m |
    | T2 (central) | 2,00 | 10,50 m |
    | T3 (leste, sobre P2–P3–P4–P5) | 4,00 | 10,50 m |
    | T4 (ala, sobre P8–P7) | −2,25 | 2,50 m |

    Vigas transversais: V1–V4 (corpo principal) = 3,60 m; V5–V6 (ala) = 2,65 m.

19. **Ajuste das terças e do beiral norte + calçada da ala** (07/09/2026 – só V1):
    - **T2 centralizada** no eixo entre T1 (x = recuo_oeste = 0,40) e
      T3 (x = 4,00) → **x = 2,20 m**.
    - **T1, T2 e T3 passam a 11,00 m** e **T4 a 3,50 m**; as quatro terças
      terminam na **mesma linha ao norte (y = 12,50)**, formando um beiral
      contínuo de **0,50 m** além dos pilares norte (y = 12,0). Ponta sul
      de T1–T3 em y = 1,50 (linha de P1/P2); T4 segue centrada no vão
      P8–P7 (mid y = 10,75), ponta sul em y = 9,00.
    - **Calçada oeste da ala** (`calcadas.py`) passa a **preencher todo o
      vão entre P8 (y = 9,5) e P7 (y = 12,0)** — antes ia de y = 10,0 a 13,0.
    - Nova cena `render_vista_10m_p5.py`.

    | Terça | x (m) | Comprimento |
    |---|---|---|
    | T1 (oeste, sobre P1–P10–P9–P6) | 0,40 | 11,00 m |
    | T2 (central, eixo T1–T3) | 2,20 | 11,00 m |
    | T3 (leste, sobre P2–P3–P4–P5) | 4,00 | 11,00 m |
    | T4 (ala, centrada em P8–P7) | −2,25 | 3,50 m |

20. **Muro tendinoso, calçada do banheiro e novas vistas** (07/09/2026 – só V1):
    - **Paredes em MURO TENDINOSO** (`wall.py` e `bathroom.py`): sistema
      colombiano de malla + varão tensionados entre os pilares de eucalipto
      e rebocados nas duas faces → parede fina (~5–8 cm), monolítica e
      rústica. Material único `Material_Muro_Tendinoso`.
    - **Fechamento do corpo principal (`wall.py`): até o topo** — painéis
      com topo em rampa acompanhando a face inferior do telhado inclinado
      (`roof_frame.roof_underside_z(ns, x)`), sem vão de ventilação.
    - **Paredes do banheiro (`bathroom.py`): 2,50 m**, mas limitadas a
      ~3 cm abaixo do telhado onde ele desce (lado oeste da ala fica
      ~2,41 m) — sempre com respiro entre a parede e a cobertura. Verga
      fechando o vão acima de cada porta até o topo da parede.
    - **Correção de z-fighting da calçada:** topo das placas subiu 1 cm
      acima do deck e as placas da volta do banheiro deixaram de se
      sobrepor (encostam em x=−2,25 e y=12,0) — sumiram os "quadrados
      pretos" na planta de topo.
    - **Calçada da ala só a OESTE e NORTE:** removida a faixa ao sul da ala
      (`Calcada_Ala_Sul`) — aquele trecho já é o `Piso_Area_Piscina`
      existente (que vai até y=9,5). `Calcada_Ala_Oeste` passa a y 9,5..13,0.
    - **V1 e V2 = 4,00 m:** as duas vigas transversais do sul avançam 0,40 m
      a oeste (até x=0, linha do beiral/calha) para **apoiar a calha**;
      antes tinham 3,60 m. Demais transversais do corpo seguem 3,60 m.
    - Fotos internas dos banheiros: 1 luz de preenchimento por cabine
      (paredes mais altas fechavam a luz antiga de 2,0 m).

21. **Drenagem pluvial** (07/09/2026 – só V1, em `calcadas.py`):
    - No chão da piscina, **alinhada com a calha** (eixo x ≈ 0), uma
      **canaleta com grelha** (`Canaleta_Pluvial` + `Canaleta_Grelha`),
      trecho aparente de y=1,0 a y=9,5.
    - `Tubo_Queda_Calha`: desce a água da calha até a canaleta.
    - `Cano_Drenagem_Pluvial_100`: cano de esgoto **Ø100 mm** enterrado
      (z ≈ −0,30), que **atravessa o banheiro (ala, y 9,5..12,0) como
      subterrâneo** e sai ao norte em `Caixa_Inspecao_Pluvial` (y ≈ 13,1).
    - `calcadas.build()` devolve `result["drenagem"]` (eixo, trechos, Ø);
      `render_floorplan.py` projeta e `annotate_floorplan.py` desenha a
      linha tracejada + rótulos na planta. `render_piso_medidas.py` também
      mostra a canaleta.

22. **Projeto do telhado + ajuste de câmera** (07/09/2026 – só V1):
    - `render_telhado_medidas.py` (novo, PIL 2D) -> `telhado_quiosque_medidas.png`:
      projeto do telhado com telha **sanduíche trapezoidal PIR 30 mm**
      (tipo Kingspan Isotelha), telhas em tamanho real. 12 telhas (8 de
      4,45 m no campo sul + 4 de 7,43 m no campo norte, útil 1,00 m).
      Comprar 65,32 m² / cobertura 62,50 m² / ~606 kg. Vãos de terça OK no
      corpo; na ala T4->T1 = 2,65 m (> 2,60 m do fabricante) -> sugere T5
      em x=-0,90.
    - `render_counter_detail.py`: `vista_area_pia.png` re-mirada para
      olhar de P10 (0,40;5,50) para P2 (4,00;1,50).
    - **Calçada do banheiro sem dente:** faixa contínua de 1,00 m rodeando
      os 3 lados livres da ala (oeste/sul/norte), placas sobrepostas nos
      cantos (`Calcada_Ala_Oeste`, `Calcada_Ala_Sul`, `Calcada_Norte`
      estendida a x=−3,25).
    - **`render_piso_medidas.py`** (novo, PIL 2D): `piso_quiosque_medidas.png`
      — só o piso em L com cotas (4,00×10,50 + ala 2,25×2,50; 47,63 m²).
    - **`render_vista_10m_p5.py`**: a 1ª vista virou `vista_15m_T2_V1.png`
      (sobre o eixo de T2, x=2,20, a 15 m ao norte de V1, olhando para o sul
      ao longo do quiosque). Mantida `vista_10m_entre_P6_P2.png`.

23. **Revisão geral + ajustes estruturais** (07/09/2026 – só V1):
    - **Piso do quiosque = um único sólido em "L"** (n-gon de 6 vértices em
      `projeto.py`), no lugar dos dois blocos sobrepostos — elimina o
      artefato preto no canto reentrante (perto de P6/P9).
    - **Pilares P1, P10, P9, P6** (fileira oeste, recuada 0,40 m) alongados
      `+caimento·recuo = +0,06 m` (topo 2,50 → **2,56 m**): sem isso o topo
      ficava 6 cm abaixo da face inferior das transversais/terça T1 nessa
      posição (T1 "flutuava"). P2–P5 (leste) seguem em 2,50 m.
    - **Telhado morre na terça T3 (x = 4,0): sem beiral no lado leste**
      (lado alto do caimento). Contorno leste de `_contorno_telhado` passa
      de x=4,40 para x=4,00. Beirais mantidos: sul/oeste 0,40 m, norte
      0,50 m, ala 0,70 m. `render_telhado_medidas.py` recalculado:
      8 telhas de 4,04 m (sul) + 4 de 7,03 m (norte) = **60,47 m²** a
      comprar / 57,85 m² de cobertura / ~561 kg.
    - **Piso da ala = CAIXA DE BRITA** (`bathroom.py`): tabuleiro rebaixado
      ~0,14 m, brita ~1 cm abaixo do piso, meio-fio de ~0,09 m contendo a
      brita (inclusive nas soleiras das portas).
    - **`render_banheiro_medidas.py`** (novo, PIL 2D) → `banheiro_planta_medidas.png`:
      planta cotada dos 4 boxes (1,30×1,15), portas 0,60×1,90, parede
      central x=−0,90, pia comunitária 1,80 m, caixa de brita.
    - `vista_area_pia.png` re-mirada de **P9 → P2** (era P10→P2; o pilar de
      P10 tapava o quadro). Câmera 0,90 m adiante de P9.
    - Câmeras dos banheiros (`render_more_angles.py`) reposicionadas para
      dentro do box (o respiro alto estourava o quadro).
    - Planta anotada: rótulo da drenagem movido para fora de T1/T2; anéis
      verdes nos pilares que apoiam cada terça.
    - Rótulos "Telhado de Zinco / 1,00×4,50" → "Telha Sanduíche PIR /
      12 telhas / terças T1–T4" em `render_labels.py`, `annotate.py`,
      `gerar_pdf.py`.

## Pendências / problemas conhecidos

- ~~Artefato preto no encontro em L do piso~~ — RESOLVIDO no item 23 (piso
  virou sólido único).
- Cosmético na planta anotada: rótulos de cota "4.00 m" do lado oeste ficam
  parcialmente atrás da linha azul da drenagem; texto "sob o banheiro
  (subterrâneo)" sobre a cabine.
- Telha da ala: vão T4→T1 = 2,65 m passa do limite de 2,60 m do fabricante
  → T5 sugerida em x=−0,90 (desenhada tracejada, NÃO implementada em 3D).
- Inconsistência: o piso da ala vai a x=0 (2,25 m) mas as paredes do
  banheiro vão a x=0,40 (2,65 m). Cliente decide se o piso da ala cresce.
