# V666 여러 next 실행선 저장 복구 검증

제품·검사·도구·delta 동결은 `fd65b6ed5b180c690e1ea1fffcf832927f9f06b0`이며 이후 마감 commit은 문서만 바꾼다.
[닫힌 경계](V2_ROUTE_GROUP_RECOVERY.md)와 [정확한 delta](v666-route-group-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `669d6770593468d40de9c1925a986e520ed870f7`의 원래 연결 UI로
`body → first → second → third`를 `body → second → first → third`로
명시적으로 해제·재연결했다. checkpoint 쓰기 실패 뒤 개인 실행선 입력 **3개가 모두
사라지고 live만 변경**, cold에서 원래 연결이 복원됐다. 물리 원본과 C#·계약은 같았다.
Baseline SHA `f962766b02ef7d96422c0b3e0fcca63a5391a25eaa16d53f425a8aa09881d10c`; 개발 증거에 JSON·화면·실제 원래 실행 결과를 보관했다.

순수한 여러 일반 next 실행선을 기존 원자 후보·최종 checkpoint CAS·ownedRoute receipt·
공유 이력에 연결했다. 같은 키/출발점/종류의 수정은 정확한 미적용 checkpoint와 전체
source proof·물리 원본이 그대로일 때만 새 시도로 저장한다. 성공 응답이 불명확하면
receipt로 확인하며 새 입력과 이전 시도를 분리한다. 무관한 입력이 더해져도 legacy
부분 쓰기로 우회하지 않는다. 자기 연결·순환은 선택한 실행선의 최종 후보에서 거절한다.

기존 직접 소유 Root의 서로 다른 일반 code/next 입력 2–64개라는 안전 경계이며,
원래 전역 64편집 예산을 재사용한다. 실제 native API/UI fixture는 실행선 세 개다.
단일 실행선·불완전 초안의 기존 의미, 원래 C# bytes·caller·입출력 ABI·ID·타입·data
연결·profile·다른 실행선은 보존한다. entry/분기/완료/call/export·소스/표시명/계약 혼합·
생성/private/copy/slot·부모/외부 편집 권한을 새로 부여하지 않는다. writer/receipt schema·
이력 planner·팝오버/레이아웃·Review→Confirm·최종 물리 CAS는 그대로다.

초기 최종 시도 `18837ceaa5a84fbcac5aaf7f373b2163`는 LF 빌드/엔진 등 8단계 후
이전 단위의 exact-delta 감사에서 멈췄다. 새로 검토한 delta를 같은 감사 체인에 연결하고
기존 Root/표시명/텍스트 guard를 유지한 뒤 재동결했다. 제품 runtime bytes는
`88aa465a4ec83f17f0b4b308c454446e69614186`과 최종 동결 사이에 같았다. 중단 증거는
보존했으며 이전 8단계를 아래 최종 실행에 재사용·합산하지 않았다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)** 통과했다.
개발 중 재현/반복 검사는 합산하지 않는다. Git 객체·실제 EOL·NuGet/home·엔진 캐시는 분리했다.

- API: stale checkpoint·변조 전체 proof·미관측 owner/private·중복/없는 출발점·없는 대상·
  잘못된 포트/필드/타입·소스/이름/계약/생성 혼합·순환/자기 연결·예산 초과를 거절했다.
  실패 시 live/checkpoint/원본을 보존하고 정확한 미적용 원본에서만 재시도했다.
  정상 저장·멱등성·공유 이력·cold receipt와 변조 receipt 거절을 확인했다.
- UI: 자기 자신/순환/이미 연결된 대상 거절, 원래 명시 해제·재연결, 개인 실행선 cold
  복원·쓰기 실패·수정/재시도·동료 checkpoint 충돌을 확인했다. 실패 후 무관한 이름이
  추가되면 모든 입력과 원래 시도를 유지했다. 응답 유실은 기존 receipt만 회수해 중복
  쓰지 않고, 응답 보류 중 새 실행선은 cold 뒤 별도 저장해 이전 선택을 재생하지 않았다.
- 공유 Undo/Redo/cold, Review 취소·Review 후 물리 graph 변경의 최종 CAS 거절·새
  Review→Confirm·실제 Linux .NET 실행·최종 cold를 확인했다. 명시한 실행선에 따라
  body/second/first/third/10 또는 body/first/second/third/10과 exit 10을 실행했다.
  next edge 외 graph 내용, 원래 C#·caller bytes·data 연결·ID·계약·profile은 같았다.
  원래 선택으로 되돌리는 경우에도 실행 의미를 보존하며 기존 edge 직렬화 이력은
  그대로 따른다. 반복 no-op Save의 zero-dirty receipt도 cold에서 복원했다.
- 기존 단일 next API/UI와 여러 표시명 API, void Root 이름의 늦은 입력 UI, 공통
  안내/JS 구문·공유 이력/runtime probe를 현재 코드에서 새로 회귀했다. 그 밖의 기존
  완료 증거는 각 기록에 남기며 신규 단계에 합산하지 않는다.
- 새 Windows 교차 패키지 구조/무결성, 패키지 엔진의 정상/응답 유실, 전체 SHA·CRC·
  권한 모드로 완전히 복원한 엔진의 쓰기 실패/늦은 입력·Confirm/실행/cold를 검사했다.
  성공/반복/실패/예외 수명관리·증거 보존·자식 종료·이번 실행 소유 임시 정리를 확인했다.
  Linux .NET/Chromium 검사이며 실제 Windows apphost/WebView2·모바일 실행은 아니다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/fe0f060d1e4d4908a74dddb1b92bcb27.json`

개발 증거 SHA `1f05351df8463ff7bfc7c4116884818c7fe676aeaddfe8efe30fb4f76650f88e`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/211a5fc4c48b4339baecb963741893f2.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/211a5fc4c48b4339baecb963741893f2.zip`

SHA `2a14951c73ae4d2c4b5c381d48d2a5786618000b9a5dd250710f4d6124369b92` (2.74MiB).

## 보관·공간·유한 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `fd65b6ed5b180c690e1ea1fffcf832927f9f06b0`, `8a5333c21e66a26a5ad3bf283260403390fa97606754827c3aba9e2cc1d2ab35.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `e560fd80ee6fbd6cf7ac8eebd6d508dc64b08c9a913be1dcbe3276f09d80a3ca`.
- rollback: `0bf4c635dcbe510e288776901dc45063d54a8f10`, `4f87ec458487e4dbf76dda4bf3dbb083f00618954a304e1cd2959fe9c16b910e.zip`, 49.14MiB, 파일 2381·디렉터리 147, manifest `f6e0685de639342e842b620acfbcac7031b98d47c8dad8f638da026f623278a2`.

전체 SHA/manifest·복원 가능성을 확인한 뒤 승인 수명관리로 latest/이전 정상 rollback과
증거를 지속 보관하고 이번 실행 소유 임시물만 정리했다. 다른 과거 자료·원본·로그·
프로필·SDK·캐시의 추가 삭제나 보관 정책 변경은 없다.

표본 최소 디스크 여유 1525.76MiB, 최대 cgroup 메모리 4826.10MiB.
최종 실행 순증가 3.80MiB, 개발 시작부터 보관 확인까지 순증가
5.55MiB, 문서 마감 전 여유 1522.00MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

이번 실제 결함은 마감했다. 다른 Root/혼합 저장/직접 배치는 재현 기반 조사 후보이며
조합마다 새 필수 항목으로 추가하지 않는다. M11/M12/M4 마감을 다시 열지 않는다.
고정 V2 후속, V3–V9 별도 팩/backend·종류 호환성/사용중 삭제 결정과 실제
Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은
각 고정 항목에 남는다. 3D/권한 별도 팩·이동 연출/실행 분리·동기 caller 명시 async
전환 규칙을 유지한다. live AI·계정/키·유료 호출·새 외부 접근은 없다. main은 보존한다.
