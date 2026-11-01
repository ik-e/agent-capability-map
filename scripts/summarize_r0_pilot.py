"""Summarize observed runtime metrics without auto-grading source correctness."""
import json
import argparse
from pathlib import Path
from statistics import median
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='r0-2026-11-01-v2');args=parser.parse_args()
if not args.run_id.replace('-','').isalnum():raise ValueError('Invalid run ID')
RUN=ROOT/'evals/runs'/args.run_id
lock=json.loads((RUN/'lock.json').read_text(encoding='utf8'))
rows=[]
for folder in sorted(RUN.glob('[0-9][0-9]-*')):
 if not (folder/'metrics.json').exists():continue
 row=json.loads((folder/'metrics.json').read_text(encoding='utf8'))
 opened=set(); searches=0; web_events=0; shell_events=0; budget_units=0; actions=[]
 for line in (folder/'events.jsonl').read_text(encoding='utf8').splitlines():
  try:event=json.loads(line)
  except ValueError:continue
  if event.get('type')!='item.completed':continue
  item=event.get('item',{})
  if item.get('type')=='command_execution':shell_events+=1
  if item.get('type')!='web_search':continue
  web_events+=1; action=item.get('action',{}); kind=action.get('type')
  if kind=='search':
   count=len(action.get('queries') or [action.get('query','')]); searches+=count;budget_units+=count
  elif kind=='open_page':
   budget_units+=1
   if action.get('url','').startswith('http'):opened.add(action['url'])
  elif kind in ('find_in_page','click'):budget_units+=1
  else:budget_units+=1
  actions.append(action)
 row.update({'web_tool_events':web_events,'search_queries':searches,'observed_web_budget_units':budget_units,'shell_events':shell_events,'opened_urls':sorted(opened),'web_actions':actions,'over_web_budget':budget_units>lock['external_calls_per_run'],'first_valid_candidate_seconds':None,'first_valid_candidate_timing_status':'not_observed','correctness_status':'not_yet_adjudicated'})
 row.update({'web_budget_units_scope':'lower bound from CLI action summaries, not exact atomic batch arguments','exact_atomic_external_calls':None,'budget_compliance_status':'not_independently_verified; over_web_budget=False does not establish compliance'})
 access_path=folder/'catalog-access.jsonl'
 accesses=[json.loads(line) for line in access_path.read_text(encoding='utf8').splitlines() if line.strip()] if access_path.exists() else []
 row.update({'catalog_tool_calls':len(accesses),'catalog_response_bytes':sum(a.get('response_bytes',0) for a in accesses),'catalog_failed_calls':sum(bool(a.get('failed')) for a in accesses)})
 if (folder/'answer.json').exists():
  try:row['answer']=json.loads((folder/'answer.json').read_text(encoding='utf8'))
  except ValueError:row['answer_error']='invalid_json'
 rows.append(row)
groups={}
for c in lock['conditions']:
 subset=[r for r in rows if r['condition']==c]
 observed=[r['usage'] for r in subset if r.get('usage') is not None]
 groups[c]={'runs':len(subset),'median_elapsed_seconds':median([r['elapsed_seconds'] for r in subset]) if subset else None,'model_input_tokens_sum':sum(u.get('input_tokens',0) for u in observed) if observed else None,'cached_input_tokens_sum':sum(u.get('cached_input_tokens',0) for u in observed) if observed else None,'uncached_input_tokens_sum':sum(u.get('input_tokens',0)-u.get('cached_input_tokens',0) for u in observed) if observed else None,'model_output_tokens_sum':sum(u.get('output_tokens',0) for u in observed) if observed else None,'usage_observed_runs':len(observed),'over_budget_runs':sum(r['over_web_budget'] for r in subset),'catalog_tool_calls':sum(r['catalog_tool_calls'] for r in subset),'catalog_response_bytes':sum(r['catalog_response_bytes'] for r in subset)}
report={'scope':'exploratory runtime audit; no automatic correctness or causal efficiency claim; external atomic budget not independently verified','catalog_revision':lock['catalog_revision'],'planned_runs':len(lock['schedule']),'finished_runs':len(rows),'visual_ui':'not_observed','conditions':groups,'runs':rows}
(RUN/'runtime-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='runs'},ensure_ascii=False,indent=2))
