# API·MCP 역량 지도와 GitHub Pages 계획서

- 상태: 소유자 검토용 초안
- 작성일: 2026-10-27
- 개정일: 2026-11-01 — 판정 계약·계측 보정 gate·재사용 효과 분리 시험 구체화
- 범위: 공개 API·MCP·SDK 지도 데이터의 설계, 게시, 검색 검증

## 1. 결정 요약

사람과 AI가 API, MCP 서버, SDK, 연동 기능을 찾아 활용할 수 있도록 공개 카탈로그를 만든다. GitHub 저장소를 사람이 검토하는 원본 데이터의 기준점으로 삼고, YAML 원본을 검증한 뒤 JSON·JSONL과 정적 검색 사이트를 생성해 GitHub Pages에 게시한다.

지도의 핵심 가설은 **인터넷 탐색에서 이미 확인한 기능·제약·근거와 유용한 탐색 경로를 재사용하면, 에이전트가 매번 다시 내려야 하는 판단을 줄일 수 있다**는 것이다. 사용 목적에서 후보와 근거로 이동하고, 남은 미확인 사항에만 외부 탐색을 사용하도록 돕는다. API·MCP·SDK 지도는 이러한 인터넷 탐색 지식층의 첫 적용 분야다. 이 가설은 현재 입증된 성능이 아니며, 아래 과제 기반 시험으로 검증한다.

공개 카탈로그는 어떤 기능이 문서화되어 있는지, 어떤 입력·권한·전송 방식이 필요한지, 그 주장을 어떤 근거로 확인했는지를 설명한다. 실제 API/MCP 실행기는 만들지 않는다. 다만 MVP 가설 검증을 위해 공개 데이터와 분리된 테스트 하네스에서 테스트용 자원에 연결하는 작업은 포함한다. 계정별 인증·권한 상태, 비밀정보, 실시간 가용성은 카탈로그에 저장하지 않는다.

이 계획은 공개 저장소 이름을 가칭 `agent-capability-map`, 공개 범위를 Public으로 두고, 데이터 CC0-1.0·사이트와 도구 코드 MIT, 초기 외부 기여 비허용이라는 방향을 반영한다. 첫 분야는 에이전트가 작업을 더 잘 수행하도록 돕는 RAG·API·MCP·SDK 관련 자원이다. 초기 세부 감사에서는 ChatGPT, Gemini, DeepSeek, Grok의 응답을 확인했다. 당시 Perplexity의 감사 응답은 확인되지 않았고 Claude는 사용량 제한으로 새 답변을 받지 못했다. 이후 검토·실행 상태는 개정 기록과 실행 보고서에서 구분한다. 이 계획은 여섯 모델의 합의 결과로 표시하지 않는다. MVP는 카탈로그 작성·검증·게시·검색을 포함하고, 실제 연결·작업 완료를 통한 효용 검증은 별도 시험 하네스에서 수행한다. 카탈로그 자체는 실행기나 자격증명 보관소가 아니다.

## 2. 목적과 성공 정의

사용자가 자연어로 원하는 일을 설명했을 때, 사람 또는 AI가 다음을 확인할 수 있어야 한다.

1. 어떤 의미상의 작업(Operation)이 필요한가.
2. 그 작업을 제공하는 API·MCP·SDK 연동(Binding)은 무엇인가.
3. 해당 구현이 요구하는 입력, 권한, 전송 방식, 버전과 제약은 무엇인가.
4. 각 설명의 근거와 확인 시점은 무엇인가.
5. 필수 조건이 확인되지 않았을 때 무엇이 불명확한가.
6. 어떤 근거를 재사용할 수 있고 무엇을 추가 확인해야 하는가.
7. 이번 요청의 검증 수준에서 탐색을 종료하거나 보류할 조건은 무엇인가.

성공은 사이트가 배포되었다는 사실만으로 판단하지 않는다. 첫째, 정적 카탈로그로 목적에 맞는 Operation·Binding을 찾고 제약 위반·무결과 상황에서 올바르게 보류하는지 확인한다. 둘째, 동일한 제한된 과제를 지도 없이 찾는 경우와 비교해 실제 연결·작업 성공률을 유지하면서 시간과 토큰을 줄이는지 시험한다. 둘째 시험은 테스트용 연결·계정·자격증명이 준비된 별도 하네스에서 수행하며, 그 결과를 공개 카탈로그가 직접 실행을 보장한다는 뜻으로 해석하지 않는다.

### 판단 재사용의 책임 구분

| 구분 | 책임 |
|---|---|
| 공개 지도 | 재사용 가능한 기능·입출력·범위·제약·근거·확인 시점과 공식 확인 경로를 제공한다. 후보의 적합 조건과 미확인 사항을 드러낸다. |
| 소비 에이전트 | 요청별 GoalSpec에서 필수조건·선호조건·검증 수준·예산·종료 조건을 정하고, 지도 조회·외부 탐색·보류를 선택한다. |
| 평가·경험 기록 | 실제 조회·선택·탈락·추가 검증·종료 사건과 관측 근거를 기록한다. 검토 후 재사용 가능한 사실과 경로만 정본에 반영한다. |

GoalSpec과 실행별 종료 판단은 요청에 속하며 영구 Operation으로 저장하지 않는다. 지도는 판단에 필요한 자료를 제공하고, 소비 에이전트가 이번 조건에 적용한다. 기존 Service·Integration·Binding·Operation·Evidence·InformationResource 구조를 우선 활용하고 반복되는 실패가 확인될 때 필요한 최소 필드를 검토한다.

인터넷 전체의 최적 후보나 전역 최적 탐색을 보장하지 않는다. 특정 과제·후보 집합·예산에서 적합성을 유지하며 재검색·출처 전환·불필요한 후보 검토를 줄였는지 평가한다. 공식 출처라는 이유만으로 모든 주장을 신뢰하거나, 최근 확인됐다는 이유만으로 현재 요청에 충분하다고 판정하지 않는다.

## 3. 범위

### 포함

- 공개 가능한 Service, Integration, Binding, Operation, Evidence 정보의 관리
- MCP Tool, Resource, Prompt를 구별해 표현
- 사람이 검토할 PR·변경 이력·기여 절차
- 스키마 및 참조 검증, 비밀정보 탐지, 생성 데이터 검증
- 사람용 정적 계층 탐색·검색 페이지와 AI·프로그램용 단계 조회 파일 게시
- 정적 산출물을 기준으로 한 사람용 탐색·AI용 검색·단계별 상세 조회
- 정적 조회 계약과 같은 결과를 내는 참조 검색기 및 고정 골든 질의 평가
- 고정된 질의와 기대 결과로 검색 품질 검증
- MCP 검색과 골든 평가가 공유하는 작은 참조 검색 라이브러리

### 제외

- API나 MCP 도구를 실제 호출하는 실행 런타임 또는 프록시
- OAuth 제공자, 자격 증명 보관소, 사용자별 권한 저장
- 사용자별 계정 연결 상태와 실시간 상태·할당량 보장
- 자동으로 통합을 설치하거나 작업을 실행하는 에이전트
- 승인 없는 자동 등록·자동 병합 및 검토 없는 의미 매핑
- 초기 버전의 벡터 데이터베이스, 자동 온톨로지 생성, 복합 작업 자동 계획

GitHub Pages는 정적 게시 표면이며 임의의 서버 측 검색이나 카탈로그 실행을 제공하지 않는다. 사람용 계층 탐색과 검색은 브라우저에서 정적 인덱스를 사용하고, AI 소비자는 공개 인덱스를 가져와 검색하거나 참조 검색기를 사용한다. MCP 어댑터는 정적 계약과 검색 품질이 검증된 뒤 같은 산출물을 읽는 후속 단계로 둔다. GitHub Pages의 사용자 정의 Actions 배포 흐름은 정적 사이트 빌드와 배포에 사용할 수 있다. [GitHub Pages 사용자 정의 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [GitHub Pages 사이트 구성](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)

## 4. 사용자와 이용 흐름

사람과 에이전트는 **같은 분류 체계, 같은 후보, 같은 근거**를 사용한다. 진입 방식은 둘 다 `분류를 따라 탐색`과 `키워드 검색`을 제공하고, 한 경로 안에서 다른 경로를 함께 쓸 수 있다. 차이는 의미나 분류가 아니라 화면 표현과 한 번에 가져오는 정보량이다. 분류 탐색은 목적을 좁히는 경로이고, 키워드는 어느 단계에서든 후보를 바로 찾는 경로다.

분류는 `분야 → 사용 목적·작업 → 필요한 정보 또는 능력 → 후보` 순으로 내려간다. 한 후보가 여러 목적에 쓰일 수 있으므로 분류는 다중 부모를 허용하는 탐색 그래프로 만들고, 인증·전송·효과·최신성 같은 속성은 분류 트리와 별개의 필터로 둔다. 이 구조는 서비스 제공자 목록을 그대로 계층화하는 대신 사용자가 해결하려는 일에서 시작한다.

### 사람

1. 지도 첫 화면에서 분류를 따라 내려가거나 키워드로 바로 검색한다. 키워드 검색은 특정 분야 안에서도 전체 지도에서도 사용할 수 있다.
2. 목적·작업별 후보에서 정보 출처와 실행 도구를 구분해 보고, 필요하면 종류·인증·전송·효과 등의 필터를 적용한다.
3. 후보의 요약을 비교한 뒤 상세 화면에서 범위, 제약, Evidence 출처와 확인 시점을 확인한다.
4. 원본 출처와 변경 이력으로 이동해 주장과 수정 근거를 확인한다.

### AI 에이전트

1. `manifest.json`에서 같은 분류 그래프와 키워드 검색 인덱스의 위치·버전을 확인한다.
2. 요청이 구체적이면 키워드 검색으로 시작하고, 범위가 넓거나 용어가 불명확하면 사람과 같은 분류 경로로 좁힌다. 필요하면 두 경로를 함께 사용한다.
3. 먼저 작은 후보 요약과 안정 ID만 읽고, 선택에 필요한 상세·Binding 또는 정보 출처·Evidence만 단계적으로 가져온다.
4. 공개된 요구 조건을 현재 런타임 정보와 비교해 만족·위반·확인 불가를 구분하고, 선택 근거와 원 출처를 반환한다.
5. 실행은 별도 권한이 있는 런타임에서만 수행한다. 검색 속도와 토큰 절감은 설계만으로 단정하지 않고 벤치마크로 확인한다.

후속 MCP 어댑터는 Pages에 게시된 정적 산출물을 읽는 얇은 읽기 전용 계층이다. 별도 카탈로그나 독립 의미 데이터를 보유하지 않으며, 검색·필터링 로직은 참조 검색기와 공유한다. 실제 통합 호출 능력이나 사용자 비밀정보를 가지지 않는다.

## 5. 데이터 모델과 공개 계약

### 핵심 관계

```text
Service
  └── Integration
        └── Binding ── operation_refs ── Operation

Category ── classifies ── InformationResource or Operation
InformationResource ── may be published by ── Service

Evidence ── supports a specific claim about any record

GoalSpec ── interpreted per request; not stored as a catalog Operation
```

- **Service:** 제공자 또는 제품의 정체성
- **Integration:** Service가 제공하는 논리적 인터페이스 묶음. 예: “지도 검색 API”, “문서 검색 SDK”. 종류나 패키지 버전이 달라져도 같은 인터페이스 목적이면 묶을 수 있다.
- **Binding:** Integration을 특정 방식으로 찾거나 설치하는 구체 항목. API 기본 URL·명세, MCP 서버 엔드포인트 또는 패키지, SDK 패키지 등 위치와 버전·전송·인증 정보를 가진다.
- **Operation:** Service에 종속되지 않는 의미상의 작업. 예: “문서에서 관련 구절 검색”. 동일 의미가 여러 Service의 여러 Binding에 구현될 수 있다.
- **Evidence:** 특정 레코드의 특정 필드가 맞다고 판단한 출처와 검증 상태. MVP에서는 Source와 Claim을 별도 테이블로 만들지 않고, Evidence 한 건이 `subject_id + claim_path + source_url`을 연결한다.
- **GoalSpec:** 사용자의 이번 요청을 해석한 임시 목표. 재사용 카탈로그 항목으로 저장하지 않음

Operation과 Binding은 다대다로 연결한다. Binding의 `operation_refs`만 편집 원본으로 두고, Operation에서 Binding으로 가는 역참조는 빌드가 생성한다. 각 관계 항목은 Binding 안에서 프로토콜 고유 참조(예: HTTP method/path 또는 MCP tool 이름)를 선택적으로 기록한다. MCP Tool은 호출 가능한 Operation의 구현으로 연결한다. MCP Resource는 읽을 수 있는 ContextSource, Prompt는 지침 템플릿으로 구분하며 둘을 실행 Operation으로 분류하지 않는다. MVP가 이 두 종류를 아직 별도 검색하지 않는다면 명시적으로 제외하고, `other`로 위장해 넣지 않는다.

### MVP 필드와 값 기준

아래 표는 v1 스키마를 구현하기 위한 제안이다. `required`는 레코드가 게시 가능한 상태가 되기 위한 조건이다. 선택 필드가 없다는 이유로 값을 추측해 채우지 않는다. 모든 ID는 소문자 ASCII 안정 문자열이며 공개 후 의미 변경·재사용을 금지한다. 모든 URL은 절대 URL이어야 한다. 예시는 예약된 `example.invalid` 도메인을 사용한다.

| 레코드 | 필드 | 필수 | 타입·허용 기준 | 의미 / 예시 |
|---|---|---:|---|---|
| Service | `id` | 예 | 안정 문자열, 전역 유일 | `svc_acme_search` |
|  | `name`, `provider_name` | 예 | 문자열 | 표시명과 제공 주체. `Acme Search`, `Acme Labs` |
|  | `summary` | 예 | 한두 문장, 목적 설명 | 검색 기능을 제공하는 가상 서비스 |
|  | `homepage_url` | 아니오 | URL | 서비스 공식 홈 |
|  | `status` | 예 | `active`, `beta`, `deprecated`, `archived`, `unknown` | 카탈로그가 파악한 제품 생명주기. 도달 가능 상태와 구별 |
| Integration | `id`, `service_id` | 예 | 안정 ID, Service 참조 | `int_acme_search_api`, `svc_acme_search` |
|  | `name`, `summary` | 예 | 문자열 | 사람에게 보일 인터페이스 묶음 |
|  | `status` | 예 | Service의 동일 enum | 인터페이스 생명주기 |
| Binding | `id`, `integration_id` | 예 | 안정 ID, Integration 참조 | `bnd_acme_search_http`, `int_acme_search_api` |
|  | `resource_kind` | 예 | `http_api`, `mcp_server`, `sdk`, `agent_connector`, `other` | 접근·설치 형태. 프로토콜·전송과 혼동하지 않음 |
|  | `name` | 예 | 문자열 | 구체 구현의 표시명 |
|  | `locations` | 예 | 아래 key 중 하나 이상인 object | 종류별 주소를 임의의 `canonical_url` 하나에 합치지 않음 |
|  | `version` | 아니오 | 불투명 문자열 | 제공자 표기 그대로: `v2`, `2026-10`, `1.4.2`; SemVer 강제 금지 |
|  | `transport` | 조건부 | `http`, `streamable_http`, `stdio`, `sse`, `websocket`, `other`, `unknown` | API/MCP에 적용. 미확인은 `unknown`, 값 생략과 의미를 구분 |
|  | `auth_schemes` | 예 | 배열: `none`, `api_key`, `bearer`, `oauth2`, `other`, `unknown` | 해당 Binding에서 허용되는 대안 방식의 목록. `none`은 무인증 선택지도 있다는 뜻이며 다른 방식과 공존 가능. `unknown`만 단독 허용 |
|  | `auth_scopes` | 아니오 | 제공자가 공개한 문자열 배열 | 공개 scope 이름만; 자격증명이나 개인별 권한 상태 금지 |
|  | `operation_refs` | 조건부 | `{operation_id, native_ref?}` 배열 | 구현 관계의 단일 편집 원본. 예: `op_search_documents`, `GET /v2/search`, MCP tool `search_documents` |
|  | `status` | 예 | Service의 동일 enum | 실제 가용성을 나타내지 않음 |
| Operation | `id` | 예 | 전역 안정 ID | `op_search_documents` |
|  | `name`, `purpose` | 예 | 짧은 식별명, 한 문장 설명 | `search_documents`; 문서 집합에서 질의와 관련된 문서를 찾는다 |
|  | `category_ids` | 아니오 | `data/vocab/categories.yaml`에 정의한 ID 배열 | 작은 통제 어휘. 미등록 자유 태그로 분류 체계를 확장하지 않음 |
|  | `aliases` | 아니오 | 문자열 배열 | 사용자 표현·동의어. 검색용이며 표준 분류가 아님 |
|  | `entity_types` | 아니오 | 문자열 배열 | 다루는 객체 종류: `document`, `passage` |
|  | `inputs`, `outputs` | 아니오 | 이름·기본 타입·필수 여부·설명 객체 배열 | 의미 수준의 입력·출력 조건. Binding별 wire schema를 대신하지 않음 |
|  | `effect` | 예 | `none`, `read`, `write`, `destructive`, `unknown` | 실행 전 부작용 구분. `read`는 상태를 바꾸지 않는 조회 |
|  | `status` | 예 | 공통 생명주기 enum | `active` Operation만 활성 Binding이 있어야 검색됨 |
| Evidence | `id` | 예 | 전역 안정 ID | `ev_bnd_acme_api_endpoint_official_docs` |
|  | `subject_id`, `claim_path` | 예 | 대상 ID, 빌드된 정규 JSON 레코드 기준 RFC 6901 JSON Pointer | `bnd_acme_search_http`, `/locations/api_base_url/url` |
|  | `source_url`, `source_type` | 예 | URL과 `official_docs`, `official_spec`, `official_repo`, `package_registry`, `official_notice`, `third_party`, `unknown` | 출처 위치와 자료 종류 |
|  | `source_grade` | 예 | 기존 정책의 `A`, `B`, `C`, `D` | 권위 등급. A 공식 1차, B 공식 보조·공지, C 제3자, D 불명확·미검증 |
|  | `verification_state` | 예 | `verified`, `unverified`, `needs_review`, `stale`, `contradicted` | 주장 확인 상태. 권위 등급과 별개 |
|  | `verified_at` | 조건부 | UTC RFC 3339 시각 | 사람이 또는 명시한 방법으로 마지막 내용 확인한 시각 |
|  | `source_locator`, `verification_method` | 아니오 | 섹션·필드·방법 식별 문자열 | `Authentication > API keys`, `manual_review`, `spec_parse` |

`locations`는 아래 key를 주소 종류로 사용하는 객체다. 허용 key는 `docs_url`, `api_base_url`, `api_spec_url`, `mcp_endpoint_url`, `mcp_package`, `mcp_repo_url`, `sdk_package`, `sdk_repo_url`, `source_repo_url`, `other_url`이다. URL key의 값은 `{url}` 객체, package key의 값은 `{package, registry}` 객체다. API Binding은 문서·기본 URL·기계 판독 명세를 서로 다른 key로 기록한다. MCP 원격 연결은 `mcp_endpoint_url`, 로컬 실행은 `mcp_package`와 선택적 repo를 기록한다. SDK는 `sdk_package` registry 좌표와 선택적 repository URL을 기록한다. HTTPS endpoint가 없다는 이유로 MCP stdio package를 endpoint URL로 위장하지 않는다. `registry`는 `npm`, `pypi`, `maven`, `nuget`, `crates_io`, `go`, `oci`, `mcp_registry`, `other` 중 하나다. 각 key는 최대 한 값을 가진다. 서로 다른 버전·지역·제품판이 서로 다른 접근 조건이나 기능을 가리키면 각각 별도 Binding으로 만든다. 동일 Binding에 여러 보조 문서가 있으면 대표 URL은 `docs_url`에 두고 추가 근거 URL은 Evidence로 기록한다. 같은 패키지가 서로 다른 Integration을 구현하면 Integration마다 Binding을 둘 수 있고 패키지 좌표는 반복한다. 여러 문서 언어/버전이 필요해지면 별도 location ID를 추가하는 스키마 버전 변경을 검토한다.

`mcp_server` Binding의 보조 필드 `mcp_primitives`는 `tool`, `resource`, `prompt`의 배열이다. 이 배열은 서버가 제공한다고 문서화한 primitive 종류만 표시한다. Operation 관계는 MCP Tool에 한해 둔다. Resource/Prompt를 검색 대상에 포함하기 전에는 각각 별도 `ContextSource`/`PromptTemplate` 레코드 설계를 추가한다. `native_ref`는 구조화 객체 `{kind, value}`이며 `kind`는 `http_operation`, `mcp_tool`, `sdk_symbol`, `other`다. 네이티브 호출 스키마 전문은 Binding에 복사하지 않고, 공개된 명세 위치를 연결한다. 필요한 경우 Operation의 I/O JSON Schema를 후속 확장한다.

공통 규칙: 생성·수정 시각은 Git 이력으로 확인 가능하므로 모든 레코드에 중복 저장하지 않는다. `verified_at`은 주장 검증 시각이며 자동 링크 점검 시각과 같지 않다. 링크 점검 시각·결과는 빌드/점검 산출물에만 기록한다. `active`는 제공자가 활성으로 공표한 생명주기 상태이지 연결 성공 판정이 아니다. 비밀값, 계정별 인증 상태, 요금·쿼터·실시간 가용성은 공개 스키마에 넣지 않는다. 인증방식의 실제 세부가 근거에서 확인되지 않으면 `unknown`을 사용한다. Operation `inputs`·`outputs`는 기능 의미 수준의 데이터 조건이며 실제 protocol wire schema를 대신하지 않는다. `none`은 제공자 데이터를 읽거나 변경하지 않는 계산·변환, `read`는 데이터를 조회하지만 상태를 바꾸지 않는 동작, `write`는 상태 변경, `destructive`는 삭제·복구 곤란 변경을 뜻한다.

### 관계와 유효성 규칙

- Service 1 → Integration 0..N, Integration 1 → Service 1, Integration 1 → Binding 0..N.
- Operation은 전역 재사용 레코드이며 Binding과 0..N 대 0..N 관계다. 편집 원본 관계는 Binding의 `operation_refs`; 반대편 목록은 생성한다.
- Integration은 같은 제품판·권한 경계 안에서 논리적으로 함께 관리되는 인터페이스 묶음이다. 별도 제품/권한 경계는 별도 Integration으로 나눈다. 버전, 지역, 패키지, 전송 방식 등 설치·접근 차이는 Integration을 나누는 기준이 아니라 Binding을 나누는 기준이다. 하나의 패키지가 여러 Integration을 구현하면 Binding을 각각 두고 패키지 좌표를 공유할 수 있다.
- 게시 가능한 `active` Binding은 종류에 맞는 주소를 하나 이상 가져야 한다. `http_api`에는 `api_base_url` 또는 `api_spec_url`; 원격 `mcp_server`에는 `mcp_endpoint_url`; 로컬 MCP에는 `mcp_package`; `sdk`에는 `sdk_package`; `agent_connector`와 `other`는 사람이 검토 가능한 URL 또는 package 위치가 필요하다. MCP Binding은 `transport`와 비어 있지 않은 `mcp_primitives`가 필수이며, stdio이면 `mcp_package`, 원격 HTTP 계열이면 `mcp_endpoint_url`이 필요하다.
- 게시 가능한 `active` Binding은 각각의 `locations` key, `auth_schemes`, 설정된 `transport`, 비어 있지 않은 `operation_refs`, MCP `mcp_primitives`에 Evidence가 있어야 한다. Evidence 존재는 그 주장이 사실이라는 보증이 아니다. 검색 인덱스에서 하드 제약을 `satisfies`로 내보내려면 해당 필드 주장이 A/B 출처이고 `verified` 상태여야 하며, 그렇지 않으면 `unknown`으로 둔다. Active Operation은 `effect`와 비어 있지 않은 `inputs`에 Evidence가 필요하다.
- `auth_schemes`는 하나 이상이어야 한다. 배열은 대안 인증 방식을 뜻하므로 `none`은 `bearer` 등과 함께 올 수 있다. `unknown`은 단독 값으로만 허용하며 미확인 상태를 빈 배열로 표시하지 않는다.
- URL은 절대 `https` URL을 기본으로 한다. 제공자가 공식적으로 다른 scheme을 요구하는 MCP/SDK 설치 명령은 package 좌표나 문서 URL로 기록하고 예외 주소는 사람 리뷰를 받는다. registry 패키지는 `package` 이름과 허용 `registry` 값을 모두 요구한다.
- 모든 참조는 해소되어야 하고 ID는 전역 유일해야 한다. operation ref의 `native_ref`는 해당 Binding의 종류와 맞아야 한다. 같은 Binding-Operation 쌍 중복은 금지한다.
- 모든 `active` Operation은 하나 이상의 `active` Binding에서 참조되어야 한다. 미참조 Operation은 CI 경고를 내고 검색 산출물에서 제외한다. 참조 대상이 없는 Binding은 `draft`일 때만 허용한다. 참조 오류는 CI 실패다.
- `resource_kind`와 `transport` 조합은 CI에서 검사한다. `http_api`는 `http` 또는 `unknown`; `mcp_server`는 `stdio`, `streamable_http`, `sse`, `unknown`만 허용하며 `sse`는 호환용 폐기 예정 값으로 경고한다; `sdk`는 transport를 생략할 수 있고 지정 시 `other` 또는 `unknown`만 허용한다. `agent_connector`와 `other`는 설명에 근거한 조합만 사람 리뷰로 승인한다.
- `other`는 필요한 자원 종류가 열거값에 없을 때만 허용하고 설명 및 사람 리뷰를 요구한다. 새 종류가 반복되면 `other`를 남발하지 말고 vocab/schema 버전 변경으로 추가한다.

다음은 값의 배치만 보여주는 가상 예시다. 실제 서비스나 주소를 뜻하지 않는다.

```yaml
# data/services/acme-search/service.yaml
service: {id: svc_acme_search, name: Acme Search, provider_name: Acme Labs,
  summary: 가상 문서 검색 서비스, status: active}
integrations:
  - id: int_acme_search
    service_id: svc_acme_search
    name: 문서 검색
    summary: 문서 집합에서 질의와 관련된 문서를 찾는다.
    status: active
bindings:
  - id: bnd_acme_search_api
    integration_id: int_acme_search
    resource_kind: http_api
    name: HTTP API
    locations:
      docs_url: {url: https://docs.example.invalid/search}
      api_base_url: {url: https://api.example.invalid/v2}
      api_spec_url: {url: https://api.example.invalid/openapi.json}
    auth_schemes: [api_key]
    transport: http
    status: active
    operation_refs:
      - operation_id: op_search_documents
        native_ref: {kind: http_operation, value: 'GET /v2/search'}
  - id: bnd_acme_search_mcp
    integration_id: int_acme_search
    resource_kind: mcp_server
    name: 로컬 MCP 서버
    locations:
      mcp_package: {package: '@acme/search-mcp', registry: npm}
      mcp_repo_url: {url: https://github.com/acme/search-mcp}
    transport: stdio
    auth_schemes: [api_key]
    mcp_primitives: [tool]
    status: active
    operation_refs:
      - operation_id: op_search_documents
        native_ref: {kind: mcp_tool, value: search_documents}
```

```yaml
# data/operations/op_search_documents.yaml
id: op_search_documents
name: search_documents
purpose: 문서 집합에서 질의와 관련된 문서를 찾는다.
category_ids: [retrieval]
aliases: [문서 검색, 관련 구절 찾기]
entity_types: [document, passage]
effect: read
```

```yaml
# data/evidence/ev_api_endpoint.yaml
id: ev_api_endpoint
subject_id: bnd_acme_search_api
claim_path: /locations/api_base_url/url
source_url: https://docs.example.invalid/search#endpoint
source_type: official_docs
source_grade: A
verification_state: verified
verified_at: '2026-10-27T00:00:00Z'
source_locator: 'Endpoint > Base URL'
verification_method: manual_review
```

이 예시에서 Operation은 검색 목적을 한 번만 정의하고 API·MCP Binding 양쪽이 구현한다. `operation_refs`가 단일 작성 관계이며, 게시 빌드는 Operation 상세에서 Binding ID 목록을 역방향으로 생성한다. SDK가 같은 작업을 제공하면 같은 Integration에 세 번째 Binding과 패키지 위치를 추가할 수 있다.

### Evidence와 최신성 정책

MVP는 **Source 레코드와 Claim 레코드를 별도로 두지 않는다**. Evidence 하나가 `subject_id + claim_path`로 표현한 단일 필드 주장과 한 출처를 연결한다. 같은 URL은 여러 Evidence에서 반복할 수 있고, 같은 필드는 여러 출처의 Evidence를 가질 수 있다. 중복 URL이 실제 운영 부담이 된 뒤에만 Source 정규화를 검토한다. Evidence에는 주장 값을 복사하지 않는다. 그 값은 대상 레코드에 단 한 번만 존재한다.

필수 근거 대상은 Binding의 위치, 버전(있을 때), 전송, 인증, 생명주기, Binding→Operation 연결이다. Operation의 목적·효과도 공식 설명/명세로 뒷받침할 수 있으면 근거를 둔다. 등급 A/B를 확보하지 못한 값은 C/D로 표시하고 `verified`라고 부풀리지 않는다. 출처 권위(`source_grade`), 내용 확인 상태(`verification_state`), 자동 링크 상태(`ok`, `redirect`, `unreachable`, `not_checked`)는 서로 다른 축이다.

자동 링크 검사 실패는 출처에 접근하지 못했다는 관측만 바꾼다. 한 번의 timeout, 403, 차단, 리다이렉트는 주장이나 출처 등급을 자동으로 무효화하지 않는다. 반복 점검 실패는 Evidence를 `needs_review`로 표시해 검토 대기시킬 수 있지만 `stale`, `contradicted`, Binding `archived`로 자동 변경하지 않는다. 사람이 자료의 내용이나 제공자 상태를 재확인한 경우에만 `stale` 또는 `contradicted`로 갱신한다. 상충하는 근거가 있으면 모두 유지하고 해당 필드의 상태를 `contradicted` 또는 `needs_review`로 둔다. 검색 결과는 상태와 마지막 확인 시점을 노출하며, 핵심 필드의 미확인을 `verified`로 간주하지 않는다.

YAML이 유일한 편집 정본이다. 빌드가 ID 참조를 검증해 그래프를 만들며, 그래프 자체는 편집 정본이 아니라 게시물을 생성하기 위한 중간 표현이다. Service → Integration → Binding은 소유·구현 경로를 나타내지만 Operation은 여러 Binding에 연결되므로 특정 Service 하위에만 고정하지 않는다. 사람용 계층 탐색은 그래프에서 생성한 뷰이고, 목표 중심 검색은 간결한 전역 Operation 색인을 사용한다.

### 원본 저장소 구조 초안

```text
api-capability-map/
├── README.md
├── data/
│   ├── services/<service-id>/
│   │   ├── service.yaml       # Service·Integration·Binding의 서비스 맥락 편집 묶음
│   ├── operations/<operation-id>.yaml # 재사용 가능한 Operation 하나당 파일 하나
│   ├── evidence/<evidence-id>.yaml     # Service/Operation을 가로지르는 근거 한 건
│   └── vocab/                 # 도메인·효과·인증 등 작은 통제 어휘
├── schemas/v1/
├── evals/golden/
├── site/                      # 정적 페이지와 생성 산출물
├── scripts/
└── .github/workflows/
```

초기 편집 구조는 **서비스 묶음 + 독립 Operation 파일 + 독립 Evidence 파일**의 혼합형이다. 서비스의 Integration과 Binding은 함께 검토할 수 있도록 서비스 폴더에 둔다. 여러 서비스가 구현할 수 있는 의미상의 Operation은 독립 파일로 둔다. Evidence는 전역 대상 ID를 가리킬 수 있도록 별도 폴더에 둔다. Evidence마다 `subject_id + claim_path + source_url`을 기록하고 Source를 별도 ID로 정규화하지 않는다. 서비스 파일이 약 400줄을 넘거나 Binding이 15개를 넘거나 반복적인 병합 충돌이 생기면 Integration·Binding 파일 분리를 검토한다. 이는 초기 운영 가설이며 실제 수정·검토 경험으로 조정한다.

YAML은 사람이 작성·리뷰하는 유일한 정본이다. JSON Schema는 필드와 타입을 검증하고 추가 CI 검사는 ID·관계·의미 규칙을 확인한다. JSON·JSONL·검색 인덱스·HTML은 전부 생성물이며 수동으로 정본처럼 수정하지 않는다. 모든 레코드는 고유하고 공개 후 바뀌지 않는 ID를 가진다. Binding의 `operation_refs`가 Operation 연결의 단일 원본이며, Operation의 역참조는 빌드에서 생성해 양방향 참조의 불일치를 방지한다. 탐색 분류는 통제 어휘 `Category`로 관리하고 Operation과 정보 출처가 여러 Category에 연결될 수 있게 한다.

`InformationResource`는 데이터셋·문서·지식 베이스·검색 색인·디렉터리처럼 에이전트가 정보를 얻는 대상을 표현한다. 호출 가능한 기능을 뜻하는 `Operation`에 정보 출처를 억지로 넣지 않는다. 정보 출처가 API나 MCP를 통해 조회될 수 있으면 InformationResource와 Service/Binding 사이의 관계를 연결하되, 정보 자체와 조회 동작은 별도 레코드로 표현한다. MVP에서는 `InformationResource`의 범위를 좁혀 탐색·비교에 필요한 유형과 출처·갱신·범위 메타데이터만 정의하고, 별도 지식 그래프나 실행기는 만들지 않는다.

Evidence는 출처 등급(`source_grade`), 내용 검증 상태(`verification_state`), 링크 점검 결과, 확인 방법·시점을 분리한다. 주장은 `subject_id`와 RFC 6901 JSON Pointer 형식의 `claim_path`로 특정하며, 대상 필드 값을 Evidence에 복사하지 않는다. `claim_path`의 기준 문서는 빌드 시 생성되는 canonical subject JSON 레코드다. 예를 들어 `bnd_acme_search_http`의 API URL은 `/locations/api_base_url/url`로 가리킨다. YAML 점 표기법이나 소스 파일 경로는 허용하지 않는다. CI는 포인터 문법과 실제 대상 경로 존재를 검사한다. 배열 순서 변경에 취약한 숫자 인덱스는 금지하며 배열 전체를 가리키고 원소 위치는 `source_locator`에 설명한다. 출처 등급은 권위만 나타내며 최신성이나 주장의 진실성을 대신하지 않는다. 한 출처가 여러 주장을 뒷받침하면 Evidence 여러 건에서 URL을 반복한다. 자동 해시 봉인보다 변경 영향에 따른 재검토 표시를 우선한다.

### 게시 경로 초안

```text
/catalog/v1/manifest.json                  # schema_version, catalog_revision, 인덱스 URL
/catalog/v1/browse/tree.json               # 사람·AI 공용의 목적 중심 분류 그래프와 하위 항목 요약
/catalog/v1/search/index.json              # 정보 출처·Operation을 함께 찾는 사람·AI 공용 후보 검색 인덱스
/catalog/v1/resources/<slug>.json          # InformationResource 상세와 출처·범위·갱신 정보
/catalog/v1/operations/<slug>.json         # Operation 상세와 Binding ID
/catalog/v1/bindings/<slug>.json           # 선택한 구현의 요구조건과 네이티브 식별자
/catalog/v1/evidence/<slug>.json           # 요청된 claim의 출처·검증 정보
/catalog/v1/services/<slug>.json           # 서비스 탐색 페이지에 필요한 상세
/catalog/v1/bulk/catalog.jsonl             # 전체 정규화 데이터, 일괄 처리 전용
/llms.txt                                  # 진입점·조회 순서·전체 덤프 주의 안내
```

사람용 UI와 AI용 산출물은 같은 검증된 데이터에서 생성한다. 두 이용자는 같은 분류와 검색 의미를 쓰며, UI는 카드·필터·설명으로, 에이전트 응답은 토큰 예산에 맞춘 간결한 JSON으로 표현한다. `llms.txt`는 진입 안내이지 분류 체계나 정본이 아니다. manifest에는 스키마 버전, 카탈로그 리비전, 양쪽 탐색 경로, 파일 크기·레코드 수를 기록한다. 초기에는 작은 전체 후보 인덱스를 쓸 수 있고, 실제 다운로드 크기·토큰·검색 지연이 설정한 한도를 넘을 때만 Category 단위 파일 분할을 추가한다. 공개 URL과 필드 호환성은 v1 소비자 계약으로 취급하고, 호환되지 않는 변경은 주 버전을 올려 마이그레이션 안내를 제공한다.

### AI 조회와 비용 원칙

전체 덤프를 제공하는 것만으로 토큰 비용이 낮아지지는 않는다. JSONL은 일괄 처리에는 편리하지만, 매 질의마다 전체 Operation과 Evidence를 모델 문맥에 넣으면 카탈로그가 커질수록 불필요한 입력 비용과 선택 오류가 늘어난다. 기본 이용 흐름은 다음의 단계 조회로 한다.

```text
manifest (버전과 탐색 경로 확인·캐시)
  → 분류 그래프 또는 키워드 인덱스 검색 (필요하면 두 경로 결합)
  → 상위 후보 요약만 확인
  → 선택한 정보 출처 또는 Operation 상세 조회
  → 도구라면 Binding, 필요한 주장이라면 Evidence만 추가 조회
```

`search/index.json`에는 안정 ID, 레코드 종류(`information_resource` 또는 `operation`), 짧은 목적, 별칭, Category 경로, 핵심 범위·제약 요약, Evidence 상태와 상세 URL 등 후보를 좁히는 필드만 둔다. Binding의 인증·전송·상태 속성을 Operation 수준의 합집합으로 합치지 않는다. 하드 제약은 같은 Binding 한 건의 모든 조건을 함께 검사하고, Operation은 적어도 한 Binding이 전체 조건을 만족할 때만 `satisfies`로 판정한다. 전체 스키마와 장문 설명은 넣지 않는다. 검색 결과 기본 limit은 5, 최대 20으로 시작하며 평가 데이터에서 조정한다. 사람용 브라우저 검색, 분류 탐색과 AI 참조 검색기는 같은 분류·후보 데이터를 사용한다. 정적 Pages에는 서버 측 검색이 없으므로 AI 클라이언트는 manifest가 가리키는 작은 인덱스를 가져와 로컬 검색하거나 참조 검색기를 사용해야 한다. MCP를 도입하면 동일한 검색·필터 함수를 감싼다.

MVP 검색 순서는 버전이 고정된 결정적 lexical baseline으로 한다. 질의와 `name`, `aliases`, `purpose`, `entity_types`를 Unicode NFKC 정규화 후 소문자화하고 토큰화한다. 기본 점수는 정확한 이름 일치 10, 이름 토큰 일치 5, alias 일치 4, purpose 일치 2, entity type 일치 1이며 한 필드 안의 반복 단어는 중복 가산하지 않는다. 점수 내림차순, 동점이면 안정 ID 오름차순으로 정렬한다. 구조화된 하드 필터는 순위 계산 전에 Binding별로 적용한다. 임계 점수 미달 또는 모든 Binding이 제약 위반/미확인인 경우 `{abstain: true, results: []}`를 반환한다. 점수, 정규화 규칙과 알고리즘 버전을 manifest에 기록하고 holdout 실행 전에 고정한다. 의미 검색은 이 baseline과 분리해 평가한 뒤 추가한다.

초기 카탈로그에서는 하나의 검색 인덱스와 Category 탐색 파일로 시작한다. 분할은 임의의 레코드 수가 아니라 실제 직렬화 크기·전송량·토큰 예산·응답 시간 측정이 합의된 한도를 넘을 때만 한다. 전체 `bulk/catalog.jsonl`은 로컬 색인 구축, 일괄 동기화, 평가용이며 일반 질의의 기본 경로로 사용하지 않는다. manifest와 리비전이 고정된 산출물은 캐시 가능하게 만들고, 모든 결과에서 catalog revision을 확인할 수 있게 한다.

Evidence는 안전성 또는 실행 가능성 판정에 필요한 경우 후보별로 조회한다. 색인에는 검증 상태와 시점의 짧은 요약을 제공해, 불확실한 항목을 상세 조회 없이도 걸러내거나 `unknown`으로 표시할 수 있게 한다. 단, 중요 제약의 근거가 없는 후보를 검증된 것으로 취급하지 않는다.

### 미확인 사항을 중심으로 한 탐색과 종료

소비 에이전트의 기본 흐름은 다음과 같다. 상세 도구 호출 순서를 모든 과제에 강제하지 않으며, 이미 확인된 범위나 후보 부재를 알 수 있으면 불필요한 조회를 생략한다.

```text
요청의 필수조건·선호조건·검증 수준·예산 정리
  → 지도에서 목적과 수록 범위 확인
  → 적합 후보의 기능·제약·근거를 필요한 만큼 조회
  → 충족·위반·미확인 조건을 후보별로 비교
  → 중요 미확인·근거 충돌·수록 범위 밖 요구만 외부 탐색
  → 이번 요청의 종료 조건으로 완료·보류·예산 종료 판정
  → 재사용 가능한 발견과 실패 경로를 검토 대상으로 남김
```

필수조건은 같은 후보·Binding의 근거로 충족해야 한다. 선호조건 미충족은 필수조건 위반과 구분하며, 무료·무인증·다른 구현을 끝없이 찾는 이유로 사용하지 않는다. 원문의 추가 확인 여부는 주장 중요도·변경 위험·근거 상태와 버전에 따라 정한다. 모든 근거를 일괄 신뢰하거나 매번 전부 다시 읽는 정책으로 고정하지 않는다.

| 요청의 검증 수준 | 종료 또는 보류 기준 |
|---|---|
| 후보 발견 | 요청 범위에 맞는 후보와 직접 근거를 식별하고, 미확인 제약을 표시하면 발견 단계 종료. 데이터 확보·작업 완료로 표시하지 않음 |
| 문서 기반 선택 | 필수조건과 중요 제약의 근거를 확인하고 치명적 미확인·충돌이 해소되면 선택 종료. 비교 후보 수·탐색 예산·선호조건의 우선순위는 사전 고정 |
| 실응답 확인 | 허용된 실제 요청의 상태·응답과 요구 출력을 확인해야 완료. 인증·접근 권한이 준비되지 않으면 필요한 준비와 차단 사유를 기록 |
| 실제 작업 완료 | 요구 산출물과 정확성 검사를 통과해야 완료. 서울 OD는 공식 키·시점·CRS·미매칭·경계 처리를 검증한 실제 결합이 필요 |
| 예산 종료·근거 부족 | 확인된 범위, 남은 중요 미확인 사항, 차단 이유를 남기고 보류. 예산 소진을 해법 부재나 완료로 바꾸지 않음 |

평가용 결과 계약은 후보 발견·문서 검증·실응답 확인·작업 완료를 별도 상태로 기록한다. 하나의 `found` 또는 `blocked` 값으로 모두 표현하지 않는다. 이 계약은 우선 평가 하네스에서 검증하고, 그 이유만으로 공개 카탈로그 스키마를 확대하지 않는다.

### 과제별 판정 계약

구현 착수 시 다음 최소 계약을 평가 파일로 먼저 확정한다. 현재 R0의 `result.schema.json`은 과거 기록용으로 보존하고, 후속 시험에는 버전이 다른 요청·결과 계약을 사용한다.

| 계약 | 필수 내용 |
|---|---|
| 요청 | `task_id`, `verification_level`, `requirements`, `preferences`, `comparison_scope`, `budget`, `stop_rules` |
| 필수조건 | 안정된 `requirement_id`, 검사할 내용, 적용 단계, 허용 근거 유형·버전/시점, 판정 방법, 미확인·충돌 시 처리 |
| 선호조건 | 선호 순서 또는 동률 처리 규칙. 실행 중 임의로 필수조건으로 승격하지 않음 |
| 후보별 판정 | 조건별 `satisfied / violated / unknown / conflicted`, 직접 Evidence 또는 응답 참조, 확인 시점, 적용 대상 Binding·자료 버전 |
| 단계별 결과 | 후보 발견·문서 검증·실응답·작업 완료 각각 `passed / failed / blocked / not_run`. 후속 단계를 수행하지 않았으면 `not_run` |
| 종료 | `requirements_met / evidence_insufficient / evidence_conflict / access_blocked / budget_exhausted / no_candidate_in_scope`, 미확인 조건 ID와 종료 이벤트 참조 |

`verification_level`은 후보 발견·문서 기반 선택·실응답 확인·작업 완료 중 하나로 고정한다. 각 수준에서 충족해야 하는 조건 ID를 실행 전에 지정하고, 에이전트가 실행 중 중요 조건을 삭제하거나 허용 근거를 완화하지 못하게 한다. 후보 발견 수준에서는 인증 등 미확인 제약을 표시한 채 종료할 수 있지만, 그것이 문서 기반 선택이나 실행 조건의 충족은 아니다. 문서 기반 선택 이상에서는 해당 단계의 모든 필수조건이 `satisfied`이고 충돌이 없어야 완료한다. 그 밖의 종료는 보류·실패·범위 내 후보 미발견으로 구분한다.

검색기의 Binding `satisfies`는 **전달되어 실제 평가된 필터 범위**에서만 해석한다. 소비 에이전트는 `evaluated_requirement_ids`와 `unchecked_requirement_ids`를 구분하고, 검색기가 지원하지 않는 상업 이용·정밀도 등의 조건은 문서·응답 근거로 별도 평가한다. 검색 결과만으로 요청 전체 충족을 선언하지 않는다. 미지원 필터와 검증된 위반을 구분하는 소비 계약도 보정 시험에서 확인한다. 검색 무결과는 정본·질의·필터 범위의 관측이며 인터넷 전체의 후보 부재로 해석하지 않는다.

종료 판정은 모델의 자기보고만으로 채점하지 않는다. 사전 고정한 조건표와 이벤트·Evidence 참조를 대조해 평가하고, 근거를 재구성하지 못하면 미판정으로 남긴다. 원문 변경 등으로 기준을 수정해야 하면 새 과제/계약 버전으로 재실행하며 이전 결과를 덮어쓰지 않는다.

### 후속 MCP 조회 계약 초안

MCP 프로토콜의 `tools/list`는 MCP 서버가 제공하는 도구 설명을 발견하는 기능이다. 여기서 `catalog.search_operations`는 MCP 기본 메서드가 아니라 이 카탈로그 서버가 정의하는 애플리케이션 도구다. 카탈로그 항목마다 MCP 도구를 하나씩 만들지 않는다. 도구 목록은 작고 고정된 상태로 유지한다. [MCP 도구 호출·목록 문서](https://ts.sdk.modelcontextprotocol.io/v2/clients/calling)

| 읽기 전용 도구 | 책임과 반환 범위 |
|---|---|
| `catalog.search_operations` | 자연어 질의와 구조화 필터로 Operation 후보를 찾는다. 기본 상위 5개 이내의 짧은 요약, 안정 ID, 일치 이유, 제약 상태를 반환한다. |
| `catalog.get_operation` | 단일 Operation의 의미 계약과 연결된 Binding ID, 제약·효과 요약을 반환한다. 모든 Binding과 Evidence 전문을 펼치지 않는다. |
| `catalog.get_binding` | 단일 Binding의 프로토콜, 버전, 도구/엔드포인트 식별자, 공개 인증 요구, 네이티브 입력·출력 스키마를 반환한다. 비밀값은 포함하지 않는다. |
| `catalog.get_evidence` | 지정된 Evidence 또는 claim의 출처와 검증 정보를 반환한다. |

이 고정된 네 도구는 카탈로그 레코드 수와 무관하다. `catalog.browse`와 개별 Service·Integration 도구는 사람용 Pages 탐색으로 제공하며, AI 이용 평가에서 필요성이 확인될 때 MCP 도구 추가를 검토한다. `tools/list`는 서버가 제공하는 도구를 알리는 MCP 기능이지 카탈로그 항목 검색 API가 아니다. 검색 결과에는 짧은 후보만 반환하고 상세는 ID로 따로 요청한다.

MCP 어댑터 구현은 MVP에서 제외하고 후속 단계로 둔다. 진입 조건은 정적 검색 평가 기준 통과와 실제 MCP 클라이언트 또는 사용자 통합 수요 확인이다. 후속 로컬 stdio 어댑터는 Pages에 게시된 manifest·색인·상세 파일만 읽으며, 자체 DB·자격증명·실행 상태를 두지 않는다. 참조 검색기와 동일한 골든 질의에서 동일한 Operation ID와 순서를 반환하는 동등성 검사를 통과해야 한다. 공개 호스팅 MCP 서버는 별도 운영 근거가 생길 때 결정한다.

## 6. 변경·검증·게시 흐름

```text
유지관리자가 YAML 수정
  → Pull Request
  → 형식·스키마·ID·참조·보안 검사
  → 생성물·검색 결과·영향 요약 미리보기
  → Evidence와 의미 변경에 대한 사람 리뷰
  → 기본 브랜치 병합
  → GitHub Actions 빌드
  → GitHub Pages 배포
```

CI 필수 검사:

- YAML 파싱 및 JSON Schema 검증
- ID 중복·불변성, 참조 무결성, Binding의 `operation_refs` 연결 유효성
- 허용 enum, URL/package 위치 타입과 `resource_kind`/`transport` 조합, ID 패턴, `claim_path` RFC 6901 문법과 대상 필드 존재를 검증
- 필수 Evidence 누락 및 대상 참조 검증. 같은 `(subject_id, claim_path, source_url)` 중복은 막되 서로 다른 출처의 반복 근거는 허용
- `operation_refs[].native_ref.kind`와 Binding 종류의 불일치, 사유 없는 `other` 사용을 검출
- 그래프의 역참조를 생성하고, 서비스 탐색 인덱스와 Operation 검색 인덱스 일관성 확인
- active Operation의 active Binding 연결 여부를 확인하고 미연결 항목은 검색 인덱스에서 제외
- 하드 제약 판정이 Binding 한 건의 조건만으로 계산되는지 검증해 속성 합집합에 따른 false pass 방지
- active Binding의 위치·인증·전송·기능 매핑과 active Operation의 입력·효과 Evidence 누락 여부 확인. `satisfies` 표시는 같은 Binding의 모든 하드 조건이 A/B 등급의 verified 근거를 가질 때만 허용
- 탐색 인덱스의 모든 자식 ID와 상세 URL이 존재하고, 순환 부모 관계가 없는지 확인
- 근거가 필요한 필드의 Evidence 존재 여부와 상태 표시. CI는 미확인 값을 검증 완료로 승격하지 않음
- 생성된 JSON/JSONL의 구조와 결정적 빌드 확인
- 비밀정보 스캔 및 비공개 필드 차단
- 골든 질의 평가와 회귀 확인
- 생성 결과의 ID·필드 변경, 영향받는 Operation/Binding, Evidence 재검토 필요, 검색 순위·응답 크기 변화를 요약

공개 저장소에 올라간 비밀정보는 이후 파일에서 지워도 Git 이력에 남을 수 있으므로 병합 전 탐지를 필수로 둔다. 모든 자유 텍스트 설명은 외부 지시로 실행하지 않고, 근거가 없는 MCP 주석이나 제공자 설명은 보안 보증으로 간주하지 않는다.

### 탐색 경험의 정본 반영

탐색 기록은 원문 도구 요청·응답 참조, 후보 ID, 선택·탈락의 짧은 사유, 미확인 항목, 추가 확인 경로, 종료 상태를 남긴다. 관측 가능한 행동과 판단 결과를 기록하며 모델의 비공개 내부 추론 전문을 요구하지 않는다. 인증정보·개인정보·비공개 대화는 공개 정본에 포함하지 않는다.

여러 과제에서 반복된 유용한 발견을 검토해 기존 레코드의 별칭·범위·제약·Evidence·공식 접근 경로에 반영한다. 한 번의 실패에서 곧바로 새 필드나 영구 정책을 만들지 않는다. 원문 접근 실패는 경로·도구·시각에 묶인 관측이며 자료 부재로 일반화하지 않는다. 재시도 회피 지식도 조건·유효기간·대체 경로를 함께 검토한다. 추측한 ID 대응이나 근거 없는 후보 배제는 재사용 지식으로 승격하지 않는다.

## 7. 단계와 완료 기준

### 0단계: 결정과 기준 확정

- 가칭 `agent-capability-map`으로 공개 저장소를 준비하고, 데이터 CC0-1.0·코드 MIT 제안과 외부 기여 비허용 정책을 기록한다.
- 초기 범주에서 RAG는 분야·역량 범주로, API·MCP·SDK는 연결 방식이나 구현 유형으로 구분한다. RAG 기법 자체는 Service/Integration이 아니므로, 실제로 조회 가능한 제품·라이브러리·자료인지 Operation/Binding을 제공하는 사례인지 포함 기준을 명시한다.
- 첫 화면의 두 동등한 진입 경로(목적 중심 분류 탐색, 키워드 검색)와 두 경로를 결합하는 규칙을 고정한다. 분류를 제공자·프로토콜 목록으로 대체하지 않고, 정보 출처와 실행 도구를 모두 후보로 찾을 수 있게 한다.
- Category는 여러 상위 목적에 연결될 수 있는 통제 분류 그래프로 정의한다. `InformationResource`와 `Operation`이 분류를 공유하되 상세 계약은 분리하는 최소 스키마 변경안을 확정한다.
- 원본은 서비스별 편집 묶음과 독립 Operation 파일을 결합한다. MCP 어댑터는 후속 단계로 두고, MVP는 정적 파일을 통한 AI 검색과 단계 조회를 검증한다.
- MVP는 최소 기능 제품(Minimum Viable Product), 즉 핵심 이용 흐름이 실제로 유용한지 검증할 가장 작은 완성 범위다. 이 계획에서는 YAML 계약·검증, 같은 분류와 검색을 쓰는 Pages 사람용 탐색, AI용 단계 조회 파일, 변경 영향 검토, 고정 골든 질의 평가가 핵심이다.

**완료 기준:** 결정 기록, 공개 데이터 정책, 기여·리뷰 책임자, 정보 출처와 실행 도구의 구분, 분류 및 검색의 공통 계약이 문서화되어 있다.

### 1단계: 최소 데이터 계약과 예시

- 핵심 객체, 불변 ID 규칙, 관계 방향, 필수·선택 필드, Category 그래프, 최소 `InformationResource`, Evidence 출처 등급과 검증 상태를 정의한다.
- 초기 seed는 약 5~10개 Service와 20~50개 Operation, 해당 기능을 구현하는 Integration·Binding으로 구성한다. 이는 초기 평가 규모 제안이며 실제 근거가 준비된 항목 수에 따라 조정한다.
- 내부 유지관리자가 쓰는 PR 체크리스트와 작성 예제를 둔다. 외부 기여 안내는 공개하되 외부 제출은 받지 않는다는 정책과 모순되지 않게 한다.

**완료 기준:** 정보 출처와 실행 도구를 각각 표현한 예시 데이터가 스키마와 참조 검사를 통과하고, 하나의 후보를 여러 목적 분류에서 찾을 수 있으며, 사람이 PR에서 변경 이유와 Evidence를 리뷰할 수 있다.

### 2단계: 생성과 게시

- YAML 원본에서 manifest, 공용 후보 검색 인덱스, 사람·AI 공용 분류 그래프, 정보 출처·Operation·Binding·Evidence 상세 JSON, bulk JSONL과 정적 사이트를 생성한다.
- pull request 검사와 기본 브랜치 Pages 배포를 구성한다.
- PR에서는 생성물 미리보기와 의미 영향 요약을 검토하고, 병합 후 Actions가 동일한 빌드를 Pages에 게시한다.
- 소비자는 manifest의 catalog revision을 기준으로 산출물 일관성과 캐시를 확인한다.

**완료 기준:** 빌드가 재현 가능하고, Pages에서 사람용 UI와 기계용 파일을 모두 읽을 수 있다. 비밀정보는 배포 산출물에 포함되지 않는다.

사람용 UI는 분류 탐색과 키워드 검색을 첫 화면에서 모두 제공한다. 분류를 내려가면서 범위를 좁힌 뒤 그 안에서 검색할 수 있고, 검색 결과에서도 Category 경로를 따라 다시 탐색할 수 있다. 정보 출처와 실행 도구는 같은 후보 목록에서 구별 가능한 종류로 표시한다.

### 3단계: 실행 파일럿과 후속 성능 입증

먼저 1인 운영자가 실행 가능한 작은 파일럿으로 탐색·판단·연결 절차와 실패 유형을 확인한다. 이후 충분한 독립 과제와 계측을 확보한 확증 시험에서 성능 가설을 검증한다. 파일럿을 수행했다는 사실만으로 지도 효용이나 토큰 절감을 입증했다고 보고하지 않는다. 이번 개정의 판단 근거와 채택하지 않은 제안은 [2026-11-01 검토 기록](./internet-map-review-summary-2026-11-01.md)에 둔다.

- 동의어·다른 표현·제약 포함·적합 항목 없음 사례를 포함하고, 정보 출처 탐색과 도구 선택을 모두 다루는 버전 관리 골든 질의를 준비한다.
- 개발용 과제에서 `분류만`, `키워드만`, `두 방식 결합` 경로를 비교하고 외부 대조 시험 전에 경로를 고정한다. 경로 선정에 사용한 과제는 외부 효용 평가용 holdout으로 재사용하지 않는다.
- 정적 인덱스와 참조 검색기로 정보 출처 또는 Operation 후보를 찾고, 도구 과제에서는 올바른 Binding과 권한·전송 조건·Evidence 부족의 설명을 확인한다.
- 에이전트는 전체 카탈로그가 아니라 필요한 분류 노드와 후보 상세만 읽는지 확인한다. 모델 입력 토큰, 다운로드 바이트, 요청 수, 탐색 깊이, 첫 유효 후보까지 시간과 과제 완료 시간을 기록한다.
- 사람 사용성 검토에서는 성공한 후보 선택률, 검색·클릭 횟수, 후보를 찾는 시간, 분류 용어의 이해도를 기록한다.
- 위 탐색 방식 비교 후 가장 나은 지도 탐색을 고정하고, 그 경로를 일반 웹 검색 및 원래 디렉터리 직접 탐색과 비교해 지도 자체의 효용을 평가한다.
- 사용자 테스트 계정 또는 무해한 샌드박스 자원을 이용해 제한된 실제 작업을 완료하는 별도 하네스를 둔다. 카탈로그는 실행·자격증명을 제공하지 않으며, 같은 허용 자원을 지도 사용군과 대조군에 제공한다.

비교 실험은 두 층으로 구분한다.

| 시험 | 지도 사용군 | 대조군 | 측정 |
|---|---|---|---|
| 탐색 방식 | 분류 탐색, 키워드 검색, 두 방식 결합 | 동일한 과제·카탈로그의 대안 탐색 방식 | 후보 정확도, 첫 정답까지 시간, 탐색 단계·요청 수; 에이전트 입력 토큰·전송 바이트, 사람 검색·클릭 수 |
| 카탈로그 효용 | 확정된 최적 지도 경로로 정보 출처·도구 탐색 | 같은 과제에서 일반 웹 검색 또는 원 디렉터리 직접 탐색 | 올바른 자원·Operation/Binding, 제약 위반, 무결과 보류, 시간·토큰·가져온 바이트 |
| 작업 완료 | 지도에서 찾은 Binding으로 테스트 하네스가 연결·실행 | 지도 없이 같은 허용 자원·권한으로 탐색·연결·실행 | 작업 성공률, 전체 시간, 총 토큰, 호출 수, 오류 유형 |

두 군은 같은 모델, 프롬프트 제약, 자원 권한, 시간·호출 한도를 사용한다. 과제 순서는 무작위화하고 새 대화 문맥을 사용해 반복 과제 학습을 줄인다. Gold set은 정답 Operation, 허용 Binding, 하드 제약, 정답 없음 여부, 작업 완료 판정을 실행 전에 고정한다. 과제는 이름 일치, 표현 바꾸기, 복수 제약, 정답 없음, 안전상 선택 불가 유형을 포함한다. 사용자 데이터 변경, 결제, 영구 삭제는 제외하고 테스트 계정에서 되돌릴 수 있는 작업만 사용한다.

### 시험 단계와 판정 게이트

G0·G1의 필수 계약과 기능을 확인한 뒤, G2의 안전상 치명 오류를 수정하고 G3의 탐색적 파일럿을 진행한다. G2의 통계 표본 부족은 파일럿 진행을 막지 않으며 성능 입증의 한계로 기록한다. G4는 필수 데이터·권한·안전 조건이 갖춰진 하위 과제에서 수행한다. 회귀 확인에는 개발 세트를 쓰고, 결과를 본 holdout으로 반복 튜닝한 뒤 독립 성능이라고 보고하지 않는다. 확증 시험에는 별도로 잠근 미사용 평가 세트를 쓴다.

| 게이트 | 확인 대상 | 반복 가능한 절차 | 통과 조건 |
|---|---|---|---|
| G0 계약·빌드 | YAML, 스키마·ID·분류와 참조·생성 파일 | 전체 무결성·비밀정보 검사, 두 번 빌드 비교, 핵심 Evidence의 확인 시점·버전 변화·출처 접근 상태 재확인 | 계약 오류 0건·산출물 재현. 링크 도달성과 주장 최신성은 별도 판정하며 미확인은 표시 |
| G1 탐색 동작 | 사람 UI와 에이전트 조회 | 분류·검색·혼합·필터·결과 없음·상세/근거의 고정 시나리오 | 같은 질의·필터·리비전의 사람/AI 구현은 같은 ID·종류·제약·Evidence를 반환. 서로 다른 탐색 전략의 결과 전체가 같을 필요는 없으며 정답 도달과 제약 판단으로 비교 |
| G2 검색 품질·안전 | 후보 적합성·제약·보류 | 기대 집합·허용 대안·판정 규칙을 고정하고 미등록/근거 부족/비신뢰 설명문 사례 포함 | 관측된 치명 오류·하드 제약 거짓 통과는 수정 후 회귀. 품질 지표와 분모·구간은 보고하되 소표본의 수치 미달만으로 탐색 파일럿을 차단하지 않음 |
| G3 지도 효용 | 지도 우선·웹·원 디렉터리 비교 | 개발 세트로 경로 선정 후 별도 평가 과제와 고정 예산으로 비교 | 파일럿은 관측 차이·실패 유형·한계 보고. 확증 시험만 사전 수치 목표로 판정 |
| G4 제한된 작업 완료 | 실제 읽기 전용 연결·결과 | 같은 자원·권한의 별도 하네스에서 실행하고 결과 검증 | success/failed/blocked/not_run 구분. 정확한 보류는 탐색 판단 성공일 수 있으나 실제 작업 성공이 아님. 전체 시도 중 차단 비율과 실행 가능 하위집합의 성공률을 함께 보고 |

### 골든 과제와 정답표

각 과제는 독립 ID와 다음 값을 가진다: 사용자의 자연어 목표, 시작 상태(무정보/분야 지정/후보 이름 지정), 기대 후보 종류(`information_resource` 또는 `operation`), 정답 ID 및 동등한 허용 ID, 필수 조건, 금지 조건, 정답 없음 여부, 정답의 1차 출처와 Evidence, 수행 완료 판정. 정답표는 실험 전에 고정하고 알고리즘·분류 변경에 맞춰 사후 수정하지 않는다. 수정이 필요하면 새 데이터 버전을 만들고 기존 결과를 보존한다.

과제 묶음은 다음 유형을 모두 포함한다.

- **정보 출처 찾기:** 특정 주제의 공식 데이터·문서·검색 인덱스를 찾고 범위·갱신 주기를 확인한다.
- **도구 찾기:** 목표를 수행할 API/MCP/SDK 기능을 찾고 Binding·인증·전송 조건을 맞춘다.
- **결합 탐색:** 정보를 제공하는 자원과 그 자원에 접근할 도구를 각각 찾고 관계를 설명한다.
- **표현 바꾸기:** 카탈로그 표현과 다른 한국어·영어·동의어·목표 중심 질문으로 같은 후보를 찾는다.
- **복수 조건:** 데이터 형식, 인증, 읽기 전용, 실행 위치 등 두 개 이상 조건을 만족하는 Binding을 찾는다.
- **미등록·불가:** 지도에 없는 기능, 조건이 충돌하는 요청, 근거가 부족하거나 오래된 주장은 보류하거나 출처로 재확인한다.

질의 문구 변형 여러 개를 독립적인 표본으로 세지 않는다. 각 과제에 `task_family`, `catalog_coverage`(in/partial/out), 정답·근거 고정 시점과 해시를 둔다. 개발 세트, 등록 항목 회수 세트, 미사용 자원 계열 일반화 holdout을 구분한다. R1 과제 문구·정보 요구·제약·판정 규칙은 R0 이전에 고정하고, 정답 ID는 실행 프롬프트에 노출하지 않는다. 가능하면 정본 작성에 참여하지 않은 사람 또는 별도 문맥의 모델이 과제 초안을 만들고 사람이 최종 확인한다. 작성자 분리가 불가능하면 자기평가 한계를 기록한다. 새 후보를 정답 대안으로 인정할 때에는 조건을 가린 채 동일 규칙으로 심사하고 버전 이력을 남긴다. 현재 표본 7개 Service·16개 Operation·17개 질의는 회귀 smoke set이며 일반적 성능 입증에 쓰지 않는다.

### 대표 과제: 서울 지도에서 POI와 따릉이 OD 연결

이 지도의 첫 실제 효용 검증 과제는 별도 프로젝트 [`seoul-population-map`](../../seoul-population-map/README.md)의 장소·인구 지도에 **서울 상가 POI 분포와 따릉이 출발·도착(OD) 흐름을 250m 격자에서 함께 표현할 수 있도록 필요한 정보와 도구를 찾고, 가능한 범위에서 연결 근거를 확인하는 것**으로 한다. 기준 문서는 [장소 맥락 확장 계획](../../seoul-population-map/docs/place-population-expansion-plan.md)과 [이동 데이터 출처 manifest](../../seoul-population-map/docs/mobility-source-manifest-2026-10-29.json)이며, 시험 시작 시 각 문서와 카탈로그의 리비전을 고정한다.

**과제 요청:** “현재 서울 지도에 있는 상가 POI와 따릉이 OD 자료를 같은 250m 격자에서 시간대별로 비교하고 싶다. 필요한 공식 데이터와 API, MCP 또는 처리 도구를 찾아 출처·필드·식별자·좌표계·시점 조건을 확인하고, 유효한 연결 경로가 있으면 재현 가능한 표본 결합 계획을 제시하라. 필요한 대응표나 근거를 찾지 못하면 추정 매칭을 하지 말고 막힌 조건과 추가로 필요한 자료를 밝혀라.”

이 과제는 “지도에서 후보를 잘 골랐는가”와 “실제 공간 결합이 가능한가”를 별도로 채점한다. 정확한 ID 대응 자료가 없을 때 이를 찾아내고 중단하는 것은 **탐색·안전 판단 성공**이지만, OD 레이어 구현 성공으로 세지는 않는다.

다음은 2026-10-29~30 조사 스냅샷의 시작 상태다. 현재 사실로 간주하지 않고 시험 직전에 공식 원천·로컬 파일 해시·기준일·접근 상태를 재확인한다.

- POI는 2026-06-30 상가 스냅샷을 250m 격자별로 집계해 지도에서 보여준다. OD와 기준일이 다르므로 같은 시점의 관측이나 방문·목적을 뜻하지 않는다.
- 따릉이 OD 표본은 2026-10-23이며 출발·도착 대여소 ID는 `ST-*` 형태다.
- 대여소 마스터 후보 OA-21235의 공식 ID·좌표 대응 파일은 확보되지 않았다. OA-13252 대체 스프레드시트는 `RENT_ID`가 없고, OD의 숫자 부분과 대여소 번호를 비교하는 방식은 근거 있는 join으로 인정하지 않는다.
- 현재 미해결 핵심은 OD 대여소 ID → 공식 대여소 좌표 → EPSG:5179 격자 `grid_id` 경로다. 이를 검증하기 전에는 OD를 POI 격자에 매핑하거나 지도에 표현하지 않는다.

에이전트가 찾아야 하는 것은 다음이다.

1. 상가 POI 원자료·업종 코드와 현재 격자 집계에 이르는 출처 및 재생성 방법
2. 따릉이 OD 원자료의 기준일·시간 버킷·출발/도착 ID와 집계 의미
3. OD와 동일한 식별자를 제공하는 공식 대여소 좌표 마스터·API·버전 이력 또는 검증된 대응표
4. 250m 격자 원천, CRS·축 순서·공간 포함/경계 규칙
5. 다운로드·압축해제·표 처리·좌표변환·공간조인에 필요한 API/MCP/SDK/라이브러리와 사용 조건
6. 각 출처의 라이선스·갱신·누락·억제·공개 조건

유효한 경로가 발견되면 내부 분석용 결과의 최소 단위는 `(grid_id, time_bucket, od_origin_count, od_destination_count, poi_business_count, poi_reference_date, od_reference_date, match_status)`로 제안하고, 출발·도착 흐름과 원자료 상태를 분리해 보존한다. POI는 격자 맥락으로만 함께 나타내며 개별 이동이 특정 상가 방문이었다고 추론하지 않는다. 원본 OD와 대여소 단위 민감 데이터는 공개 Pages에 올리지 않는다.

서울 과제는 다음 세 단계로 각각 채점한다.

| 단계 | 결과와 수용 기준 | 차단 시 처리 |
|---|---|---|
| S1 자료·도구 발견 | 필요한 정보원/API/MCP/처리 도구를 공식 근거·시점·조건과 함께 제시 | 미발견 항목과 후속 판단에 미치는 영향 기록 |
| S2 연결 가능성 판단 | 공식 ID 대응, CRS·축 순서·경계 규칙, 시점·누락 조건을 확인하거나 근거 부족을 정확히 보류 | 숫자 접미사 추정으로 연결 가능 판정 시 실패 |
| S3 읽기 전용 표본 결합 | S2에서 검증된 연결 경로로 표본을 실제 결합하고 입력·매칭/미매칭·집계 결과를 대조 | 공식 키·데이터·권한 미확보는 blocked/not_run. S2의 올바른 보류를 S3 또는 G4 성공으로 세지 않음 |

서울 과제는 사용자 지정 실제 평가 과제로 유지하되 결과의 일반화 범위는 서울 과제로 제한한다. 다른 분야에 대한 효용 주장은 별도 미사용 자원 계열 과제로 확인한다.

### 새 정보 발견 성과

각 시험 전에 카탈로그 리비전을 고정하고 후보를 **기존 정보 회수**, **새로운 유효 정보 발견**, **유효하지 않은 발견**으로 구분한다. 새 정보는 카탈로그에 없던 고유 데이터셋·공식 API/MCP/SDK·ID 대응 자료 또는 기존 항목의 미확인 사실을 뜻한다. 새로 보였다는 이유만으로 유효하다고 세지 않고 1차 출처와 현재 기준을 확인한다.

새 발견의 전체 인터넷 recall은 정답 모집단을 알 수 없어 주장하지 않는다. 다음 지표의 분모를 따로 고정한다.

- **고정 reference-set 회수율:** 실행 전에 확인·잠근 유효 후보 중 회수한 비율. 알려진 집합에 대한 결과로만 해석한다.
- **필수 정보 coverage:** POI 원천·OD 원천·공식 ID 대응·격자/CRS·사용 조건 등 사전 정보 요구 중 근거로 확인한 비율. 후보 개수와 다른 지표다. 자료 부재를 확인한 판단과 실제 정보 확보도 구분한다.
- **발견 정밀도:** 발견한 고유 신규 후보 중 1차 출처로 유효성을 확인한 비율. 미검증·중복·오인식 수를 별도 기록한다.
- **차단 해소:** 공식 키 확보처럼 실제 다음 작업을 가능하게 만든 발견 수와 소요 시간·호출 수.

출처 URL·고유 ID·검색 시각·버전/스냅샷·라이선스를 저장하며 디렉터리 등재와 기능 근거를 구분한다. 실행 중 조건 간 결과를 공유하지 않는다. 필요하면 종료 후 모든 조건의 검증 후보 합집합 대비 pooled coverage를 보조 지표로 보고하되 전체 인터넷 recall로 해석하지 않는다.

**R0 발견 회차**는 시작 카탈로그를 동결하고 기존 회수·지도 밖 신규 발견·차단 조건 파악을 측정한다. 서울 항목의 현재 수록 여부도 실행 전 재확인한다. 미수록 자료를 지도 내부에서 찾지 못하는 것은 시작 상태의 결과로 기록한다.

**R1 사용 회차**는 R0에서 공식 근거를 확인한 항목을 등록한 새 카탈로그를 동결하고, 그 동일 정본에서 분류·키워드·혼합 사용을 비교한다. 등록한 항목을 다른 표현으로 찾는 것은 ‘등록 항목 회수’이며, 미사용 자원 계열의 일반화 holdout과 별도 보고한다. R0와 R1은 평가 목적·데이터가 달라 점수 차이를 지도 개선 효과로 해석하지 않는다. 동일 질의 재사용이나 문구 변경을 독립 holdout으로 세지 않는다. R0 발견 항목을 R1에서 일괄 제외하지 않으며, 무엇을 학습·등록·평가에 썼는지 연결 기록을 남긴다.

### 비교 실험 절차

**탐색 방식 비교:** 같은 카탈로그·같은 목표를 사람과 에이전트 각각에 제시한다. 세 조건은 (A) 분류 경로만 허용, (B) 키워드 검색만 허용, (C) 두 방식을 자유롭게 조합한다. 에이전트 조건 C는 구체적인 이름·요구가 있으면 검색, 범위가 넓거나 모호하면 분류, 후보가 충분히 좁혀지지 않으면 둘을 결합하는 정책을 사용한다. 조건 순서와 동등 난이도 과제 배정을 무작위화/역균형화하고, 에이전트 매 실행은 새 문맥에서 시작한다.

**지도 효용 비교:** 개발용 과제로 탐색 방식을 선정·고정한 뒤 별도 평가 과제를 다음 세 조건에서 비교한다. 조건마다 시작점·허용 도구·도메인·시간·호출 한도·원문 확인 규칙을 실행 전에 잠근다.

| 조건 | 시작점·허용 행동 | 오염과 비용 기록 |
|---|---|---|
| A 지도 우선 | 고정 Pages 리비전에서 시작해 공식 원문으로 확인 | 최초 manifest·분류/스키마 학습과 원문 확인 비용 포함 |
| B 일반 웹 검색 | 일반 검색에서 시작하며 검색 중 발견한 디렉터리·공식 문서 열람 허용 | 지도 도메인/복제 내용은 도구가 지원하면 사전 차단. 열람 시 오염 표시, 미열람·오염 결과를 분리 보고 |
| C 원 디렉터리 우선 | 실행 전에 운영자가 고정한 과제별 공식 디렉터리 목록에서 시작, 공식 원문 열람 허용 | 디렉터리 목록·선정 근거·호출을 기록. 임의로 정답 상세 URL을 시작점으로 주지 않음 |

첫 파일럿은 개방형 업무 비교로 세 조건 모두 같은 일반 검색 기능을 제공하고 `catalog_hit/web_hit/directory_hit`의 최초 발견·후속 확인 경로를 기록한다. 검색 허용 자체를 지도 효과로 오인하지 않으며 한 조건에만 추가 실행 권한을 주지 않는다. 구조 자체의 탐색 비교는 별도 개발 시험으로 같은 카탈로그의 분류/키워드/혼합을 비교한다. 폐쇄형 비교를 추가하면 배타적 도구 집합과 해석 범위를 별도 프로토콜로 고정해 개방형 결과와 합산하지 않는다.

지도 구축·갱신·근거 확인의 사전 비용은 온라인 탐색 비용과 별도로 보고한다. 후속 소형 과제에서 ‘웹 검색 + 짧은 where-to-look 안내문’ 조건을 추가해 단순 출처 안내와 구조화된 지도 효과를 구분할 수 있다. 첫 파일럿의 세 조건을 이 조건으로 대체하지 않는다.

**사람 평가:** 최초에는 운영자의 고정 UI 시나리오로 결함을 찾고, 가능하면 운영자 외 1~2명의 비공식 관찰을 추가한다. 5~8명 형성 평가는 후속 단계로 두며 첫 에이전트 파일럿의 필수 진입 조건으로 삼지 않는다. 참가자별 동등 난이도의 다른 과제에서 성공·시간·클릭·재검색·선택 이유·근거 이해도를 기록한다. 이런 소표본을 통계적 사용성 입증으로 해석하지 않는다.

**에이전트 평가:** 최초에는 한 모델 계열에서 조건을 비교하고 두 번째 계열은 후속 재현·민감도 확인에 쓴다. 조건마다 새 문맥을 사용하고 같은 지침·도구·권한·예산을 적용한다. 모델명·정확한 버전은 관측 가능한 값만 기록하며, 미관측 버전의 결과를 고정 버전 반복 실험으로 표시하지 않는다. 실행 시각을 기록하고 가능한 한 짧은 기간 안에 비교해 드리프트 영향을 제한한다. 검색 판정과 G4 실행 판정은 별도다.

### 최초 실행 파일럿

1. R0 전에 과제·채점 기준·예산·개발/회수/일반화 구분을 잠근다. 서로 다른 정보 요구 6개를 고르며 지도 안/부분/밖, 정답 없음 또는 근거 부족 사례를 포함한다. 서울 S1/S2를 포함하고, 다른 분야 일반화 과제는 별도 표기한다.
2. G0·G1 필수 검사와 G2의 치명적 안전 오류를 확인·수정한다. 핵심 Evidence의 기준일·버전 변화·공식 접근 상태를 재확인하고 비신뢰 설명문의 지시를 따르지 않는 사례도 넣는다.
3. 먼저 R0의 6개 과제를 A/B/C 세 조건에서 각각 1회 실행한다(18회). 전체 시도는 과제별 시간 15분·외부 호출 20회 상한을 초기 예산으로 사전 고정한다. 이 값은 운영 예산이며 성능 수용 목표가 아니다. 인증·권한 차단, 공식 키 미확인, 시간·호출 상한 도달 시 상태와 이유를 남기고 종료한다.
4. 측정 절차에 문제가 없고 자원이 허용되면 전 조건에 동일한 두 번째 반복을 적용한다(총 36회). 결과가 좋은 조건만 선택적으로 반복하지 않는다. 과제 순서를 무작위화/역균형화하고 반복과 문구 변형을 독립 과제로 세지 않는다.
5. 검증된 발견을 등록한 뒤 R1 회수 세트와 미사용 자원 계열 평가를 별도 실행한다. 예산은 시작 전에 다시 고정하고 R0/R1 점수를 합산하지 않는다. 등록 회수 결과만으로 일반화를 주장하지 않는다.
6. 공식 연결 경로가 확인된 서울 S3 또는 별도 실행 가능한 읽기 전용 과제에서 G4를 수행한다. 서울 키가 없으면 차단을 기록하고, 별도 성공 가능한 조회로 하네스 자체를 확인할 수 있다. 서울 실제 결합 성공을 대신한 것으로 세지 않는다.

이 규모는 절차·실패 유형·관측 변동을 확인하는 파일럿이다. 파일럿 결과를 본 뒤 확증 시험의 표본 수·모델·시간/토큰 계측 가능성과 실행 여부를 결정한다.

### R0 이후 판단 재사용 검증

2026-11-01 R0 v2의 18회 실행을 완료했다. 전체 완료 시간 중앙값은 지도 95.024초·웹 검색 83.258초·원 디렉터리 81.345초로, 현재 정본의 전반적 효율 우위를 확인하지 못했다. 정보원은 0건이었고 지도 조건의 최초 후보 발견은 지오코딩 1건만 정본에서, 나머지는 웹 전환으로 이뤄졌다. 원자 조회 예산 준수는 CLI batch 요약의 한계로 미판정이며, R1·독립 holdout·서울 실제 조인은 미검증이다. 상세 수치·사후 실제 접근·다섯 웹 AI의 검토와 Grok 미응답은 [실행 보고서](./seoul-discovery-pilot-2026-11-01.md)에 보존한다.

이 결과는 현재 수록 범위와 비용의 기준선이다. 탐색 중 목표 해석·후보 선택·추가 검증·종료 판단을 재사용하면 도움이 된다는 가설까지 부정하거나 입증한 결과로 해석하지 않는다. 후속 구현과 시험은 다음 순서로 진행한다.

1. **과제별 판정 계약과 계측부터 보정한다.** 위 요청·결과 계약과 아래 계측 보정 gate를 확정한다. 원자 요청과 첫 유효 후보 시점을 기록하고, 발견·문서 검증·실응답·작업 완료를 분리한다. 계측이 불가능한 항목은 미판정으로 남긴다. 큰 비교 시험을 먼저 반복하지 않는다.
2. **작은 개발 과제 세 종류로 흐름을 확인한다.** 수록된 공개 URL 본문 추출 같은 정확 회수, 같은 목적에 추가 필수조건이 붙는 부분 충족, 서울 ST ID 대응처럼 외부 근거가 필요한 과제를 고른다. 과제별 필수·선호조건, 검증 수준, 비교 범위·예산, 종료·보류 기준을 실행 전에 고정한다. 세 종류는 개발용이며 독립 holdout으로 표시하지 않는다.
3. **조건 간 공통 정책과 지도 제공 효과를 분리한다.** 지도 우선·웹 우선·원 디렉터리 우선 모두 같은 GoalSpec·종료 규칙·계측을 적용한다. 지도 조건만 더 자세한 요청 해석이나 좋은 종료 지침을 받아 유리해지지 않게 한다. 알려진 사실 재사용과 외부 탐색의 기여를 구분한다.
4. **서울 공식 정보원과 비교 후보를 검증해 등록한다.** 공식 POI·분류표·OD·대여소·격자 자료의 접근 경로와 제약을 우선 확인한다. 목표에 필요한 대안을 비교할 수 있을 만큼 후보를 확보하고, 수집량 자체를 성공 기준으로 삼지 않는다. ID·시점·CRS가 미확인인 관계는 검증 완료로 등록하지 않는다.
5. **정상·실패 사례와 재사용 효과를 구분해 검증한다.** 아래 필수 사례를 먼저 통과한 뒤 같은 사실을 쓰는 두 조건으로 탐색 안내의 추가 효과를 확인한다. 이후 회수와 일반화를 따로 평가한다. 기존 개발 과제 재실행은 회귀 평가로, 별도 잠근 미사용 과제는 일반화 평가로 보고한다. 별도 예산의 대안 탐색으로 누락 후보와 선택 손실도 점검한다.

이번 개정은 평가·이용 흐름의 계약이며 새로운 스키마, 자동 정책 엔진 또는 수집기를 구현했다는 뜻이 아니다. 반복 관측된 필요를 바탕으로 기존 정적 계약과 얇은 소비 인터페이스부터 개선한다.

### 계측 경로 보정과 시험 진입 조건

현재 CLI 내장 웹 검색의 완료 이벤트만으로는 batch 원문 인자를 복원할 수 없다. 후속 시험은 원래 인자를 관측·계수할 수 있는 검색·열람 어댑터 또는 동등한 실행 경계를 선택하고, 모든 비교 조건에 같은 경로를 적용한다. CLI 요약에서 원자 요청을 추정하는 방식으로 보정을 통과시키지 않는다. 사용할 검색 제공자·접근 권한·도구 버전과 인자 관측 가능성을 먼저 확인한다. 준비되지 않으면 외부 조회 효율 시험은 차단으로 남기고 정적 계약 검사만 진행한다. 경로 변경 후 시행은 새 프로토콜로 잠그고 R0 수치와 직접 합산하지 않는다.

예산 단위는 외부 도구 인자의 query/open/find/click 하나이며 batch의 각 하위 동작을 1회로 센다. 지도 조회 수는 별도로 기록한다. 전송한 동작은 실패·timeout이어도 예산에 포함하고, 재전송은 새 동작으로 계수한다. HTTP 리다이렉트·내부 네트워크 재시도는 가능하면 별도 시도 기록으로 연결하되 이 논리 동작 수와 혼합하지 않는다. 남은 예산보다 큰 batch는 기본적으로 전체 실행을 거부하고 거부 이벤트를 남긴다. 조용히 일부만 실행하지 않는다.

다음 보정 사례는 모의 응답을 통제할 수 있는 어댑터에서 기대 이벤트와 실제 로그를 대조한다. 선택한 실제 제공자에서도 소규모 검색·열람으로 같은 인자 연결과 시간 기록을 확인해야 한다.

| 보정 사례 | 통과 기준 |
|---|---|
| query 2개·open 2개·find 1개 batch | 논리 동작 5개가 각각 고유 ID·원문 인자·시작/종료·상태·근거 참조로 연결됨 |
| 성공·접근 실패·timeout | 전송된 3개 동작 모두 누락 없이 기록·계수됨 |
| 실패 후 같은 요청 재전송 | 두 시도를 서로 다른 ID로 기록하고 재시도 관계를 보존함 |
| 남은 예산 2회에 3개 batch | 외부 동작 0개 실행, 예산 거부 이벤트와 이유 기록 |
| 첫 후보와 첫 적합 후보가 다름 | 후보 도착 시각과 요구조건 검증 완료 시각을 구분. 과제 수준의 첫 유효 후보 시간은 후자에서 산정 |
| 요청·응답·종료 사건 연결 | 모든 선택·보류를 조건 ID와 실제 기록에서 재구성 가능. 누락 시 해당 지표 미판정 |

고정 보정 사례는 기대 계수·관계·상태와 정확히 일치해야 한다. 로그 누락이나 예산 초과 실행이 하나라도 있으면 계측 보정을 통과하지 못한다. 첫 유효 후보를 판정할 과제 조건표와 응답 참조가 없으면 시각을 추정하지 않는다. 이 gate는 계측의 정확성을 확인하며 제품 효용·통계적 우위의 통과 판정은 아니다.

### 종료와 근거 재사용의 필수 사례

| 사례 | 기대 행동 |
|---|---|
| 요구 수준의 조건·근거가 모두 충족됨 | 완료 상태와 근거를 기록하고 필수적이지 않은 탐색을 반복하지 않음 |
| 무인증은 확인됐으나 필수 상업 이용 조건은 미확인 | 검색 `satisfies`와 별개로 해당 조건은 `unknown`. 추가 확인하거나 보류 |
| 버전·시점이 과제 기준에 맞지 않는 근거 | 과거 확인 사실은 보존하고 현재 조건 충족으로 재사용하지 않음. 재확인 또는 보류 |
| 같은 주장에 충돌하는 근거 | `conflicted`를 유지하며 충돌 해소 전 문서 기반 선택 완료를 선언하지 않음 |
| 수록 범위에서 후보가 없거나 필수조건을 모두 위반함 | 범위를 명시해 무결과 기록. 허용 예산 내 외부 탐색 또는 보류, 후보·대응키를 생성하지 않음 |
| 공식 후보는 있으나 인증·접근이 차단됨 | 발견 상태를 보존하고 실응답·작업 완료는 차단/미실행으로 구분 |
| 필수 확인이 남았지만 예산이 종료됨 | 예산 종료와 미확인 조건을 기록. 완료나 인터넷 전체 해법 부재로 바꾸지 않음 |

각 사례의 조건표·Evidence·기대 상태를 사전에 고정한다. 정상 사례의 불필요한 탐색 여부는 사전 허용한 비교·재확인 범위로 판정한다. 실패 사례를 완료로 오판하거나 근거 없는 `satisfied`를 만들면 해당 흐름은 수정 후 회귀 확인 전 비교 시험에 진입하지 않는다. 이 사례를 개발에 사용한 뒤 일반화 holdout으로 재명명하지 않는다.

### 탐색 안내의 추가 효과 분리

지도·웹·디렉터리 비교는 전체 이용 흐름의 효용을 평가한다. 그와 별도의 작은 개발 시험에서 다음 두 조건을 비교해 사전 조사된 사실의 효과와 탐색 안내의 추가 효과를 구분한다.

- **사실 제공 조건:** 같은 후보·기능·제약·근거 URL·공식 접근 URL·상태·버전의 목록을 제공한다.
- **탐색 안내 추가 조건:** 같은 목록에 과제 유형별 확인 순서·기존 공식 접근 경로의 선택 방법·미확인 항목 확인 안내를 추가한다. 새로운 후보·사실·판정 정답은 추가하지 않는다.

두 조건은 같은 GoalSpec·종료 규칙·도구·권한·예산과 동결 정본을 사용하고 매회 새 문맥으로 수행한다. 안내는 시험 과제의 정답을 본 뒤 작성하지 않고 별도 개발 자료로 만들거나 평가 전에 잠근다. 안내의 입력·생성·갱신 비용을 포함해 별도 보고한다. 일반 지침과 종료 규칙은 양쪽에 동일하게 제공한다.

양쪽의 후보·주장·URL 집합이 동일한지 실행 전에 검사한다. 추가 안내는 기존 정보의 확인 순서와 관계만 설명한다. 안내 조건에만 새 URL·우회 경로·중요 사실이 들어갔다면 같은 사실의 비교로 인정하지 않고 구성을 수정하거나 별도 정보 추가 시험으로 분류한다.

비교는 조건별 검토 품질·안전 상태를 먼저 확인하고, 재검색·출처 전환·불필요 조회·종료 단계·시간·토큰을 짝지어 보고한다. 더 일찍 끝났더라도 필수조건을 놓쳤으면 개선으로 인정하지 않는다. 이 시험은 탐색 안내의 추가 기여만 평가하며 구조화된 데이터 표현 자체의 효과나 인터넷 전체의 최적성을 입증하지 않는다. 소표본에서는 차이와 실패 유형을 기술하고 승자를 확정하지 않는다.

### 지표와 사전 통과 기준

모든 보고서는 검색 순위만으로 성공을 판정하지 않는다.

- **검색 품질:** Top-1 정확도, Recall@5, MRR, 정답 후보 종류 정확도, 올바른 Binding 선택률.
- **발견 성과:** 기존 카탈로그 회수율, 고유 신규 후보 수, 1차 출처 확인 정밀도, 고정 reference-set 회수율, 필수 정보 coverage, 중복·오인식률, 필요한 join 조건의 정확한 발견·보류 비율.
- **안전·보류:** 하드 조건을 어긴 후보의 `satisfies` 반환 수, 정답 없음·근거 충돌·미확인 조건에서 올바르게 보류한 비율, 근거와 설명의 일치율.
- **속도·비용:** 첫 유효 후보까지 시간, 전체 완료 시간, 모델 입력·출력 토큰, Pages 요청 수, 가져온 바이트, 탐색 노드와 상세 레코드 수.
- **사람 사용성:** 과제 성공, 완료 시간, 탐색 단계·클릭·검색어 수정 횟수, 정보 출처와 도구의 구분 이해도.
- **실제 작업:** 최종 결과 정확성, 수행 성공률, 오류 유형, 작업 완료 시간, 전체 토큰·호출 수.

판단 재사용 가설은 검색 질의 생성·수정 수, 검색 수단·출처 전환 수, 고유 방문 문서 수, 검토 후 탈락한 후보 수와 사유, 선택 시 필수조건의 근거 충족 비율, 남은 중요 미확인 수, 종료 이유를 추가로 본다. 적합한 대안을 검토한 것은 낭비로 세지 않으며, 탈락 수를 무조건 줄이는 목표로 삼지 않는다. 판단 수는 내부 추론량의 추정치가 아니라 기록된 행동·선택 사건의 대리 지표다.

종료의 적절성은 같은 요구조건과 사전 예산으로 평가한다. 근거가 부족한데 종료한 사례와 충분한 근거 뒤에도 불필요하게 반복한 사례를 구분한다. 별도 고정 예산의 사후 검토에서 더 적합한 후보가 발견되면, 선택 당시의 필수·선호조건에 따른 후보 품질 차이와 누락 이유를 보고한다. 이는 관측한 후보 집합 내 손실의 대리 지표이며 인터넷 전체의 최적 후보 대비 regret라고 주장하지 않는다. 사후 후보를 원래 시행의 성공으로 소급하지 않는다.

G0·G1은 고정 기능 시나리오를 통과해야 한다. 필수 조건이 틀린 Binding의 `satisfies` 판정이나 **공식 대여소 ID 대응 근거 없는 격자 join 성공 보고**는 치명 실패이며 수정·회귀 확인 전 해당 경로 진행을 중단한다. 공식 키 미확인을 정확히 보고하면 S2 탐색·안전 판단은 성공일 수 있으나 S3/G4는 차단 상태다. 관측 위반 0건을 위험 0으로 해석하지 않는다. 보류율은 정답 없음 과제 수, 검색 지표는 평가 가능한 과제 수 등 각 분모와 과제별 오류를 공개한다.

파일럿에서는 과제별 짝지은 관측 차이·실패 유형·표본 수를 기술하고, 해석 가능한 구간이 있으면 한계와 함께 제시한다. **후속 확증 시험의 사전 가설 목표**로 G2의 Recall@5·올바른 보류 각각 90% 이상, G3의 정확도 유지·중앙값 시간 10% 이상·실측 모델 토큰 15% 이상 절감, G4의 성공률 차이 하한 −5%p 이내 비열등성을 보존한다. 이 수치는 현재 달성 사실이나 첫 파일럿 진입 조건이 아니다. 확증 holdout을 열기 전에 주 지표·추정 방법·유의수준·80% 검정력·독립 과제 수·제외 규칙을 고정한다. 표본·실측 계측이 부족하면 판정은 탐색적 파일럿/해당 가설 미검증으로 남기며 목표를 사후 완화하지 않는다.

### 계측 계약과 판정 상태

모든 조건에서 공통으로 첫 유효 후보까지 시간, 총 경과 시간, 검색·원문 열람·고유 URL 수, 잘못된 후보 선택, 안전 오류를 기록한다. 도구가 제공하는 usage가 있을 때만 입력·출력·캐시 토큰을 실측으로 집계한다. 웹 UI에서 실토큰·정확한 모델 버전을 알 수 없으면 값은 `null`, 관측 상태는 `not_observed`로 두고 0으로 대체하거나 결측을 제외한 절감률을 만들지 않는다. 문자·바이트·호출·노드 수는 별도 대리 지표이며 실토큰/비용의 대체 측정으로 혼합하지 않는다. 토큰 15% 가설은 양쪽 조건을 동일 범위로 실측한 경우에만 판정한다.

외부 조회 예산은 실행 전 원래 도구 인자의 각 query/open/find/click을 계수하고 batch의 하위 요청을 각각 기록한다. 요청 시작·종료·URL 또는 검색 질의·상태·반환량·근거 참조와 원문 요청 이벤트를 연결한다. 원래 인자를 확보할 수 없는 도구에서는 정확 횟수와 예산 준수 판정을 미계측으로 둔다. 대표 동작만 남는 CLI 요약이나 모델 자기보고로 원자 요청 수를 확정하지 않는다.

결과는 `ready_for_pilot`(필수 기능·안전 조건 확인), `exploratory`(소표본 관측), `fail_critical`(치명 오류), `blocked/not_run`(외부 조건 미충족), `confirmed/not_confirmed`(사전 확증 시험 판정)을 구분한다. G4는 전체 배정 과제 중 성공·실패·차단·미실행 수와 비율을 먼저 공개하고, 실행 가능 하위집합의 성공률도 따로 보고한다. 차단 과제를 임의로 분모에서 빼지 않는다.

### 결과 기록과 재검증

각 실행에 날짜·시각, Git commit(사용 가능 시), 문서/출처 manifest 해시, catalog revision, schema·검색 알고리즘 버전, 평가 세트/정답표 버전과 해시, 과제 family·coverage 구분, 모델명·관측 버전/미관측 상태, 프롬프트·도구 정의 해시, 조건별 허용 기능·시작점·도메인·예산·캐시 상태, 최초 발견 경로·오염 플래그, 정답/결과·실패/차단 이유·계측 범위·분모를 저장한다. 구축·유지 비용은 별도 장부에 둔다. 비밀정보·계정 정보는 기록하지 않는다. 변경 시 G0·G1과 개발 회귀 세트를 다시 확인하고, 확증이 필요하면 별도 잠근 미사용 holdout을 쓴다. 정식 MCP 소비 인터페이스를 추가하면 같은 질의·필터·리비전의 정적 Pages 참조와 MCP 경로가 같은 후보·근거를 내는지 별도 계약 검사한다.

## 8. 위험과 대응

| 위험 | 대응 |
|---|---|
| 공개 카탈로그의 설명이 오래되거나 틀림 | 필드별 Evidence, 확인 시점, 검증 상태와 재확인 규칙을 둔다. |
| AI가 그럴듯하지만 실행 불가능한 후보를 추천 | 의미 검색과 실행 가능성 판단을 분리하고, 만족·위반·확인 불가를 구별한다. |
| 의미 분류와 관계 모델이 과도하게 커짐 | 작은 통제 어휘와 검증된 필드부터 시작하고 평가에서 필요가 확인될 때 확장한다. |
| 저장소나 Git 이력에 비밀정보가 유입 | 비밀정보 스캔, 공개 필드 allowlist, 리뷰 절차를 PR 병합 조건으로 둔다. |
| Pages를 실시간 API·실행 서버로 오해 | 문서와 UI에 “공개 문서 카탈로그이며 실행 보장 없음”을 명시한다. |
| 표준·Binding 스키마가 바뀜 | Binding 버전·호환 정보와 카탈로그 스키마 버전을 분리하고 변경 이력을 유지한다. |
| 한 조직이나 작성자의 용어에 검색이 과적합 | 골든 세트에 실제 사용자 표현과 미등록·무결과 질의를 포함한다. |

## 9. 결정 사항과 초기 운영 정책

1. **저장소 이름과 공개 범위 — 방향 결정됨.** 가칭 `agent-capability-map`으로 Public 저장소를 만든다. 정식 이름은 생성 전까지 바꿀 수 있다.
2. **라이선스와 외부 기여 — 방향 결정됨.** 데이터는 CC0-1.0, 사이트·도구 코드는 MIT를 적용하는 안으로 한다. 초기에는 외부 PR·이슈·토론을 통한 기여를 받지 않고 공개 열람용으로 운영한다. 실제 공개 전에 라이선스 파일과 저장소 설정을 확정한다.
3. **첫 분야와 분류 축 — 방향 결정됨.** 범위는 에이전트가 작업을 더 잘 수행하도록 돕는 기술이다. RAG는 문제 영역·역량 범주로, API·MCP·SDK는 기능을 제공하거나 연결하는 구현 방식으로 분리한다. 레코드에는 구체적인 Service, Operation, Integration 또는 Binding이 있어야 하며, 단순히 범주 이름만 나열하지 않는다.
4. **MVP 범위 — 정적 카탈로그와 별도 실행 평가.** MVP 제품은 검증된 YAML 원본, 재현 가능한 정적 산출물, GitHub Pages 사람용 검색·탐색, AI용 단계 조회를 포함한다. MCP 서버와 로컬 stdio 어댑터는 MVP 제품에서 제외하고 후속 단계로 둔다. 계획의 핵심 가설을 검증하기 위한 별도 실험에서는 테스트 계정·자원과 연결 하네스를 사용해 실제 과제 완료를 비교한다. 이 하네스는 공개 Pages에서 실행되지 않고, 비밀정보도 카탈로그에 저장하지 않는다. 정적 검색·조회가 유용하고 데이터 계약이 안정되며 소비자 측 MCP 수요가 확인되면 같은 산출물과 검색 로직을 쓰는 얇은 읽기 전용 어댑터를 검토한다.
5. **Evidence 신뢰·검증 정책 — 초기 기준.** 주장을 뒷받침하는 직접 링크, 확인 시점, 검증 상태를 기록한다. 출처 권위 등급과 현재 검증 상태는 별도 필드로 관리한다.
   - **A:** 표준·프로토콜 공식 문서, 제공자의 공식 API/제품 문서, 공식 저장소의 태그·릴리스 자료. 핵심 기능·권한·전송 방식 주장에 우선 사용한다.
   - **B:** 관리 주체가 확인되는 공식 공지·지원 문서·이슈. A등급 자료를 보완하고 가능한 경우 대조한다.
   - **C:** 제3자 기술 자료·사례. 발견과 맥락에 쓰며 핵심 실행 가능성이나 권한을 단독 확정하지 않는다.
   - **D:** 출처·작성 시점이 불분명한 자료와 검색 요약. 후보 발견에만 활용하고 검증 근거로 세지 않는다.
   - 주 1회 자동 링크 상태 확인은 링크 생존만 표시한다. 월 1회 에이전트가 문서·버전 변화 신호를 분류하고 재검토 후보를 만든다. 분기 1회 사람 유지관리자가 위험도에 따라 표본을 확인한다. 보안·권한·폐기·호환성 변화는 즉시 재검토한다. 링크가 살아 있다는 이유만으로 주장이 검증됐다고 처리하지 않는다.
6. **검토와 공개 승인 — 운영 기준.** 자동 검사는 스키마·관계·비밀정보·링크와 변경 영향을 확인한다. 에이전트는 근거와 변경안을 제시하는 검토자이며, 사람 유지관리자가 공개 전 최종 승인한다. 외부 기여를 받기 시작하면 권한과 절차를 다시 정한다.

따라서 저장소 구조와 작업 순서는 정적 우선 MVP를 기준으로 진행한다. 남은 결정은 정식 저장소 이름, 라이선스 파일 확정 등 공개 저장소 생성 시 필요한 운영 세부사항이다.

## 10. AI 검토 의견과 남은 이견

이 절의 첫 목록과 감사 참여 기록은 2026-10-27 설계 라운드의 이력이다. 현재 개정 상태와 참여 범위는 아래 2026-11-01 기록을 따른다.

- **이번 라운드에서 확인된 공통 의견:** 정적 원본에서 생성된 인덱스와 상세 자료를 게시하고, 전체 덤프 대신 후보를 좁혀 필요한 상세만 읽게 한다. Operation↔Binding은 다대다이며, Binding이 편집 관계를 소유하고 역방향 참조를 생성하는 안이 서비스별 편집 묶음과 맞는다. 품질은 Recall@5만으로 판단하지 않고 올바른 Binding, 제약 위반, 무결과 보류, 탐색 시간·토큰과 실제 과제 완료를 함께 본다. 검색 필터는 개별 Binding에서 판정해야 하며, 서로 다른 Binding의 속성을 합쳐 hard constraint 만족으로 오인하면 안 된다.
- **구조 선택:** 한 파일에 모든 정보를 몰아넣기보다 Service 단위의 유지관리 묶음과 독립 Operation 파일을 결합한다. 사람용 계층 탐색은 생성 뷰로 제공하고, 원본 모델은 관계형 정본으로 유지한다.
- **검색 선택:** 사람과 AI가 함께 쓰는 소형 공용 검색 자료를 두고, 사람용 계층 색인은 별도로 둔다. 정적 사이트만으로 임의 서버 검색이 된다고 가정하지 않으며, 브라우저와 AI 호스트가 참조 검색기로 후보를 찾는다. 결과 수와 색인 크기는 측정 후 조정한다.
- **MCP 시점:** 정적 사이트와 파일만으로도 공개 데이터와 검색 계약을 먼저 검증할 수 있다는 의견을 반영해 MCP 어댑터를 후속 단계로 미뤘다. MCP가 필수 소비 경로라는 가정이 검증되면 새 정본을 만들지 않고 같은 생성물에 연결하는 얇은 읽기 전용 어댑터를 추가한다.
- **Evidence와 안전:** 출처의 권위와 내용 검증·링크 도달 상태는 서로 다른 값이다. 자동 링크 점검 실패는 주장이 거짓임을 뜻하지 않으며, 재검토 표지만 남긴다. MVP에서는 Source/Claim 별도 테이블을 두자는 의견도 있었으나, 중복 최소화와 소규모 운영을 위해 Evidence가 대상·JSON Pointer 경로·출처를 직접 보유하는 안을 택했다. 같은 출처 URL은 여러 Evidence에 반복할 수 있다. 정규 Source 엔터티는 데이터 중복이 실제 문제가 될 때 후속 검토한다.
- **검증 범위 조정:** 정적 카탈로그 평가만으로는 사용자가 원하는 “찾은 뒤 실제로 연결해 일을 마치는가”를 증명하지 못한다. 반대로 실행기·비밀정보를 공개 카탈로그에 넣을 이유도 없다. 따라서 제품은 정적 조회로 유지하고 별도 테스트 하네스가 같은 조건의 지도 사용군과 일반 웹 탐색 대조군의 실제 작업 성공률·시간·토큰을 비교한다.
- **평가와 운영:** 골든 질의, 하드 제약 위반 0건 목표, 조회량·토큰 측정을 포함한다. 자동 검증과 에이전트 리뷰가 변경 후보를 만들고 사람 유지관리자가 공개를 승인한다.

이번 세부 감사에서는 ChatGPT, Gemini, DeepSeek, Grok의 답변을 확인했다. Perplexity의 이번 감사 응답은 확인되지 않았고, Claude는 사용량 제한으로 새 답변을 받지 못했다. 따라서 이번 라운드에서 여섯 모델의 합의가 이뤄졌다고 주장하지 않는다. Claude 또는 Perplexity의 새 답변이 확보되면 현재 결정과 충돌하는 부분만 추가 검토한다.

### 2026-10-30 사용자 결정 반영 — 공통 탐색 경로 개정

- 사람과 에이전트 모두 지도에서 **목적 중심 탑다운 분류 탐색과 키워드 검색**을 사용할 수 있어야 한다. 두 경로는 대체 관계가 아니라 동등한 진입점이며 탐색 중 결합할 수 있다.
- 공통 분류·후보·검색 의미·Evidence를 사용한다. 에이전트에 별도 taxonomy를 만들지 않는다. 에이전트 측은 작은 분류 노드와 후보 요약부터 읽고 선택된 상세만 추가 조회해 속도·토큰을 최적화한다.
- 정보 출처와 실행 도구를 별도 종류로 표현한다. 정보 출처의 조회 API가 있으면 두 객체를 연결하되 정보와 실행 기능을 하나로 합치지 않는다.
- 평가를 두 층으로 나눈다. 먼저 분류만·키워드만·결합 탐색을 비교해 경로를 고정하고, 이후 지도 사용을 일반 웹 검색·원 디렉터리 직접 탐색과 비교한다. 에이전트 토큰뿐 아니라 전송량·요청 수·시간·정확도·보류를 측정한다.
- **당시 AI 검토 상태(2026-10-30):** BW 도구 미노출로 서울 POI–OD와 R0/R1을 포함한 개정안은 미전송 상태였다. 이는 과거 기록이며 현재 검토 상태는 아래 2026-11-01 개정 기록을 따른다.

### 2026-11-01 — 평가계획 웹 AI 검토 반영

BW로 ChatGPT·Gemini·Claude·Perplexity·DeepSeek·Grok의 새 답변을 확인했다. 다섯 곳은 7장 원문과 목적/구조 요약을, DeepSeek은 후속 고정 요약을 검토했다. 서울 확장 계획·출처 manifest 전문과 전체 스키마를 여섯 곳에 동일하게 전달한 감사는 아니다. 일부 모델은 자동/빠른 모드였고 정확한 모델 버전이 미관측인 곳도 있다. 답변·반론·채택/미채택 판단은 [검토 기록](./internet-map-review-summary-2026-11-01.md)에 남겼다. 이는 파일럿 전의 검토 기록이다. 이후 R0 실행 결과는 위 후속 검증 절과 실행 보고서를 따른다.

이번에 반영한 결정:

- 공통 목적 분류·키워드·단계 조회, 공개 카탈로그와 별도 실행 하네스의 구분을 유지한다.
- R0/R1을 독립 질문으로 정의하고, 등록 회수·미사용 자원 계열 일반화·경로 선정 개발 과제를 구분한다.
- 오픈웹 전체 recall 대신 고정 reference-set 회수율·필수 정보 coverage·발견 정밀도·차단 해소를 쓴다.
- G0·G1과 치명적 안전 오류는 필수로 확인하되, 소표본 통계 미달은 탐색적 파일럿의 금지 조건으로 쓰지 않는다.
- 서울 S1/S2/S3 채점, 실제 결합 차단 상태, 세 외부 대조 조건의 권한·시작점·오염·초기 학습비용을 명시한다.
- 첫 R0는 6개 정보 요구×3조건×1회(18회), 필요 시 전 조건 2회(36회)로 시작한다. 이 규모로 일반적 우위를 주장하지 않는다.
- 90%·시간10%·실토큰15%·G4 −5%p는 후속 확증 가설로 남기고, 미관측 계측은 명시적으로 보고한다.

웹 검색 대조군 삭제, R0/R1 통합, 서울 과제/G4 삭제, 올바른 보류를 실제 결합 성공으로 세는 제안은 채택하지 않았다. 기술 사실은 AI 다수결로 확정하지 않으며 공식 원천 확인을 유지한다.

### 2026-11-01 판단 재사용과 종료 기준 반영

소유자가 지정한 웹 대화 `인터넷 지도 평가`의 목표·탐색 방식·종료 판단 논의를 분석해 반영했다. 이 개정은 해당 대화에서 제안된 효과를 실증 결과로 채택한 것이 아니며, 개정본을 여섯 웹 AI가 다시 검토했다는 의미도 아니다. 공개 문서에는 비공개 대화 주소와 원문을 싣지 않는다.

- 지도 목적을 확인된 탐색 판단과 경로의 재사용으로 구체화하고, 요청별 GoalSpec·정책 적용과 공개 정본의 책임을 구분했다.
- 중요 미확인 사항을 중심으로 외부 탐색하며, 검증 수준별 종료·보류와 경험의 검토 후 반영을 정의했다.
- 시간·토큰 외에 재검색·출처 전환·후보 탈락·남은 미확인·종료 적절성·고정 예산 내 누락 후보를 평가하도록 했다.
- R0 기준선과 원자 요청 집계 정정을 보존하고, 계측 보정·작은 개발 과제·공식 정보원 등록·회수/일반화 분리 순으로 후속 작업을 정했다.

R0 당시 프로토콜은 당시 계획서 해시와 정본에 고정되어 있다. 이번 실행 후 계획 개정은 과거 시행의 프롬프트·점수·조건을 바꾸지 않는다. 과거 입력과 대조할 때는 현재 계획서 파일이 아닌 해당 실행의 잠금 해시와 당시 Git 리비전을 사용한다.

### 2026-11-01 구현 전 자체 검증 반영

과제별 필수조건·허용 근거·미확인 처리와 단계별 결과 계약을 구체화했다. 검색 필터의 `satisfies`와 요청 전체 충족을 구분하고, 원자 인자를 관측할 수 있는 실제 계측 경로의 선정·보정 통과를 비교 시험의 진입 조건으로 두었다. 오래된 근거·충돌·무결과·인증 차단·예산 종료 사례와, 같은 사실을 제공한 상태에서 안내의 추가 효과를 분리하는 개발 시험을 추가했다.

후속 순서는 **과제별 판정 계약 확정 → 계측 경로 보정 → 정상·실패 사례 회귀 → 소규모 비교 시험**이다. 이 보완 당시에는 새 계약이 미구현 상태였으며, 이후의 구현·gate 상태는 다음 절에서 구분한다. 공개 카탈로그 필드 확대와 과거 R0 재채점은 이번 보완에 포함하지 않는다.

### 2026-11-01 후속 구현과 보정 상태

[개발 시험 계약과 실행 방법](../evals/discovery-v1/README.md)에 별도 버전의 요청·결과 스키마, 세 개발 과제, 조건별 근거 판정기, 원자 동작을 기록하는 시험용 stdio MCP를 구현했다. 기계적 계약·계측 회귀 19개와 기존 카탈로그·검색 계약 검사를 통과했다. 실제 공식 문서와 읽기 전용 좌표 API에서 open·find·click을 포함한 4개 동작의 시작/종료·응답 해시 연결을 확인했고, 숫자형 위경도 수신이라는 좁은 요구의 실응답 계약도 통과했다. 이는 모델이 정상·실패 사례를 올바르게 판단하는지에 대한 시험이나 서울 실제 조인 성공을 뜻하지 않는다.

같은 사실·URL을 가진 26개 레코드의 비교 입력을 준비했고 안내 추가분의 바이트도 기록했다. 실제 모델 비교는 0회다. 현재 설정에서 활성 검색 연결은 503을 반환하고, 직접 계측하는 검색 제공자의 키도 준비되지 않아 **전체 비교 gate는 blocked**다. 열람 성공을 검색 보정 성공으로 대신하지 않는다. 재개 시 검색 연결 보정을 먼저 통과하고, 모델의 정상·실패 사례와 작은 비교 시험을 새 프로토콜로 잠가 수행한다. 기존 R0 및 공개 카탈로그 스키마는 유지한다.

위 gate는 외부 검색을 포함하는 통제 효율 비교에 적용한다. 지도 자체의 조회·조건·종료 판단을 웹 AI와 확인하는 형성 평가까지 차단하지 않는다. 이후 여섯 웹 AI의 지도 사용과 접근 실패 시 노드 중계를 진행했으며, 실제 관측·허위 노드 인용·재현되지 않은 지적과 후속 정정은 [지도 사용 검증 기록](./web-map-use-validation-2026-11-01.md)에 구분했다. 이 형성 평가를 통제 비교나 검색 gate 통과로 대체하지 않는다.

### 외부 AI 검토 프로토콜

1. 기존 ChatGPT 대화 `인터넷 지도 활용 설명`을 유지한다. Gemini, Claude, Perplexity, DeepSeek, Grok도 각 사용자가 지정해 둔 세션을 사용하고, 접근 가능한 세션을 먼저 inspect한다. 로그인·대화·모델 상태와 미전송 초안을 확인한다.
2. 각 플랫폼에서 현재 선택 가능한 높은 추론 모드를 사용한다. 조사형 검토가 지원되는 플랫폼은 리서치/웹 조사 기능을 켠다. 제공자 간 모델명이 달라 동일 모델을 억지로 맞추지 않고, 실제 모델명·추론/리서치 모드·검토 시각을 기록한다.
3. 첫 라운드에서는 서로의 의견을 보여주지 않고 동일한 계획서 리비전, 서울 지도 확장 계획, 출처 manifest, 같은 검토 질문을 독립적으로 전달한다. 질문은 POI–OD 연결 경로의 실현 가능성, 정보 출처·API/MCP/처리 도구의 누락, R0/R1 설계의 순환·편향, 새 정보 발견 정밀도/재현율, 평가 조건과 판정 기준의 타당성, 실패·안전 gate를 구체적으로 비판하도록 한다.
4. 모든 독립 답변을 받은 뒤에만 의견이 갈린 쟁점과 근거를 요약해 두 번째 라운드에 보낸다. 다수결로 결론내리지 않고 각 모델이 제시한 근거와 반론을 확인한다.
5. 데이터 ID, schema, 좌표계, 시간 정의, 출처 이용 조건은 웹 AI의 주장만으로 확정하지 않는다. 서울시·공공데이터의 공식 원문 및 로컬 manifest와 대조한다. 전송 결과가 불명확하면 중복 전송하지 않고 먼저 해당 세션을 inspect한다.
6. 완료 보고에는 전송 성공·실제 응답 확인이 된 제공자만 포함하고, 불참 모델, 모델 설정, 합의·불일치, 독립적으로 확인한 사실, 남은 의문을 구분한다.
