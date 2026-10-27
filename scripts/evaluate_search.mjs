import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { searchCatalog } from "../site/search-core.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const index = JSON.parse(fs.readFileSync(path.join(root, "site/catalog/v1/search/operations.json"), "utf8"));
const fixture = JSON.parse(fs.readFileSync(path.join(root, "evals/golden/queries.json"), "utf8"));
const limit = 5;
let positives = 0;
let relevantFound = 0;
let returned = 0;
let relevantReturned = 0;
let topOneCorrect = 0;
let noMatchCount = 0;
let noMatchAbstained = 0;
let hardConstraintQueries = 0;
let falsePasses = 0;
let bindingExpectedCount = 0;
let bindingCorrect = 0;
const rows = [];

for (const entry of fixture.queries) {
  const result = searchCatalog(index.items, entry.query, entry.filters || {}, "", limit);
  const ids = result.results.map((row) => row.item.id);
  const expected = entry.expected_ids || [];
  const expectedSet = new Set(expected);
  if (!entry.no_match) {
    positives += 1;
    relevantFound += ids.filter((id) => expectedSet.has(id)).length;
    relevantReturned += ids.filter((id) => expectedSet.has(id)).length;
    returned += ids.length;
    if (ids[0] && expectedSet.has(ids[0])) topOneCorrect += 1;
  } else {
    noMatchCount += 1;
    if (result.abstain && ids.length === 0) noMatchAbstained += 1;
  }
  if (Object.values(entry.filters || {}).some(Boolean)) {
    hardConstraintQueries += 1;
    for (const row of result.results) {
      const expectedBinding = entry.expected_bindings?.[row.item.id];
      const selected = row.bindings.some((item) => item.verdict === "satisfies" && (!expectedBinding || item.binding.id === expectedBinding));
      if (!selected) falsePasses += 1;
    }
  }
  for (const [operationId, bindingId] of Object.entries(entry.expected_bindings || {})) {
    if (!expectedSet.has(operationId)) continue;
    bindingExpectedCount += 1;
    const found = result.results.find((row) => row.item.id === operationId);
    if (found?.bindings.some((item) => item.binding.id === bindingId && item.verdict === "satisfies")) bindingCorrect += 1;
  }
  rows.push({ id: entry.id, expected_ids: expected, returned_ids: ids, abstain: result.abstain });
}

const report = {
  algorithm: index.algorithm,
  query_count: fixture.queries.length,
  positive_queries: positives,
  recall_at_5: positives ? relevantFound / fixture.queries.filter((entry) => !entry.no_match).reduce((sum, entry) => sum + (entry.expected_ids || []).length, 0) : 0,
  precision_at_5: returned ? relevantReturned / returned : 0,
  top_one_accuracy: positives ? topOneCorrect / positives : 0,
  binding_selection_rate: bindingExpectedCount ? bindingCorrect / bindingExpectedCount : 0,
  hard_constraint_queries: hardConstraintQueries,
  false_hard_constraint_passes: falsePasses,
  no_match_queries: noMatchCount,
  no_match_abstention_rate: noMatchCount ? noMatchAbstained / noMatchCount : 0,
  gates_evaluable: hardConstraintQueries >= fixture.gates.min_hard_constraint_queries && noMatchCount >= fixture.gates.min_no_match_queries,
  gates: fixture.gates,
  results: rows,
};
console.log(JSON.stringify(report, null, 2));

if (falsePasses > fixture.gates.false_hard_constraint_passes) process.exitCode = 1;
if (report.gates_evaluable) {
  if (report.recall_at_5 < fixture.gates.recall_at_5) process.exitCode = 1;
  if (report.no_match_abstention_rate < fixture.gates.no_match_abstention) process.exitCode = 1;
}
