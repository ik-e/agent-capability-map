"""Write the versioned preflight schemas and three development tasks."""
import json
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'evals/discovery-v1'
OUT.mkdir(parents=True,exist_ok=True)
def obj(properties, required=None):
    return {'type':'object','additionalProperties':False,'properties':properties,'required':required or list(properties)}
def arr(items, **kw): return {'type':'array','items':items,**kw}
def enum(values): return {'type':'string','enum':values}
S={'type':'string','minLength':1}
stages=['candidate','documentation','live_response','task']
types=['official_document','provider_response','execution_result']
requirement=obj({'id':S,'statement':S,'stage':enum(stages),'evidence_types':arr(enum(types),minItems=1,uniqueItems=True),
                 'max_age_days':{'type':'integer','minimum':0},'version':S,'on_unknown':{'const':'block'},'on_conflict':{'const':'block'}},
                ['id','statement','stage','evidence_types','on_unknown','on_conflict'])
task=obj({'version':{'const':'discovery-eval-v1'},'task_id':S,'as_of':{'type':'string','format':'date-time'},
          'verification_level':enum(stages),'request':S,'requirements':arr(requirement,minItems=1),
          'preferences':arr(obj({'id':S,'statement':S,'priority':{'type':'integer','minimum':1}})),
          'comparison_scope':obj({'candidate_limit':{'type':'integer','minimum':1},'notes':S}),
          'budget':obj({'external_actions':{'type':'integer','minimum':1},'max_seconds':{'type':'integer','minimum':1}}),
          'stop_rules':obj({'required_ids':arr(S,minItems=1,uniqueItems=True),'allow_unverified_preferences':{'const':True}})})
evidence=obj({'id':S,'type':enum(types),'url':{'type':'string','format':'uri'},'observed_at':{'type':'string','format':'date-time'},
              'subject_id':S,'version':S,'requirement_ids':arr(S,minItems=1,uniqueItems=True),'source_event_id':S},
             ['id','type','url','observed_at','subject_id','requirement_ids','source_event_id'])
result=obj({'version':{'const':'discovery-eval-v1'},'task_id':S,'selected_candidate_id':{'type':['string','null']},
            'checks':arr(obj({'candidate_id':S,'requirement_id':S,'verdict':enum(['satisfied','violated','unknown','conflicted']),
                              'evidence_ids':arr(S,uniqueItems=True)})),
            'evidence':arr(evidence),'evaluated_requirement_ids':arr(S,uniqueItems=True),'unchecked_requirement_ids':arr(S,uniqueItems=True),
            'stages':obj({s:enum(['passed','failed','blocked','not_run']) for s in stages}),
            'stop_reason':enum(['requirements_met','evidence_insufficient','evidence_conflict','access_blocked','budget_exhausted','no_candidate_in_scope']),
            'stop_event_id':S})
for name,value in [('task.schema.json',task),('result.schema.json',result)]:
    value={'$schema':'https://json-schema.org/draft/2020-12/schema',**value}
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def rule(id,statement,stage='documentation',**extras):
    return {'id':id,'statement':statement,'stage':stage,'evidence_types':['official_document'],
            'on_unknown':'block','on_conflict':'block',**extras}
tasks=[]
for task_id,request,rules in [
    ('url-extraction-candidate','공개 URL 본문을 Markdown으로 읽는 후보를 공식 문서에서 찾는다. 실제 실행 성공은 주장하지 않는다.',
     [rule('capability','공식 문서가 공개 URL 본문 추출을 설명한다.','candidate'),rule('format','공식 문서가 Markdown 출력을 설명한다.','candidate')]),
    ('url-extraction-no-auth','공개 URL 본문을 Markdown으로 읽고 API 키 없이 이용할 수 있는 후보를 문서로 선택한다.',
     [rule('capability','공개 URL 본문의 Markdown 추출이 공식 문서로 확인된다.'),rule('no_auth','지정한 공용 서비스의 무인증 이용 조건이 확인된다.')]),
    ('seoul-st-mapping','서울 OD의 ST-* ID를 공식 좌표에 대응할 문서 근거를 확인한다. 접미사·이름 매칭과 실제 조인 성공 주장을 금지한다.',
     [rule('namespace','OD와 대여소 좌표의 동일 식별자 또는 공식 대응 근거'),rule('temporal','OD와 좌표의 유효 시점 호환'),rule('crs','대여소 원좌표계의 공식 근거')]),
]:
    level='candidate' if task_id=='url-extraction-candidate' else 'documentation'
    tasks.append({'version':'discovery-eval-v1','task_id':task_id,'as_of':'2026-11-01T12:00:00Z',
        'verification_level':level,'request':request,'requirements':rules,
        'preferences':[{'id':'simple','statement':'조건을 충족하면 연결이 단순한 후보를 선호','priority':1}],
        'comparison_scope':{'candidate_limit':3,'notes':'개발용 세 종류. 독립 holdout이 아니며 실제 연결·조인은 별도 과제.'},
        'budget':{'external_actions':12,'max_seconds':300},
        'stop_rules':{'required_ids':[r['id'] for r in rules],'allow_unverified_preferences':True}})
(OUT/'tasks.json').write_text(json.dumps({'scope':'development only; not executed model trials','tasks':tasks},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Wrote versioned task/result contracts and three development tasks.')
