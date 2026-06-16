const state = {
  pages: [],
  visiblePages: [],
  selectedId: null,
  compareIds: new Set(),
};

const els = {
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
  renderPageList(state.visiblePages.length ? state.visiblePages : state.pages);
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
  const data = await requestJson("/api/pages");
  state.pages = data.pages;
  state.visiblePages = data.pages;
  const defaultProperties = state.pages.filter((page) => page.type === "property").slice(0, 2);
  defaultProperties.forEach((page) => state.compareIds.add(page.id));
  renderPageList(state.pages);
  renderCompareChoices();
  showTools(data.tools_used);
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

els.searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const q = els.searchInput.value.trim();
  const data = await requestJson(`/api/search?q=${encodeURIComponent(q)}`);
  renderPageList(data.pages);
  showTools(data.tools_used);
  if (data.pages[0]) {
    await selectPage(data.pages[0].id);
  }
});

els.resetSearch.addEventListener("click", () => {
  renderPageList(state.pages);
});

loadPages().catch((error) => {
  els.pageBody.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
});
