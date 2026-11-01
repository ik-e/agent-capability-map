"""Export public metrics without raw conversations, trial answers or local paths."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'evals/runs/r0-2026-11-01-v2'
result_lock = json.loads((RUN / 'results-lock.json').read_text(encoding='utf8'))
for relative, expected in result_lock['files'].items():
    assert hashlib.sha256((RUN / relative).read_bytes()).hexdigest() == expected, relative
summary = json.loads((RUN / 'runtime-summary.json').read_text(encoding='utf8'))
protocol = json.loads((RUN / 'lock.json').read_text(encoding='utf8'))
erratum = json.loads((RUN / 'budget-audit-erratum.json').read_text(encoding='utf8'))
rows = []
for row in summary['runs']:
    usage = row['usage']
    rows.append({key: row[key] for key in ('task_id', 'condition', 'elapsed_seconds', 'catalog_tool_calls', 'catalog_response_bytes')} | {
        'input_tokens': usage['input_tokens'], 'cached_input_tokens': usage['cached_input_tokens'],
        'uncached_input_tokens': usage['input_tokens'] - usage['cached_input_tokens'],
        'output_tokens': usage['output_tokens'],
        'model_reported_outcome': row['answer']['outcome'],
        'first_discovery_route_self_reported': row['answer']['first_discovery_route'],
        'self_reported_external_calls': row['answer']['self_reported_external_calls'],
        'exact_atomic_external_calls': None,
        'quality_score': None,
    })
conditions = {c: {k: v for k, v in g.items() if k != 'over_budget_runs'} for c, g in summary['conditions'].items()}
public = {
    'date': '2026-11-01', 'scope': 'single-model exploratory R0 discovery pilot; not a performance pass',
    'catalog_revision': summary['catalog_revision'], 'model': protocol['model'], 'reasoning': protocol['reasoning'],
    'model_backend_revision': 'not_observed', 'tasks': 6, 'conditions': 3, 'repetitions': 1,
    'protocol_sha256': hashlib.sha256((RUN / 'lock.json').read_bytes()).hexdigest(),
    'results_lock_sha256': hashlib.sha256((RUN / 'results-lock.json').read_bytes()).hexdigest(),
    'runtime_v1_excluded': True, 'r1_executed': False, 'holdout_created': False,
    'visual_ui': 'not_observed', 'first_valid_candidate_seconds': None,
    'external_atomic_budget': '20 instructed; exact compliance not independently verified; CLI batches collapse arguments',
    'budget_erratum_sha256': hashlib.sha256((RUN / 'budget-audit-erratum.json').read_bytes()).hexdigest(),
    'token_scope': 'CLI-reported model usage; cached and uncached separate; no billing-cost claim',
    'total_pilot_cost_including_setup_postflight_and_reviews': None,
    'conditions': conditions, 'runs': rows,
}
target = ROOT / 'evals/pilot/r0-v2-summary.json'
target.write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print('Public export verifies all locked result files.')
for task in protocol['tasks']:
    selected = [r for r in rows if r['task_id'] == task['id']]
    print(task['id'], ' | '.join(f"{r['condition']}: {r['elapsed_seconds']:.3f}s / {r['uncached_input_tokens']:,} uncached / {r['output_tokens']:,} output" for r in selected))
