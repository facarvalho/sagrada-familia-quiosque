(function(){
  var BASE = "../";
  var GROUPS = [
    {
      id: "plantas", label: "Plantas técnicas",
      items: [
        ["V1/renders/planta_quiosque_anotada.png", "Planta geral — pilares, terças e vigas, cotada"],
        ["V1/renders/piso_quiosque_medidas.png", "Piso do quiosque + calçada — medidas"],
        ["V1/renders/telhado_quiosque_medidas.png", "Projeto do telhado — telha sanduíche PIR, terças"],
        ["V1/renders/banheiro_planta_medidas.png", "Banheiros da ala — planta e medidas (caixa de brita)"],
        ["V1/renders/esgoto_quiosque_medidas.png", "Rede hidrossanitária — água fria, esgoto e represa"]
      ]
    },
    {
      id: "externas", label: "Vistas externas",
      items: [
        ["V1/renders/projeto_render.png", "Vista geral do projeto"],
        ["V1/renders/vista_entrada.png", "Vista da entrada, do lado da piscina"],
        ["V1/renders/vista_aerea.png", "Vista aérea 3/4 da propriedade"],
        ["V1/renders/vista_15m_T2_V1.png", "Vista externa — eixo da terça T2, 15 m ao norte"],
        ["V1/renders/vista_10m_entre_P6_P2.png", "Vista externa — 10 m entre P6 e P2"],
        ["V1/renders/vista_360_fisheye.png", "Vista 360° (fisheye) do interior"]
      ]
    },
    {
      id: "interior", label: "Interiores",
      items: [
        ["V1/renders/vista_corredor.png", "Vista interna do corredor"],
        ["V1/renders/vista_corredor_cozinha.png", "Corredor olhando para a cozinha"],
        ["V1/renders/vista_area_pia.png", "Área da pia / bancada gourmet (de P9 para P2)"],
        ["V1/renders/banheiro_ducha_interior.png", "Interior da ducha"],
        ["V1/renders/banheiro_lavabo_interior.png", "Interior do lavabo"]
      ]
    },
    {
      id: "sol", label: "Estudo solar",
      items: [
        ["V1/renders/sol_verao_13h_anotado.png", "Verão, 13h"],
        ["V1/renders/sol_verao_15h_anotado.png", "Verão, 15h"],
        ["V1/renders/sol_verao_17h_anotado.png", "Verão, 17h"],
        ["V1/renders/sol_inverno_13h_anotado.png", "Inverno, 13h"],
        ["V1/renders/sol_inverno_15h_anotado.png", "Inverno, 15h"],
        ["V1/renders/sol_inverno_17h_anotado.png", "Inverno, 17h"]
      ]
    },
    {
      id: "v3", label: "Quiosque com fundo p/ casa da mãe",
      items: ["10h","11h","12h","13h","14h","15h","16h","17h","18h","19h"].map(function(h){
        return ["V3/renders/projeto_render_"+h+".png", "Fundo p/ casa da mãe — "+h];
      })
    },
    {
      id: "v4", label: "Quiosque com fundo p/ milho/abóbora",
      items: ["7h","8h","9h","10h","11h","12h","13h","14h","15h","16h","17h","18h"].map(function(h){
        return ["V4/renders/projeto_render_"+h+".png", "Fundo p/ milho/abóbora — "+h];
      })
    },
    {
      id: "v6", label: "Quiosque com fundo p/ cerca do Fernando",
      items: [].concat(
        ["15h","16h","17h","18h","19h"].map(function(h){
          return ["V6/renders/sol_verao_"+h+"_anotado.png", "Cerca do Fernando — verão, "+h];
        }),
        ["15h","16h","17h","18h","19h"].map(function(h){
          return ["V6/renders/sol_inverno_"+h+"_anotado.png", "Cerca do Fernando — inverno, "+h];
        })
      )
    }
  ];

  var tabsEl = document.getElementById("groupTabs");
  var stageImg = document.getElementById("stageImg");
  var capEl = document.getElementById("slideCap");
  var countEl = document.getElementById("slideCount");
  var thumbsEl = document.getElementById("thumbs");
  var prevBtn = document.getElementById("prevBtn");
  var nextBtn = document.getElementById("nextBtn");

  var groupIdx = 0, itemIdx = 0;

  function currentGroup(){ return GROUPS[groupIdx]; }

  function renderTabs(){
    tabsEl.innerHTML = "";
    GROUPS.forEach(function(g, i){
      var b = document.createElement("button");
      b.textContent = g.label;
      b.className = (i === groupIdx) ? "active" : "";
      b.addEventListener("click", function(){ groupIdx = i; itemIdx = 0; renderAll(); });
      tabsEl.appendChild(b);
    });
  }

  function renderThumbs(){
    thumbsEl.innerHTML = "";
    currentGroup().items.forEach(function(it, i){
      var im = document.createElement("img");
      im.src = BASE + it[0];
      im.loading = "lazy";
      im.alt = it[1];
      im.className = (i === itemIdx) ? "active" : "";
      im.addEventListener("click", function(){ itemIdx = i; renderStage(); });
      thumbsEl.appendChild(im);
    });
  }

  function renderStage(){
    var it = currentGroup().items[itemIdx];
    stageImg.src = BASE + it[0];
    stageImg.alt = it[1];
    capEl.textContent = it[1];
    countEl.textContent = (itemIdx + 1) + " / " + currentGroup().items.length + " — " + currentGroup().label;
    Array.prototype.forEach.call(thumbsEl.children, function(el, i){
      el.classList.toggle("active", i === itemIdx);
    });
    var frag = "#" + currentGroup().id;
    if (history.replaceState) history.replaceState(null, "", frag);
  }

  function renderAll(){ renderTabs(); renderThumbs(); renderStage(); }

  prevBtn.addEventListener("click", function(){
    itemIdx = (itemIdx - 1 + currentGroup().items.length) % currentGroup().items.length;
    renderStage();
  });
  nextBtn.addEventListener("click", function(){
    itemIdx = (itemIdx + 1) % currentGroup().items.length;
    renderStage();
  });
  document.addEventListener("keydown", function(e){
    if (e.key === "ArrowLeft") prevBtn.click();
    if (e.key === "ArrowRight") nextBtn.click();
  });

  var hash = (location.hash || "").replace("#", "");
  var found = GROUPS.findIndex(function(g){ return g.id === hash; });
  if (found >= 0) groupIdx = found;

  renderAll();
})();
