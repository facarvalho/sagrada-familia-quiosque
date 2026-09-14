#!/bin/bash
# Regenera TODOS os renders/documentos do projeto (projeto real, organizado
# por disciplina, + as 3 visões de posicionamento: casa-da-mae,
# milho-abobora, cerca-fernando).
# Retomavel: pula etapas cujo arquivo de saida ja existe e e mais novo que
# o marcador .regerar_tudo.START (criado no inicio de cada execucao completa).
#
# Uso:
#   ./regerar_tudo.sh          -> rebuild completo (recria o marcador)
#   ./regerar_tudo.sh --resume -> retoma, sem recriar o marcador
set -u
cd /home/fac/piscina
R=renders
LOG=regerar_tudo.log
MARK=.regerar_tudo.START
BL="blender --background --factory-startup --python-expr __import__('sys').path.insert(0,'/home/fac/piscina') --python"

if [ "${1:-}" != "--resume" ] || [ ! -f "$MARK" ]; then
  touch "$MARK"
  : > "$LOG"
  rm -f regerar_tudo.DONE
fi

step() {  # step <saida> <comando...>
  local out="$1"; shift
  if [ -f "$out" ] && [ "$out" -nt "$MARK" ]; then
    echo "== SKIP (ja feito): $out" | tee -a "$LOG"; return 0
  fi
  echo "== RUN: $* -> $out" | tee -a "$LOG"
  "$@" >>"$LOG" 2>&1
  if [ -f "$out" ] && [ "$out" -nt "$MARK" ]; then
    echo "== OK: $out" | tee -a "$LOG"
  else
    echo "== FALHOU: $out" | tee -a "$LOG"
  fi
}

echo "===== INICIO $(date) =====" | tee -a "$LOG"

# --- Desenhos 2D (PIL puro, rapidos) ---------------------------------------
step $R/piso_quiosque_medidas.png       python3 arquitetonico/render_piso_medidas.py
step $R/telhado_quiosque_medidas.png    python3 estrutural/render_telhado_medidas.py
step $R/banheiro_planta_medidas.png     python3 arquitetonico/render_banheiro_medidas.py
step $R/esgoto_quiosque_medidas.png     python3 hidrossanitario/render_esgoto_medidas.py

# --- Planta tecnica -------------------------------------------------------
step $R/planta_quiosque_base.png      $BL arquitetonico/render_floorplan.py
step $R/planta_quiosque_anotada.png   python3 arquitetonico/annotate_floorplan.py

# --- Render principal + rotulos -----------------------------------------
step $R/projeto_render.png            $BL renders/scripts/render_projeto.py
step $R/projeto_render_base.png       $BL arquitetonico/render_labels.py
step $R/projeto_render_anotado.png    python3 arquitetonico/annotate.py

# --- Vistas 3D -----------------------------------------------------------
step $R/vista_entrada.png             $BL renders/scripts/render_more_angles.py
step $R/vista_area_pia.png            $BL renders/scripts/render_counter_detail.py
step $R/vista_15m_T2_V1.png           $BL renders/scripts/render_vista_10m_p5.py
step $R/vista_corredor_cozinha.png    $BL renders/scripts/render_corredor_cozinha.py
step $R/banheiro_planta.png           $BL arquitetonico/render_bathroom_plan.py
step $R/vista_360_fisheye.png         $BL renders/scripts/render_360_fisheye.py

# --- Documento + video -------------------------------------------------
step documentacao/Caderno_de_Obra.pdf python3 -m documentacao.gerar_pdf
step $R/passeio_quiosque.mp4          $BL renders/scripts/render_walkthrough.py

# --- Estudo de sol da posicao atual (projeto real) ----------------------
step $R/sol_verao_15h.png             $BL renders/scripts/render_sun_study.py
step $R/sol_verao_15h_anotado.png     python3 renders/scripts/annotate_sun_study.py

# --- Outras visoes (posicao real + estudo de insolacao completo) -------
step visao-casa-da-mae/renders/sol_verao_15h.png     $BL visao-casa-da-mae/render_v3_sol.py
step visao-casa-da-mae/renders/sol_verao_15h_anotado.png   python3 visao-casa-da-mae/annotate_sun_study.py
step visao-milho-abobora/renders/sol_verao_15h.png   $BL visao-milho-abobora/render_v4_sol.py
step visao-milho-abobora/renders/sol_verao_15h_anotado.png python3 visao-milho-abobora/annotate_sun_study.py
step visao-cerca-fernando/renders/sol_verao_15h.png  $BL visao-cerca-fernando/render_v6_sol.py
step visao-cerca-fernando/renders/sol_verao_15h_anotado.png python3 visao-cerca-fernando/annotate_sun_study.py

echo "===== FIM $(date) =====" | tee -a "$LOG"
touch regerar_tudo.DONE
