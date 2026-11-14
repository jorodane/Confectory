# 두 고급 native 입력 계약·C# 본문 공동 저장 검증

동결 runtime `d17f83d35e6d87c23db90617b708a5e6f55beb35`의 [두 고급 native 입력 공동 저장](V666_NATIVE_TYPE_GROUP.md)을 **신규 42단계·재사용 0·실패0**으로 검증했다. LF21·CRLF13·새 package/전체 ZIP 복원8이다. 개발 진단은 최종 통과 수와 구분한다.

- 원래 두 함수와 겹치지 않는 직접 C# 호출자가 실제 프로그램70을 실행했다. 같은 정보의 두 입력을 기존 Payload/Leaf 구조체 타입으로 명시 선택하고 네 C# 본문을 직접 작성한 뒤 실제 결과73을 확인했다. 전환 순서를 바꿔도 동일한 후보와 원래 source hash를 유지했다.
- 기존 native/type 선택 UI·C# chooser에서 두 함수의 선택·취소·네 본문·Undo/Redo·미저장/저장 cold·기본/독립 창·한 Save·쓰기 실패/재시도·응답 유실·늦은 이름/두 번째 Save·동일 namespace 프로젝트 왕복과 stale form 거절을 검증했다. 원본 카드/상세창 코드와 layout bytes는 바꾸지 않았다.
- 누락/교차 함수 scope·누락 타입 proof·caller 본문 누락·stale source·잘못된 C#·source 공유를 전체 거절했다. 저장 캡처의 proof/read 누락·교차, 해시를 다시 계산한 import alias/native 이름 변경·stale 본문/함수·바깥 경로 이동도 거절했다. 순수 검사에서 checkpoint·원문 쓰기는 없었다.
- 후속 owner/function metadata Save 뒤에도 같은 native ABI·네 본문·함수별 type proof/read set을 유지했다. Review 뒤 둘째 C# caller 또는 Payload 정의가 바뀌면 최종 Confirm을 차단하고 원본·peer text·checkpoint를 보존했다. 원본 복원과 cold 뒤 새 Review/Confirm으로 실제73을 확인했다.
- 기존 역할 import native/guard, 기존 단일 고급 전환 candidate/API와 반환 import native 및 incremental 경계를 별도 회귀로 검사했다. 새 package 생성·구조/probe·UI, 전체 ZIP 추출/file hash/probe·응답 유실·후속 입력·독립 창 및 반복 성공/실패 수명을 새로 확인했다.

제품은 FunctionNativeTypes·InformationDefinitions·InformationFunctionBatch·InformationFunctionBodyGuards와 새 InformationFunctionNativeTypes 다섯 파일이다. 함수별 proof를 원래 snapshot에서 먼저 검증하고 겹치지 않는 직접 동기 native 입력/본문 계획만 기존 단일 검증기로 합성한다. 원래 이름·순서·역할·scalar 반환·caller ABI를 유지하며 source를 추측해 생성/수정하지 않는다. 새 JSON bypass·receipt 필드/버전·등록/권한이 없다. 기존 version2 workspace·version3 slot receipt·native-type-source-guards-v1·read240/member64·Review/Confirm·최종 CAS를 유지한다. 외부 header/manifest는 읽기 관측이며 쓰기 그룹에 들어가지 않는다. 정보별 struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류를 유지한다.

선행 개발26단계의 실패2건과 원래 로그를 보존했다. JsonNode/JsonObject 컴파일 오류는 API 실행 전에 고쳤고, 저장 선언 shortcut이 캡처 검사를 건너뛴 반례는 native 캡처를 먼저 확인하도록 고쳤다. 첫 동결 `72569e925af5bc01470f6c16a44fc1ec0005df89`의 최종 검사는19단계 중 단일 고급 함수의 cold 선택 회귀에서 실패해 중단됐다. 이전 온전한 package도 단일 전환의 cold 선택 뒤 Review에서 거절됐다. 첫 동결은 cold 선택에서 실패하므로 같은 실패 지점으로 간주하지 않는다. 초기 이전 package 진단의 이름/설명은 cold였지만, 로그 caret의 실제 실패 호출은 reviewGroup으로 재확인했다. 원래 로그는 고치지 않았다. 새 결과에 그18단계 통과를 재사용하지 않았다.

복구 개발 11단계의 실패는 0건이다. 기존 단일 타입 receipt를 원래 타입/읽기 lease로 cold 복원하고, 다중 scope는 완전한 원래 공동 계획 또는 캡처된 같은 scope 집합으로 제한했다. 기존 단일 전환의 실제31·확정 후 본문 편집32, 공동 전환73, 두 경로의 cold·경합·증거·후속 입력을 확인했다. 단일 전환을 먼저 저장한 뒤 두 번째 scope를 덧붙이는 순수 guard/API 요청은 checkpoint와 원문 변경 전에 거절했다. 이 경계 검사1건을 추가해 최종 신규42단계로 검증했다.

환경 조회가 `exec-server transport disconnected`로 실패하고 같은 환경이 offline/unavailable였던 동안 마지막 완료 상태를 추정하지 않았다. 재연결 뒤 실제 checkout·diff·종료 프로세스·보관된 실패 record·원격·package index를 먼저 확인했다. 환경 초기화·덮어쓰기·불확실한 명령 재실행이나 중복 검증은 없었다. 기존 commit과 증거를 유지하며 수정 commit을 그 위에 추가했다.

이전 온전한 package `c5a2cc4d4ca6c47e0b0c7ce3b9639d78fb54b740` 전체 파일/hash를 별도 추출했다. 기존 단일 고급 전환의 cold 재진입 뒤 Review 거절 재현과, 수정 뒤의 새 공동 저장 캡처에 대한 이전 pending guard 수용 `False`는 이번에 새로 측정했다. 이전 package의 원래70 실행·두-scope Save 거절·UI 입력/checkpoint/원문 보존은 선행 개발 증거 `f18cc96cd2cf6a046aec7a786e672992c8e10d68af616086a0f66ebf42ad10bc`의 두 호환성 진단을 재사용했다. UI·receipt 형식·이전 package는 바꾸지 않았으며, 이 재사용 진단은 최종 신규42단계/재사용0 통과 수에 포함하지 않는다. 이전 전체 UI의 cold/Review/Confirm 교환, 자동 migration/downgrade 또는 구 Reference parser 변경을 완료했다고 주장하지 않는다.

Linux 실제 .NET/portable 실행·Chromium 자동화다. Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 미검증이며 과거 간헐 초기 빈 화면 원인은 미확정이다.

| 보관 | runtime source | SHA256 | bytes |
|---|---|---|---:|
| latest | d17f83d35e6d87c23db90617b708a5e6f55beb35 | 7b78d992c39fd248f0af7b771ae95371b70d028698e09971749c0b125bd4943d | 54143678 |
| rollback | c5a2cc4d4ca6c47e0b0c7ce3b9639d78fb54b740 | d4cf81e4a1d94d749b3e6fed0fa8e95ef0d370bcb3aad79c9f83cd668e0eebdf | 54137967 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/7a467283cbc94062afce659990c731e2.json` · evidence SHA256 `51150f10c092bda44e54526516fae5c357422df87433071a0a26ab78f1a9a691`.
복구 개발 record `/workspace/artifacts/v536-verification-managed/runs/c9e6888eb29d4700bf16ac9791bc9eb1.json` · evidence SHA256 `c271d2716af306564b81739d40dc82e24fdfb3b75e62d7114693630b72644a19`.
선행 개발 evidence SHA256 `f18cc96cd2cf6a046aec7a786e672992c8e10d68af616086a0f66ebf42ad10bc` · 첫 실패 최종 evidence SHA256 `398ba4980497080ff024c12681b7904aa4a3989ddd043db0e2147edbbe13de46`.
두 package와 네 evidence archive hash를 재확인했다. 이번 등록 소유 임시물과 기존 latest/직전 정상 rollback 교대만 정리하고 원본 checkout·과거 증거를 보존했다. 디스크 여유 24361545728bytes(22.69GiB)다.

두 구조체 입력·네 disjoint C# 본문의 실제 흐름을 닫는다. 공유 caller·선택 함수 간 고급 import, 고급 반환·reference/array·out/ref·async·private/whole/override 및 외부 수정 결합은 이 완료로 대신하지 않는다. 구 reader 전체 UI 교환·실제 기기/전체 UI·초기 빈 화면 원인은 구별된 잔여이며 main은 사용자 검토/merge에 남긴다.
