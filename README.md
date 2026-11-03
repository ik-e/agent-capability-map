# Agent Capability Map

공개 API·MCP·SDK 자원을 사람이 검토하고 AI가 단계적으로 찾을 수 있도록 하는 정적 카탈로그입니다. YAML이 원본이고 JSON·JSONL 및 Pages 사이트는 생성물입니다. 카탈로그는 외부 서비스를 실행하거나 인증 정보를 보관하지 않습니다.

## 로컬 빌드

Python 3.11 이상이 필요합니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_catalog.py
python scripts/check_secrets.py
python scripts/test_catalog_contracts.py
node scripts/test_search_contracts.mjs
node scripts/evaluate_search.mjs
python -m http.server 8000 --directory site
```

브라우저에서 `http://localhost:8000`을 엽니다. 원본 데이터는 `data/`에서 수정하고, `site/catalog/v1/`은 생성 파일이므로 직접 편집하지 않습니다.

검색 평가기는 `evals/golden/queries.json`을 사용합니다. 현재 예시는 17개 질의로 동작 확인용이며, 계획의 통계적 게이트(하드 제약 30개·무결과 20개)를 만족하는 평가 세트는 아닙니다.

## 데이터 구조

- `data/services/<service-id>/service.yaml`: Service·Integration·Binding
- `data/operations/`: 재사용 가능한 의미 기능
- `data/resources/`: 정보원 정본(메타 정보원 2건·선택한 개별 자료 1건). active 항목은 출처·범위·접근·이용조건 Evidence 필요
- `data/evidence/`: 필드 주장의 출처와 검증 기록
- `schemas/v1/`: JSON Schema 계약
- `site/catalog/v1/`: manifest, 검색·탐색 인덱스, 개별 상세, 일괄 JSONL

사람과 AI는 같은 목적 분류 DAG와 후보 인덱스를 사용합니다. `manifest.search_index`의 `search/index.json`은 정보원·실행 기능을 구분하며, 기존 `search/operations.json`은 기능 전용 호환 경로로 유지합니다. 분류 안에서 검색하거나 전체 후보로 돌아갈 수 있습니다. 하나의 후보는 여러 상위 목적에 속할 수 있습니다. 공공데이터포털·서울 열린데이터광장에 실제 탐색 방법을 기록하고, OD 문서가 직접 참조하는 따릉이 대여소 마스터만 선택 등록했습니다. 포털 전체 하위 목록과 원자료는 복제하지 않습니다. 과거 R0의 동결 입력·결과는 유지합니다. [개정 계획](docs/api-capability-map-github-pages-plan.md)과 [수집 범위 검토](docs/internet-map-scope-review-2026-11-03.md)를 참고하세요.

`site/catalog/v1/index.html`은 JavaScript 없이 분류·자료·근거로 이동하는 생성 페이지입니다. manifest의 `entrypoints`에는 절대 HTTPS 진입 URL도 제공합니다. 다른 주소에 게시할 때는 `scripts/build_catalog.py --public-base-url https://example.org/catalog/v1/`로 지정합니다. 정보원 상세는 `update_notes`의 탐색 방법·한계와 주장별 확인 시각을 사람용 화면과 JSON에서 함께 제공합니다. 문서 확인은 실제 API 실행이나 좌표 조인 성공을 뜻하지 않습니다.

현재 표본은 7개 Service와 16개 Operation입니다. GitHub, Open-Meteo, OpenAI에 더해 MCP Registry, Context7, Tavily, Hugging Face Hub를 포함하며, MCP 서버 발견·최신 개발 문서 조회·웹 검색과 URL 추출·모델/데이터셋 탐색·장소 지오코딩을 다룹니다. 아직 계획의 20~50개 Operation 목표에는 미달하며, 각 레코드는 공식 출처 Evidence를 붙여 확장합니다.

## GitHub Pages 게시

`gh auth status`로 GitHub CLI 로그인 상태를 확인한 뒤, 저장소를 새로 만들 때 다음 명령을 실행할 수 있습니다.

```powershell
gh repo create ik-e/agent-capability-map --public --disable-issues --disable-wiki --source . --remote origin
gh api repos/ik-e/agent-capability-map/pages --method POST -f build_type=workflow
git push -u origin main
```

이 순서로 공개 저장소를 만들고 GitHub Actions를 Pages 게시 소스로 설정한 뒤 첫 배포를 시작합니다. 외부 기여는 현재 받지 않는 운영 방침이며, 이슈와 위키는 비활성화합니다. 기존 저장소에 연결할 때는 `gh repo set-default`와 `git remote add origin`을 사용합니다.

## 기존 API Connector CLI

기존 manifest 생성기는 별도 기능으로 유지합니다.

```powershell
./New-ApiConnectorManifest.ps1 `
  -InputPath ./api-connector.request.json `
  -OutputPath ./api-connector.manifest.json
```

요청 형식은 `api-connector.request.json`을 참고하세요. 이 CLI는 외부 API를 호출하지 않습니다.
