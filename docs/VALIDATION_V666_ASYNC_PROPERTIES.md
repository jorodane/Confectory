# v666 M4 속성 편집 최종 검증

동결 제품·검사 source는 `e4c0646ac22cbe3f73c251064b1095565a4f0399`이다. `--suite async-property`의 **신규 LF21·CRLF18·새 패키지/전체 복원/실패 수명관리9, 총48단계**가 모두 통과했다. 재사용 근거는 0이며 개발 반복을 이 수치에 합하지 않는다. 종료 문서 commit 뒤에도 src/targets/packs/examples/tests/tools 트리를 동결 source와 비교한다.

## 실제 지원과 확인

- 기존 직접 소유 async root에서 원본 속성 검색·receiver·소비 작업 연결과 필드 쓰기를 [기존 속성 계획](M4_ASYNC_PROPERTIES.md)에 연결했다. 실행 시점 읽기·출력 보관·필드 쓰기·다른 읽기를 같은 typed 계약으로 처리한다. 명시적 편집 전 C#·IO·시계·Task metadata·ID와 다른 원본을 보존한다. 속성 저장 뒤 사용자가 C# 본문에 주석을 추가하는 실제 편집·취소·Save·cold 복원도 확인하며 이 경우에만 해당 본문 파일도 최종 반영한다. 전환 가능 여부와 현재 async 표시를 구분한다.
- 독립 LF/CRLF checkout·Git object·캐시·빈 편집기 cache에서 Release/MCP/편집기를 빌드했다. 속성/authoring/async Core runtime과 물리 원본 관측/거절/후속 C# 편집 호환 검사 18개, 실제 UI의 검색·연결·Undo/Redo·cold·Save·Review 취소/Confirm·CLR 실행을 새로 확인했다. 실제 Task/await에서 10→쓰기20→별도읽기20, 다음 호출20→30과 앞서 저장한 출력의 정체성을 유지한다. async의 field-ref와 잘못된 receiver는 거절한다.
- 저장 실패·Save 전 물리 원본 경합·Review 뒤 manifest 경합은 원자 거절하고 후보/입력을 보존한다. 재시도는 원래 checkpoint·전체 source proof·물리 원본이 그대로인 경우에만 허용한다. 응답 유실은 cold 후 기존 영수증을 먼저 조회하고 노드/연결을 중복 생성하지 않는다. 늦은 새 Set 이름은 이전 응답으로 지우지 않고 별도로 저장한다.
- 서버 작성 propertyObservations의 필수 manifest·소유 객체/스키마·본문/C#·계약 ID·경로·물리 원본 baseline을 검사한다. 후보 해시용 저장 응답 영수증과 분리하여 이후 C# 후보 편집이나 expected-missing 신규 소스를 거절하지 않고 원래 CAS를 유지한다. 필수 항목 생략·변조·부분 Review·경로 별칭/이탈·외부 ID를 거절한다. cold에서 알려진 영수증 ID만 로드하고 무관한 lazy locator는 읽도록 강요하지 않는다. checkpoint와 최종 원본 쓰기의 같은 CAS에 읽기 전용 검사를 전달한다. 전체 후보가 실제 Confirm으로 반영된 뒤에는 이전 관측을 종료하고 같은 세션의 반복 Save도 확인했다. 이 관측으로 새 권한이나 외부 접근을 만들지 않는다.
- 기존 동기 속성 UI/계획과 공개 완료/async 전환을 회귀 검사했다. 기존 copy 내부 본문 편집도 영향 회귀로 검사했다. 새 Windows 교차 패키지와 전체 SHA/manifest 압축 복원본에서 UI·Task 실행·저장 실패/늦은 응답을 실행했다. 패키지 실패/예외/재시작의 증거 보존과 소유 임시물 정리를 확인했다. Linux 검사이며 실제 Windows/모바일 기기 실행·전체 UI·Space 전달 완료가 아니다.

## 보관과 공간

- 실행 기록: `/workspace/artifacts/v536-verification-managed/runs/163dfcca309045beacd26301a24ef495.json`
- 증거 ZIP: `/workspace/artifacts/v536-verification-managed/runs/163dfcca309045beacd26301a24ef495.zip`
- 증거 SHA-256: `ad34f7b82b76154722f83f83d737d9225631eaafdfdcac06189933120b94e327`
- 최신 source: `e4c0646ac22cbe3f73c251064b1095565a4f0399`; archive `f3e74fd601800894723dc4e43cc3385ab322056987e965e01629942ea857be7e.zip`; SHA-256 `f3e74fd601800894723dc4e43cc3385ab322056987e965e01629942ea857be7e`; 51456853 bytes.
- 최신 전체 manifest SHA-256: `b9a1c5efce17a173f461c1f103524dc11210f402375786f4f2e2eb9e37d7975e`
- 정상 rollback source: `262f1a5cf5122e63701d0ffdb7524c17fbcc2016`; archive `88ee710d7a82f32cd0cdfb7ccb7f4e153e26c6cc8b98a8b8d417981cc1a7ce98.zip`; SHA-256 `88ee710d7a82f32cd0cdfb7ccb7f4e153e26c6cc8b98a8b8d417981cc1a7ce98`.
- index: `/workspace/artifacts/v536-verification-managed/packages/index.json`. 전체 파일·압축 무결성/복원 실행·증거를 지속 보관한 뒤 원자 승격했고, 자식 종료·소유권 확인 후 이번 RAM 임시물만 정리했다. 기존 승인된 최신/롤백 교체 외 과거 자료는 추가 삭제하지 않았다.
- 최종 실행 순증가 3.04MiB, 검증 종료 여유 1781.87MiB, 명령 관측 최소 여유 1784.86MiB, 최대 cgroup 메모리 4462.58MiB. 개발 증거/Git·게시까지의 측정은 최종 보고에 구분한다. 3–6MiB는 보장값이 아니다.

## 한계와 유한한 잔여

M4의 Result 없는 next/native/whole-body 출력 보존 어댑터와 새/내부 소유 본문의 명시 전환은 남는다. 기존 직접 소유 root 속성 흐름을 다시 조합별 잔여로 늘리지 않는다. copy/slot/private의 기존 보호, ref·실제 await/내부 async 호출의 동기 복귀 거절과 override 공개 계약 보호는 유지한다. M11/M12는 관련 회귀 외 닫힌 상태이며 V2–V9·별도 팩/backend·종류 호환성 결정·실제 기기/전체 UI/Space 전달은 기존 별도 잔여다.

이전 compiler는 async property-set을 거절한다. 코드 rollback만으로 새 프로젝트/초안을 복구한다고 보장하지 않으며 최신 패키지와 원본/초안을 함께 보존한다. 기존 저장 응답 영수증을 새 물리 원본 관측으로 자동 재해석하지 않는다. 새 propertyPlan 저장에서 명시적 관측을 확정하며 legacy 자동 변환은 하지 않는다.

개발 기록 `/workspace/artifacts/v536-verification-managed/runs/6a856e2584994b598c4b4648f862a5d0.json`과 증거 ZIP에는 공개 전 발견한 관측/CAS 누락, raw 확인 응답과 해시로 검증한 생성 재현 원본을 남겼다. 숨긴 모바일 캔버스 키 주입, 작은 화면 Review 취소 후 편집기 재진입, 실패 때 추가되는 시도 journal 및 structured Confirm 거절을 fixture에서 바로잡았다. 추가 사전 검증 d28d6cdee4094823b100ff441ff39ce1의 완료 LF 결과도 보존했다. 공개 전 검토에서 저장 응답 해시와 물리 원본 CAS의 결합이 후속 C# 편집을 막는 문제를 발견해 패키지 승격 전에 중단했고, 분리 후 실제 C# 편집·재시작 회귀를 추가했다. 개발 보완 실행의 source/오류/fixture 수정·11개 UI 확인·18개 원본 관측 확인은 보관 기록과 사전 실행 f24f202830744586932633b4f619768a의 development-count-correction.json에 구분한다. 추가 개발 실행14550a0b173d4e2d92deb887d7abd502에는 수정 전 d4b02d2의 C# 저장 실패 개인 입력 손실 재현과 입력 전후/실패 응답을 보존했다. 수정본은 관측된 소유 속성 본문의 C# 및 관련 단순 편집을 기존 authorBatch의 후보/확인/실패 수명관리에 연결했다. source-only 요청이 관측 없는 문맥을 새로 열지 못하게 거절하며 기존 copy/slot 경로는 유지했다. 이 개발 반복은 최종 신규 단계와 구분한다.
