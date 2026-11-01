"""Erratum: CLI web events can collapse batches; atomic call counts are unknown."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'evals/runs/r0-2026-11-01-v2'
rows = []
for folder in sorted(RUN.glob('[0-9][0-9]-*')):
    metrics = json.loads((folder / 'metrics.json').read_text(encoding='utf8'))
    answer = json.loads((folder / 'answer.json').read_text(encoding='utf8'))
    lower = 0
    collapsed = []
    for line in (folder / 'events.jsonl').read_text(encoding='utf8').splitlines():
        event = json.loads(line)
        item = event.get('item', {})
        if event.get('type') != 'item.completed' or item.get('type') != 'web_search':
            continue
        action = item.get('action', {})
        lower += len(action.get('queries') or [action.get('query', '')]) if action.get('type') == 'search' else 1
        if action.get('type') == 'other' or (action.get('type') != 'search' and len(item.get('results', [])) > 1):
            collapsed.append({'item_id': item.get('id'), 'summary_action': action,
                              'result_count': len(item.get('results', []))})
    rows.append({'run': folder.name, 'task_id': metrics['task_id'], 'condition': metrics['condition'],
                 'summary_action_lower_bound': lower,
                 'exact_atomic_external_calls': None,
                 'self_reported_external_calls': answer['self_reported_external_calls'],
                 'collapsed_batch_evidence': collapsed,
                 'budget_verdict': 'not_independently_verifiable_from_complete_atomic_arguments'})
report = {'supersedes': 'runtime-summary over_web_budget=False and protocol-review budget-pass wording',
          'reason': 'Completed CLI web_search events can expose only the first action of a batch or type=other. Counting each as one undercounts atomic URL reads/finds. Search-result rows are not a safe replacement for raw request arguments.',
          'scope': 'Elapsed time, CLI usage, frozen outputs, unique contexts and schema checks unaffected. No claim of fully audited 20-atomic-call compliance. Raw locked results retained.',
          'runs': rows}
(RUN / 'budget-audit-erratum.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'runs': len(rows), 'runs_with_visible_collapsed_batches': sum(bool(r['collapsed_batch_evidence']) for r in rows), 'exact_budget_compliance': 'not_independently_verified'}, indent=2))
