# API·MCP 역량 지도와 GitHub Pages 계획서

- 상태: 소유자 검토용 초안
- 작성일: 2026-10-27
- 범위: 공개 API·MCP·SDK 지도 데이터의 설계, 게시, 검색 검증

## 1. 결정 요약

사람과 AI가 API, MCP 서버, SDK, 연동 기능을 찾아 활용할 수 있도록 공개 카탈로그를 만든다. GitHub 저장소를 사람이 검토하는 원본 데이터의 기준점으로 삼고, YAML 원본을 검증한 뒤 JSON·JSONL과 정적 검색 사이트를 생성해 GitHub Pages에 게시한다.

공개 카탈로그는 어떤 기능이 문서화되어 있는지, 어떤 입력·권한·전송 방식이 필요한지, 그 주장을 어떤 근거로 확인했는지를 설명한다. 실제 API/MCP 실행기는 만들지 않는다. 다만 MVP 가설 검증을 위해 공개 데이터와 분리된 테스트 하네스에서 테스트용 자원에 연결하는 작업은 포함한다. 계정별 인증·권한 상태, 비밀정보, 실시간 가용성은 카탈로그에 저장하지 않는다.

이 계획은 공개 저장소 이름을 가칭 `agent-capability-map`, 공개 범위를 Public으로 두고, 데이터 CC0-1.0·사이트와 도구 코드 MIT, 초기 외부 기여 비허용이라는 방향을 반영한다. 첫 분야는 에이전트가 작업을 더 잘 수행하도록 돕는 RAG·API·MCP·SDK 관련 자원이다. 이번 세부 감사에서는 ChatGPT, Gemini, DeepSeek, Grok의 응답을 확인했다. Perplexity의 이번 감사 응답은 확인되지 않았고 Claude는 사용량 제한으로 새 답변을 받지 못했다. 따라서 이 계획은 여섯 모델의 합의 결과가 아니다. MVP는 카탈로그 작성·검증·게시·검색을 포함하고, 실제 연결·작업 완료를 통한 효용 검증은 별도 시험 하네스에서 수행한다. 카탈로그 자체는 실행기나 자격증명 보관소가 아니다.

## 2. 목적과 성공 정의

사용자가 자연어로 원하는 일을 설명했을 때, 사람 또는 AI가 다음을 확인할 수 있어야 한다.

1. 어떤 의미상의 작업(Operation)이 필요한가.
2. 그 작업을 제공하는 API·MCP·SDK 연동(Binding)은 무엇인가.
3. 해당 구현이 요구하는 입력, 권한, 전송 방식, 버전과 제약은 무엇인가.
4. 각 설명의 근거와 확인 시점은 무엇인가.
5. 필수 조건이 확인되지 않았을 때 무엇이 불명확한가.

성공은 사이트가 배포되었다는 사실만으로 판단하지 않는다. 첫째, 정적 카탈로그로 목적에 맞는 Operation·Binding을 찾고 제약 위반·무결과 상황에서 올바르게 보류하는지 확인한다. 둘째, 동일한 제한된 과제를 지도 없이 찾는 경우와 비교해 실제 연결·작업 성공률을 유지하면서 시간과 토큰을 줄이는지 시험한다. 둘째 시험은 테스트용 연결·계정·자격증명이 준비된 별도 하네스에서 수행하며, 그 결과를 공개 카탈로그가 직접 실행을 보장한다는 뜻으로 해석하지 않는다.

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

### 사람

1. 분야·범주 → Service → Integration → Binding의 파생 탐색 경로를 사용하거나, 전체 Operation을 가로질러 검색한다.
2. Operation 설명과 연결된 Binding을 비교한다. 하나의 Operation이 여러 Binding에 연결될 수 있으므로 검색 결과에서 상호 이동할 수 있다.
3. 필요한 권한, 제약, Evidence 출처와 확인 시점을 확인한다.
4. 원본 레코드와 변경 이력으로 이동해 수정 근거를 검토한다.

### AI 에이전트

1. `manifest.json`에서 카탈로그·스키마 버전과 작은 Operation 검색 인덱스의 위치를 확인한다.
2. 정적 인덱스를 로컬 또는 참조 검색기로 검색해 짧은 후보 목록과 안정 ID를 얻는다.
3. 필요한 항목만 Operation → 선택한 Binding → 필요한 Evidence 순으로 가져온다.
4. 공개된 요구 조건을 현재 런타임 정보와 비교해 만족·위반·확인 불가를 구분한다.
5. 실행은 별도 권한이 있는 런타임에서만 수행한다. MCP를 붙이면 동일 조회 계약을 고정된 읽기 전용 도구로 제공한다.

후속 MCP 어댑터는 Pages에 게시된 정적 산출물을 읽는 얇은 읽기 전용 계층이다. 별도 카탈로그나 독립 의미 데이터를 보유하지 않으며, 검색·필터링 로직은 참조 검색기와 공유한다. 실제 통합 호출 능력이나 사용자 비밀정보를 가지지 않는다.

## 5. 데이터 모델과 공개 계약

### 핵심 관계

```text
Service
  └── Integration
        └── Binding ── operation_refs ── Operation

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

YAML은 사람이 작성·리뷰하는 유일한 정본이다. JSON Schema는 필드와 타입을 검증하고 추가 CI 검사는 ID·관계·의미 규칙을 확인한다. JSON·JSONL·검색 인덱스·HTML은 전부 생성물이며 수동으로 정본처럼 수정하지 않는다. 모든 레코드는 고유하고 공개 후 바뀌지 않는 ID를 가진다. Binding의 `operation_refs`가 Operation 연결의 단일 원본이며, Operation의 역참조는 빌드에서 생성해 양방향 참조의 불일치를 방지한다.

Evidence는 출처 등급(`source_grade`), 내용 검증 상태(`verification_state`), 링크 점검 결과, 확인 방법·시점을 분리한다. 주장은 `subject_id`와 RFC 6901 JSON Pointer 형식의 `claim_path`로 특정하며, 대상 필드 값을 Evidence에 복사하지 않는다. `claim_path`의 기준 문서는 빌드 시 생성되는 canonical subject JSON 레코드다. 예를 들어 `bnd_acme_search_http`의 API URL은 `/locations/api_base_url/url`로 가리킨다. YAML 점 표기법이나 소스 파일 경로는 허용하지 않는다. CI는 포인터 문법과 실제 대상 경로 존재를 검사한다. 배열 순서 변경에 취약한 숫자 인덱스는 금지하며 배열 전체를 가리키고 원소 위치는 `source_locator`에 설명한다. 출처 등급은 권위만 나타내며 최신성이나 주장의 진실성을 대신하지 않는다. 한 출처가 여러 주장을 뒷받침하면 Evidence 여러 건에서 URL을 반복한다. 자동 해시 봉인보다 변경 영향에 따른 재검토 표시를 우선한다.

### 게시 경로 초안

```text
/catalog/v1/manifest.json                  # schema_version, catalog_revision, 인덱스 URL
/catalog/v1/search/operations.json         # 사람·AI 공용의 소형 후보 검색 인덱스
/catalog/v1/browse/index.json              # 사람용 계층 탐색 요약, 전체 설명은 중복하지 않음
/catalog/v1/operations/<slug>.json         # Operation 상세와 Binding ID
/catalog/v1/bindings/<slug>.json           # 선택한 구현의 요구조건과 네이티브 식별자
/catalog/v1/evidence/<slug>.json           # 요청된 claim의 출처·검증 정보
/catalog/v1/services/<slug>.json           # 서비스 탐색 페이지에 필요한 상세
/catalog/v1/bulk/catalog.jsonl             # 전체 정규화 데이터, 일괄 처리 전용
/llms.txt                                  # 진입점·조회 순서·전체 덤프 주의 안내
```

사람용 UI와 AI용 산출물은 같은 검증된 데이터에서 생성한다. 사람과 AI의 Operation 검색은 같은 컴팩트 인덱스를 공유하고, 계층 탐색 요약만 별도의 파생물로 둔다. `llms.txt`는 안내 자료이며 정본이 아니다. manifest에는 스키마 버전, 카탈로그 리비전, 색인·상세 경로와 레코드 수를 기록한다. 공개 URL과 필드 호환성은 v1 소비자 계약으로 취급하고, 호환되지 않는 변경은 주 버전을 올려 마이그레이션 안내를 제공한다.

### AI 조회와 비용 원칙

전체 덤프를 제공하는 것만으로 토큰 비용이 낮아지지는 않는다. JSONL은 일괄 처리에는 편리하지만, 매 질의마다 전체 Operation과 Evidence를 모델 문맥에 넣으면 카탈로그가 커질수록 불필요한 입력 비용과 선택 오류가 늘어난다. 기본 이용 흐름은 다음의 단계 조회로 한다.

```text
manifest (버전과 검색 인덱스 경로 확인·캐시)
  → 작은 Operation 인덱스 검색
  → 상위 후보만 Operation 상세 조회
  → 선택한 Binding 상세 조회
  → 결정에 필요한 Evidence만 선택 조회
```

`search/operations.json`에는 안정 ID, 짧은 목적, 별칭, 분류·효과, Binding별 짧은 조건 요약, Evidence 상태 요약, 상세 URL 등 후보를 좁히는 필드만 둔다. Binding의 인증·전송·상태 속성을 Operation 수준의 합집합으로 합치지 않는다. 하드 제약은 같은 Binding 한 건의 모든 조건을 함께 검사하고, Operation은 적어도 한 Binding이 전체 조건을 만족할 때만 `satisfies`로 판정한다. 전체 스키마와 장문 설명은 넣지 않는다. 검색 결과 기본 limit은 5, 최대 20으로 시작하며 평가 데이터에서 조정한다. 브라우저 검색과 참조 검색기는 같은 인덱스를 사용한다. 정적 Pages에는 서버 측 검색이 없으므로 AI 클라이언트는 인덱스를 가져와 로컬 검색하거나 참조 검색기를 사용해야 한다. MCP를 도입하면 동일한 검색·필터 함수를 감싼다.

MVP 검색 순서는 버전이 고정된 결정적 lexical baseline으로 한다. 질의와 `name`, `aliases`, `purpose`, `entity_types`를 Unicode NFKC 정규화 후 소문자화하고 토큰화한다. 기본 점수는 정확한 이름 일치 10, 이름 토큰 일치 5, alias 일치 4, purpose 일치 2, entity type 일치 1이며 한 필드 안의 반복 단어는 중복 가산하지 않는다. 점수 내림차순, 동점이면 안정 ID 오름차순으로 정렬한다. 구조화된 하드 필터는 순위 계산 전에 Binding별로 적용한다. 임계 점수 미달 또는 모든 Binding이 제약 위반/미확인인 경우 `{abstain: true, results: []}`를 반환한다. 점수, 정규화 규칙과 알고리즘 버전을 manifest에 기록하고 holdout 실행 전에 고정한다. 의미 검색은 이 baseline과 분리해 평가한 뒤 추가한다.

초기 20~50개 Operation에서는 하나의 검색 인덱스로 시작한다. 분할은 임의의 레코드 수가 아니라 실제 직렬화 크기·전송량·토큰 예산 측정이 합의된 한도를 넘을 때만 한다. 전체 `bulk/catalog.jsonl`은 로컬 색인 구축, 일괄 동기화, 평가용이며 일반 질의의 기본 경로로 사용하지 않는다. manifest와 리비전이 고정된 산출물은 캐시 가능하게 만들고, 모든 결과에서 catalog revision을 확인할 수 있게 한다.

Evidence는 안전성 또는 실행 가능성 판정에 필요한 경우 후보별로 조회한다. 색인에는 검증 상태와 시점의 짧은 요약을 제공해, 불확실한 항목을 상세 조회 없이도 걸러내거나 `unknown`으로 표시할 수 있게 한다. 단, 중요 제약의 근거가 없는 후보를 검증된 것으로 취급하지 않는다.

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

## 7. 단계와 완료 기준

### 0단계: 결정과 기준 확정

- 가칭 `agent-capability-map`으로 공개 저장소를 준비하고, 데이터 CC0-1.0·코드 MIT 제안과 외부 기여 비허용 정책을 기록한다.
- 초기 범주에서 RAG는 분야·역량 범주로, API·MCP·SDK는 연결 방식이나 구현 유형으로 구분한다. RAG 기법 자체는 Service/Integration이 아니므로, 실제로 조회 가능한 제품·라이브러리·자료인지 Operation/Binding을 제공하는 사례인지 포함 기준을 명시한다.
- 원본은 서비스별 편집 묶음과 독립 Operation 파일을 결합한다. MCP 어댑터는 후속 단계로 두고, MVP는 정적 파일을 통한 AI 검색과 단계 조회를 검증한다.
- MVP는 최소 기능 제품(Minimum Viable Product), 즉 핵심 이용 흐름이 실제로 유용한지 검증할 가장 작은 완성 범위다. 이 계획에서는 YAML 계약·검증, Pages의 사람용 탐색, AI용 정적 검색 인덱스와 상세 파일, 변경 영향 검토, 고정 골든 질의 평가가 핵심이다.

**완료 기준:** 결정 기록, 공개 데이터 정책, 기여·리뷰 책임자가 문서화되어 있다.

### 1단계: 최소 데이터 계약과 예시

- 핵심 객체, 불변 ID 규칙, 관계 방향, 필수·선택 필드, Evidence 출처 등급과 검증 상태를 정의한다.
- 초기 seed는 약 5~10개 Service와 20~50개 Operation, 해당 기능을 구현하는 Integration·Binding으로 구성한다. 이는 초기 평가 규모 제안이며 실제 근거가 준비된 항목 수에 따라 조정한다.
- 내부 유지관리자가 쓰는 PR 체크리스트와 작성 예제를 둔다. 외부 기여 안내는 공개하되 외부 제출은 받지 않는다는 정책과 모순되지 않게 한다.

**완료 기준:** 예시 데이터가 스키마와 참조 검사를 통과하고, 사람이 PR에서 변경 이유와 Evidence를 리뷰할 수 있다.

### 2단계: 생성과 게시

- YAML 원본에서 manifest, 공용 Operation 검색 인덱스, 사람용 계층 요약, ID별 상세 JSON, bulk JSONL과 정적 사이트를 생성한다.
- pull request 검사와 기본 브랜치 Pages 배포를 구성한다.
- PR에서는 생성물 미리보기와 의미 영향 요약을 검토하고, 병합 후 Actions가 동일한 빌드를 Pages에 게시한다.
- 소비자는 manifest의 catalog revision을 기준으로 산출물 일관성과 캐시를 확인한다.

**완료 기준:** 빌드가 재현 가능하고, Pages에서 사람용 UI와 기계용 파일을 모두 읽을 수 있다. 비밀정보는 배포 산출물에 포함되지 않는다.

### 3단계: 검색 및 실제 작업 비교 검증

- 동의어·다른 표현·제약 포함·적합 항목 없음 사례를 포함한 버전 관리 골든 질의를 준비한다.
- 정적 인덱스와 참조 검색기로 Operation 후보와 Binding을 선택하고, 권한·전송 조건·Evidence 부족을 설명하는지 확인한다.
- 대표 질의마다 전체 카탈로그가 아니라 필요한 색인과 후보 상세만 조회하는지, 조회 바이트·모델 입력 토큰·검색 호출 수를 기록한다.
- 소규모 사람 사용성 검토를 통해 검색 용어와 페이지 구조를 수정한다.
- 사용자 테스트 계정 또는 무해한 샌드박스 자원을 이용해 제한된 실제 작업을 완료하는 별도 하네스를 둔다. 카탈로그는 실행·자격증명을 제공하지 않으며, 같은 허용 자원을 지도 사용군과 대조군에 제공한다.

비교 실험은 두 층으로 구분한다.

| 시험 | 지도 사용군 | 대조군 | 측정 |
|---|---|---|---|
| 카탈로그 검색 | 정적 인덱스와 상세 파일로 Binding 선택 | 같은 과제에서 일반 웹 검색·문서 탐색으로 선택 | 올바른 Operation/Binding, 제약 위반, 무결과 보류, 탐색 시간·토큰·가져온 바이트 |
| 작업 완료 | 지도에서 찾은 Binding으로 테스트 하네스가 연결·실행 | 지도 없이 같은 허용 자원·권한으로 탐색·연결·실행 | 작업 성공률, 전체 시간, 총 토큰, 호출 수, 오류 유형 |

두 군은 같은 모델, 프롬프트 제약, 자원 권한, 시간·호출 한도를 사용한다. 과제 순서는 무작위화하고 새 대화 문맥을 사용해 반복 과제 학습을 줄인다. Gold set은 정답 Operation, 허용 Binding, 하드 제약, 정답 없음 여부, 작업 완료 판정을 실행 전에 고정한다. 과제는 이름 일치, 표현 바꾸기, 복수 제약, 정답 없음, 안전상 선택 불가 유형을 포함한다. 사용자 데이터 변경, 결제, 영구 삭제는 제외하고 테스트 계정에서 되돌릴 수 있는 작업만 사용한다.

**완료 기준 초안:**

- 모든 질의에서 스키마·ID·참조·비밀정보 검사가 통과한다.
- Recall@5뿐 아니라 Precision@5, Top-1, 올바른 Binding 선택률, 제약 위반 통과율, 정답 없음 보류율을 보고한다. 초기 목표는 정답 Operation Recall@5 90% 이상, 하드 제약 위반 통과 0건(최소 30개 하드 제약 질의), 정답 없음 보류 90% 이상(최소 20개 무결과 질의)이다. 표본 수와 쿼리별 결과를 함께 공개하고, 작은 표본의 0건 오류를 일반적인 오류율 0으로 해석하지 않는다.
- 질의당 기본 경로에서 전체 덤프를 모델 문맥에 넣지 않고, 참조 검색기가 후보를 좁힌 뒤 필요한 상세만 전달한다. 색인·후보 수와 입력 토큰 예산은 첫 벤치마크에서 측정해 수치 기준을 확정한다.
- 대표 시나리오에서 전체 덤프 없이 정적 인덱스→후보 상세→선택 Binding→필요한 근거 순으로 조회한다. MCP `tools/list`와 MCP 도구 동등성은 후속 어댑터 단계에서 검증한다.
- 실제 작업 비교는 동일 과제를 두 조건에서 짝지어 실행하고 순서는 무작위화한다. 최소 20개 과제를 2개 이상의 모델에서 평가하고, 파일럿 분산을 사용해 필요한 표본 수를 산정한다. 사전 목표는 성공률 차이의 비열등성 한계를 −5%p로 두고, 지도 사용군의 중앙값 시간은 10% 이상, 총 토큰은 15% 이상 줄이는 것이다. 이 목표는 holdout을 보기 전에 고정한다. holdout에서는 짝지은 차이의 95% 신뢰구간을 보고하며, 성공률 차이의 하한이 −5%p보다 커야 하고 시간비의 상한이 0.90 이하, 토큰비의 상한이 0.85 이하일 때만 E2E 가설을 통과한다. 검색 후보를 찾더라도 실제 작업이 실패하면 end-to-end 가설은 통과하지 않는다.
- 전역 검색과 계층 탐색이 모두 성공하고, 상호참조로 다른 Service의 Binding을 찾을 수 있다.
- Evidence가 없거나 오래된 경우 불확실성을 명시하고, 근거가 있는 설명만 제공한다.
- 최소 5개의 실제 작업 시나리오에서 사람이 적합 후보와 근거를 찾을 수 있는지 확인한다.

수치는 첫 평가 후 조정할 수 있지만, 하드 제약 오류와 데이터 검증 기준은 완화하지 않는다. 작은 파일럿만으로 일반적인 절감을 주장하지 않고 holdout 규모와 불확실성도 함께 보고한다.

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

- **이번 라운드에서 확인된 공통 의견:** 정적 원본에서 생성된 인덱스와 상세 자료를 게시하고, 전체 덤프 대신 후보를 좁혀 필요한 상세만 읽게 한다. Operation↔Binding은 다대다이며, Binding이 편집 관계를 소유하고 역방향 참조를 생성하는 안이 서비스별 편집 묶음과 맞는다. 품질은 Recall@5만으로 판단하지 않고 올바른 Binding, 제약 위반, 무결과 보류, 탐색 시간·토큰과 실제 과제 완료를 함께 본다. 검색 필터는 개별 Binding에서 판정해야 하며, 서로 다른 Binding의 속성을 합쳐 hard constraint 만족으로 오인하면 안 된다.
- **구조 선택:** 한 파일에 모든 정보를 몰아넣기보다 Service 단위의 유지관리 묶음과 독립 Operation 파일을 결합한다. 사람용 계층 탐색은 생성 뷰로 제공하고, 원본 모델은 관계형 정본으로 유지한다.
- **검색 선택:** 사람과 AI가 함께 쓰는 소형 공용 검색 자료를 두고, 사람용 계층 색인은 별도로 둔다. 정적 사이트만으로 임의 서버 검색이 된다고 가정하지 않으며, 브라우저와 AI 호스트가 참조 검색기로 후보를 찾는다. 결과 수와 색인 크기는 측정 후 조정한다.
- **MCP 시점:** 정적 사이트와 파일만으로도 공개 데이터와 검색 계약을 먼저 검증할 수 있다는 의견을 반영해 MCP 어댑터를 후속 단계로 미뤘다. MCP가 필수 소비 경로라는 가정이 검증되면 새 정본을 만들지 않고 같은 생성물에 연결하는 얇은 읽기 전용 어댑터를 추가한다.
- **Evidence와 안전:** 출처의 권위와 내용 검증·링크 도달 상태는 서로 다른 값이다. 자동 링크 점검 실패는 주장이 거짓임을 뜻하지 않으며, 재검토 표지만 남긴다. MVP에서는 Source/Claim 별도 테이블을 두자는 의견도 있었으나, 중복 최소화와 소규모 운영을 위해 Evidence가 대상·JSON Pointer 경로·출처를 직접 보유하는 안을 택했다. 같은 출처 URL은 여러 Evidence에 반복할 수 있다. 정규 Source 엔터티는 데이터 중복이 실제 문제가 될 때 후속 검토한다.
- **검증 범위 조정:** 정적 카탈로그 평가만으로는 사용자가 원하는 “찾은 뒤 실제로 연결해 일을 마치는가”를 증명하지 못한다. 반대로 실행기·비밀정보를 공개 카탈로그에 넣을 이유도 없다. 따라서 제품은 정적 조회로 유지하고 별도 테스트 하네스가 같은 조건의 지도 사용군과 일반 웹 탐색 대조군의 실제 작업 성공률·시간·토큰을 비교한다.
- **평가와 운영:** 골든 질의, 하드 제약 위반 0건 목표, 조회량·토큰 측정을 포함한다. 자동 검증과 에이전트 리뷰가 변경 후보를 만들고 사람 유지관리자가 공개를 승인한다.

이번 세부 감사에서는 ChatGPT, Gemini, DeepSeek, Grok의 답변을 확인했다. Perplexity의 이번 감사 응답은 확인되지 않았고, Claude는 사용량 제한으로 새 답변을 받지 못했다. 따라서 이번 라운드에서 여섯 모델의 합의가 이뤄졌다고 주장하지 않는다. Claude 또는 Perplexity의 새 답변이 확보되면 현재 결정과 충돌하는 부분만 추가 검토한다.
