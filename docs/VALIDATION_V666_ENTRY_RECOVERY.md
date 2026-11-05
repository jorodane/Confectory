# v666 기존 함수 시작점 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `fe44bc6910e7b5da7b1d810c8ef5c9e0703911eb`다. 이후 마감 commit은 검증 문서
두 개만 바꾼다. [지원 경계](V2_ENTRY_RECOVERY.md), [정확한 delta](v666-entry-recovery-delta.json)를 따른다.

## 재현과 변경

게시본 5f3d31e의 생성 프로젝트에서 기존 직접 소유 root의 시작 포트로 다른 시작
노드를 고르고 checkpoint 쓰기를 실패시켰다. 일반 Save가 live entry를 바꾸고 개인
입력을 지워 cold에서는 원래 시작점만 복원됐다. 원본·C#과 checkpoint는 그대로였다.
수정 전 입력·실패·traffic·스크린샷·cold 결과를 보존했다. 원래 시작과 두 명시 시작
선택의 native 실행도 먼저 검증해 fixture와 기존 C# 의미의 유효성을 확인했다.

entry 전용 입력 하나를 기존 private 후보/checkpoint CAS/receipt·공유 Undo/Redo에
연결했다. 정확한 가상 시작점 `$entry`·문자열 목적지의 단일 편집만 허용하며 기존
native entry/프로필 검증을 유지한다. 선언된 호출 노드를 시작 대상으로 고를 수 있지만
호출 원본을 편집하는 권한으로 해석하지 않는다. 새 함수 생성·공개 핀/분기·override
계약·slot/copy/private/whole-body 전환이나 다른 입력 혼합을 새로 구현하지 않았다.

같은 checkpoint·전체 source proof·물리 원본이고 미반영임이 확인된 시도에서만 새
선택으로 명시 재시도한다. 응답 유실은 receipt만 회수하며 저장 중 새 시작 선택은
분리해 보존하고 이전 선택을 재전송하지 않는다. 변경 파일이 없는 반복 Save에도
`ownedEntry` receipt를 보관하며 기존 source/name/route receipt를 유지한다.
가짜 graph/C# 변경이나 임의의 시작점·새 권한은 만들지 않는다.

명시한 시작 선택만 실행 순서에 반영하고 C# bytes·ID·핀/출력·signature·profile·다른
연결·부모/외부 원본과 권한을 보존한다. 물리 쓰기는 Review→Confirm과 최종 CAS를
따른다. 제품 delta는 feature-authoring.js·그 JS canonical metadata·Blueprint.csbody·
Export.csbody뿐이다. 관련 저장 분리 안내 2문구·3곳만 문체를 정리하며 컴파일러의
원문 진단은 전역 번역하지 않았다. UI/레이아웃과 공개 .celem 계약은 그대로다.

## 최종 검증

독립 LF 18·CRLF 20·새 패키지/전체 복원/실패 수명관리
8, **총 46단계: 신규 46·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발 통과/실패 수는 합산하지 않는다.

- 정확한 제품/안내 delta·canonical asset·JS 문법과 이전 완료 문구를 대조했다. 공유
  history inverse/CAS/restart/owner 및 표시명/실제 의미 변경 native 보호를 검사했다.
- 실제 API에서 stale checkpoint·위조 source closure·잘못된 가상 시작 식별·owner/slot/
  frame·없는 목적지/잘못된 분기 반환·추가 포트·매개변수/본문 혼합·숫자 목적지를
  거절했다. 저장은 멱등이며 cold·공유 history·receipt hash 위조 거절을 유지한다.
  해당 프로필의 명시 시작 연결 해제는 빈 entry 그대로 저장·cold 복원하며, 명시 재연결
  전까지 임의 시작 노드나 물리 원본을 쓰지 않는다.
- 기존 시작 포트 키보드 선택 취소·개인 입력의 정확한 cold 복원, 쓰기 실패 후 새
  시작 선택/명시 재시도, 동료 checkpoint 충돌/cold를 확인했다. 응답 유실은 receipt만
  회수하고 저장 중 새 선택을 별도 저장한다. 이전 시작 선택은 재전송하지 않는다.
- 저장 뒤 공유 Undo/Redo/cold·Review 취소·검토 후 Main.graph.json 원본 충돌 거절·
  새 Review/Confirm·실제 .NET 실행을 검사했다. 물리 graph는 entry만 바뀌고 모든 기존
  연결·노드·ID·profile·다른 파일/C# bytes는 같다. 반환 10,
  `lead → callee:1 → after:10` 또는 `late → callee:1 → after:10`을 확인했다.
- 변경 파일이 없는 반복 entry Save도 receipt를 보관하고 cold에서 물리 쓰기 없이
  판정한다. 기존 source/name/route API를 양쪽에서 새로 회귀했다. CRLF에서는 수정한
  route 늦은 입력 UI와 C# 쓰기 실패/새 입력/cold/Undo/Review·Confirm·실행 UI 및 property
  observation·부분 Review·경로/원본 위조·expected-missing/readonly CAS 거절도 새로 검사했다.
- 새 Windows 교차 패키지의 구성/무결성·패키지 엔진 웹 시작과 entry normal/loss UI·
  실행을 확인했다. 압축 CRC·전체 파일 SHA/모드를 검증해 완전히 복원하고, 복원 엔진의
  entry 쓰기 실패/새 선택과 늦은 선택을 최종 Confirm·실행/cold까지 새로 검사했다.
- 성공·실패·예외·증거 보존/복원·자식 종료·소유 임시물 cleanup 수명관리도 통과했다.

저장 전 모든 private Undo/Redo와 모든 포인터/터치/문맥/프로젝트 왕복을 신규 완료로
주장하지 않는다. 이번 연결 조작은 기존 시작 포트의 키보드 경로다. 안내의 모든 오류
조건을 각각 UI 주입하지 않았으며 전체 UI 검증과 구분한다.

## 검증 보완과 증거

이전 route 늦은 입력 검사는 실제 packet의 `to` 대신 `text`를 보아 요청 목적지의
검증이 약했다. `to`가 새 목적지와 정확히 같고 새 요청이 존재하는지 확인하도록
route/entry 검사를 고쳤다. 이전 최종 archive의 전체 SHA·manifest와 두 late 사례의
traffic을 읽기 전용 대조한 결과 각각 `tail → lateTail` 두 요청뿐이고 이전 목적지
재전송은 없었다. 이번에는 수정한 route UI도 최종 코드에서 새로 실행했다.
이 감사 결과는 최종 단계 재사용/합산으로 취급하지 않는다.

이전 record `7e8debc0c33f41158a177321a6a82ba2`, archive SHA `d14af1b5249806d94750e4d403f88a13d741a718bf6e19ed91e6d7a28e6d10fb`.

개발 record `/workspace/artifacts/v536-verification-managed/runs/06e91756150c47e1b2d569ed978bb7f1.json`

개발 SHA `6374b0fdc1772ef425243753b5648ebb9ac2364bfaea5f83bb66b94a1c04e027`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/0b3447c46202416aa125448f67cf06dd.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/0b3447c46202416aa125448f67cf06dd.zip`

SHA256 `8e548faa5a9cbec786807daf6f4747be7e63891fec1bfa602e6c1987277a757a` (2.80MiB).

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `fe44bc6910e7b5da7b1d810c8ef5c9e0703911eb`, `c3e44542905a8d719d2f0b2ed05f1272d52c34a1c59719780e261f10be234580.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `ad18d4f10d16417e5fd464934180360daa5e7184f4a24fda00cf32332912bd7f`.

- rollback: 출처 `877534e95d4c15f3ef14e4d2951a66637f58a0ef`, `f4c6accb960f60d37c89ad726abb0c489aeb05d76b8bf7b20ce4f03de4f73bc4.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `d8af87461d294a9f832b434767a1e615d5d2c90c67c749334337d029ddc58fef`.

최신은 최종 동결 코드와 일치한다. 정상 롤백·증거·기존 원본을 유지하고, 자식 종료와
archive 검증 후 이 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 과거 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1621.90MiB, 최대 cgroup 메모리
4680.73MiB. 최종 실행 순증가 3.93MiB, 개발 시작부터
보관 확인까지 5.82MiB, 문서 마감 전 여유 1618.03MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여와 한계

root 핀/export·혼합 signature/description·서로 다른 입력 혼합 등 다른 일반 Save는
별도 읽기 점검 후보다. 재현 없이 결함/정상 금지/새 필수 조합으로 확정하지 않는다.
나머지 V2와 V3–V9·기존 팩/backend·종류 호환성 결정, 실제 Windows/모바일·전체 UI·
Space 전달은 남는다. 완료 M11/M12/M4를 조합별 잔여로 다시 열지 않는다.

검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이다. 실제 Windows apphost/
WebView2·모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space는 미검증이다.
live AI·계정/자격증명·유료 호출·새 외부 권한은 사용하지 않았다.
