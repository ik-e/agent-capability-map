"""Behavioral preflight: metering failures and false completion must be caught."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from discovery_contracts import ROOT, validate_task, adjudicate, first_valid_assessment
from research_runtime import ResearchRuntime

class MeteringTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
    def runtime(self,budget=10,backend=None):
        return ResearchRuntime(Path(self.tmp.name)/'events.jsonl',budget,[],backend=backend or (lambda action,eid:{'ok':True}))
    def events(self,r): return [json.loads(v) for v in r.log.read_text(encoding='utf8').splitlines()]
    def test_batch_records_five_distinct_actions(self):
        r=self.runtime()
        out=r.execute_batch([{'kind':'query','query':'one'},{'kind':'query','query':'two'},
          {'kind':'open','url':'https://example.org/a'},{'kind':'open','url':'https://example.org/b'},
          {'kind':'find','document_id':'mock','pattern':'term'}])
        self.assertEqual(r.used,5); self.assertEqual(len(out['results']),5)
        self.assertEqual(len({v['event_id'] for v in out['results']}),5)
        self.assertEqual(len([e for e in self.events(r) if e['event']=='action_started']),5)
        for row in out['results']:
            self.assertTrue((r.log.parent/row['response_artifact']).exists())
            self.assertIn('response_sha256',row)
    def test_failures_timeout_and_retry_are_counted(self):
        calls=[]
        def backend(action,eid):
            calls.append(action['query'])
            if action['query']=='failure': raise OSError('not recorded in public log')
            if action['query']=='timeout': raise TimeoutError()
            return {'ok':True}
        r=self.runtime(backend=backend)
        out=r.execute_batch([{'kind':'query','query':x} for x in ('ok','failure','timeout')])
        self.assertEqual([v['status'] for v in out['results']],['ok','error','timeout'])
        prior=out['results'][1]['event_id']
        r.execute_batch([{'kind':'query','query':'failure','retry_of':prior}])
        self.assertEqual(r.used,4); self.assertEqual(len(calls),4)
    def test_over_budget_batch_executes_nothing(self):
        calls=[];r=self.runtime(2,lambda a,e:calls.append(a))
        out=r.execute_batch([{'kind':'query','query':str(i)} for i in range(3)])
        self.assertEqual(out['status'],'rejected'); self.assertEqual(r.used,0); self.assertEqual(calls,[])
    def test_invalid_retry_and_existing_log_rejected(self):
        r=self.runtime()
        with self.assertRaises(ValueError): r.execute_batch([{'kind':'query','query':'x','retry_of':'missing'}])
        with self.assertRaises(ValueError): ResearchRuntime(r.log,2,[])
    def test_private_and_unlisted_urls_rejected(self):
        r=self.runtime();r.backend=None
        for url in ('http://example.org','https://127.0.0.1','https://user:pass@example.org','https://example.org:8443'):
            with self.assertRaises(ValueError): r.check_url(url)
        r.hosts={'127.0.0.1'}
        with self.assertRaises(ValueError): r.check_url('https://127.0.0.1')
    def test_time_expiry_rejects_or_explicitly_interrupts_batch(self):
        r=self.runtime();r.deadline=0
        self.assertEqual(r.execute_batch([{'kind':'query','query':'x'}])['reason'],'time_exhausted')
        self.assertEqual(r.used,0)
    def test_partial_batch_on_time_expiry_is_never_silent(self):
        def backend(action,eid):
            r.deadline=0
            return {'ok':True}
        r=self.runtime(backend=backend)
        out=r.execute_batch([{'kind':'query','query':'x'},{'kind':'query','query':'y'}])
        self.assertEqual(out['status'],'interrupted');self.assertEqual(out['not_run'],1);self.assertEqual(r.used,1)
    def test_find_offsets_refer_to_original_unicode_text(self):
        r=self.runtime();r.backend=None
        text='Straße TOKEN 문서'
        r.documents['doc']={'text':text,'url':'https://example.org','source_event_id':'original'}
        out=r.execute_batch([{'kind':'find','document_id':'doc','pattern':'token'}])
        self.assertEqual(out['results'][0]['result']['matches'][0]['offset'],text.index('TOKEN'))

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.task=json.loads((ROOT/'evals/discovery-v1/tasks.json').read_text(encoding='utf8'))['tasks'][1]
        self.events=[{'event_id':'response','kind':'open','status':'ok','response_sha256':'fixture','source_url':'https://example.org/docs','at':'2026-11-01T11:00:00Z'},
                     {'event_id':'end','kind':'stop','status':'ok','reason':'requirements_met','at':'2026-11-01T11:01:00Z'}]
        self.result={'version':'discovery-eval-v1','task_id':self.task['task_id'],'selected_candidate_id':'binding-a',
          'checks':[{'candidate_id':'binding-a','requirement_id':r['id'],'verdict':'satisfied','evidence_ids':['e']} for r in self.task['requirements']],
          'evidence':[{'id':'e','type':'official_document','url':'https://example.org/docs','observed_at':'2026-11-01T11:00:00Z',
                       'subject_id':'binding-a','requirement_ids':['capability','no_auth'],'source_event_id':'response'}],
          'evaluated_requirement_ids':['capability','no_auth'],'unchecked_requirement_ids':[],
          'stages':{'candidate':'passed','documentation':'passed','live_response':'not_run','task':'not_run'},
          'stop_reason':'requirements_met','stop_event_id':'end'}
    def test_development_tasks_are_valid(self):
        for t in json.loads((ROOT/'evals/discovery-v1/tasks.json').read_text(encoding='utf8'))['tasks']: validate_task(t)
    def test_documented_selection_does_not_claim_execution(self):
        out=adjudicate(self.task,self.result,self.events)
        self.assertTrue(out['completed_at_requested_level'])
        self.assertEqual(out['factual_support'],'requires_separate_source_adjudication')
    def test_unknown_mandatory_condition_cannot_complete(self):
        self.result['checks'][1].update(verdict='unknown',evidence_ids=[])
        with self.assertRaises(ValueError): adjudicate(self.task,self.result,self.events)
    def test_search_satisfaction_does_not_cover_unchecked_commercial_scope(self):
        rule=copy.deepcopy(self.task['requirements'][1]);rule.update(id='commercial',statement='상업 이용 조건 확인')
        self.task['requirements'].append(rule);self.task['stop_rules']['required_ids'].append('commercial')
        self.result['unchecked_requirement_ids']=['commercial']
        with self.assertRaises(ValueError): adjudicate(self.task,self.result,self.events)
    def test_supported_abstentions_remain_incomplete(self):
        for verdict,reason in [('unknown','evidence_insufficient'),('conflicted','evidence_conflict'),
                               ('unknown','access_blocked'),('unknown','budget_exhausted')]:
            r=copy.deepcopy(self.result); e=copy.deepcopy(self.events)
            r['checks'][1].update(verdict=verdict,evidence_ids=[])
            r['stages']['documentation']='blocked'; r['stop_reason']=reason; e[-1]['reason']=reason
            self.assertFalse(adjudicate(self.task,r,e)['completed_at_requested_level'])
    def test_empty_candidate_scope_is_not_global_absence(self):
        r=copy.deepcopy(self.result);e=copy.deepcopy(self.events)
        r.update(selected_candidate_id=None,checks=[],evidence=[],evaluated_requirement_ids=[],
                 unchecked_requirement_ids=['capability','no_auth'],stop_reason='no_candidate_in_scope')
        r['stages'].update(candidate='blocked',documentation='not_run');e[-1]['reason']='no_candidate_in_scope'
        self.assertFalse(adjudicate(self.task,r,e)['completed_at_requested_level'])
    def test_old_version_conflict_and_cross_binding_cannot_pass(self):
        variants=[]
        t=copy.deepcopy(self.task);t['requirements'][0]['max_age_days']=0
        variants.append((t,copy.deepcopy(self.result)))
        t=copy.deepcopy(self.task);t['requirements'][0]['version']='v2'
        variants.append((t,copy.deepcopy(self.result)))
        r=copy.deepcopy(self.result);r['evidence'][0]['subject_id']='binding-b';variants.append((self.task,r))
        r=copy.deepcopy(self.result);r['checks'][0]['verdict']='conflicted';variants.append((self.task,r))
        for t,r in variants:
            with self.assertRaises(ValueError): adjudicate(t,r,self.events)
    def test_no_model_can_remove_mandatory_conditions_or_invent_execution(self):
        t=copy.deepcopy(self.task);t['stop_rules']['required_ids']=['capability']
        with self.assertRaises(ValueError): validate_task(t)
        r=copy.deepcopy(self.result);r['stages']['task']='passed'
        with self.assertRaises(ValueError): adjudicate(self.task,r,self.events)
    def test_missing_source_or_stop_record_cannot_complete(self):
        with self.assertRaises(ValueError): adjudicate(self.task,self.result,self.events[1:])
        with self.assertRaises(ValueError): adjudicate(self.task,self.result,self.events[:1])
    def test_first_hit_is_not_first_valid_candidate(self):
        earlier=copy.deepcopy(self.result);earlier['checks'][1].update(verdict='unknown',evidence_ids=[])
        earlier['stop_event_id']='early'
        self.events.append({'event_id':'early','kind':'stop','status':'ok','reason':'requirements_met','at':'2026-11-01T11:00:10Z'})
        out=first_valid_assessment(self.task,[earlier,self.result],self.events)
        self.assertEqual(out['at'],'2026-11-01T11:01:00Z')
        self.assertIsNone(first_valid_assessment(self.task,[earlier],self.events))
    def test_wrong_source_url_and_search_snippets_cannot_support_document(self):
        for updates in ({'source_url':'https://example.org/different'}, {'kind':'query'}):
            events=copy.deepcopy(self.events);events[0].update(updates)
            with self.assertRaises(ValueError): adjudicate(self.task,self.result,events)

if __name__=='__main__': unittest.main()
