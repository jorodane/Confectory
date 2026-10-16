# v424 전체 UI 연결 작업

사용자의 2026-10-15 05:45 UTC 요청은 v424 UI의 모든 내용을 실제 엔진·데이터·영속화에 연결하는 것이다. Codex 단계 완료를 이 전체 요청의 완료로 취급하지 않는다. 실제 사용자 계정·토큰·유료 호출·온라인 배포를 개발 검증에 사용하지 않는다. main, 사용자 업로드, 이전 원본 ZIP, Android 설정을 보존한다. 기존 Workspace·의미 편집·Save/Review/Confirm·Helper·Worker·Run/Stop·Yogi의 소유권과 CAS는 유지한다.

## 기준과 현재 체크포인트

사용자 업로드 `main` 커밋 `18e27bc17c28cfb7925150bb3ded7c237edf6afb`는 이전 `work/current` 코드에 v424 ZIP 하나만 추가했다. ZIP 16,240,596바이트, Git blob `a5314fc12f34e1f5c2069eefcbcc79d0495135f2`, SHA-256 `b7969cd109ea2dad38bde9c9ab13967c20162c920a45a8cd51a8f82df6041874`. 내부 manifest는 v424, source `21da0b48256439a530c3e2097b2cb354c43e3956`이며 24개 파일 해시, ZIP 25개 항목의 CRC·경로·링크 검사를 통과했다. 원본을 수정하지 않고 별도 폴더의 로컬 HTTP/Chromium에서 29개 화면 상태를 열어 확인했으며 페이지 오류는 없었다. 외부 요청은 차단했다. README의 실행 설명과 데모 데이터는 작업 지시나 실제 엔진 상태로 사용하지 않았다.

Codex 준비·공식 기기 코드 로그인 단계는 `114e00ffb35f6c3f4e5cdfd361ff37b535b1e2cf`로 `work/current`에 게시했다. 원격 main은 사용자 업로드 커밋 그대로다. [별도 구현/검증 기록](codex-preparation.md). 17개 실제 웹 편집 회귀, 소유 stdio 실행 경계, Home Windows/Android 관리 프로필 컴파일, 일반 Git 체크아웃/19개 리소스 시작 검사가 전체 실행과 수정 후 재실행을 통해 통과했다. 이는 아래 미완료 영역의 검증 결과가 아니다.

[구조 목록](evidence/v424-integration/source-inventory.json)은 원본 app.js의 전역 함수 452개와 blueprint.js를 포함한 data 속성 257개를 추적한다. 함수·속성에는 내부 도우미와 표시용 마커도 있다. 이 수를 사용자 동작 수나 구현 완료 수로 사용하지 않는다. 동적 메뉴·키보드·입력·드래그 동작은 아래 묶음으로 별도 확인한다.

## 동작 지도

`기존`은 실제 소유 계약과 기존 회귀가 있다는 뜻이며 v424 전체 정합 완료 표시가 아니다. `부분`은 일부 동작만 연결됨, `bridge`는 하위 계약이 있으나 공개 연결이 없음, `계약`은 소유·생명주기 계약 추가가 필요함, `서비스`는 외부 주체/서비스의 실재성과 설정을 별도 검증해야 함을 뜻한다. 각 행은 취소·반복·닫기·프로젝트 전환·재시작·실패 경로까지 통과하기 전 완료로 바꾸지 않는다.

| ID | 화면과 동작 | 현재 | 실제 소유자 / 다음 연결 |
|---|---|---|---|
| S01 | 로고·로딩·Home 진입·Agent 선택·나중에 | 기존 | EditorHome 엔트리/실제 연결 상태. v424 전환/접근성 대조 |
| S02 | 앱 최소화·최대화·복원·닫기 | 부분 | 공통 WebUI/네이티브 창 수명. 각 호스트 능력 확인 |
| H01 | 프로젝트 검색·정렬·즐겨찾기·열기·목록에서 제거 | 기존 | ProjectManager/소유 Home cards. 파일 삭제와 목록 제거 구분 |
| H02 | 프로젝트 제목·설명·아이콘·폴더 열기 | 부분 | 실제 프로젝트 식별자와 카드/프로젝트 메타데이터의 경계 |
| H03 | 프로젝트/내 팩/시장 탭·팩 검색·즐겨찾기 | 부분 | LocalInventory와 실제 등록/소유 라이브러리. 데모 팩 제거 |
| H04 | 새 프로젝트: 필수 팩·유형·디렉터리·이름·설명 | 부분 | PlanCreation/CreateProject/선언된 대상. 임의 pack 요구를 실제 registry로 검증 |
| H05 | 새 프로젝트의 선택적 Helper/Agent·임의 이름 | 부분 | 실제 Helper membership/프로필. 생성만으로 호출 승인하지 않음 |
| H06 | 프로젝트 정보·설정·숨기기·완전 닫기·최근 기록 | 부분 | 실제 context와 Source/Execution/AI owner, 명시적 close 확인 |
| W01 | 팬·줌·슬라이더·프리셋·원점·메인 창 | 기존 | 공통 Workspace runtime + 소유 presentation 저장 |
| W02 | 창 이동·리사이즈·접기·스냅·다중 선택·키보드 | 기존 | 공통 노드/선택/드래그 소유. v424 추가 차이 검토 |
| W03 | 탭 생성·이동·재정렬·분리·닫기·재열기 | 부분 | 실제 공유 초안/독립 View 수명, 입력 보존 |
| W04 | 노트·그룹·자식 Workspace·포털·제거 취소 | 기존 | 공통 presentation. 의미 객체 삭제와 구분 |
| W05 | Workspace 링크 연결·해제·관계 메뉴·검색 배치 | 부분 | 실제 presentation 링크와 엔진 의미 관계 분리 |
| W06 | 창/노드 혼합 선택·이동·부모/자식 공간 전환 | 기존 | 공통 runtime. v424 상호작용 대조 |
| B01 | 개념/기능/모듈 브라우저·트리·범위·밀도·정렬·검색 | 부분 | 실제 LocalInventory/SemanticCatalog/PackWorkspace |
| B02 | 브라우저 복제·분리·도킹·폴더·하위 탐색 | 부분 | 실제 namespace/관계와 독립 View/presentation |
| B03 | object/schema/category/concept/function/module 생성 | 연결/검증 | SourceEditor/Create/EditWorkspace/Create는 6종 지원. WebInvoke/생성 UI 제한 확장 |
| B04 | 바리에이션·부모/정보 선택·상속 관계 변경 | 부분 | 소유 객체 바리에이션의 부모 버전/CAS·새 선언/등록부 원자적 초안·상속/로컬 재정의·묶음 Review/Confirm 연결. 기능/외부 부모의 생성 UX는 후속 |
| B05 | 이름·아이콘·설명 변경·F2·헤더 사용 | 부분 | 표시 이름과 qualified ID 구분. 실제 메타데이터/초안 CAS |
| B06 | 삭제·다중 삭제·참조 조사·대체/정리·취소 | 계약 | 등록/참조 변경의 소유 초안과 묶음 Review/Confirm. 임의 파일 삭제 금지 |
| D01 | 실제 필드·참조·enum·벡터·복합 값 편집 | 기존 | SchemaEditing, 경로/리비전과 inherited origin 유지 |
| D02 | 필드 초기화·상속으로 되돌리기·배열/복합 항목 이동 | 소유 초안 연결/검증 | 로컬 unset, 명시적 부모 값 재정의, 배열 항목 이동·복합 JSON 편집과 로컬 schema 필드 순서/제거를 소스 SHA·리비전에 연결. 원본은 별도 Review/Confirm |
| D03 | Data 테이블: 열/행·검색·정렬·열 너비·Fill | 부분 | InstantTable에서 실제 schema/data path·정밀 정수 정렬·열 순서/너비·다중 편집 CAS 연결. 브라우저 Data 모드의 전체 속성 열은 후속 |
| D04 | 비교/즉석 테이블 구성·대상 추가/제거·창 분리 | 소유 초안 연결/검증 | 공개 객체/필드 구성·구성 해시 CAS·borrowed 공유 초안·표시 리비전/소스/스키마 해시·64행/16열·정밀 JSON·private 구성/입력/열 배치 재시작 연결. 요청 문구는 설명이며 임의 계산/AI 표 생성은 후속 |
| D05 | 참조 드래그·원본 정의 이동·상속 출처·읽기 전용 팩 | 부분 | 직접 참조의 소스 SHA/리비전·등록/팩/정의 identity·읽기 전용 source View 연결. 참조 드래그와 임의 깊이 탐색은 후속 |
| D06 | 개념 맵: 실제 노드·간선·선택·집중·전체 보기 | 소유 초안 연결/검증 | 실제 선언·관계·버전/해시, 선택·검색·역할·집중·배치·재시작. 소유 View 밖 참조와 해석 오류 표시. 실제 직접 참조의 외부 정의 읽기 전용 열기 연결 |
| E01 | 스키마/정보 필드 추가·수정·제거·타입·개수·순서 | 부분 | Parser/SchemaContracts 실제 지원 형태와 원본 출처 |
| E02 | enum 정의·이름·값·아이콘·참조·선택 메뉴 | 부분 | 실제 enum schema/data contract와 리뷰 가능한 변경 |
| E03 | 객체 함수/동작 목록·상속·연결/해제·순서 | 계약 | 실제 function datum, module/feature 관계, 임의 데모 methods 제외 |
| E04 | 함수 입력·출력·이름·설명·타입·시그니처 편집 | 연결/검증 | 실제 FunctionSignature/Parser의 타입·이름·순서와 메타데이터, 독립 View·입력 보존·리비전+내용 해시 CAS·compiler Confirm 검증. graph 연결 후 계약 영향 표시는 후속 |
| E05 | 모듈 require/default/provide/import·구현 선택·호환성 | 계약 | 실제 요구/제공 관계와 compiler-backed 검증 |
| E06 | 함수 노드·입출력 pin·연결·접기·설명·직접 작성 | 계약 | 실제 소스/관계와 별도 배치. graph 장식과 실행 의미 분리 |
| E07 | Blueprint 노드 추가/삭제/링크/저장/확대·맞춤 | 설계 확정/구현 중 | [확정 구조](FEATURE_BLUEPRINT_ARCHITECTURE.md): graph+노드 파일이 원본, 시스템이 최종 C# 조립. 기존 AlgorithmProjection은 레거시 설명용. 원본·노드 Worker·파생 산출물의 별도 소유/버전/빌드 경계를 단계적으로 연결 |
| E08 | 계약 검토·모듈 검토·컨셉/밸런스/테스트 요청 | 부분 | 실제 검사 또는 Helper 요청 미리보기/동의/도구 범위 |
| C01 | Apply/Save/버리기/공유 초안/재시작 | 기존 | PackWorkspace/EditWorkspace, 최종 파일과 작업 사본 구분 |
| C02 | 묶음/부분 Review·Before/After·타깃·Confirm·취소 | 기존 | source hash/revision/token/CAS, 생성 등록부 필수, 실제 컴파일 |
| C03 | 충돌 비교·로컬/상대 변경·선택·재검토 | 계약 | 실제 충돌 스냅샷과 새 리비전. 예시 HP 값/처리됨 표시 제외 |
| C04 | 의미 편집 Undo/Redo·이력·현재 리비전 충돌 | 계약 | 실제 소유 초안의 전/후 상태와 새 CAS 편집. 외부 변경을 덮어쓰지 않음 |
| I01 | 신문고 목록·건수·긴급도·문제/요청/승인/충돌 | 계약 | 실제 source/build/AI/task 사건과 소유 inbox 기록 |
| I02 | 재시도·승인 검토·충돌 이동·Yogi 첨부·처리 이력 | 계약 | 원 사건/현재 상태 검증. 표시상의 해결을 실제 해결로 취급하지 않음 |
| Y01 | Exactly·텍스트·Seal·제거·이미지 캡처/미리보기·복구 | 기존 | YogiBox 실제 영속/CAS/프로젝트/소유 scope. 최신 기록 EDITOR_V318_YOGI.md |
| Y02 | 프로젝트/Helper/사용자 recipient 선택·첨부/해제·전달 | bridge/계약 | YogiBox.Handoff/Receive의 불변 sealed snapshot 경계가 있다. 소비자 recipient 소유·영속·중복/취소/실패 계약 연결 필요 |
| Y03 | 재수신·기록·오래된/삭제된 의미 항목·수신 권한 | 부분 | 기존 Revalidate 유지, 전달이 기억/실행/승인으로 확대되지 않음 |
| A01 | 증강 실제 생성·리롤·방향·닫기·선택·Task | 기존 | ProjectAI/Augment/WorkerTasks, 별도 내용/사용량 승인 |
| A02 | 로컬 Custom·제안 제출·Skip/증강 삭제·이력 | 연결/검증 | 실제 chief/scope/CAS/idempotency와 로컬 owner, 생성 묶음 고정 비우기·보관·최신32개씩 페이지 조회. 35개 이력/재시작/읽기 전용과 별도 모델 승인 경계 검증 |
| A03 | 선택된 작업 취소·진행 중 중지·구현/채택·복구 | 부분 | 실제 task owner/state. Skip·선택 취소·실행 중단 구분 |
| A04 | Worker 진행/범위·기여·검증·Review/Adopt·재시작 | 기존 | 실제 journal, 비밀/권한/실행 owner 재생 금지 |
| R01 | Play/Stop·빌드/실행/실패/종료·출력·대상 | 기존 | ProjectExecution의 실제 소유 프로세스. 원본 소스로 실행 |
| R02 | 단독 빌드 job·취소·진행·결과/산출물 | 계약 | 실행하지 않는 별도 job start/observe/output/stop |
| R03 | 실제 렌더 삽입·크기·입력·detach/close | 계약 | 자식 surface 획득/전달/수명. 예시 CSS 장면 제외 |
| R04 | Pause/Resume/Step·실제 frame/ack | 계약 | 런타임 scheduler/control. OS 신호나 임의 카운터 대체 금지 |
| R05 | 실행 owner 재연결·이전 프로세스 관찰/종료 | 계약 | durable launch identity/lease/시작 신원, 명시적 재연결. PID 추측 금지 |
| R06 | 소스 팩 내보내기·타깃 빌드 다운로드·APK | 부분 | 실제 source closure/artifact, 선언된 대상/서명 상태. Android 설정 보존 |
| P01 | Helper 모집·선택·전역/프로젝트 소속·기억 범위 | 기존 | Helper 실제 membership/소유권·curated context |
| P02 | Helper 이름·직함·상태·소개·이미지·편집·제거 | 부분 | 소유 프로필/이미지 저장·버전/참조, 실제 존재 membership |
| P03 | Helper 이미지 생성·수정·선택 | 계약 | 별도 image provider/content/usage 권한·실제 산출물, 개발은 소유 fixture |
| P04 | Helper 창 pin/대화 입력/배치·즐겨찾기·이력 | 부분 | 기존 private input/presentation 복구 + 실제 history 데이터 |
| P05 | 프로젝트 채팅·전역 채팅·첨부·기억·재시작 | 부분 | 명확한 project/global actor owner와 실제 journal, 미전송 입력/전송 이력 구분 |
| G01 | Codex 탐색·별도 준비·로그인·모델/연결 확인 | 연결/검증 | 114e00f. 설치/로그인/모델 확인/실제 요청 권한 분리 |
| G02 | Claude Code/Gemini/사용자 지정 Agent·버전/설치 | 계약/서비스 | 실제 provider/CLI 프로토콜·소유 config·공식 source authority·검증된 profile |
| G03 | Agent 상세·계정/사용량·중지/연결 해제·Helper 연결 | 부분 | 실제 지원 metadata만 표시. 근거 없는 백분율/계정 상태 제외 |
| U01 | 내 정보·이미지·직함·상태·소개·화면 설정 | 부분 | 실제 로컬 owner/profile와 private presentation 저장 |
| U02 | co-worker 검색/요청/수락/차단/해제/제거/알림 | 계약/서비스 | 실재 actor/membership와 검증된 서비스 또는 명시적 지역 scope |
| U03 | co-worker 대화·읽음/미읽음·news·Yogi 전달 | 계약/서비스 | sender/recipient/room/ack/persistence, 데모 친구/응답 제외 |
| M01 | 내 팩 저장/편집/제거·설치 목록·사용/의존성 | 부분 | 실제 pack namespace/version/manifest와 소유 라이브러리 |
| M02 | 시장 목록·검색·정렬·상세·즐겨찾기 | 서비스 | 실제 configured registry/catalogue. 임의 예시 항목 제외 |
| M03 | 다운로드/설치/업데이트/제거·의존성 추가/제외 | 계약/서비스 | 원본/digest/소유 경로·버전 충돌·manifest Review/Confirm |
| M04 | 공개/외부 게시·수정·철회·배포 이력 | 계약/서비스 | 실제 publisher/registry와 명시적 게시 권한. 개발 중 온라인 게시하지 않음 |

## 구현 순서와 제품 결정 기록

1. 먼저 이미 있는 의미 생성/관계/초안 API의 공개 bridge와 실제 데이터 View를 연결한다. 생성 종류 확장, 관계 맵과 즉석 테이블, 필드/정의 편집, 계약·모듈 검토를 동일한 소유 초안과 Review/Confirm에 둔다.
2. 기존 Augment.Custom/Skip을 로컬 계획 owner에 연결한다. Custom은 서술 후보, Skip은 현재 미선택 제안의 이력/해제이며 작업 실행·취소·새 유료 생성과 구분한다. 닫기는 제안을 보존한다.
3. 실제 사건 inbox, Yogi recipient/attachment, 프로필/대화/소속의 소유·영속 계약을 추가한다. 현재 Yogi 영속/CAS를 다시 구현하거나 이미지/권한/토큰을 presentation에 복사하지 않는다.
4. 빌드 job·surface/control·실행 재연결을 일반적인 런타임/실행 계약으로 추가한다. 특정 Editor 화면 전용 완료 신호로 우회하지 않는다.
5. 추가 Agent와 사용자/registry 서비스는 공식 프로토콜과 실제 source/identity authority를 검증하고, configured provider를 소유 fixture로 시험한다. 서비스가 설정되지 않은 상태를 온라인 연결/설치/게시 완료로 표시하지 않는다. 실제 계정·토큰·모델/유료 호출·외부 배포는 별도 활성화/검증 범위다.
6. 각 묶음마다 실제 일반 ProjectPack UI의 사용·취소·반복·닫기·전환·재시작·실패와 해당 owner의 CAS/권한/리비전/해시를 검증하고 work/current에 게시한다. 마지막에 전체 묶음 회귀와 일반 체크아웃 시작을 반복한다.

확인된 언어 제약: 현재 FunctionSignature의 런타임 타입 문법은 primitive/배열이며 schema 필드는 general/compound/reference/function을 구분한다. UI 시그니처/타입 목록은 실제 파서/메타데이터를 따른다. 프로토타입 JSON의 임의 객체를 새로운 런타임 타입이나 실행 모델로 간주하지 않는다. 미지원 타입·서비스·호스트 기능은 구체적 상태로 남기고 구현/검증 행을 미완료로 유지한다.

전체 완료 조건은 이 지도와 구조 목록의 사용자 동작에 연결·저장·수명·실패·검증 근거가 모두 있는 것이다. 현재 문서는 진행 지도이며 v424 전체 구현 완료 보고가 아니다.

## 2026-10-15 추가 연결 검증 중

- B03: 6종 선언 생성 bridge와 메뉴를 연결했다. category/concept/function/module도 기존 생성 등록부 필수 묶음과 Save/Review/Confirm을 사용한다. 여섯 종류의 실제 컴파일 Confirm과 독립 프로세스 재시작 후 각 선언 재열기가 통과했다. 새 종류를 object로 저장하거나 자동 확정하지 않는다.
- E08/C02: authoring host가 함수 signature와 parent/module/include/require/default/provide/use/contain/import의 실제 전후 차이를 설명한다. 순서 변경도 검토에 포함한다. identity/body/tool/options/comments 등 요약하지 않은 변경의 전체 소스 확인은 유지한다.
- A02: 실제 로컬 계획 owner와 Custom/현재 생성 묶음 비우기/보관을 공개 UI에 연결했다. 계정·모델 없는 실제 UI의 chief/scope/명령 중복/CAS/작업 선택/보관/재시작/오래된 제안 거부 검사가 통과했다. 선택한 연결로 Worker 전 검토를 바인딩·거부·취소하는 경로와, Helper 공유 권한 변경 후 이전 소유자의 제안 추가/선택 거부도 통과했다. 이 경로도 새 내용·사용량 승인 전에는 모델을 호출하지 않는다.
- 제품 결정: 사용자 자신의 제안과 Helper에게 새 생성을 요청하는 동작을 각각 ‘내 제안’, ‘Helper에 제안 요청’으로 표시한다. 닫기는 제안을 유지한다. 생성 묶음 비우기는 미선택 생성 제안만 화면에서 해제하며 과거 이력·직접 쓴 제안·이미 선택한 작업은 보존한다. 직접 쓴 제안의 보관도 작업 취소로 해석하지 않는다.

추가 묶음의 관련 회귀 근거는 [검증 기록](evidence/v424-integration/authoring-local-planning.json)에 있다. 6종 생성/재열기, 계약·모듈 요약, 실제 증강 저널, 기존 전체 편집, 생성 실패 시 원본 보존, Helper 재시작, Windows/Android 관리 프로필 컴파일이 해당 단계의 실행과 영향 수정 후 재실행을 통해 통과했다. 마지막 로컬 검증은 실제 계정 없이 먼저 실행했고, 연결·거부·취소 시 HTTP 호출 0회를 확인했다. Helper 권한을 새로 준비·명시 승인한 뒤에는 소유 loopback fixture에만 제안 요청 1회가 도달했다. 외부 계정·모델·유료 호출 검증이 아니다.

[내 제안 실제 화면](evidence/v424-integration/local-custom.png)과 [6종 선언 재열기 화면](evidence/v424-integration/six-kinds.png)은 일반 Home 소비자의 소유 샘플에서 촬영했다. 720px 높이에서 로컬 카드와 하단 동작이 보이는 것을 확인했다. 새 로컬 소유자가 기록된 작업을 자동 실행하지 않는다. 준비 상태 작업 취소, 모든 과거 제안의 페이지 구성과 전체 지도 나머지 행은 별도의 미완료 범위다. **이 체크포인트는 전체 v424 완료가 아니다.**

일반 Git 체크아웃 검증은 구현 커밋 `0c46fbb6ab7d5de87e54a2579eeb423a63f83816`에서 통과했다(64.598초). 이전 CRLF 파일을 유지한 정상 pull과 새 LF 체크아웃에서 19개 리소스의 실제 시작·해시 일치 및 변조 거부를 확인했다. main·원본 ZIP·Android 설정 변경은 없다.

## 확정된 기능 내부 구조 반영

2026-10-15 08:47:48 UTC 기능 구조 개편이 확정되었다. [Blueprint 원본·노드 파일·시스템 조립 설계](FEATURE_BLUEPRINT_ARCHITECTURE.md)를 전체 연결 기준으로 삼는다. 기존 외부 계약과 일반 소스 경로는 보존한다. 현재 v424 비충돌 UI 연결을 계속하며, 새 기능 화면은 사용자의 다음 명시적 전달에 맞춘다. live Site를 임의로 새 기준본으로 바꾸지 않는다. 새 경로에서 Worker가 최종 C#을 직접 편집하거나 영역 패치하는 동작을 제공하지 않는다. 루프·비동기·예외 등 미정 graph 실행 의미는 기존 계약을 확인하고 필요한 결정만 보고한다.

## 선언 View·준비 작업 취소의 추가 체크포인트

[검증 기록](evidence/v424-integration/declaration-views-ready-cancel.json). 함수·구현의 입출력/순서, 모듈 require/default/provide/include, 실제 implementation import와 선언 속성을 기존 파서·초안에 연결했다. `declaration` 독립 View는 기존 3개 슬롯과 수명을 공유한다. 편집은 표시한 리비전과 UTF-8 내용 해시를 함께 확인하며, 외부 변경·재시작·충돌 시 미적용 입력을 유지한다. 표시 이름은 ID 변경이 아니다. Save와 묶음 Review/Confirm은 유지한다. schema field/data의 로컬 초기화·순서 API는 파서로 검증했지만 해당 기존 테이블의 모든 UI 연결 완료를 뜻하지 않는다.

준비 작업 취소는 실제 WorkerTasks의 잠금·lease·명령 재생·저널 CAS에서 처리하며 Agent를 시작하거나 취소하지 않는다. 실행 중·완료 작업은 ready-only 취소가 거부한다. 기존 Cancel도 시작 전 작업의 취소 상태를 기록한다. Task 기록 후 Augment 기록이 실패한 경우에는 그 취소 명령의 실제 증거로만 연결 상태를 복구한다. 35개 로컬 제안은 보존하고 최신 32개씩 조회하며 페이지 이동은 저널을 쓰지 않는다.

영향 회귀는 전체 실행의 12개 통과와 수정 후 두 메타데이터 표적 회귀 통과로 14개 서로 다른 gate를 확인했다. 별도의 Worker 소유자 회귀도 통과했다. Android/browser 메타데이터 템플릿의 잘못된 ReviewSummary 클래스 위치를 수정하고 동일한 선언 변환·검토 코드를 연결했다. 이는 SDK·서명·Android 설정 변경이 아니다. 실제 계정·유료 모델·장치 실행 검증으로 해석하지 않는다.

전체 v424와 새 Blueprint 경로는 계속 구현 중이다. 아래 첫 compiler 경로는 연결했으며, 새 기능 UI/명시적 신규 graph 생성·전환과 Node Task/Agent 공개 흐름 등은 후속 범위다.

일반 Git 체크아웃·시작 검증은 선언 View 구현 커밋 `ca9a78a2d7ca95d9abdb2b14a64cc4cd711012da`에서 **1 통과/0 실패/0 건너뜀, 59.373초**로 통과했다. 정상 clone/pull의 기존 CRLF와 새 LF 체크아웃에서 20개 리소스의 실제 Home 시작과 변조 거부를 확인했다. 이 증거는 전체 v424 및 Blueprint 완료를 뜻하지 않는다.

## Blueprint 원본과 첫 compiler 경로

일반 Builder에 명시적 blueprint target 원본, 별도 노드 파일, 결정적 조립·typed 기존 기능 호출·compiler 검증을 연결했다. graph/정의/계약/노드 파일 입력 해시와 compiler identity를 고정하며 실패/원본 변경 시 이전 성공 결과를 유지한다. graph/node 초안과 Save/복원/Confirm, 한 노드 전용 DevelopmentTools capability를 실제 소비자로 검증했다. 별도 작업 경로의 동일 DLL 재현성과 컴파일 도중 원본 변경 거부도 확인했다. [상세 경계](FEATURE_BLUEPRINT_ARCHITECTURE.md), [실행 예제](../examples/feature-blueprint/README.md), [검증 기록](evidence/v424-integration/blueprint-compiler.json).

이 단계의 profile은 sync-acyclic-v1이며 새 기능 화면·graph 전환 UI와 Task/Agent 통합, 지도 나머지 UI를 완료로 표시하지 않는다. 외부 계정·유료 호출·장치 실행은 수행하지 않았다.

Blueprint 구현 커밋 `d326d57df4ed43dcbc1e41e126d17a5ecacf565f`의 일반 Git checkout/20개 리소스 시작·변조 거부는 **1/0/0, 95.007초**로 통과했다. 그 후 native 메타데이터의 중복 BodyUnitMetadata 도우미도 desktop과 동기화하고, graph/node 종류·작업 사본 locator·검증 결과가 C# body나 compiler 완료로 바뀌지 않음을 별도 adapter gate에서 확인했다. UI 리소스와 compiler 코드는 후속 수정에서 바뀌지 않았다.

## 실제 선언 관계 맵

[검증 기록](evidence/v424-integration/declared-relations-map.json), [실제 화면](evidence/v424-integration/declared-relations-map.png). 개념 맵은 현재 소유 공유 초안의 category/concept/function/module/object/schema/implementation 선언을 읽고, 실제 DeclaredRelations 간선과 소스 리비전·해시를 고정한 읽기 전용 snapshot을 표시한다. 초안 수정이 반영되고 반복 조회는 원본·선택·기존 Review token을 변경하지 않는다. 소유 목록 밖 참조는 존재 여부를 추정하거나 편집 가능으로 표시하지 않는다. 구문을 해석할 수 없는 선언도 오류 노드로 보존한다.

실제 선언 열기, 역할/검색/집중/전체 보기, 이동/팬/줌과 private 배치·필터·카메라의 프로세스 재시작 복원을 연결했다. 집중 배치는 기본 배치를 보존하는 별도 presentation이다. 저장하는 것은 배치이며 관계 snapshot은 현재 초안에서 다시 읽는다. 이 맵은 정적 선언 관계이며, 새 Blueprint의 실행 원본 graph 또는 실행 증거로 취급하지 않는다. 읽기 전용 외부 정의 탐색·이름/참조 정리·즉석 테이블 등 나머지 지도는 계속 구현한다.

관계 맵 구현 `3d432c6bed35eacd41ee10619632d15865fb055a`의 일반 Git checkout/21개 리소스 시작·변조 거부는 **1/0/0, 65.262초**로 통과했다. 기존 전체 편집·선언 View/재시작·PackWorkspace 영향 회귀는 5/0/0, 408.815초이며, 집중 배치의 최종 UI/실제 재시작 표적 검사는 1/0/0, 13.651초로 통과했다. 이 수는 서로 중복되어 합산하지 않는다.

## 소유 초안 기반 InstantTable

소유 객체를 페이지별로 선택하고 메타데이터·설명·schema data path를 실제 공유 초안에서 읽는 Table을 공개 Home 소비자에 연결했다. 대상/필드 구성 변경은 표시한 구성 해시를 확인하고 새 구독/조회 준비를 완료한 뒤 이전 View를 해제한다. 준비 실패와 오래된 구성은 기존 표를 유지한다. 값은 Table 소유 모델로 복사해 저장하지 않는다. 사용자 요청 문구는 구성 설명으로 보존하며 새 AI 요청으로 해석하지 않는다.

표시한 소스 리비전·UTF-8 해시·effective view 해시로 셀/다중 행 편집을 확인한다. workspace 잠금과 EditBatch의 전체 후보 검사 후 함께 초안을 적용하며, 잘못된 배열 원소·참조·스키마 또는 오래된 행이 있으면 전체 Fill을 거부한다. 로컬 설명/메타데이터/data 재정의 제거는 기존 선언 API를 사용해 현재 상속값을 다시 보인다. 원본과 최종 반영은 Save/Review/Confirm의 기존 소유자에게 둔다. Table 읽기는 Review token을 유지하고, 수락한 편집은 해당 주 View의 이전 Review를 해제한다.

정수·배열 입력은 원시 JSON 문자열을 전달하고 정수 정렬은 BigInt로 비교해 64비트 정수를 보존한다. 객체/필드 선택, 검색·이름/값 정렬, 열 순서/너비, 행 선택과 미적용 입력은 private presentation으로 프로세스 재시작 후 복원한다. Table 해제는 구독만 해제하고 공유 초안을 닫지 않는다. 경로별 inherited origin과 명시적 부모 재정의 조건을 표시하며, 조회할 수 없는 schema는 읽기 불가 상태로 둔다.

표적 엔진·실제 브라우저/재시작·native 메타데이터 비교는 **3/0/0, 95.758초**로 통과했다. 기존 편집과 관리 프로필 영향 회귀·일반 checkout 시작 검사는 별도 기록 후 게시한다. 이 단계는 전체 v424 또는 Blueprint UI/Task 완료 보고가 아니다.

추가 경계 검증에서 예약 메타데이터 이름(`value:"description"`)과 선언 설명을 분리하고, 잘못된 객체의 필드 조회가 실패해도 실제 객체 선택기를 유지하도록 보완했다. Table의 자식 Workspace 이동·제거·재열기에서도 미적용 입력과 초안 소유자를 보존한다. 변경 검토의 숫자/복합 값도 원시 JSON을 표시해 큰 정수의 전후 차이를 반올림하지 않는다. 기존 영향 회귀 **11/0/0, 565.006초** 후 엔진·Workspace 경계와 최종 Table/compact Review 표적을 추가 확인했다. 최종 UI 두 검사는 **2/0/0, 88.768초**이며, 각 실행은 일부 중복되어 합산하지 않는다. 관리 프로필은 컴파일 검증이며 실제 기기·계정·유료 호출 검증이 아니다.

[Table 검증 기록](evidence/v424-integration/instant-table.json)과 [실제 화면](evidence/v424-integration/instant-table.png). 검증 단계와 추가 수정의 범위·중복은 기록에서 구분한다.

Table 구현 커밋 `d03774a6a3688482ac8b8442b52f8e59de73a535`의 일반 Git checkout/22개 리소스 실제 시작·변조 거부는 **1/0/0, 64.513초**로 통과했다. 이후 수정은 이 검증 기록뿐이다. main·원본 ZIP·Android 설정은 변경하지 않았다.

## 일반 스키마 속성창의 정밀 값과 로컬 편집

속성창도 scalar/data path/메타데이터의 `valueJson`을 표시하고 원시 JSON으로 편집을 요청한다. 효과값의 origin과 로컬 재정의 여부를 유지하며 큰 정수·배열 원소·복합 값이 JavaScript Number를 거쳐 저장되지 않는다. 새 정밀 요청에는 표시한 소스 해시가 필요하고, 기존 value/revision 호출은 호환 경로로 유지한다. 미적용 입력은 처음 편집한 해시와 리비전을 보존한다. 현재 값 다시 읽기는 입력을 자동으로 새 버전에 맞추지 않으며, 기존 입력 취소와 실제 로컬 재정의 제거는 별도 동작이다.

공통 선언 API의 unset-description/unset-value/unset-data/move-data/remove-field/field-order를 UI에 연결했다. 상속된 복합/배열의 자식 경로는 부모 값을 명시적으로 재정의하기 전까지 편집하지 않는다. 새 로컬 필드 순서는 실제 선언 순서이며, 값·필드 제거도 최종 원본 변경 전에 같은 Review/Confirm을 사용한다. 이 UI는 새 runtime 타입이나 자동 데이터 마이그레이션을 추가하지 않는다.

정밀 scalar/메타데이터/배열 원소·상속값·해시 충돌·기존 호출·미적용 입력 재시작·독립 View·compiler Confirm 첫 검사는 **1/0/0, 66.146초**로 통과했다. 확장한 로컬 편집과 영향 회귀/일반 checkout은 현재 검증 중이다. 전체 지도와 Blueprint UI/Task는 계속 미완료 범위다.

로컬 동작의 실제 UI·compiler Confirm 검사는 **1/0/0, 55.455초**로 통과했다. 구문이 잘못된 JSON과 오래된 구조 변경은 초안/입력을 보존하며, 로컬 정의 순서 변경도 전체 소스 검토 대상으로 남는다. compiler Confirm 시험은 동일 요청의 결과를 제한된 시간 동안 기다리며 재전송하지 않는다. 이 묶음의 기존 전체 편집/생성/연결·독립 View·Table·Workspace와 관리 프로필 영향 회귀는 별도 진행 중이다.

일반 속성 변경의 영향 회귀는 **9/0/0, 818.791초**로 통과했다. 전체 Home/ButtonGame 편집·기존 연결 설정, 새 개념 생성/최종 반영/재열기, Workspace 입력 수명, Table, 선언 View, PackWorkspace와 Windows/Android 관리 프로필 컴파일을 포함한다. 마지막 후속 수정은 schema 정의 행의 버튼 열 폭이며 해당 UI 배치와 동작을 별도로 검사한다.

[스키마 검증 기록](evidence/v424-integration/schema-fields.json)과 [실제 필드 편집 화면](evidence/v424-integration/schema-fields.png). 마지막 consumer CSS의 버튼 열 덮어쓰기를 정리하고, 표시된 다섯 동작이 한 줄에 있으며 이동 버튼이 창 안에 있는지를 검사했다. 최종 표적 UI/실제 compiler Confirm은 **1/0/0, 42.707초**로 통과했다. 위 회귀는 일부 중복되므로 합산하지 않는다. 일반 Git checkout 검사는 구현 커밋을 고정한 뒤 수행한다.

스키마 구현 커밋 `946d5e511e4f5eaf8a0033f4cf4265de70c9b437`의 일반 Git checkout/22개 리소스 실제 시작·변조 거부는 **1/0/0, 63.514초**로 통과했다. 이후 변경은 검증 기록뿐이다.

## 직접 참조한 등록 팩의 읽기 전용 정의

관계 맵의 외부 참조와 선언 정보의 직접 참조 목록에서 현재 등록 팩의 정의를 읽기 전용으로 연다. 조회는 표시한 소스의 리비전·내용 해시, 실제 직접 참조와 현재 root manifest의 직접 의존성/등록을 검사한다. 선택한 등록 manifest와 대상 선언만 읽으며 pack namespace/kind/locator identity·경로 범위·1MiB 예산·조회 도중 변경을 확인한다. 정의의 실제 선택 버전과 해시를 표시하며, 호환성·provider 선택·실행 완료를 의미하지 않는다. 구현의 body locator는 선언에 보이지만 body 파일은 읽지 않는다.

기존 선택과 Review token, 공유 초안 수명을 보존한다. 창 배치에는 참조 ID와 조회 기준만 저장하고 등록 팩의 소스 본문은 넣지 않는다. 프로세스 복원 후에는 빈 읽기 상태를 표시하고 명시적 다시 읽기로 조회한다. 참조 소스가 바뀌면 맵/선언을 새로 읽고 다시 열어야 한다. Native adapter는 기존 configured owner root의 읽기 범위를 유지하므로 외부 리소스가 제공되지 않으면 unavailable을 반환한다. 참조 드래그·임의 깊이 탐색은 후속 범위다.

[검증 기록](evidence/v424-integration/reference-definition.json)과 [실제 읽기 전용 화면](evidence/v424-integration/reference-definition.png). 기존 맵/선언/스키마/Workspace/관리 프로필 영향 회귀는 **7/0/0, 317.457초**, compact 창 배치 후 실제 UI/재시작은 **1/0/0, 24.700초**로 통과했다. 헤더와 하단 동작이 창 및 Workspace 안에 함께 있는지도 검사했다. Native helper의 별도 범위 검사도 통과했으며 검증 단계의 중복과 관리 프로필의 한계는 기록에 구분했다. 일반 Git checkout 검사는 구현 커밋 고정 후 수행한다.

참조 정의 구현 커밋 `b8f348d663ff6d8bf542a9367bb2b01829539d4f`의 일반 Git checkout/22개 리소스 실제 시작·변조 거부는 **1/0/0, 62.548초**로 통과했다. 이후 변경은 검증 기록뿐이다.

## 소유 객체 바리에이션

객체 메뉴의 바리에이션 생성은 표시한 부모의 소스 리비전·내용 해시를 전달한다. EditWorkspace는 부모 identity와 등록부를 확인하고 일반 object extends 선언과 등록부 후보를 먼저 만든 뒤 함께 초안에 적용한다. 후보 준비 실패·오래된 부모·동시 등록 변경·기존 목적지는 부분 생성 없이 거부한다. 새 객체는 부모 참조로 값과 설명을 상속하고, 사용자가 바꾼 값만 로컬 재정의로 보유한다. 부모 파일은 변경하지 않는다.

PackWorkspace의 전용 공개 생성 역할이 View 선택과 수명을 맡는다. 기존 Command 소비자에게 새 dependency를 요구하지 않는다. Save/생성 등록부 필수 묶음/일반 compiler Confirm을 그대로 사용하며, 현재 소유 object 부모만 지원한다. 기능 바리에이션이나 Blueprint 전환을 자동으로 만들지 않으며 승인된 부모 구현 재사용 설계는 유지한다. 첫 실제 UI/재시작/compiler Confirm은 1/0/0, 96.115초, 전용 계약 정리 후 같은 UI와 기존 PackWorkspace 전체 회귀는 4/0/0, 79.983초로 통과했다. 일부 중복되므로 합산하지 않는다. 추가 영향 회귀와 일반 checkout은 진행 중이다.

추가 영향 회귀에서는 6종 선언의 생성·Confirm은 끝났지만 cold startup이 편집창 복원과 초기 Helper 조회의 동시 요청으로 stale_revision을 내는 경우를 찾았다. 해당 묶음은 **6 통과/1 실패, 648.345초**이며 전체 성공으로 합산하지 않는다. 실제 browser fetch의 Helper 초기 조회만 300ms 지연시키는 별도 검사로 수정 전의 `objects → select → inspectDeclaration → helperList` 순서를 재현했다. 응답이나 모델 상태를 가짜로 만들지 않는다. mount 이전부터 초기화 상태를 유지하도록 순서를 바꿨으며, 일반 소스 CAS의 자동 재시도는 추가하지 않았다. 수정 후 전체 Home과 재시작 관련 UI 검사는 진행 중이다.

[바리에이션·시작 검증 기록](evidence/v424-integration/object-variation.json). 연결이 끊긴 뒤 미커밋 코드와 로그를 보존하고 마지막 묶음을 회수했다. 초기화 지연·Helper/Workspace/Yogi·바리에이션·6종 생성·독립 View의 수정 후 7개 통과는 재실행하지 않았다. 전체 Home/ButtonGame의 실패는 복원된 Run 창 뒤쪽의 닫기 버튼을 누르던 시험 동작이었다. Dock/Nav로 창을 앞으로 선택한 뒤 닫도록 시험만 보완했으며, 같은 제품 코드의 전체 검사는 **1/0/0, 337.147초**로 통과했다. [일반 개념 Confirm 후 실제 재열기 화면](evidence/v424-integration/ordinary-reopen.png)은 이 최종 실행에서 촬영했다. 수정 후 8개 UI gate를 확인한 것이며 앞선 단계의 반복 실행 수를 합산하지 않는다. 일반 Git checkout은 구현 커밋 고정 후 검사한다.
