export function tokenize(value) {
  return (String(value ?? "").normalize("NFKC").toLocaleLowerCase().match(/[\p{L}\p{N}]+/gu) || []);
}

function score(item, query) {
  const terms = tokenize(query);
  if (!terms.length) return 0;
  const nameTokens = tokenize(item.name);
  const name = nameTokens.join(" ");
  const aliases = (item.aliases || []).map((value) => tokenize(value));
  const purpose = tokenize(item.purpose);
  const entities = (item.entity_types || []).flatMap(tokenize);
  let total = name === terms.join(" ") ? 10 : 0;
  for (const term of new Set(terms)) {
    if (nameTokens.includes(term)) total += 5;
    if (aliases.some((alias) => alias.includes(term))) total += 4;
    if (purpose.includes(term)) total += 2;
    if (entities.includes(term)) total += 1;
  }
  return total;
}

function bindingVerdict(binding, filters, item) {
  let hasUnknown = false;
  for (const [field, expected] of Object.entries(filters)) {
    if (!expected) continue;
    if (field === "effect") {
      if (item.effect === "unknown") hasUnknown = true;
      else if (item.effect !== expected) return "violates";
      continue;
    }
    const actual = binding[field];
    if (actual === "unknown" || (Array.isArray(actual) && actual.includes("unknown"))) {
      hasUnknown = true;
      continue;
    }
    if (Array.isArray(actual) ? !actual.includes(expected) : actual !== expected) return "violates";
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
    if (Object.values(filters).some(Boolean) && !passing.length) continue;
    candidates.push({ item, points, bindings: passing.length ? passing : bindings });
  }
  candidates.sort((a, b) => b.points - a.points || (a.item.id < b.item.id ? -1 : a.item.id > b.item.id ? 1 : 0));
  const boundedLimit = Math.min(20, Math.max(1, Number(limit) || 5));
  const results = candidates.slice(0, boundedLimit);
  return { abstain: results.length === 0, results };
}
