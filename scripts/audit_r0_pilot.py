"""Audit isolation/protocol adherence; source correctness still needs adjudication."""
import json
import argparse
import hashlib
from pathlib import Path
from urllib.parse import urlparse
from jsonschema import validate
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='r0-2026-11-01-v2');args=parser.parse_args()
if not args.run_id.replace('-','').isalnum():raise ValueError('Invalid run ID')
RUN=ROOT/'evals/runs'/args.run_id
schema=json.loads((RUN/'result.schema.json').read_text(encoding='utf8'))
lock=json.loads((RUN/'lock.json').read_text(encoding='utf8'))
input_checks={relative:hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==value for relative,value in lock['input_hashes'].items()}
snapshot_checks={relative:hashlib.sha256((RUN/relative).read_bytes()).hexdigest()==value for relative,value in lock['snapshot_hashes'].items()}
if lock.get('input_hashes_adapter'):
 input_checks['scripts/pilot_catalog_mcp.mjs']=hashlib.sha256((ROOT/'scripts/pilot_catalog_mcp.mjs').read_bytes()).hexdigest()==lock['input_hashes_adapter']
rows=[]; thread_ids=[]
for folder in sorted(RUN.glob('[0-9][0-9]-*')):
 if not (folder/'metrics.json').exists():continue
 metrics=json.loads((folder/'metrics.json').read_text(encoding='utf8')); flags=[]; tools=[]; map_exposure=[]
 for line in (folder/'events.jsonl').read_text(encoding='utf8').splitlines():
  try:event=json.loads(line)
  except ValueError:continue
  if event.get('type')=='thread.started':thread_ids.append(event.get('thread_id'))
  if event.get('type')=='item.completed' and event.get('item',{}).get('type') in ('web_search','command_execution','mcp_tool_call'):
   tools.append(event['item'])
   if metrics['condition']!='catalog-first':
    text=json.dumps(event['item'],ensure_ascii=False)
    if 'ik-e.github.io/agent-capability-map' in text or 'github.com/ik-e/agent-capability-map' in text:map_exposure.append(event['item']['id'])
 answer=None
 if (folder/'answer.json').exists():
  try:
   answer=json.loads((folder/'answer.json').read_text(encoding='utf8'));validate(answer,schema)
  except Exception as e:flags.append('invalid_result_schema: '+str(e)[:200])
 else:flags.append('missing_answer')
 if answer:
  if answer['task_id']!=metrics['task_id'] or answer['condition']!=metrics['condition']:flags.append('wrong_trial_identity')
  if answer['catalog_contamination'] or map_exposure:flags.append('catalog_exposure_or_contamination')
  if metrics['task_id']=='building-occupancy-abstain' and answer['outcome']=='found':flags.append('check_false_precision')
 if tools:
  first=tools[0]
  if metrics['condition']=='web-first' and first.get('action',{}).get('type')!='search':flags.append('check_startpoint_web')
  if metrics['condition']=='directory-first':
   action=first.get('action',{}); host=urlparse(action.get('url','')).hostname
   if action.get('type')!='open_page' or host not in ('data.seoul.go.kr','www.data.go.kr','pypi.org','open-meteo.com'):flags.append('check_startpoint_directory')
  if metrics['condition']=='catalog-first' and not (first.get('type')=='mcp_tool_call' and first.get('tool')=='catalog.manifest'):flags.append('check_startpoint_catalog')
 rows.append({'run':folder.name,'task_id':metrics['task_id'],'condition':metrics['condition'],'outcome':answer.get('outcome') if answer else None,'flags':flags,'first_tool':tools[0] if tools else None,'map_exposure_items':map_exposure,'correctness':'pending_manual_source_adjudication'})
report={'completed':len(rows),'frozen_inputs_still_match':all(input_checks.values()) and all(snapshot_checks.values()),'input_checks':input_checks,'snapshot_checks':snapshot_checks,'unique_thread_count':len(set(thread_ids)),'thread_count':len(thread_ids),'all_threads_unique':len(set(thread_ids))==len(thread_ids),'exposure_audit_scope':'logged tool actions and model self-report; search-result content is not fully captured, so no guarantee of zero incidental exposure','runs':rows}
(RUN/'protocol-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'completed':len(rows),'all_threads_unique':report['all_threads_unique'],'flagged':[{'run':r['run'],'flags':r['flags']} for r in rows if r['flags']]},ensure_ascii=False,indent=2))
