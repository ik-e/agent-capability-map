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

// Independent check of whether a returned "satisfies" verdict is supported by
// both the Binding's raw values and verified field-level Evidence.
function independentlySatisfies(binding, item, filters) {
  for (const [field, expected] of Object.entries(filters)) {
    if (!expected) continue;
    if (field === "effect") {
      if (item.effect !== expected || item.effect_evidence_state !== "verified") return false;
      continue;
    }
    const actual = binding[field];
    const matches = Array.isArray(actual) ? actual.includes(expected) : actual === expected;
    if (!matches) return false;
    const claimPath = field === "resource_kind" ? "/resource_kind"
      : field === "status" ? "/status"
      : field === "transport" ? "/transport"
      : field === "auth_schemes" ? "/auth_schemes"
      : null;
    if (claimPath && binding.claim_states?.[claimPath] !== "verified") return false;
  }
  return true;
}

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
      for (const selected of row.bindings.filter((candidate) => candidate.verdict === "satisfies")) {
        if (!independentlySatisfies(selected.binding, row.item, entry.filters || {})) falsePasses += 1;
      }
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
report.gates_status = report.gates_evaluable ? "evaluated" : "not_evaluable";
console.log(JSON.stringify(report, null, 2));
if (!report.gates_evaluable) {
  console.warn(`WARNING: quality gates not evaluated (${hardConstraintQueries}/${fixture.gates.min_hard_constraint_queries} hard-constraint and ${noMatchCount}/${fixture.gates.min_no_match_queries} no-match queries). This run is a smoke check only.`);
}
if (process.env.GITHUB_STEP_SUMMARY) {
  const gateLabel = report.gates_evaluable ? "evaluated" : "not evaluable — smoke check only";
  const summary = [
    "### Search evaluation",
    "",
    `- Acceptance gates: **${gateLabel}**`,
    `- Hard-constraint fixtures: ${hardConstraintQueries}/${fixture.gates.min_hard_constraint_queries}`,
    `- No-match fixtures: ${noMatchCount}/${fixture.gates.min_no_match_queries}`,
    `- Recall@5: ${report.recall_at_5.toFixed(2)}; no-match abstention: ${report.no_match_abstention_rate.toFixed(2)}`,
    "",
  ].join("\n");
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, summary, "utf8");
}

if (falsePasses > fixture.gates.false_hard_constraint_passes) process.exitCode = 1;
if (report.gates_evaluable) {
  if (report.recall_at_5 < fixture.gates.recall_at_5) process.exitCode = 1;
  if (report.no_match_abstention_rate < fixture.gates.no_match_abstention) process.exitCode = 1;
}
