"""Export observable counters and citation integrity, not an automatic truth score."""
import hashlib
import json
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--run-dir',type=Path,default=ROOT/'evals/runs/meta-first-comparison-2026-11-03')
p.add_argument('--output',type=Path,default=ROOT/'evals/meta-first-v1/comparison-summary-2026-11-03.json')
args=p.parse_args()
RUN=args.run_dir.resolve()
if not RUN.is_relative_to((ROOT/'evals/runs').resolve()):raise ValueError('Run outside ignored run directory')
lock=json.loads((RUN/'lock.json').read_text(encoding='utf8'))
trials=[]
for folder in sorted(RUN.glob('[0-9][0-9]-*')):
    if not (folder/'metrics.json').exists(): continue
    metrics=json.loads((folder/'metrics.json').read_text(encoding='utf8'))
    cli=[json.loads(l) for l in (folder/'cli.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
    research=[json.loads(l) for l in (folder/'research.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
    starts={e['event_id']:e for e in research if e['event']=='action_started'}
    ends={e['event_id']:e for e in research if e['event']=='action_finished'}
    answer=json.loads((folder/'answer.json').read_text(encoding='utf8')) if metrics['answer_exists'] else {}
    bad=[]
    for claim in answer.get('claims',[]):
        event=ends.get(claim['event_id'])
        if not event or event['status']!='ok': bad.append('unobserved event');continue
        if event.get('source_url')!=claim['source_url']: bad.append('source mismatch');continue
        artifact=folder/event['response_artifact']
        if hashlib.sha256(artifact.read_bytes()).hexdigest()!=event['response_sha256']:bad.append('artifact mismatch')
    tools=[e['item'] for e in cli if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='mcp_tool_call']
    catalog=[json.loads(l) for l in (folder/'catalog-access.jsonl').read_text(encoding='utf8').splitlines()] if (folder/'catalog-access.jsonl').exists() else []
    usage=metrics.get('usage') or {}
    trials.append({**metrics,'uncached_input_tokens':usage.get('input_tokens',0)-usage.get('cached_input_tokens',0),
        'mcp_research_requests':sum(e.get('server')=='research' for e in tools),
        'failed_research_mcp_requests':sum(e.get('server')=='research' and e.get('status')=='failed' for e in tools),
        'catalog_requests':len(catalog),'catalog_response_bytes':sum(e['response_bytes'] for e in catalog),
        'selected_direct_resource_detail_reads':sum(e['tool']=='catalog.detail' and e.get('args',{}).get('id')=='res_seoul_bike_station_master' for e in catalog),
        'all_started_actions_finished':set(starts)==set(ends),
        'within_action_budget':len(starts)<=lock['atomic_actions_per_trial'],
        'citation_integrity_errors':bad,'claim_count':len(answer.get('claims',[])),
        'actual_execution':answer.get('execution'),'semantic_support':'Reference integrity only; semantic source review is recorded separately in the report'})
result={'version':lock['version'],'catalog_revision':lock['working_tree_catalog_revision'],
    'protocol_sha256':lock['protocol_sha256'],'portal_preflight':lock['portal_preflight'],
    'trial_count':len(trials),'trials':trials,
    'scope':lock['scope'],
    'first_valid_candidate_time':'not observed',
    'registration_and_maintenance_cost':'incomplete measurement; no total-cost or long-term break-even conclusion',
    'statistical_gate':'not evaluated; one run per task and condition'}
out=args.output
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
