const state = {
  pages: [],
  visiblePages: [],
  graphEdges: [],
  filterActive: false,
  selectedId: null,
  compareIds: new Set(),
};

const els = {
  knowledgeGraph: document.querySelector("#knowledgeGraph"),
  graphLegend: document.querySelector("#graphLegend"),
  graphStats: document.querySelector("#graphStats"),
  pageList: document.querySelector("#pageList"),
  pageTitle: document.querySelector("#pageTitle"),
  pageType: document.querySelector("#pageType"),
  pageBody: document.querySelector("#pageBody"),
  tagList: document.querySelector("#tagList"),
  relatedList: document.querySelector("#relatedList"),
  tradePanel: document.querySelector("#tradePanel"),
  toolLog: document.querySelector("#toolLog"),
  compareChoices: document.querySelector("#compareChoices"),
  compareTable: document.querySelector("#compareTable"),
  searchForm: document.querySelector("#searchForm"),
  searchInput: document.querySelector("#searchInput"),
  resetSearch: document.querySelector("#resetSearch"),
};

const typeLabels = {
  property: "매물",
  region: "생활권",
  checklist: "체크",
  trade_summary: "실거래",
  field_note: "노트",
};

const typeColors = {
  property: "#b84a32",
  region: "#286b4d",
  checklist: "#d6a83e",
  trade_summary: "#28708a",
  field_note: "#7357a4",
  default: "#3a3730",
};

async function requestJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json();
}

function showTools(tools = []) {
  els.toolLog.innerHTML = tools.map((tool) => `<span class="tool-chip">${escapeHtml(tool)}</span>`).join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function truncateLabel(value, maxLength = 13) {
  const text = String(value);
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

function getTypeLabel(type) {
  return typeLabels[type] || type;
}

function getTypeColor(type) {
  return typeColors[type] || typeColors.default;
}

function buildGraphEdges(pages) {
  const knownIds = new Set(pages.map((page) => page.id));
  const edges = new Map();

  for (const page of pages) {
    for (const relatedId of page.related_pages || []) {
      if (!knownIds.has(relatedId) || relatedId === page.id) {
        continue;
      }

      const [first, second] = [page.id, relatedId].sort();
      const key = `${first}::${second}`;
      const edge = edges.get(key) || {
        source: first,
        target: second,
        weight: 0,
        directions: new Set(),
      };
      edge.weight += 1;
      edge.directions.add(`${page.id}>${relatedId}`);
      edges.set(key, edge);
    }
  }

  return Array.from(edges.values()).map((edge) => ({
    ...edge,
    directions: Array.from(edge.directions),
  }));
}

function neighborIdsFor(pageId) {
  const neighbors = new Set();
  for (const edge of state.graphEdges) {
    if (edge.source === pageId) {
      neighbors.add(edge.target);
    }
    if (edge.target === pageId) {
      neighbors.add(edge.source);
    }
  }
  return neighbors;
}

function sortGraphPages(pages) {
  const typeRank = {
    property: 0,
    region: 1,
    checklist: 2,
    trade_summary: 3,
    field_note: 4,
  };
  return [...pages].sort((a, b) => {
    const rankDiff = (typeRank[a.type] ?? 9) - (typeRank[b.type] ?? 9);
    return rankDiff || a.title.localeCompare(b.title, "ko");
  });
}

function placeOnRing(pages, positions, center, rx, ry, startAngle) {
  const count = Math.max(pages.length, 1);
  pages.forEach((page, index) => {
    const angle = startAngle + (Math.PI * 2 * index) / count;
    positions[page.id] = {
      x: center.x + Math.cos(angle) * rx,
      y: center.y + Math.sin(angle) * ry,
    };
  });
}

function graphPositions(pages) {
  const center = { x: 480, y: 170 };
  const positions = {};
  const selected = pages.find((page) => page.id === state.selectedId);

  if (!selected) {
    placeOnRing(sortGraphPages(pages), positions, center, 360, 122, -Math.PI / 2);
    return positions;
  }

  positions[selected.id] = center;
  const neighborIds = neighborIdsFor(selected.id);
  const neighbors = sortGraphPages(pages.filter((page) => neighborIds.has(page.id)));
  const remainder = sortGraphPages(
    pages.filter((page) => page.id !== selected.id && !neighborIds.has(page.id)),
  );

  placeOnRing(neighbors, positions, center, 230, 92, -Math.PI / 2);
  placeOnRing(remainder, positions, center, 382, 132, Math.PI / 6);
  return positions;
}

function renderGraphLegend() {
  const types = [...new Set(state.pages.map((page) => page.type))];
  els.graphLegend.innerHTML = sortGraphPages(
    types.map((type) => ({ id: type, type, title: getTypeLabel(type) })),
  )
    .map(
      (item) => `
        <span class="legend-pill">
          <span class="legend-dot" style="background:${getTypeColor(item.type)}"></span>
          ${escapeHtml(item.title)}
        </span>
      `,
    )
    .join("");
}

function renderGraphStats() {
  const selected = state.pages.find((page) => page.id === state.selectedId);
  const visibleCount = state.filterActive ? state.visiblePages.length : state.pages.length;
  const linkedCount = selected ? neighborIdsFor(selected.id).size : state.graphEdges.length;
  els.graphStats.innerHTML = `
    <div><strong>${state.pages.length}</strong><span>Pages</span></div>
    <div><strong>${state.graphEdges.length}</strong><span>Relations</span></div>
    <div><strong>${visibleCount}</strong><span>Shown</span></div>
    <div><strong>${linkedCount}</strong><span>${selected ? "Linked" : "Edges"}</span></div>
  `;
}

function renderKnowledgeGraph() {
  if (!els.knowledgeGraph) {
    return;
  }

  renderGraphStats();
  const pages = state.pages;
  if (!pages.length) {
    els.knowledgeGraph.innerHTML = "";
    return;
  }

  const positions = graphPositions(pages);
  const visibleIds = new Set((state.filterActive ? state.visiblePages : pages).map((page) => page.id));
  const hasSearchFilter = state.filterActive;
  const connectedIds = state.selectedId ? neighborIdsFor(state.selectedId) : new Set();

  const edgeMarkup = state.graphEdges
    .map((edge) => {
      const source = positions[edge.source];
      const target = positions[edge.target];
      if (!source || !target) {
        return "";
      }

      const active =
        !state.selectedId ||
        edge.source === state.selectedId ||
        edge.target === state.selectedId ||
        (connectedIds.has(edge.source) && connectedIds.has(edge.target));
      const highlightedBySearch = visibleIds.has(edge.source) && visibleIds.has(edge.target);
      const className = [
        "graph-edge",
        active ? "active" : "muted",
        highlightedBySearch ? "search-hit" : "",
        edge.weight > 1 ? "strong" : "",
      ]
        .filter(Boolean)
        .join(" ");
      const midX = (source.x + target.x) / 2;
      const path = `M ${source.x} ${source.y} C ${midX} ${source.y}, ${midX} ${target.y}, ${target.x} ${target.y}`;
      return `<path class="${className}" d="${path}" />`;
    })
    .join("");

  const nodeMarkup = pages
    .map((page) => {
      const position = positions[page.id];
      const selected = page.id === state.selectedId;
      const connected = connectedIds.has(page.id);
      const hiddenBySearch = hasSearchFilter && !visibleIds.has(page.id);
      const className = [
        "graph-node",
        selected ? "selected" : "",
        connected ? "connected" : "",
        hiddenBySearch ? "filtered" : "",
      ]
        .filter(Boolean)
        .join(" ");
      return `
        <g class="${className}" data-page-id="${escapeHtml(page.id)}" tabindex="0" role="button" aria-label="${escapeHtml(page.title)}" transform="translate(${position.x} ${position.y})">
          <circle class="node-halo" r="${selected ? 42 : 34}" />
          <circle class="node-dot" r="${selected ? 25 : 21}" fill="${getTypeColor(page.type)}" />
          <text class="node-label" y="48">${escapeHtml(truncateLabel(page.title))}</text>
          ${selected ? "" : `<text class="node-type" y="-30">${escapeHtml(getTypeLabel(page.type))}</text>`}
        </g>
      `;
    })
    .join("");

  els.knowledgeGraph.innerHTML = `
    <defs>
      <filter id="nodeShadow" x="-40%" y="-40%" width="180%" height="180%">
        <feDropShadow dx="0" dy="7" stdDeviation="5" flood-color="#1b1712" flood-opacity="0.22" />
      </filter>
    </defs>
    <g class="graph-grid">
      <path d="M 40 70 H 920 M 40 170 H 920 M 40 270 H 920 M 150 32 V 308 M 480 32 V 308 M 810 32 V 308" />
    </g>
    <g class="graph-edges">${edgeMarkup}</g>
    <g class="graph-nodes">${nodeMarkup}</g>
  `;
}

function renderMarkdown(markdown) {
  const lines = markdown.split("\n");
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
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<h1>${escapeHtml(text.slice(2))}</h1>`;
    } else if (text.startsWith("## ")) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<h2>${escapeHtml(text.slice(3))}</h2>`;
    } else if (text.startsWith("- ")) {
      if (!inList) {
        html += "<ul>";
        inList = true;
      }
      html += `<li>${escapeHtml(text.slice(2))}</li>`;
    } else {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += `<p>${escapeHtml(text)}</p>`;
    }
  }

  if (inList) {
    html += "</ul>";
  }
  return html;
}

function renderPageList(pages) {
  state.visiblePages = pages;
  els.pageList.innerHTML = pages
    .map(
      (page) => `
        <button class="page-button ${page.id === state.selectedId ? "active" : ""}" data-page-id="${escapeHtml(page.id)}">
          <strong>${escapeHtml(page.title)}</strong>
          <span>${escapeHtml(page.type)} · ${escapeHtml(page.tags.join(", "))}</span>
        </button>
      `,
    )
    .join("");
}

function renderCompareChoices() {
  const properties = state.pages.filter((page) => page.type === "property");
  els.compareChoices.innerHTML = properties
    .map(
      (page) => `
        <label>
          <input type="checkbox" value="${escapeHtml(page.id)}" ${state.compareIds.has(page.id) ? "checked" : ""} />
          ${escapeHtml(page.title)}
        </label>
      `,
    )
    .join("");
}

async function selectPage(pageId) {
  const data = await requestJson(`/api/pages/${encodeURIComponent(pageId)}`);
  const page = data.page;
  state.selectedId = page.id;
  els.pageTitle.textContent = page.title;
  els.pageType.textContent = page.type;
  els.tagList.innerHTML = page.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");
  els.pageBody.innerHTML = renderMarkdown(page.body);
  renderPageList(state.filterActive ? state.visiblePages : state.pages);
  renderKnowledgeGraph();
  showTools(data.tools_used);
  await Promise.all([loadRelated(page.id), loadTradeSample()]);
}

async function loadRelated(pageId) {
  const data = await requestJson(`/api/pages/${encodeURIComponent(pageId)}/related`);
  els.relatedList.innerHTML = data.pages.length
    ? data.pages
        .map(
          (page) => `
            <div class="related-item">
              <button type="button" data-page-id="${escapeHtml(page.id)}">
                <strong>${escapeHtml(page.title)}</strong><br />
                <span>${escapeHtml(page.relation)} · ${escapeHtml(page.type)}</span>
              </button>
            </div>
          `,
        )
        .join("")
    : '<p class="empty">연결된 페이지가 없습니다.</p>';
}

async function loadTradeSample() {
  const data = await requestJson("/api/trade/rent?lawd_cd=11710&deal_ymd=202405");
  const first = data.items[0] || {};
  els.tradePanel.innerHTML = `
    <div class="trade-item">
      <strong>${escapeHtml(first.apt_name || first.aptNm || "No result")}</strong><br />
      <span>source: ${escapeHtml(data.source)}</span><br />
      <span>deposit: ${escapeHtml(first.deposit || first.depositAmount || "-")}</span><br />
      <span>monthly: ${escapeHtml(first.monthly_rent || first.monthlyRent || "-")}</span>
    </div>
  `;
}

async function loadCompare() {
  const ids = Array.from(state.compareIds);
  if (ids.length < 2) {
    els.compareTable.innerHTML = '<p class="empty">비교할 매물 2개 이상을 선택하세요.</p>';
    return;
  }
  const data = await requestJson(`/api/compare?ids=${encodeURIComponent(ids.join(","))}`);
  const headers = ["criterion", ...data.properties.map((page) => page.id)];
  els.compareTable.innerHTML = `
    <table>
      <thead>
        <tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${data.comparison
          .map(
            (row) => `
              <tr>
                ${headers.map((header) => `<td>${escapeHtml(row[header] || "")}</td>`).join("")}
              </tr>
            `,
          )
          .join("")}
      </tbody>
    </table>
  `;
  showTools(data.tools_used);
}

async function loadPages() {
  const [data, graph] = await Promise.all([requestJson("/api/pages"), requestJson("/api/graph")]);
  state.pages = data.pages;
  state.visiblePages = data.pages;
  state.graphEdges = graph.edges || buildGraphEdges(data.pages);
  state.filterActive = false;
  const defaultProperties = state.pages.filter((page) => page.type === "property").slice(0, 2);
  defaultProperties.forEach((page) => state.compareIds.add(page.id));
  renderPageList(state.pages);
  renderGraphLegend();
  renderKnowledgeGraph();
  renderCompareChoices();
  showTools([...(data.tools_used || []), ...(graph.tools_used || [])]);
  if (defaultProperties[0] || state.pages[0]) {
    await selectPage((defaultProperties[0] || state.pages[0]).id);
  }
  await loadCompare();
}

els.pageList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page-id]");
  if (button) {
    selectPage(button.dataset.pageId);
  }
});

els.relatedList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page-id]");
  if (button) {
    selectPage(button.dataset.pageId);
  }
});

els.compareChoices.addEventListener("change", (event) => {
  if (event.target.matches("input[type='checkbox']")) {
    if (event.target.checked) {
      state.compareIds.add(event.target.value);
    } else {
      state.compareIds.delete(event.target.value);
    }
    loadCompare();
  }
});

els.knowledgeGraph.addEventListener("click", (event) => {
  const node = event.target.closest("[data-page-id]");
  if (node) {
    selectPage(node.dataset.pageId);
  }
});

els.knowledgeGraph.addEventListener("keydown", (event) => {
  const node = event.target.closest("[data-page-id]");
  if (node && (event.key === "Enter" || event.key === " ")) {
    event.preventDefault();
    selectPage(node.dataset.pageId);
  }
});

els.searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const q = els.searchInput.value.trim();
  const data = await requestJson(`/api/search?q=${encodeURIComponent(q)}`);
  state.filterActive = true;
  renderPageList(data.pages);
  renderKnowledgeGraph();
  showTools(data.tools_used);
  if (data.pages[0]) {
    await selectPage(data.pages[0].id);
  }
});

els.resetSearch.addEventListener("click", () => {
  state.filterActive = false;
  renderPageList(state.pages);
  renderKnowledgeGraph();
});

loadPages().catch((error) => {
  els.pageBody.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
});
