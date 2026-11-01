"""Lock completed pilot results before sending task-focused external reviews."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'evals/runs/r0-2026-11-01-v2'
lock = json.loads((RUN / 'lock.json').read_text(encoding='utf8'))
summary = json.loads((RUN / 'runtime-summary.json').read_text(encoding='utf8'))
audit = json.loads((RUN / 'protocol-audit.json').read_text(encoding='utf8'))
assert summary['finished_runs'] == len(lock['schedule']) == 18
assert audit['completed'] == 18 and audit['all_threads_unique'] and audit['frozen_inputs_still_match']
assert not any(r['flags'] for r in audit['runs']), 'Inspect audit flags before external review'
assert not any(r['over_web_budget'] for r in summary['runs']), 'Inspect lower-bound overruns; false does not prove atomic-budget compliance'
files = [RUN / 'lock.json', RUN / 'runtime-summary.json', RUN / 'protocol-audit.json']
for folder in sorted(RUN.glob('[0-9][0-9]-*')):
    files.extend(folder / name for name in ('answer.json', 'metrics.json', 'events.jsonl', 'prompt.txt'))
result_lock = {'locked_at': datetime.now(timezone.utc).isoformat(), 'files': {
    str(p.relative_to(RUN)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
encoded = json.dumps(result_lock, ensure_ascii=False, indent=2) + '\n'
path = RUN / 'results-lock.json'
if path.exists():
    previous = json.loads(path.read_text(encoding='utf8'))
    assert previous['files'] == result_lock['files'], 'Results changed after lock'
else:
    path.write_text(encoded, encoding='utf8')
review = RUN / 'reviews'
review.mkdir(exist_ok=True)
assignment = {'chatgpt': 'geocoding-tool', 'gemini': 'poi-source',
              'claude': 'station-grid-join', 'perplexity': 'bike-od-source',
              'deepseek': 'coordinate-tool', 'grok': 'building-occupancy-abstain'}
base = '''인터넷 지도 R0 v2 파일럿의 사후 검토입니다. 새 탐색 시험이 아니라 잠긴 결과의 오류·한계를 검토해 주세요.
방법: 6과제×3조건×1회=18회. 같은 gpt-6.1-sol medium, 매회 새 CLI 문맥, 순서 무작위 고정. A 지도 우선(동결 정본을 읽는 시험용 MCP), B 웹검색 우선, C 공식 디렉터리 메인 우선 뒤 웹검색 허용. 외부 조회 예산 20회로 지시, 900초. 스키마는 동일, B/C의 지도 MCP 데이터 접근은 거부. B/C 지도 도메인 제한은 지시+사후감사이며 강제 네트워크 격리는 아님. 정본 변경 없음, 독립 문맥 18개, 스키마·기록된 시작점 검사 통과. 원자 조회는 CLI batch 축약으로 정확히 계측되지 않아 20회 예산 준수 미판정. external 숫자는 요약 동작 하한이며 모델 자기보고도 확정 계측이 아님. 기록된 지도 노출은 없으나 우발 노출까지 0이라고 보장하지 않음.
정본은 7서비스/16동작/9연결/108근거/정보원0건. 지오코딩만 in, 좌표도구 partial, 나머지 out. 지도 범위 밖 탐색과 범위 안 조회를 섞어 일반화하지 말 것. 최초 유효후보 시간 미계측. 입력 total/cached/uncached/output을 구분하며 전체입력=청구비용 아님. 1회·소표본이며 통계적 효용 입증 아님. UI 시각검증 미관측. R1 미실시·holdout 미작성. v1 파일읽기 차단 실패는 전부 제외, 같은 개발과제로 v2 재실행하여 fresh holdout 아님. 실행시간에는 모델·도구·출력 시간이 포함, 인터넷 전송 성능 비교 아님。디렉터리 조건에는 분야별 메인 URL을 미리 지정한 사전정보가 있음. 무차별 무지식 비교 아님.
별도 사후 재확인(시행에 소급 반영 안 함): 직접 HTTPS GET에서 Open-Meteo name=Seoul,count=3,countryCode=KR가 무인증 HTTP200, 좌표 있는 KR 후보 3개를 반환했다. 그중 1개가 Seoul, 나머지는 다른 지역의 유사 지명이다. 범용 POI 정확도나 대여소 ID 조인 성공은 아님. 서울 OD/마스터 상세 HTML도 직접 GET200으로 설명은 읽혔지만 마스터 레코드·ST 키 대응은 확보 안 됨. 시행의 웹도구 blocked와 실제 서비스 부재를 구분할 것. 사후 검색·문서·API 재확인 비용과 외부 리뷰 비용은 시행별 토큰·시간에 포함되지 않으며 파일럿 전체 총비용은 미계측.
요청: 담당 과제의 세 답변을 아래 required별로 supported/partial/unverified/incorrect로 검토하고, outcome(found/blocked/보류)가 과장됐는지 판단해 주세요. 'found' 자체를 실행성공으로 채점하지 마세요. 답변에 적힌 observed는 실행 모델의 자기보고이며 독립적으로 확인된 정답이 아닙니다. 가능하면 공식 원문을 확인하고 확인하지 못한 부분을 분명히 하세요. 없는 자료를 단정하거나 소수표본으로 승자를 정하지 마세요. 마지막에 치명적 오류와 개선 우선순위 3개, 이 시험으로 말할 수 없는 결론을 적어 주세요. 1200~1800자 정도의 간결한 검토를 원합니다.
'''
for provider, task_id in assignment.items():
    task = next(t for t in lock['tasks'] if t['id'] == task_id)
    text = f'답변 첫 줄은 R0-V2-REVIEW-{provider} 로 시작해 주세요.\n' + base
    text += '\n담당 과제: ' + task['request'] + '\nrequired=' + ', '.join(task['required']) + '\n'
    if task_id in ('station-grid-join', 'bike-od-source'):
        text += '''\n추가 사후 교차확인: 다른 OD 시행이 웹에서 T-DATA를 발견했고, 책임자가 공식 HTML을 직접 재열람했다. https://t-data.seoul.go.kr/dataprovide/trafficdataviewopenapi.do?data_id=1045 는 OD 예시 startStatnId=ST-1006/endStatnId=ST-1017, https://t-data.seoul.go.kr/dataprovide/trafficdataviewopenapi.do?data_id=1044 는 stationId=ST-1080/stationLatitude/stationLongitude를 명시한다. 인증키 필수. 같은 ST 형식의 공식 좌표 후보는 있지만 예시 ID가 겹치지는 않으며 동일 namespace·버전·원본 CRS·실제 전체매칭은 입증 안 됨. 이 발견은 앞선 station 시행들과 공유하지 않았고 해당 시행 성공으로 소급 채점하지 않는다. '이번 탐색에서 미확인'과 '공식 연결 후보가 존재하지 않음'을 구분해 검토해 달라.\n'''
    for row in summary['runs']:
        if row['task_id'] != task_id:
            continue
        a, u = row['answer'], row['usage']
        text += f"\n[{row['condition']}] outcome={a['outcome']}; seconds={row['elapsed_seconds']}; input={u['input_tokens']}; cached={u['cached_input_tokens']}; uncached={u['input_tokens']-u['cached_input_tokens']}; output={u['output_tokens']}; external_summary_lower_bound={row['observed_web_budget_units']} (atomic calls unknown)\n"
        text += a['answer'] + '\n'
        text += '근거목록(자기보고):\n' + '\n'.join(s['url'] if task_id == 'coordinate-tool' else f"{s['url']} [observed={s['observed']}]" for s in a['sources']) + '\n'
        if task_id != 'coordinate-tool':
            text += '미확인: ' + '; '.join(a['unverified']) + '\n'
        else:
            text += '별도 중복 미확인 목록은 길이 제한으로 생략. 위 답변 본문은 전문이며 실제 데이터·변환·조인·패키지 환경·접근/재이용 조건은 미검증.\n'
    assert len(text) <= 12000, (provider, len(text))
    (review / (provider + '.request.txt')).write_text(text, encoding='utf8')
    print(provider, task_id, len(text))
print('results_lock_sha256', hashlib.sha256(path.read_bytes()).hexdigest())
