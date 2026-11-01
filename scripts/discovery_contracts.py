"""Deterministic preflight verdicts; these do not verify the truth of source text."""
from datetime import datetime
from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGES = ('candidate', 'documentation', 'live_response', 'task')

def validate_schema(kind, value):
    schema = json.loads((ROOT / 'evals/discovery-v1' / (kind + '.schema.json')).read_text(encoding='utf8'))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)

def timestamp(value):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timezone required')
    return parsed

def validate_task(task):
    validate_schema('task', task)
    ids = [r['id'] for r in task['requirements']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate requirement ID')
    active = [r['id'] for r in task['requirements'] if STAGES.index(r['stage']) <= STAGES.index(task['verification_level'])]
    if set(task['stop_rules']['required_ids']) != set(active):
        raise ValueError('Stop requirements must include every applicable mandatory condition')
    timestamp(task['as_of'])

def adjudicate(task, result, events):
    """Validate references and derive completion without trusting a model outcome label.

    Source support/authority must be adjudicated separately. Passing this function
    establishes a consistent record, not an independently verified factual answer.
    """
    validate_task(task)
    validate_schema('result', result)
    if result['task_id'] != task['task_id']:
        raise ValueError('Wrong task identity')
    requirements = {r['id']: r for r in task['requirements']}
    event_map = {e['event_id']: e for e in events}
    if len(event_map) != len(events):
        raise ValueError('Duplicate event ID')
    evidence = {e['id']: e for e in result['evidence']}
    if len(evidence) != len(result['evidence']):
        raise ValueError('Duplicate evidence ID')
    checks = {}
    final_clock=event_map.get(result['stop_event_id'],{}).get('at')
    if not final_clock:
        raise ValueError('A controller-recorded assessment timestamp is required')
    assessed_at=timestamp(final_clock)
    for check in result['checks']:
        key = (check['candidate_id'], check['requirement_id'])
        if key in checks or check['requirement_id'] not in requirements:
            raise ValueError('Duplicate or unknown requirement check')
        checks[key] = check
        for reference in check['evidence_ids']:
            if reference not in evidence:
                raise ValueError('Missing evidence reference even for an uncertain verdict')
        if check['verdict'] not in ('satisfied', 'violated'):
            continue
        rule = requirements[check['requirement_id']]
        if not check['evidence_ids']:
            raise ValueError('Definite verdict requires evidence')
        for reference in check['evidence_ids']:
            if reference not in evidence:
                raise ValueError('Missing evidence')
            item = evidence[reference]
            event = event_map.get(item['source_event_id'])
            if not event or event.get('status') != 'ok' or not event.get('response_sha256'):
                raise ValueError('Evidence must reference an observed successful response')
            if event.get('kind') == 'query' and item['type'] == 'official_document':
                raise ValueError('Search results are not observed official document bodies')
            if event.get('source_url') != item['url']:
                raise ValueError('Evidence URL must match the observed source response')
            if item['subject_id'] != check['candidate_id']:
                raise ValueError('Cannot merge evidence across candidates/bindings')
            if check['requirement_id'] not in item['requirement_ids'] or item['type'] not in rule['evidence_types']:
                raise ValueError('Evidence scope/type mismatch')
            if event.get('kind') in ('open','click'):
                if not event.get('at') or timestamp(event['at']) != timestamp(item['observed_at']):
                    raise ValueError('Observation time must match the recorded source response')
            age = (assessed_at - timestamp(item['observed_at'])).total_seconds() / 86400
            if age < 0 or ('max_age_days' in rule and age > rule['max_age_days']):
                raise ValueError('Evidence outside task time window')
            if rule.get('version') and item.get('version') != rule['version']:
                raise ValueError('Evidence version mismatch')
    selected = result['selected_candidate_id']
    declared = set(result['evaluated_requirement_ids'])
    unchecked = set(result['unchecked_requirement_ids'])
    if declared & unchecked or declared | unchecked != set(requirements):
        raise ValueError('Evaluated/unchecked partition must cover all requirements')
    actual = {rid for (cid, rid) in checks if cid == selected}
    if actual != declared:
        raise ValueError('Evaluated list disagrees with selected candidate checks')
    mandatory = task['stop_rules']['required_ids']
    met = bool(selected) and all(checks.get((selected, rid), {}).get('verdict') == 'satisfied' for rid in mandatory)
    final = event_map.get(result['stop_event_id'])
    if not final or final.get('kind') != 'stop' or final.get('reason') != result['stop_reason']:
        raise ValueError('Missing or inconsistent stop event')
    if final.get('status') != 'ok':
        raise ValueError('Invalid stop event')
    requested_stage = result['stages'][task['verification_level']]
    complete = result['stop_reason'] == 'requirements_met'
    if complete != (met and requested_stage == 'passed'):
        raise ValueError('Completion must match all applicable requirements and requested stage')
    for stage in STAGES[STAGES.index(task['verification_level']) + 1:]:
        if result['stages'][stage] != 'not_run':
            raise ValueError('A shallower task cannot claim unrequested deeper execution')
    attempts = [e for e in events if e.get('kind') in ('query', 'open', 'find', 'click')]
    if len(attempts) > task['budget']['external_actions']:
        raise ValueError('External action budget exceeded')
    return {'contract_valid': True, 'completed_at_requested_level': complete,
            'factual_support': 'requires_separate_source_adjudication',
            'external_actions': len(attempts), 'stop_reason': result['stop_reason']}

def first_valid_assessment(task, assessments, events):
    """Return the first evaluator-recorded valid candidate decision, not tool arrival.

    Each assessment has its own recorded stop/decision event and complete contract.
    This requires evaluator-controlled records; model self-reported timestamps are
    never used as the measurement clock.
    """
    candidates=[]
    event_map={e['event_id']:e for e in events}
    for result in assessments:
        try:
            verdict=adjudicate(task,result,events)
        except (ValueError, ValidationError):
            # Malformed records must be adjudicated separately; they cannot supply
            # a first-valid timestamp. No estimate is substituted.
            continue
        if verdict['completed_at_requested_level']:
            event=event_map[result['stop_event_id']]
            if 'at' in event:
                candidates.append((timestamp(event['at']),event['at'],result['selected_candidate_id']))
    if not candidates: return None
    _,at,candidate=min(candidates)
    return {'at':at,'candidate_id':candidate,'scope':'first valid evaluator-recorded assessment; not first search hit'}
