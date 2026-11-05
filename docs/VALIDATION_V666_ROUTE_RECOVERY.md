# v666 일반 다음 실행선 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `877534e95d4c15f3ef14e4d2951a66637f58a0ef`다. 이후 마감 commit은 검증 문서
두 개만 바꾼다. [지원 경계](V2_ROUTE_RECOVERY.md), [정확한 delta](v666-route-recovery-delta.json)를 따른다.

## 재현과 변경

게시본 5db09dc의 생성 프로젝트에서 직접 소유 ordinary root code `after`의 기존
next 포트를 명시적으로 다른 동작에 연결하고 checkpoint 쓰기를 실패시켰다. 기존
일반 Save가 live 연결을 바꾸고 개인 입력을 지워 cold에서는 원래 목적지만 복원됐다.
원본·C#과 checkpoint는 그대로였다. 수정 전 입력·실패·traffic·스크린샷·cold 결과를
개발 증거에 보존했다.

단일 직접 소유 root code의 next 입력을 기존 private 후보/checkpoint CAS/receipt와
공유 Undo/Redo로 연결했다. 목적지 변경/명시 해제는 기존 route 검증을 사용한다.
없는 목적지·다른 포트/분기·참조 call·owner/slot/frame·본문/계약 혼합을 새로 허용하지
않는다. 공개/override 계약·부모/외부 원본·권한과 레이아웃은 그대로다.

checkpoint·전체 source proof·물리 원본이 그대로이고 미반영임이 확인된 시도에서만
새 목적지로 명시 재시도한다. 응답 유실은 receipt만 회수하고 이전 연결을 재전송하지
않는다. 저장 중 새 연결은 분리해 보존한다. `ownedRoute` receipt는 변경 파일이 없는
반복 Save도 cold 후 판정하도록 보관하며 기존 source/name receipt를 유지한다.
가짜 graph/C# 변경이나 암묵적 기본 목적지는 만들지 않는다.

명시한 실행 연결만 바꾸고 ID·핀/출력·signature·profile·다른 연결·C# bytes를 보존한다.
물리 원본 쓰기는 기존 Review→Confirm과 최종 CAS를 따른다. 제품 변경은
feature-authoring.js·그 JS canonical metadata·Blueprint.csbody·Export.csbody뿐이다.
관련 실행선 해제 안내 2문구·2곳을 “주십시오”로 맞췄고 컴파일러의 원문 진단은 전역 번역하지 않았다.

## 최종 검증

독립 LF 17·CRLF 18·새 패키지/전체 복원/실패 수명관리
8, **총 43단계: 신규 43·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발 통과/실패 수는 합산하지 않는다.

- 정확한 제품/안내 delta·canonical asset·JS 문법과 이전 완료 문구를 확인했다. 공유
  history inverse/CAS/restart/owner와 표시명/실제 의미 변경 native 보호도 검사했다.
- 실제 API에서 stale checkpoint·위조 source closure·없는 노드/목적지·참조 call·잘못된
  owner/slot/frame·다른 포트/분기 반환·route/매개변수/본문 혼합을 거절했다. 저장은
  멱등이며 cold·공유 history·위조 receipt 거절을 유지한다. 명시 해제의 빈 목적지는
  그대로 저장·재시작 복원하고 명시 재연결 전까지 물리 파일이나 기본 경로를 쓰지 않는다.
- 기존 next 포트의 키보드 선택/연결 취소·자기 자신/앞쪽 복귀 연결 거절, 개인 목적지의
  정확한 cold 복원을 확인했다. 쓰기 실패 후 새 목적지·명시 재시도와 동료 checkpoint
  충돌/cold, 응답 유실과 저장 중 새 연결의 분리를 검사했다. 이전 목적지는 재전송하지 않는다.
- 저장 후 공유 Undo/Redo/cold·Review 취소·검토 뒤 Main.graph.json 원본 충돌 거절·새
  Review/Confirm·실제 .NET 실행을 확인했다. graph의 해당 next 관계만 바뀌고 다른
  관계·ID·profile·핀/계약·다른 모든 물리 파일과 C# bytes는 같다. 반환 10,
  `callee:1 → after:10 → tail:10` 또는 새 목적지의 `callee:1 → after:10 → late:10`을 확인했다.
- 변경 파일이 없는 반복 route Save도 receipt를 보관하고 cold에서 물리 쓰기 없이
  판정한다. 기존 C# source와 이름 API를 LF/CRLF에서 새로 회귀했다. CRLF에서는 기존
  C# 쓰기 실패/새 입력/cold/Undo/Review·Confirm·실행 UI 및 property observation·부분
  Review·경로/원본 위조·expected-missing/readonly CAS 거절도 새로 검사했다.
- 새 Windows 교차 패키지의 구성/무결성·패키지 엔진 웹 시작과 route normal/loss UI·
  실행을 확인했다. 압축 CRC·전체 파일 SHA/모드를 검증해 완전히 복원하고, 복원 엔진의
  route 쓰기 실패/새 입력과 늦은 입력을 최종 Confirm·실행/cold까지 새로 검사했다.
- 성공·실패·예외·증거 보존/복원·자식 종료·소유 임시물 cleanup 수명관리도 통과했다.

저장 전 모든 연결 편집의 private Undo/Redo나 모든 포인터/터치/문맥/프로젝트 왕복을
신규 완료로 주장하지 않는다. 이번 연결 조작은 기존 포트 키보드 경로다. 안내의 모든
오류 조건을 각각 새로 UI 주입하지 않았으며 전체 UI 검증과 구분한다. 기존 C# 전체 UI
회귀는 CRLF에서, source/name API는 양쪽에서 새로 수행했다.

## 증거와 보관

개발 record `/workspace/artifacts/v536-verification-managed/runs/3293a02e3c87412d84221502370dcd79.json`

개발 SHA `5cb54331e7ef4ef915cc974cf307f4dc9ab3f4550cd6401852e16b5e508b505d`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/7e8debc0c33f41158a177321a6a82ba2.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/7e8debc0c33f41158a177321a6a82ba2.zip`

SHA256 `d14af1b5249806d94750e4d403f88a13d741a718bf6e19ed91e6d7a28e6d10fb` (2.56MiB).

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `877534e95d4c15f3ef14e4d2951a66637f58a0ef`, `f4c6accb960f60d37c89ad726abb0c489aeb05d76b8bf7b20ce4f03de4f73bc4.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `d8af87461d294a9f832b434767a1e615d5d2c90c67c749334337d029ddc58fef`.

- rollback: 출처 `305271cbcfe8468cbfec0d2eef5d9526e1f1a484`, `4bdb3349994d7e5eaea4708c2c49be1b125e6ff4b42605aafebb18300f7848da.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `6aba0698f3f32fa6283047c5a64c022054d690db902cae27355e1a50ffdfa2ac`.

최신은 최종 동결 코드와 일치하고 정상 롤백·증거·기존 원본을 유지한다. 자식 종료와
archive 검증 후 이 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 과거 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1627.50MiB, 최대 cgroup 메모리
4664.64MiB. 최종 실행 순증가 3.63MiB, 개발 시작부터
보관 확인까지 5.33MiB, 문서 마감 전 여유 1623.92MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여와 한계

entry/다른 실행 포트·root 핀/export·혼합 signature/description·서로 다른 입력 혼합
등 다른 일반 Save는 별도 읽기 점검 후보다. 재현 없이 결함/정상 금지/새 필수 조합으로
확정하지 않는다. 나머지 V2와 V3–V9·기존 팩/backend·종류 호환성 결정, 실제 Windows/
모바일·전체 UI·Space 전달은 남는다. 완료 M11/M12/M4를 조합별 잔여로 다시 열지 않는다.

검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이다. 실제 Windows apphost/
WebView2·모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space는 미검증이다.
live AI·계정/자격증명·유료 호출·새 외부 권한은 사용하지 않았다.
