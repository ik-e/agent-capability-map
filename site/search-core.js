export function tokenize(value) {
  return (String(value ?? "").normalize("NFKC").toLocaleLowerCase().match(/[\p{L}\p{N}]+/gu) || []);
}

function termVariants(term) {
  const values = new Set([term]);
  const particles = ["으로", "에서", "에게", "한테", "부터", "까지", "처럼", "보다", "은", "는", "이", "가", "을", "를", "에", "의", "와", "과", "도", "로"];
  for (const suffix of particles) {
    if (term.endsWith(suffix) && term.length - suffix.length >= 2) values.add(term.slice(0, -suffix.length));
  }
  return [...values];
}

function hasTerm(fieldTokens, term) {
  return termVariants(term).some((variant) => fieldTokens.includes(variant));
}

function score(item, query) {
  const terms = tokenize(query);
  if (!terms.length) return 0;
  const normalizedQuery = terms.join(" ");
  if (tokenize(item.id).join(" ") === normalizedQuery) return 20;
  const idTerms = tokenize(item.id);
  if (idTerms[0] === "op") idTerms.shift();
  if (idTerms.join(" ") === normalizedQuery) return 20;
  const nameTokens = tokenize(item.name);
  const name = nameTokens.join(" ");
  const aliases = (item.aliases || []).map((value) => tokenize(value));
  const purpose = tokenize(item.purpose);
  const entities = (item.entity_types || []).flatMap(tokenize);
  const context = (item.binding_summaries || []).flatMap((binding) => [
    ...tokenize(binding.name), ...tokenize(binding.integration_name), ...tokenize(binding.service_name),
    ...tokenize(binding.provider_name), ...tokenize(binding.resource_kind), ...tokenize(binding.transport),
    ...binding.auth_schemes.flatMap(tokenize),
  ]).concat((item.category_labels || []).flatMap(tokenize));
  let total = name === normalizedQuery ? 10 : 0;
  let matchedTerms = 0;
  for (const term of new Set(terms)) {
    let termScore = 0;
    if (hasTerm(nameTokens, term)) termScore = Math.max(termScore, 5);
    if (aliases.some((alias) => hasTerm(alias, term))) termScore = Math.max(termScore, 4);
    if (hasTerm(purpose, term)) termScore = Math.max(termScore, 2);
    if (hasTerm(entities, term)) termScore = Math.max(termScore, 1);
    if (hasTerm(context, term)) termScore = Math.max(termScore, 2);
    if (termScore) matchedTerms += 1;
    total += termScore;
  }
  if (terms.length > 1 && matchedTerms < Math.min(2, new Set(terms).size)) return 0;
  return total;
}

function bindingVerdict(binding, filters, item) {
  let hasUnknown = false;
  for (const [field, expected] of Object.entries(filters)) {
    if (!expected) continue;
    if (field === "effect") {
      if (item.effect === "unknown") hasUnknown = true;
      else if (item.effect !== expected) return "violates";
      if (item.effect_evidence_state !== "verified") hasUnknown = true;
      continue;
    }
    const actual = binding[field];
    if (actual === "unknown" || (Array.isArray(actual) && actual.includes("unknown"))) {
      hasUnknown = true;
      continue;
    }
    if (Array.isArray(actual) ? !actual.includes(expected) : actual !== expected) return "violates";
    const claimPath = field === "resource_kind" ? "/resource_kind"
      : field === "status" ? "/status"
      : field === "transport" ? "/transport"
      : field === "auth_schemes" ? "/auth_schemes"
      : null;
    if (claimPath && binding.claim_states?.[claimPath] !== "verified") hasUnknown = true;
  }
  return hasUnknown ? "unknown" : "satisfies";
}

export function searchCatalog(items, query, filters = {}, category = "", limit = 5) {
  const candidates = [];
  for (const item of items) {
    if (category && !(item.category_ids || []).includes(category)) continue;
    const points = score(item, query);
    if (query && points <= 0) continue;
    const bindings = (item.binding_summaries || []).map((binding) => ({ binding, verdict: bindingVerdict(binding, filters, item) }));
    const passing = bindings.filter((row) => row.verdict === "satisfies");
    const possible = bindings.filter((row) => row.verdict !== "violates");
    if (Object.values(filters).some(Boolean) && !possible.length) continue;
    candidates.push({ item, points, bindings: passing.length ? passing : possible });
  }
  candidates.sort((a, b) => b.points - a.points || (a.item.id < b.item.id ? -1 : a.item.id > b.item.id ? 1 : 0));
  const boundedLimit = Math.min(20, Math.max(1, Number(limit) || 5));
  const results = candidates.slice(0, boundedLimit);
  return { abstain: results.length === 0, results };
}
