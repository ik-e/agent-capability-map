"""Freeze same-facts development inputs. Does not execute an agent or score it."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'site/catalog/v1'
def canonical(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def urls(value):
    if isinstance(value,dict): return set().union(*(urls(v) for v in value.values())) if value else set()
    if isinstance(value,list): return set().union(*(urls(v) for v in value)) if value else set()
    return {value} if isinstance(value,str) and value.startswith(('https://','http://')) else set()

def prepare():
    manifest=json.loads((CAT/'manifest.json').read_text(encoding='utf8'))
    records={}; routes=[]
    def read(kind,id):
        value=json.loads((CAT/kind/(id+'.json')).read_text(encoding='utf8'))
        records[id]=value
        return value
    for id in ('op_tavily_extract_url','op_get_github_repo_content'):
        operation=read('operations',id)
        for eid in operation['evidence_ids']: read('evidence',eid)
        for bid in operation['binding_ids']:
            binding=read('bindings',bid)
            for eid in binding['evidence_ids']: read('evidence',eid)
            routes.append({'operation_id':id,'binding_id':bid,
                           'evidence_ids':operation['evidence_ids']+binding['evidence_ids']})
    facts=[records[id] for id in sorted(records)]
    common='요청 계약의 필수조건을 항목별로 확인한다. 검색 필터 판정은 요청 전체 완료를 뜻하지 않는다. 실제 기록으로 판정을 뒷받침하고 미확인·충돌·차단·미실행을 구분한다.'
    # Both variants have the same policy and complete facts. Guidance contains only
    # already-present graph IDs, not task answers, extra URLs or external facts.
    facts_only={'condition':'facts','instructions':common,'facts':facts}
    guided={'condition':'facts-plus-navigation','instructions':common,'facts':facts,'navigation':routes}
    assert canonical(facts_only['facts'])==canonical(guided['facts'])
    assert urls(facts_only)==urls(guided)
    for route in routes:
        assert route['binding_id'] in records[route['operation_id']]['binding_ids']
        assert all(eid in records for eid in route['evidence_ids'])
    out=ROOT/'evals/runs'/('discovery-inputs-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    out.mkdir(parents=True)
    hashes={}
    for name,value in [('facts.json',facts_only),('guided.json',guided)]:
        raw=canonical(value);(out/name).write_bytes(raw);hashes[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
    task_raw=(ROOT/'evals/discovery-v1/tasks.json').read_bytes()
    (out/'tasks.json').write_bytes(task_raw)
    lock={'scope':'development packets only; no model trials performed','catalog_revision':manifest['catalog_revision'],
          'facts_identical':True,'url_sets_identical':True,'record_count':len(facts),
          'fact_sha256':hashlib.sha256(canonical(facts)).hexdigest(),'task_sha256':hashlib.sha256(task_raw).hexdigest(),
          'conditions':hashes,'all_packet_bytes_count_toward_model_input':True,
          'cost_of_navigation_preparation_and_maintenance':'record separately in future trials'}
    (out/'lock.json').write_text(json.dumps(lock,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'run':out.name,**lock},ensure_ascii=False,indent=2))

if __name__=='__main__': prepare()
