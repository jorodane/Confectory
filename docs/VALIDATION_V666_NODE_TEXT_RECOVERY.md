# V666 한 동작 이름·설명·본문 저장 복구 검증

제품·검사·도구·delta 동결은 `7cf9aaa875e9f038a8b316cc1716087e3a12b6ee`이다. 이후 마감 commit은 문서만 바꾼다.
[닫힌 범위](V2_NODE_TEXT_RECOVERY.md)와 [정확한 delta](v666-node-text-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `5d090e97ad1a1fbf2a80f9f61ee3bd8aeec476c7`에서 같은 직접 소유 ordinary root
code/next 노드의 이름·설명·C# 본문을 원래 UI로 입력했다. checkpoint 쓰기 실패 뒤
개인 입력 3개가 모두 사라지고 live에만 남았다. checkpoint·물리 원본·기존 caller는
같았으며 cold에서는 이전 세 값만 복원됐다. baseline JSON SHA는
`187b4ff3e48f8186df25f94490803c0cafd88acc158c1096b77c7256cf6c07d3`이다.

같은 기존 동작의 rename/intent/source 세 종류 중 중복 없는 2–3개 문자열을 기존 원자
후보·checkpoint CAS·receipt·공유 이력으로 저장한다. 이름이 포함된 native 허용 범위를
같은 직접 소유 code/next 노드로 닫고, 설명/본문의 기존 native 지원은 보존했다.
단독 편집이나 다른 이미 지원된 문맥을 새로 제한하지 않는다. 이 결합 경로로 다른 노드/실행선/핀/계약/
생성/네 번째 입력·중복 종류·권한 추정을 허용하지 않는다. writer·receipt 형식·소유/
권한 정책·Review→Confirm·최종 CAS·원본 화면/문구/레이아웃을 바꾸지 않는다.

미적용/같은 checkpoint·전체 원본 closure가 확인될 때만 같은 key/종류/노드의 수정된
텍스트로 명시 재시도한다. 추가 root 값 등이 섞이면 모든 입력과 원래 시도를 보존하며
legacy live 저장으로 우회하지 않는다. 확정 receipt 뒤에는 자신의 캡처 origin·동일한
전체 소스 ID/해시를 대조한 늦은 텍스트만 별도 저장한다. cold의 process-local revision
차이를 다른 원본·누락 origin·다른 필드/노드의 허용 근거로 사용하지 않는다.

본문을 포함한 저장은 기존 ownedSource receipt/복구 경계를 사용하고, 이름·설명만
있을 때는 기존 일반 receipt 의미를 유지한다. 새 source 편집 권한이나 자동 C# 재작성,
공개/override 계약 변경은 없다. 설명 변경의 기존 C# 재검토 의미를 유지한다.
사용자가 명시한 세 텍스트 외 C#·caller·ID·타입·핀·값·연결·profile과 부모/외부 원본을 보존한다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)** 통과했다.
개발 결과는 이 수에 합산하지 않는다. Git 객체·실제 EOL·NuGet/home·엔진 캐시를 분리했다.

- 정확한 UI/native delta 세 경로와 canonical 자산 SHA/크기를 대조했다. 실제 JS guard·
  origin/receipt proof·기존 root 이름 대응·공유 이력/컴파일 probe와 JS 문법을 확인했다.
  세 필드의 모든 두 입력 하위집합·전체 집합을 닫힌 하나의 텍스트 편집 흐름으로 검사했다.
- API에서 stale checkpoint·변조 전체 closure·다른 노드·미관측 owner/private·추가 계약/
  실행선/인자·중복 설명·비문자열/길이 초과 설명·잘못된 이름을 거절했다. 쓰기 실패 시
  live/checkpoint/원본을 보존하고 미적용 증명은 원래 checkpoint/전체 closure/물리 원본이
  같을 때만 인정했다. 정상 적용·멱등성·cold receipt·변조 graph 해시 거절을 확인했다.
- 세 텍스트 및 이름/본문·이름/설명·설명/본문 하위집합의 실제 native 저장과 공유
  Undo/Redo를 확인했다. 나머지 필드·계약·원본을 보존했다. 기존 이름/본문 API도
  수정된 닫힌 지원 범위에서 무관한 argument 혼합을 거절하며 회귀했다.
- 실제 제목·설명·C# 편집기의 고정 선언 보호·취소·Undo/Redo, 세 private 입력의 cold 복원,
  쓰기 실패 뒤 세 값 수정/명시 재시도, 동료 checkpoint 충돌을 확인했다. 실패 후 root 값이
  더해지면 네 입력을 cold 뒤에도 보존하고 legacy live 변경으로 우회하지 않았다.
- 응답 유실은 확정 receipt만 회수하며 이미 저장한 세 텍스트를 재실행하지 않았다.
  응답 보류 중 새 이름·설명·본문을 입력하고 cold 뒤 별도 저장했다. 공유 Undo/Redo/cold는
  세 값을 같은 이력으로 움직이고 ID/계약/연결을 유지했다.
- Review 취소·Review 후 물리 graph 변경의 최종 CAS 거절·새 Review→Confirm·실제 .NET
  실행·최종 cold를 확인했다. 명시한 본문 편집에 따라 `body`와 11 또는 12를 출력하고 같은
  값을 반환한다. 원래 caller와 다른 원본은 유지했다. 동일한 세 값의 no-op Save와 반복
  빈 Save/cold에서도 receipt와 원본이 유지됐다.
- 잘못된 C#은 CS0103/원래 심벌 진단을 전달하고 Confirm을 거절했다. 저장된 초안·원본을
  보존하고 명시 수정 뒤에만 다시 Confirm했다. 기존 두 텍스트/단독 source의 늦은 입력
  UI도 회귀했다. 이전 다른 고정 기능의 증거는 해당 기록에 유지하며 신규 수로 재합산하지 않는다.
- 새 Windows 교차 패키지 구조·무결성과 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  전체 파일 SHA·압축 CRC·권한 모드로 전부 복원한 엔진에서 쓰기 실패 복구·늦은 세 입력의
  Confirm/실행/cold를 확인했다. 성공/반복/실패/예외 수명관리와 증거 보존·자식 종료·
  소유 임시물 정리도 통과했다. 실제 Windows apphost/WebView2 또는 모바일 실행은 아니다.

## 개발 검사 수정과 증거

첫 정적 guard VM은 실제 proof(data) 바인딩을 누락해 late-proof assertion이 실패했다.
제품 변경 없이 그 실제 함수를 주입한 뒤 guard와 source/root proof 회귀가 통과했다.
개발 notes에 원인과 같은 제품 SHA를 남겼다.

첫 late UI는 의도적으로 authorBatch 응답을 보류한 중에 설명 helper가 f.pending을
무조건 호출했다. confectoryFlushPresentation이 busy 해제를 기다려 서로 대기하는 검사
문제였다. private 세 입력의 cold 복원 이후 제품의 늦은 입력 판정 전이었다. 해당 fixture/
checkpoint·진척과 원인 JSON을 보존하고 정확한 소유 worker만 종료했다(exit -15).
보류 중에는 검증 flush만 건너뛰고 응답을 해제한 다음 모든 텍스트/receipt/CAS 검사를
수행하도록 수정했다. 같은 제품의 수정 late UI가 최종 Confirm/실행/cold까지 통과했다.
제품 실패나 최종 통과로 합산하지 않고, 종료/자식 회수 기록을 보존한다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/5525b2081d184904994144d2e53d2f38.json`

개발 증거 SHA `e2de56b92644ea7a713a68a5e8535ea56ba531d4eea85fe3ad95c72bb35909eb`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/807a5d095bb64c0ea2575362973d012e.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/807a5d095bb64c0ea2575362973d012e.zip`

SHA `3b79e051ffe72efae5ce4ccff8e3926a5b2cc265308c527698a2ddb464a1b311` (2.85MiB).

## 보관·공간·남은 범위

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `7cf9aaa875e9f038a8b316cc1716087e3a12b6ee`, `3c3fa47440113d1aad7cdb4337043d6b007aa597637a3d4fbf474847ee68663f.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `7cf513eb2e8228b9f8dfcbc9e3fb4f3685bcb87a9c6d86014b8cc2569a4d4f16`.

- rollback: 출처 `93512e020fb4e43f9a84112f951c27945d003a68`, `af82b94505ededa7e968d22344e662597ba3b1f465b3416a7835bb45dc138dfe.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `f61a5693f88c5e8ed3a34ac5252a11eae660d63058aa10fdb2433de25efe7c2c`.

최신은 동결 코드와 같고 이전 정상 최신본을 rollback으로 보관했다. 전체 SHA/manifest와
복원 가능성을 확인한 뒤 이번 실행 소유 임시물만 승인 수명대로 정리했다. 다른 과거 자료·
원본·로그·프로필·SDK·캐시 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1548.14MiB, 최대 cgroup 메모리
4778.26MiB. 최종 실행 순증가 3.94MiB, 개발 시작부터 보관
확인까지 5.32MiB, 문서 마감 전 여유 1544.27MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

이 단위는 같은 ordinary 동작의 유한한 세 텍스트 흐름을 마감했다. 다른 root·혼합 저장·
직접 배치 형태는 재현 기반 점검 후보이며 가능한 조합마다 새 필수 항목을 늘리지 않는다.
완료 M11/M12/M4를 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/backend·종류 호환성 결정,
실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달의
한계를 유지한다. 3D 표시/권한 팩과 이동 연출·실행 분리, 동기 caller의 명시적 async 전환
정책도 바꾸지 않는다. live AI·실제 계정/키·유료 호출·새 외부 접근/권한은 사용하지 않았다.
main은 사용자 검토/병합용으로 보존한다.
