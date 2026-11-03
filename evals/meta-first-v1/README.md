# 메타 지도 우선 개발 검증

`protocol.json`은 두 공식 포털의 경로를 책임자가 직접 점검하는 개발 과제의 사전 계약이다. 시작점·허용 호스트·30개 원자 동작/600초 예산·필수 확인과 종료 기준을 고정했다. 모델 성능·토큰을 측정한 시험이 아니다. 원문과 이벤트는 Git 제외 경로 `evals/runs/meta-first-2026-11-03/`에 보관한다.

`comparison.json`은 이후 고정한 포털 한정 M/M+D 개발 비교다. 등록 자원 재조회와 같은 포털의 새 자원 탐색을 구분하고 조건 순서를 교차 배치한다. 일반 웹 검색 없이 계측한 HTTPS open/find/click만 허용한다. 실제 stdio와 서울 검색 페이지의 open/find 보정 후 새 CLI 문맥 네 개로 실행한다. 현재 설정의 일반 웹 검색 gate를 통과했다고 해석하지 않는다.

```powershell
py -3.12 scripts/run_meta_first_pilot.py --freeze --run
```

동일 실행 경로가 잠겼으면 덮어쓰지 않는다. 두 조건은 공개 정본에서 파생한 동결 artifact이며 직접 Pages 접근이 아니다. M은 선택 등록한 대여소 마스터와 해당 근거를 제외하고 M+D는 이를 포함한다. 기존 공개 정본 자체에서 자료를 삭제하지 않는다. 입력 파일 해시와 모델·예산은 실행 전에 잠근다. 새 문맥이라도 등록 자원 재조회 과제를 독립 발견 holdout으로 세지 않는다.

개별 원문·실행 로그는 공개하지 않는다. CLI 토큰은 관측된 모델 사용량이며 외부 서비스 전체 비용이 아니다. 잘못된 인자로 거부된 MCP 요청, 실행된 원자 동작, 실제 네트워크 시도는 따로 집계한다. 새 자원 하나와 조건당 한 번으로 일반적인 효율 우위나 통계적 합격을 선언하지 않는다. 전체 관리 시간의 측정이 부족하면 장기 손익분기점도 산출하지 않는다.

`name-regression.json`은 최초 네 시행에서 드러난 자료명 검색 누락을 고친 뒤의 별도 회귀다. 원래 비교를 덮어쓰거나 독립 효율 비교에 합산하지 않는다.

```powershell
py -3.12 scripts/run_meta_first_pilot.py --protocol evals/meta-first-v1/name-regression.json --run-dir evals/runs/meta-first-name-regression-2026-11-03 --freeze --run
py -3.12 scripts/export_meta_first_pilot.py
py -3.12 scripts/export_meta_first_pilot.py --run-dir evals/runs/meta-first-name-regression-2026-11-03 --output evals/meta-first-v1/name-regression-summary-2026-11-03.json
```

[개발 결과와 해석](../../docs/meta-first-implementation-2026-11-03.md)을 따른다. 참조 검사 통과와 내용의 의미적 정확성은 별개다.
