const state = {
  atlas: [],
  selectedProvince: null,
  pages: [],
  visiblePages: [],
  graphAllNodes: [],
  graphAllEdges: [],
  graphNodes: [],
  graphEdges: [],
  graphFocusId: null,
  graphMode: "empty",
  selectedId: null,
  compareIds: new Set(),
};

const els = {
  menuToggle: document.querySelector("#menuToggle"),
  homeBrand: document.querySelector("#homeBrand"),
  sideMenu: document.querySelector("#sideMenu"),
  menuItems: document.querySelectorAll(".menu-item"),
  toolLog: document.querySelector("#toolLog"),
  homeSearchForm: document.querySelector("#homeSearchForm"),
  homeSearchInput: document.querySelector("#homeSearchInput"),
  finderForm: document.querySelector("#finderForm"),
  finderInput: document.querySelector("#finderInput"),
  recommendationPanel: document.querySelector("#recommendationPanel"),
  atlasStats: document.querySelector("#atlasStats"),
  koreaMap: document.querySelector("#koreaMap"),
  scopeLabel: document.querySelector("#scopeLabel"),
  graphTitle: document.querySelector("#graphTitle"),
  graphMeta: document.querySelector("#graphMeta"),
  graphReset: document.querySelector("#graphReset"),
  knowledgeGraph: document.querySelector("#knowledgeGraph"),
  graphInspector: document.querySelector("#graphInspector"),
  pageList: document.querySelector("#pageList"),
  pageTitle: document.querySelector("#pageTitle"),
  pageType: document.querySelector("#pageType"),
  pageBody: document.querySelector("#pageBody"),
  tagList: document.querySelector("#tagList"),
  relatedList: document.querySelector("#relatedList"),
  resetSearch: document.querySelector("#resetSearch"),
  writerForm: document.querySelector("#writerForm"),
  writerTitle: document.querySelector("#writerTitle"),
  writerType: document.querySelector("#writerType"),
  writerProvince: document.querySelector("#writerProvince"),
  writerDistrict: document.querySelector("#writerDistrict"),
  writerTags: document.querySelector("#writerTags"),
  writerRelated: document.querySelector("#writerRelated"),
  writerBody: document.querySelector("#writerBody"),
  writerStatus: document.querySelector("#writerStatus"),
  compareChoices: document.querySelector("#compareChoices"),
  compareTable: document.querySelector("#compareTable"),
};

const PROVINCE_LAYOUT = [
  ["서울특별시", 238, 144, 54, 34, "#c95c43"],
  ["인천광역시", 170, 155, 58, 42, "#3c8a75"],
  ["경기도", 244, 202, 132, 86, "#d3a43d"],
  ["강원특별자치도", 360, 154, 150, 118, "#4f86a5"],
  ["충청북도", 300, 300, 112, 80, "#8568ab"],
  ["충청남도", 190, 324, 122, 90, "#6d9a50"],
  ["세종특별자치시", 242, 300, 44, 28, "#d88d3f"],
  ["대전광역시", 252, 358, 54, 34, "#9f6b55"],
  ["경상북도", 370, 390, 150, 124, "#4f8f83"],
  ["대구광역시", 388, 468, 58, 38, "#b9626e"],
  ["전북특별자치도", 218, 454, 128, 90, "#6e78b8"],
  ["광주광역시", 182, 562, 56, 36, "#be7353"],
  ["전라남도", 190, 610, 156, 104, "#3e8b99"],
  ["경상남도", 370, 570, 150, 94, "#b69b3f"],
  ["부산광역시", 448, 610, 62, 38, "#6d82a8"],
  ["울산광역시", 450, 548, 58, 36, "#8a6a9f"],
  ["제주특별자치도", 208, 710, 86, 36, "#4f8f65"],
];

const TYPE_COLORS = {
  province: "#f0d56b",
  region: "#3b82a0",
  property: "#cf6a4c",
  field_note: "#8b6fc0",
  ontology: "#d2a73c",
  checklist: "#4b9a69",
  trade_summary: "#6f7f91",
};

const TYPE_LABELS = {
  province: "지역",
  region: "생활권",
  property: "매물",
  field_note: "임장",
  ontology: "개념",
  checklist: "체크",
  trade_summary: "거래",
};

const TYPE_RANK = {
  province: 0,
  region: 1,
  ontology: 2,
  property: 3,
  field_note: 4,
  checklist: 5,
  trade_summary: 6,
};

const TERM_LABELS = {
  low_noise: "저소음",
  station_access: "역 접근성",
  sunlight: "채광",
  safety: "야간 안전",
  green_access: "녹지",
  river_access: "수변",
  school_district: "교육",
  office_access: "직주근접",
  low_rent: "비용",
  new_building: "신축",
  pet_friendly: "반려동물",
  parking: "주차",
};

async function requestJson(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || `${response.status} ${response.statusText}`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function parseCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function showTools(tools = []) {
  const uniqueTools = [...new Set(tools.filter(Boolean))];
  els.toolLog.innerHTML = uniqueTools.map((tool) => {
    const kind = tool === "error" ? " error" : "";
    return `<span class="tool-chip${kind}">${escapeHtml(tool)}</span>`;
  }).join("");
}

function showError(message, target = null) {
  showTools(["error"]);
  if (target) {
    target.innerHTML = `<p class="empty">${escapeHtml(message)}</p>`;
  }
  console.error(message);
}

function setView(viewName) {
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelector(`#${viewName}View`)?.classList.add("active");
  els.menuItems.forEach((item) => item.classList.toggle("active", item.dataset.view === viewName));
  els.sideMenu.classList.remove("open");
}

function goHome() {
  setView("home");
  showTools([]);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function termLabel(term) {
  return TERM_LABELS[term] || term;
}

function truncate(value, max = 18) {
  const text = String(value || "");
  return text.length > max ? `${text.slice(0, max)}...` : text;
}

function graphLabel(node) {
  if (node.type === "province") return node.title;
  if (node.type === "region" && node.district) return node.district;
  if (node.type === "ontology") {
    const term = (node.ontology_terms || [])[0] || (node.tags || []).find((tag) => TERM_LABELS[tag]);
    return term ? termLabel(term) : node.title.replace(state.selectedProvince || "", "").replace("온톨로지", "").trim();
  }
  if (node.type === "property") {
    return node.description || node.title.replace(state.selectedProvince || "", "").replace(node.district || "", "").trim();
  }
  if (node.type === "field_note" && node.district) return `${node.district} 임장`;
  return node.description || node.title;
}

function renderMarkdown(markdown) {
  const lines = String(markdown || "").split("\n");
  let html = "";
  let inList = false;
  for (const line of lines) {
    const text = line.trim();
    if (!text) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      continue;
    }
    if (text.startsWith("# ")) {
      if (inList) html += "</ul>";
      inList = false;
      html += `<h1>${escapeHtml(text.slice(2))}</h1>`;
    } else if (text.startsWith("## ")) {
      if (inList) html += "</ul>";
      inList = false;
      html += `<h2>${escapeHtml(text.slice(3))}</h2>`;
    } else if (text.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${escapeHtml(text.slice(2))}</li>`;
    } else {
      if (inList) html += "</ul>";
      inList = false;
      html += `<p>${escapeHtml(text)}</p>`;
    }
  }
  if (inList) html += "</ul>";
  return html;
}

function renderAtlasStats() {
  const pageCount = state.atlas.reduce((sum, item) => sum + item.page_count, 0);
  const propertyCount = state.atlas.reduce((sum, item) => sum + item.property_count, 0);
  els.atlasStats.innerHTML = `
    <span>${state.atlas.length} 시도</span>
    <span>${pageCount.toLocaleString()} Pages</span>
    <span>${propertyCount.toLocaleString()} 매물</span>
  `;
}

function renderKoreaMap() {
  const atlasByProvince = new Map(state.atlas.map((item) => [item.province, item]));
  const shapes = PROVINCE_LAYOUT.map(([province, x, y, w, h, color]) => {
    const item = atlasByProvince.get(province);
    const count = item?.page_count || 0;
    const active = province === state.selectedProvince ? "active" : "";
    return `
      <g data-province="${escapeHtml(province)}">
        <ellipse class="province-shape ${active}" cx="${x}" cy="${y}" rx="${w / 2}" ry="${h / 2}" fill="${color}" opacity="${count ? 0.94 : 0.42}" />
        <text class="province-label" x="${x}" y="${y + 4}">${escapeHtml(province.replace("특별자치도", "").replace("광역시", "").replace("특별시", ""))}</text>
      </g>
    `;
  }).join("");

  els.koreaMap.innerHTML = `
    <path d="M250 86 C318 70 421 94 466 176 C509 257 472 345 444 418 C503 494 477 646 360 674 C286 693 230 658 169 651 C93 642 70 565 102 498 C55 431 72 338 134 292 C109 229 144 118 250 86 Z" fill="rgba(255,253,245,.72)" stroke="#151515" stroke-width="3" />
    ${shapes}
  `;
}

function graphNodeMap(nodes = state.graphAllNodes) {
  return new Map(nodes.map((node) => [node.id, node]));
}

function graphDegreeMap(edges = state.graphAllEdges) {
  const degree = new Map();
  for (const edge of edges) {
    degree.set(edge.source, (degree.get(edge.source) || 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) || 0) + 1);
  }
  return degree;
}

function graphAdjacency(edges = state.graphAllEdges) {
  const adjacency = new Map();
  for (const edge of edges) {
    if (!adjacency.has(edge.source)) adjacency.set(edge.source, new Set());
    if (!adjacency.has(edge.target)) adjacency.set(edge.target, new Set());
    adjacency.get(edge.source).add(edge.target);
    adjacency.get(edge.target).add(edge.source);
  }
  return adjacency;
}

function sortedGraphNodes(nodes, degree = graphDegreeMap()) {
  return [...nodes].sort((a, b) => {
    const typeDiff = (TYPE_RANK[a.type] ?? 99) - (TYPE_RANK[b.type] ?? 99);
    if (typeDiff) return typeDiff;
    const degreeDiff = (degree.get(b.id) || 0) - (degree.get(a.id) || 0);
    if (degreeDiff) return degreeDiff;
    return String(a.title).localeCompare(String(b.title), "ko");
  });
}

function pickByType(nodes, limits, degree = graphDegreeMap()) {
  const counts = {};
  const picked = [];
  for (const node of sortedGraphNodes(nodes, degree)) {
    const limit = limits[node.type] ?? limits.default ?? 0;
    const count = counts[node.type] || 0;
    if (count < limit) {
      picked.push(node);
      counts[node.type] = count + 1;
    }
  }
  return picked;
}

function visibleEdgesFor(nodeIds, includeSecondary = true) {
  const visible = new Set(nodeIds);
  return state.graphAllEdges
    .filter((edge) => visible.has(edge.source) && visible.has(edge.target))
    .filter((edge) => includeSecondary || edge.source === state.graphFocusId || edge.target === state.graphFocusId)
    .slice(0, 90);
}

function hubNode(province = state.selectedProvince) {
  const atlasItem = state.atlas.find((item) => item.province === province);
  return {
    id: `scope:${province}`,
    title: province || "전국",
    type: "province",
    virtual: true,
    page_count: atlasItem?.page_count || state.graphAllNodes.length,
    property_count: atlasItem?.property_count || state.graphAllNodes.filter((node) => node.type === "property").length,
  };
}

function setGraphDisplay(nodes, edges, mode, focusId = null) {
  state.graphNodes = nodes;
  state.graphEdges = edges;
  state.graphMode = mode;
  state.graphFocusId = focusId;
  const totalNodes = state.graphAllNodes.length;
  const totalEdges = state.graphAllEdges.length;
  els.graphMeta.innerHTML = `
    <span>${nodes.length}/${totalNodes} nodes</span>
    <span>${edges.length}/${totalEdges} edges</span>
  `;
  renderGraph();
  renderGraphInspector(nodes.find((node) => node.id === focusId) || nodes[0]);
}

function renderProvinceOverview() {
  if (!state.selectedProvince) return;
  const degree = graphDegreeMap();
  const hub = { ...hubNode(), ring: 0 };
  const regions = pickByType(
    state.graphAllNodes.filter((node) => node.type === "region" && node.district),
    { region: 9 },
    degree,
  ).map((node) => ({ ...node, ring: 1 }));
  const ontology = pickByType(
    state.graphAllNodes.filter((node) => node.type === "ontology"),
    { ontology: 7 },
    degree,
  ).map((node) => ({ ...node, ring: 1 }));
  const properties = pickByType(
    state.graphAllNodes.filter((node) => node.type === "property"),
    { property: 8 },
    degree,
  ).map((node) => ({ ...node, ring: 2 }));

  const nodes = [hub, ...regions, ...ontology, ...properties];
  const nodeIds = nodes.map((node) => node.id);
  const guideEdges = [...regions, ...ontology].map((node) => ({
    source: hub.id,
    target: node.id,
    virtual: true,
    primary: true,
  }));
  const realEdges = visibleEdgesFor(nodeIds).map((edge) => ({ ...edge, primary: false }));
  els.scopeLabel.textContent = "REGION OVERVIEW";
  els.graphTitle.textContent = `${state.selectedProvince} 요약 그래프`;
  setGraphDisplay(nodes, [...guideEdges, ...realEdges], "overview", hub.id);
}

function focusGraphNode(nodeId) {
  if (!nodeId || nodeId.startsWith("scope:")) {
    renderProvinceOverview();
    return;
  }
  const nodeById = graphNodeMap();
  const focus = nodeById.get(nodeId);
  if (!focus) return;

  const adjacency = graphAdjacency();
  const degree = graphDegreeMap();
  const neighborIds = [...(adjacency.get(nodeId) || [])];
  const neighbors = neighborIds.map((id) => nodeById.get(id)).filter(Boolean);
  const firstRing = pickByType(neighbors, {
    region: 5,
    ontology: 6,
    property: 8,
    field_note: 6,
    checklist: 2,
    trade_summary: 2,
    default: 2,
  }, degree).map((node) => ({ ...node, ring: 1 }));

  const used = new Set([nodeId, ...firstRing.map((node) => node.id)]);
  const secondRingPool = [];
  if (firstRing.length < 16) {
    for (const neighbor of firstRing) {
      for (const id of adjacency.get(neighbor.id) || []) {
        if (!used.has(id)) {
          const candidate = nodeById.get(id);
          if (candidate) {
            secondRingPool.push(candidate);
            used.add(id);
          }
        }
      }
    }
  }
  const secondRing = pickByType(secondRingPool, {
    property: 3,
    field_note: 3,
    ontology: 2,
    checklist: 1,
    trade_summary: 1,
    default: 1,
  }, degree).map((node) => ({ ...node, ring: 2 }));

  const nodes = [{ ...focus, ring: 0 }, ...firstRing, ...secondRing];
  const ids = nodes.map((node) => node.id);
  const secondIds = new Set(secondRing.map((node) => node.id));
  const edges = visibleEdgesFor(ids)
    .filter((edge) => edge.source === nodeId || edge.target === nodeId || secondIds.has(edge.source) || secondIds.has(edge.target))
    .slice(0, 60)
    .map((edge) => ({
      ...edge,
      primary: edge.source === nodeId || edge.target === nodeId,
    }));
  els.scopeLabel.textContent = "FOCUSED GRAPH";
  els.graphTitle.textContent = focus.title;
  setGraphDisplay(nodes, edges, "focus", nodeId);
}

function distributeArc(items, center, radius, startDeg, endDeg, positions) {
  if (!items.length) return;
  const total = items.length;
  const spread = endDeg - startDeg;
  items.forEach((node, index) => {
    const ratio = total === 1 ? 0.5 : index / (total - 1);
    const angle = (startDeg + spread * ratio) * Math.PI / 180;
    positions[node.id] = {
      x: center.x + Math.cos(angle) * radius,
      y: center.y + Math.sin(angle) * radius,
    };
  });
}

function graphPositions(nodes) {
  const center = { x: 480, y: 280 };
  const positions = {};
  const focus = nodes.find((node) => node.ring === 0) || nodes[0];
  if (focus) positions[focus.id] = center;

  const byRingAndType = (ring, type) => nodes.filter((node) => node.ring === ring && node.type === type);
  const arcMap = {
    region: [118, 242],
    ontology: [230, 310],
    property: [-42, 60],
    field_note: [58, 128],
    checklist: [-128, -94],
    trade_summary: [94, 128],
  };
  for (const [type, arc] of Object.entries(arcMap)) {
    distributeArc(byRingAndType(1, type), center, 212, arc[0], arc[1], positions);
    distributeArc(byRingAndType(2, type), center, 306, arc[0], arc[1], positions);
  }

  const unplaced = nodes.filter((node) => !positions[node.id]);
  distributeArc(unplaced, center, 270, 0, 360, positions);
  return positions;
}

function renderGraph() {
  const nodes = state.graphNodes;
  const edges = state.graphEdges;
  if (!nodes.length) {
    els.knowledgeGraph.innerHTML = "";
    els.graphInspector.innerHTML = "";
    return;
  }
  const positions = graphPositions(nodes);
  const focusId = state.graphFocusId;

  const edgeMarkup = edges.map((edge) => {
    const source = positions[edge.source];
    const target = positions[edge.target];
    if (!source || !target) return "";
    const primary = edge.primary || edge.source === focusId || edge.target === focusId;
    const classes = ["graph-edge", primary ? "primary" : "secondary", edge.virtual ? "guide" : ""].join(" ");
    return `<line class="${classes}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" />`;
  }).join("");

  const nodeMarkup = nodes.map((node) => {
    const pos = positions[node.id];
    const focused = focusId === node.id;
    const far = node.ring === 2;
    const r = focused ? 22 : node.ring === 1 ? 13 : 9;
    const label = focused || node.ring === 1 || node.type === "province" || node.type === "ontology" || node.type === "region";
    const labelMax = focused ? 24 : node.type === "property" ? 14 : 12;
    const visibleLabel = graphLabel(node);
    return `
      <g class="graph-node ${focused ? "focused" : ""} ${far ? "far" : ""}" data-page-id="${escapeHtml(node.id)}" transform="translate(${pos.x} ${pos.y})">
        <title>${escapeHtml(node.title)}</title>
        ${focused ? `<circle class="node-halo" r="${r + 12}" />` : ""}
        <circle class="node-core" r="${r}" fill="${TYPE_COLORS[node.type] || "#c8c1ad"}" />
        ${label ? `<text class="node-label" y="${r + 18}">${escapeHtml(truncate(visibleLabel, labelMax))}</text>` : ""}
        ${focused ? `<text class="node-kind" y="${-r - 10}">${escapeHtml(TYPE_LABELS[node.type] || node.type)}</text>` : ""}
      </g>
    `;
  }).join("");

  els.knowledgeGraph.innerHTML = `<g>${edgeMarkup}</g><g>${nodeMarkup}</g>`;
}

function renderGraphInspector(node) {
  if (!node) {
    els.graphInspector.innerHTML = "";
    return;
  }
  if (node.virtual) {
    const atlasItem = state.atlas.find((item) => item.province === state.selectedProvince);
    const terms = (atlasItem?.ontology_terms || []).slice(0, 6);
    els.graphInspector.innerHTML = `
      <p class="eyebrow">SCOPE</p>
      <h4>${escapeHtml(node.title)}</h4>
      <dl>
        <dt>Pages</dt><dd>${Number(node.page_count || 0).toLocaleString()}</dd>
        <dt>매물</dt><dd>${Number(node.property_count || 0).toLocaleString()}</dd>
        <dt>표시</dt><dd>${state.graphNodes.length} nodes</dd>
      </dl>
      <div class="term-row">
        ${terms.map((item) => `<span class="term-chip">${escapeHtml(termLabel(item.term))}</span>`).join("")}
      </div>
    `;
    return;
  }

  const terms = (node.ontology_terms || []).slice(0, 6);
  const relatedCount = graphAdjacency().get(node.id)?.size || 0;
  els.graphInspector.innerHTML = `
    <p class="eyebrow">${escapeHtml(TYPE_LABELS[node.type] || node.type)}</p>
    <h4>${escapeHtml(node.title)}</h4>
    <dl>
      <dt>지역</dt><dd>${escapeHtml([node.province, node.district].filter(Boolean).join(" ") || "-")}</dd>
      <dt>연결</dt><dd>${relatedCount.toLocaleString()}개</dd>
      <dt>ID</dt><dd>${escapeHtml(node.id)}</dd>
    </dl>
    <div class="term-row">
      ${terms.map((term) => `<span class="term-chip">${escapeHtml(termLabel(term))}</span>`).join("")}
    </div>
    <button type="button" data-graph-open="${escapeHtml(node.id)}">문서 열기</button>
  `;
}

async function loadAtlas() {
  const data = await requestJson("/api/atlas");
  state.atlas = data.provinces || [];
  renderAtlasStats();
  renderKoreaMap();
  showTools(data.tools_used);
}

async function selectProvince(province) {
  state.selectedProvince = province;
  renderKoreaMap();
  const graph = await requestJson(`/api/graph?province=${encodeURIComponent(province)}&limit=850`);
  state.graphAllNodes = graph.nodes || [];
  state.graphAllEdges = graph.edges || [];
  state.graphNodes = [];
  state.graphEdges = [];
  state.graphFocusId = null;
  state.graphMode = "overview";
  renderProvinceOverview();
  await loadWikiPages(province);
  showTools(graph.tools_used);
  return graph;
}

function renderRecommendations(data) {
  const normalized = data.normalized || {};
  const terms = normalized.ontology_terms || [];
  const items = data.recommendations || [];
  const answer = items.length
    ? `${normalized.province || "전국"}에서 ${terms.map(termLabel).join(", ") || "질문 조건"}에 맞는 후보를 찾았습니다.`
    : "조건에 맞는 후보를 찾지 못했습니다.";
  els.recommendationPanel.innerHTML = `
    <div class="answer-block">
      <strong>${escapeHtml(answer)}</strong>
      <div class="term-row">
        ${(terms || []).map((term) => `<span class="term-chip">${escapeHtml(termLabel(term))}</span>`).join("")}
        ${normalized.province ? `<span class="term-chip">${escapeHtml(normalized.province)}</span>` : ""}
      </div>
    </div>
    <div class="recommendation-list">
      ${items.map((item) => renderRecommendationItem(item)).join("") || '<p class="empty">검색어를 바꿔보세요.</p>'}
    </div>
  `;
}

function renderRecommendationItem(item) {
  const page = item.page;
  const path = item.ontology_path || [];
  return `
    <article class="recommendation-item">
      <h3>${escapeHtml(page.title)}</h3>
      <p class="muted">${escapeHtml(page.province || "")} ${escapeHtml(page.district || "")} · score ${escapeHtml(item.score)}</p>
      <div class="path-row">
        ${path.map((step) => `<span class="term-chip">${escapeHtml(step.label)}</span>`).join("")}
      </div>
      <p>${escapeHtml(item.snippet || "")}</p>
      <button type="button" data-open-page="${escapeHtml(page.id)}">문서 열기</button>
    </article>
  `;
}

async function runRecommendation(query) {
  if (!query) return;
  els.recommendationPanel.innerHTML = '<p class="empty">조건을 온톨로지로 연결하는 중입니다.</p>';
  const data = await requestJson(`/api/recommend?q=${encodeURIComponent(query)}&limit=6`);
  renderRecommendations(data);
  showTools(data.tools_used);
  if (data.normalized?.province) {
    const graph = await selectProvince(data.normalized.province);
    showTools([...(data.tools_used || []), ...(graph.tools_used || [])]);
  }
}

function renderPageList(pages) {
  state.visiblePages = pages;
  els.pageList.innerHTML = pages.map((page) => `
    <button class="page-button ${page.id === state.selectedId ? "active" : ""}" data-page-id="${escapeHtml(page.id)}">
      <strong>${escapeHtml(page.title)}</strong>
      <span>${escapeHtml(page.type)} · ${escapeHtml(page.province || "")} ${escapeHtml(page.district || "")}</span>
    </button>
  `).join("");
}

async function loadWikiPages(province = state.selectedProvince) {
  const path = province
    ? `/api/pages?province=${encodeURIComponent(province)}&limit=120`
    : "/api/pages?limit=120";
  const data = await requestJson(path);
  state.pages = data.pages || [];
  renderPageList(state.pages);
  renderCompareChoices();
}

async function selectPage(pageId) {
  const data = await requestJson(`/api/pages/${encodeURIComponent(pageId)}`);
  const page = data.page;
  state.selectedId = page.id;
  els.pageTitle.textContent = page.title;
  els.pageType.textContent = page.type;
  els.tagList.innerHTML = (page.tags || []).slice(0, 8).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
  els.pageBody.innerHTML = renderMarkdown(page.body);
  renderPageList(state.visiblePages.length ? state.visiblePages : state.pages);
  await loadRelated(page.id);
  renderGraph();
  setView("wiki");
  showTools(data.tools_used);
}

async function openPage(pageId) {
  try {
    await selectPage(pageId);
  } catch (error) {
    showError(error.message || "문서를 열지 못했습니다.");
  }
}

async function loadRelated(pageId) {
  const data = await requestJson(`/api/pages/${encodeURIComponent(pageId)}/related`);
  els.relatedList.innerHTML = (data.pages || []).slice(0, 12).map((page) => `
    <div class="related-item">
      <button type="button" data-page-id="${escapeHtml(page.id)}">
        <strong>${escapeHtml(page.title)}</strong>
        <span>${escapeHtml(page.relation)} · ${escapeHtml(page.type)}</span>
      </button>
    </div>
  `).join("") || '<p class="empty">연결된 문서가 없습니다.</p>';
}

function renderCompareChoices() {
  const properties = state.pages.filter((page) => page.type === "property").slice(0, 18);
  els.compareChoices.innerHTML = properties.map((page) => `
    <label>
      <input type="checkbox" value="${escapeHtml(page.id)}" ${state.compareIds.has(page.id) ? "checked" : ""} />
      ${escapeHtml(truncate(page.title, 24))}
    </label>
  `).join("");
}

async function loadCompare() {
  const ids = Array.from(state.compareIds);
  if (ids.length < 2) {
    els.compareTable.innerHTML = '<p class="empty">후보 2개 이상을 선택하세요.</p>';
    return;
  }
  const data = await requestJson(`/api/compare?ids=${encodeURIComponent(ids.join(","))}`);
  const headers = ["criterion", ...data.properties.map((page) => page.id)];
  els.compareTable.innerHTML = `
    <table>
      <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
      <tbody>${data.comparison.map((row) => `<tr>${headers.map((header) => `<td>${escapeHtml(row[header] || "")}</td>`).join("")}</tr>`).join("")}</tbody>
    </table>
  `;
  showTools(data.tools_used);
}

async function submitWriterForm(event) {
  event.preventDefault();
  const province = els.writerProvince.value.trim();
  const district = els.writerDistrict.value.trim();
  const payload = {
    title: els.writerTitle.value.trim(),
    type: els.writerType.value,
    body: els.writerBody.value.trim(),
    tags: parseCsv(els.writerTags.value),
    related_pages: parseCsv(els.writerRelated.value),
    source: "gui_writer",
    province,
    district,
  };
  if (!payload.title || !payload.body) {
    els.writerStatus.textContent = "제목과 본문이 필요합니다.";
    return;
  }
  els.writerStatus.textContent = "저장 중...";
  try {
    const data = await requestJson("/api/pages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    els.writerStatus.textContent = `저장됨: ${data.page.id}`;
    els.writerForm.reset();
    await loadWikiPages(province || state.selectedProvince);
    await selectPage(data.page.id);
  } catch (error) {
    els.writerStatus.textContent = error.message;
  }
}

els.menuToggle.addEventListener("click", () => els.sideMenu.classList.toggle("open"));
els.homeBrand.addEventListener("click", goHome);
els.menuItems.forEach((item) => {
  item.addEventListener("click", async () => {
    try {
      setView(item.dataset.view);
      if (item.dataset.view === "atlas" && !state.atlas.length) await loadAtlas();
      if (item.dataset.view === "wiki" && !state.pages.length) await loadWikiPages();
      if (item.dataset.view === "compare" && !state.pages.length) await loadWikiPages();
    } catch (error) {
      showError(error.message || "화면을 불러오지 못했습니다.");
    }
  });
});

els.homeSearchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = els.homeSearchInput.value.trim();
  els.finderInput.value = query;
  setView("finder");
  try {
    await runRecommendation(query);
  } catch (error) {
    showError(error.message || "추천 결과를 불러오지 못했습니다.", els.recommendationPanel);
  }
});

els.finderForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await runRecommendation(els.finderInput.value.trim());
  } catch (error) {
    showError(error.message || "추천 결과를 불러오지 못했습니다.", els.recommendationPanel);
  }
});

els.koreaMap.addEventListener("click", async (event) => {
  const group = event.target.closest("[data-province]");
  if (group) {
    try {
      await selectProvince(group.dataset.province);
    } catch (error) {
      showError(error.message || "지역 그래프를 불러오지 못했습니다.", els.graphInspector);
    }
  }
});

els.knowledgeGraph.addEventListener("click", (event) => {
  const node = event.target.closest("[data-page-id]");
  if (node) focusGraphNode(node.dataset.pageId);
});

els.graphReset.addEventListener("click", () => renderProvinceOverview());

els.graphInspector.addEventListener("click", (event) => {
  const button = event.target.closest("[data-graph-open]");
  if (button) openPage(button.dataset.graphOpen);
});

els.pageList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page-id]");
  if (button) openPage(button.dataset.pageId);
});

els.relatedList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page-id]");
  if (button) openPage(button.dataset.pageId);
});

els.recommendationPanel.addEventListener("click", (event) => {
  const button = event.target.closest("[data-open-page]");
  if (button) openPage(button.dataset.openPage);
});

els.compareChoices.addEventListener("change", (event) => {
  if (!event.target.matches("input[type='checkbox']")) return;
  if (event.target.checked) {
    state.compareIds.add(event.target.value);
  } else {
    state.compareIds.delete(event.target.value);
  }
  loadCompare().catch((error) => showError(error.message || "비교표를 불러오지 못했습니다.", els.compareTable));
});

els.resetSearch.addEventListener("click", () => {
  loadWikiPages(null).catch((error) => showError(error.message || "문서 목록을 불러오지 못했습니다.", els.pageList));
});
els.writerForm.addEventListener("submit", submitWriterForm);

showTools([]);
