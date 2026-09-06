#!/bin/bash
# Regenera todos os renders/documentos apos a mudanca do quiosque (12 m -> 10,5 m).
# Retomavel: pula etapas cujo arquivo de saida ja existe e e mais novo que projeto.py.
set -u
cd /home/fac/piscina
R=V1/renders
LOG=regerar_tudo.log
BL="blender --background --factory-startup --python-expr __import__('sys').path.insert(0,'/home/fac/piscina') --python"
PROJ=V1/projeto.py

step() {  # step <saida> <comando...>
  local out="$1"; shift
  if [ -f "$out" ] && [ "$out" -nt "$PROJ" ]; then
    echo "== SKIP (ja feito): $out" | tee -a "$LOG"; return 0
  fi
  echo "== RUN: $* -> $out" | tee -a "$LOG"
  "$@" >>"$LOG" 2>&1
  if [ -f "$out" ] && [ "$out" -nt "$PROJ" ]; then
    echo "== OK: $out" | tee -a "$LOG"
  else
    echo "== FALHOU: $out" | tee -a "$LOG"
  fi
}

echo "===== INICIO $(date) =====" | tee -a "$LOG"

step $R/projeto_render.png            $BL V1/render_projeto.py
step $R/projeto_render_base.png       $BL V1/render_labels.py
step $R/projeto_render_anotado.png    python3 V1/annotate.py
step $R/planta_quiosque_base.png      $BL V1/render_floorplan.py
step $R/planta_quiosque_anotada.png   python3 V1/annotate_floorplan.py
step $R/vista_entrada.png             $BL V1/render_more_angles.py
step $R/vista_area_pia.png            $BL V1/render_counter_detail.py
step $R/vista_corredor_cozinha.png    $BL V1/render_corredor_cozinha.py
step $R/banheiro_planta.png           $BL V1/render_bathroom_plan.py
step $R/vista_360_fisheye.png         $BL V1/render_360_fisheye.py
step V1/Caderno_de_Obra.pdf           python3 -m V1.gerar_pdf
step $R/passeio_quiosque.mp4          $BL V1/render_walkthrough.py

step V3/renders/projeto_render_10h.png $BL V3/render_v3_sol.py
step V4/renders/projeto_render_10h.png $BL V4/render_v4_sol.py
step V5/renders/projeto_render_10h.png $BL V5/render_v5_sol.py

echo "===== FIM $(date) =====" | tee -a "$LOG"
touch regerar_tudo.DONE
