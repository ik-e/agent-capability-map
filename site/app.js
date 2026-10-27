import { searchCatalog } from "./search-core.js";

const CATALOG_ROOT = "./catalog/v1";
const state = { index: null, browse: null, selectedCategory: "", query: "", filters: {} };
const $ = (selector) => document.querySelector(selector);
const escapeText = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character]));

function renderCategories() {
  const container = $("#categories");
  const counts = new Map();
  for (const item of state.index.items) {
    for (const id of item.category_ids || []) counts.set(id, (counts.get(id) || 0) + 1);
  }
  const all = document.createElement("button");
  all.className = `category-button${state.selectedCategory ? "" : " active"}`;
  all.type = "button";
  all.innerHTML = `<span>전체 기능</span><span class="category-count">${state.index.items.length}</span>`;
  all.addEventListener("click", () => { state.selectedCategory = ""; renderCategories(); runSearch(); });
  container.append(all);
  for (const category of state.browse.categories) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `category-button${state.selectedCategory === category.id ? " active" : ""}`;
    button.innerHTML = `<span>${escapeText(category.label)}</span><span class="category-count">${counts.get(category.id) || 0}</span>`;
    button.addEventListener("click", () => { state.selectedCategory = category.id; renderCategories(); runSearch(); });
    container.append(button);
  }
}

function renderResults(outcome) {
  const list = $("#results");
  list.replaceChildren();
  $("#detail-panel").innerHTML = '<div class="detail-empty"><span class="detail-symbol">↖</span><h2>항목을 선택하세요</h2><p>기능, 필요한 입력, 연결 방식과 근거를 확인할 수 있습니다.</p></div>';
  $("#result-count").textContent = outcome.results.length ? `${outcome.results.length}개 결과` : "";
  if (outcome.abstain) {
    $("#status-message").textContent = "조건을 만족한다고 확인된 항목이 없습니다. 조건을 바꾸거나 공식 문서에서 확인해 주세요.";
    list.innerHTML = '<div class="empty-state">검색 결과가 없습니다</div>';
    $("#detail-panel").innerHTML = '<div class="detail-empty"><span class="detail-symbol">?</span><h2>확인 가능한 후보가 없습니다</h2><p>미확인 조건은 만족으로 간주하지 않습니다.</p></div>';
    return;
  }
  $("#status-message").textContent = state.query ? "목적에 가까운 기능부터 표시합니다. 상세에서 구현별 조건과 근거를 확인하세요." : "분야를 고르거나 자주 쓰는 기능부터 둘러보세요.";
  for (const row of outcome.results) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "result-card";
    button.dataset.id = row.item.id;
    const chips = row.bindings.slice(0, 3).map(({ binding, verdict }) => {
      const label = binding.resource_kind === "mcp_server" ? "MCP" : binding.resource_kind === "http_api" ? "HTTP API" : binding.resource_kind;
      const transport = binding.transport !== "unknown" ? ` · ${binding.transport}` : "";
      const result = verdict === "satisfies" ? "조건 일치" : "조건 미확인";
      return `<span class="chip ${verdict === "satisfies" ? "good" : "unknown"}">${escapeText(label + transport + " · " + result)}</span>`;
    }).join("");
    button.innerHTML = `<div class="card-top"><h3 class="card-title">${escapeText(row.item.name)}</h3><span class="score">${row.points ? `점수 ${row.points}` : "분야 항목"}</span></div><p class="card-purpose">${escapeText(row.item.purpose)}</p><div class="chips">${chips}</div>`;
    button.addEventListener("click", () => selectOperation(row.item.id, button));
    list.append(button);
  }
  $("#results-title").textContent = state.selectedCategory ? (state.browse.categories.find((category) => category.id === state.selectedCategory)?.label || "검색 결과") : (state.query ? "검색 결과" : "둘러보기");
}

async function getJson(path) {
  const response = await fetch(`${CATALOG_ROOT}/${path}`);
  if (!response.ok) throw new Error(`Catalog request failed (${response.status}): ${path}`);
  return response.json();
}

function detailSection(title, content) {
  return `<section class="detail-section"><h3>${escapeText(title)}</h3>${content}</section>`;
}

async function selectOperation(id, selectedButton) {
  document.querySelectorAll(".result-card").forEach((node) => node.classList.toggle("selected", node === selectedButton));
  const operation = await getJson(`operations/${encodeURIComponent(id)}.json`);
  const bindings = await Promise.all((operation.binding_ids || []).map((bindingId) => getJson(`bindings/${encodeURIComponent(bindingId)}.json`)));
  const evidence = await Promise.all((operation.evidence_ids || []).map((evidenceId) => getJson(`evidence/${encodeURIComponent(evidenceId)}.json`)));
  const inputList = (operation.inputs || []).map((input) => `<li><strong>${escapeText(input.name)}</strong> · ${escapeText(input.type)}${input.required ? " · 필수" : " · 선택"}<br>${escapeText(input.description)}</li>`).join("") || "<li>정의된 의미 입력 없음</li>";
  const bindingCards = bindings.map((binding) => {
    const loc = Object.values(binding.locations || {}).map((value) => value.url || value.package).filter(Boolean)[0] || "주소 없음";
    return `<button type="button" class="binding-link" data-binding="${escapeText(binding.id)}"><strong>${escapeText(binding.name)}</strong><span>${escapeText(binding.resource_kind)} · ${escapeText(binding.transport || "전송 미정")} · 인증: ${escapeText(binding.auth_schemes.join(", "))}</span><span>${escapeText(loc)}</span></button>`;
  }).join("");
  const evidenceCards = evidence.map((entry) => `<a class="evidence-link" href="${escapeText(entry.source_url)}" target="_blank" rel="noreferrer"><strong>${escapeText(entry.source_grade)}등급 · ${escapeText(entry.verification_state)}</strong><span>${escapeText(entry.source_locator || entry.claim_path)} ↗</span></a>`).join("") || "<p>연결된 근거가 없습니다.</p>";
  $("#detail-panel").innerHTML = `<article class="detail-content"><p class="eyebrow">OPERATION · ${escapeText(operation.id)}</p><h2>${escapeText(operation.name)}</h2><p class="purpose">${escapeText(operation.purpose)}</p>${detailSection("요구 입력", `<ul>${inputList}</ul>`)}${detailSection("효과", `<p>${escapeText(operation.effect)}</p>`)}${detailSection("구현 Binding", bindingCards || "<p>활성 구현이 없습니다.</p>")}${detailSection("출처와 근거", evidenceCards)}</article>`;
  for (const anchor of $("#detail-panel").querySelectorAll("a[data-binding]")) {
    anchor.addEventListener("click", (event) => {
      event.preventDefault();
      const binding = bindings.find((entry) => entry.id === anchor.dataset.binding);
      if (binding) showBinding(binding);
    });
  }
  for (const button of $("#detail-panel").querySelectorAll("button[data-binding]")) {
    button.addEventListener("click", () => {
      const binding = bindings.find((entry) => entry.id === button.dataset.binding);
      if (binding) showBinding(binding);
    });
  }
}

async function showBinding(binding) {
  const urls = Object.entries(binding.locations || {}).map(([kind, value]) => {
    const rendered = value.url ? `<a href="${escapeText(value.url)}" target="_blank" rel="noreferrer">${escapeText(value.url)} ↗</a>` : `${escapeText(value.package)} (${escapeText(value.registry)})`;
    return `<li><strong>${escapeText(kind)}</strong>: ${rendered}</li>`;
  }).join("");
  const refs = (binding.operation_refs || []).map((ref) => `<li>${escapeText(ref.native_ref?.kind || "capability")}: ${escapeText(ref.native_ref?.value || ref.operation_id)}</li>`).join("");
  const evidence = await Promise.all((binding.evidence_ids || []).map((evidenceId) => getJson(`evidence/${encodeURIComponent(evidenceId)}.json`)));
  const evidenceCards = evidence.map((entry) => `<a class="evidence-link" href="${escapeText(entry.source_url)}" target="_blank" rel="noreferrer"><strong>${escapeText(entry.source_grade)}등급 · ${escapeText(entry.verification_state)}</strong><span>${escapeText(entry.source_locator || entry.claim_path)} ↗</span></a>`).join("") || "<p>연결된 근거가 없습니다.</p>";
  const back = `<button id="back-to-operation" type="button" class="detail-url">← 기능 상세로 돌아가기</button>`;
  $("#detail-panel").innerHTML = `<article class="detail-content">${back}<p class="eyebrow">BINDING · ${escapeText(binding.id)}</p><h2>${escapeText(binding.name)}</h2><p class="purpose">${escapeText(binding.resource_kind)} · ${escapeText(binding.transport || "전송 미정")} · ${escapeText(binding.version || "버전 미기록")} · ${escapeText(binding.status)}</p>${detailSection("위치", `<ul>${urls}</ul>`)}${detailSection("인증 대안", `<p>${escapeText(binding.auth_schemes.join(", "))}</p>`)}${detailSection("연결된 기능", `<ul>${refs}</ul>`)}${detailSection("출처와 근거", evidenceCards)}</article>`;
  $("#back-to-operation").addEventListener("click", runSearch);
}

function runSearch() {
  if (!state.index) return;
  state.query = $("#query").value.trim();
  state.filters = { resource_kind: $("#kind-filter").value, transport: $("#transport-filter").value, auth_schemes: $("#auth-filter").value };
  const filters = Object.fromEntries(Object.entries(state.filters).filter(([, value]) => value).map(([key, value]) => [key, key === "auth_schemes" ? value : value]));
  const outcome = searchCatalog(state.index.items, state.query, filters, state.selectedCategory, 5);
  renderResults(outcome);
}

async function initialize() {
  try {
    const [manifest, index, browse] = await Promise.all([getJson("manifest.json"), getJson("search/operations.json"), getJson("browse/index.json")]);
    state.index = index;
    state.browse = browse;
    $("#revision").textContent = `${manifest.counts.searchable_operations}개 기능`;
    $("#footer-revision").textContent = `revision ${manifest.catalog_revision}`;
    renderCategories();
    runSearch();
  } catch (error) {
    $("#status-message").textContent = "카탈로그를 불러오지 못했습니다. 로컬 HTTP 서버로 열거나 잠시 후 다시 시도하세요.";
    $("#results").innerHTML = `<div class="empty-state">${escapeText(error.message)}</div>`;
  }
}

$("#search-form").addEventListener("submit", (event) => { event.preventDefault(); state.selectedCategory = ""; renderCategories(); runSearch(); });
for (const selector of ["#kind-filter", "#transport-filter", "#auth-filter"]) $(selector).addEventListener("change", runSearch);
$("#query").addEventListener("input", runSearch);
initialize();
