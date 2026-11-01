"""Exercise the real stdio boundary and official HTTPS sources; no model trial."""
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
from datetime import datetime, timezone
from discovery_contracts import adjudicate

ROOT=Path(__file__).resolve().parents[1]
def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out=ROOT/'evals/runs'/('discovery-live-'+stamp);out.mkdir(parents=True)
    args=[sys.executable,'-X','utf8',str(ROOT/'scripts/research_mcp.py'),'--log',str(out/'events.jsonl'),
          '--budget','8','--seconds','120','--hosts','open-meteo.com','geocoding-api.open-meteo.com']
    replies=queue.Queue()
    with (out/'stderr.log').open('w',encoding='utf8') as err:
        child=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,encoding='utf8')
        def read():
            for line in child.stdout:
                replies.put(json.loads(line))
        threading.Thread(target=read,daemon=True).start()
        sequence=0
        def rpc(method,params):
            nonlocal sequence
            sequence+=1;child.stdin.write(json.dumps({'jsonrpc':'2.0','id':sequence,'method':method,'params':params})+'\n');child.stdin.flush()
            response=replies.get(timeout=45)
            if response.get('id')!=sequence or 'error' in response: raise RuntimeError(str(response))
            return response['result']
        def batch(actions):
            result=rpc('tools/call',{'name':'research.batch','arguments':{'actions':actions}})
            return json.loads(result['content'][0]['text'])
        report={'scope':'real MCP and HTTPS calibration; not a model efficiency trial','run':out.name}
        try:
            rpc('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'preflight','version':'1'}})
            report['mcp_tool_names']=[t['name'] for t in rpc('tools/list',{})['tools']]
            first=batch([{'kind':'open','url':'https://open-meteo.com/en/docs/geocoding-api'},
                         {'kind':'open','url':'https://geocoding-api.open-meteo.com/v1/search?name=Seoul&count=1&countryCode=KR'}])
            report['official_reads']=[{'event_id':r['event_id'],'status':r['status'],'http_status':r.get('result',{}).get('status_code'),
                                      'response_sha256':r.get('response_sha256')} for r in first['results']]
            if any(r['status']!='ok' for r in first['results']):
                report['live_fetch']='blocked'
            else:
                docs=first['results'][0]['result'];sample=json.loads(first['results'][1]['result']['text'])
                found=batch([{'kind':'find','document_id':docs['document_id'],'pattern':'apikey'}])
                report['find_apikey_matches']=len(found['results'][0].get('result',{}).get('matches',[]))
                report['sample_coordinate_observed']=any(isinstance(v.get('latitude'),(float,int)) and isinstance(v.get('longitude'),(float,int)) for v in sample.get('results',[]))
                if docs['links']:
                    clicked=batch([{'kind':'click','link_id':docs['links'][0]['link_id']}])
                    report['click_status']=clicked['results'][0]['status']
                report['live_fetch']='passed' if report['sample_coordinate_observed'] and report['find_apikey_matches'] else 'failed'
            # No key is printed or written. Search is not silently replaced by another provider.
            if os.environ.get('TAVILY_API_KEY'):
                search=batch([{'kind':'query','query':'site:open-meteo.com geocoding API documentation'}])
                report['live_search']='passed' if search['results'][0]['status']=='ok' else 'blocked'
            else:
                report['live_search']='blocked: no configured search provider key'
        except Exception as error:
            report['error_type']=type(error).__name__
        finally:
            child.stdin.close()
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: child.kill();child.wait()
    events=[json.loads(l) for l in (out/'events.jsonl').read_text(encoding='utf8').splitlines()]
    starts=[e for e in events if e['event']=='action_started'];ends=[e for e in events if e['event']=='action_finished']
    report['atomic_actions']=len(starts)
    report['all_started_actions_finished']=set(e['event_id'] for e in starts)==set(e['event_id'] for e in ends)
    report['response_hashes_match']=all(hashlib.sha256((out/e['response_artifact']).read_bytes()).hexdigest()==e['response_sha256'] for e in ends if e['status']=='ok')
    if report.get('live_fetch')=='passed':
        # Controller checks a narrow, observable requirement, not general POI quality.
        sample_row=first['results'][1]
        source=next(e for e in ends if e['event_id']==sample_row['event_id'])
        assessed_at=datetime.now(timezone.utc).isoformat()
        stop={'event':'stop','event_id':'controller-stop','kind':'stop','status':'ok','reason':'requirements_met','at':assessed_at}
        with (out/'events.jsonl').open('a',encoding='utf8') as stream: stream.write(json.dumps(stop)+'\n')
        task={'version':'discovery-eval-v1','task_id':'live-coordinate-probe','as_of':assessed_at,'verification_level':'live_response',
              'request':'알려진 공개 API에서 좌표가 있는 응답을 실제로 수신했는지만 확인한다.',
              'requirements':[{'id':'coordinates','statement':'JSON 후보에 숫자형 위경도가 있다.','stage':'live_response',
                'evidence_types':['provider_response'],'max_age_days':1,'on_unknown':'block','on_conflict':'block'}],
              'preferences':[],'comparison_scope':{'candidate_limit':1,'notes':'사전 지정 API의 연결 보정. 검색·정확도·OD 대응 시험 아님.'},
              'budget':{'external_actions':8,'max_seconds':120},'stop_rules':{'required_ids':['coordinates'],'allow_unverified_preferences':True}}
        result={'version':'discovery-eval-v1','task_id':task['task_id'],'selected_candidate_id':'open-meteo-geocoding',
                'checks':[{'candidate_id':'open-meteo-geocoding','requirement_id':'coordinates','verdict':'satisfied','evidence_ids':['response']}],
                'evidence':[{'id':'response','type':'provider_response','url':source['source_url'],'observed_at':source['at'],
                             'subject_id':'open-meteo-geocoding','requirement_ids':['coordinates'],'source_event_id':source['event_id']}],
                'evaluated_requirement_ids':['coordinates'],'unchecked_requirement_ids':[],
                'stages':{'candidate':'passed','documentation':'not_run','live_response':'passed','task':'not_run'},
                'stop_reason':'requirements_met','stop_event_id':'controller-stop'}
        report['read_only_response_contract']=adjudicate(task,result,ends+[stop])
        for name,value in [('probe-task.json',task),('probe-result.json',result)]:
            (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report['comparison_gate']='ready' if report.get('live_fetch')=='passed' and report.get('live_search')=='passed' and report['all_started_actions_finished'] and report['response_hashes_match'] else 'blocked'
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
