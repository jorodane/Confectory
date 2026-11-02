# M12: 기존 반환값과 공개 실행 분기

## 원본 요구와 이번 범위

저장소 v666 `dist/app.js:2469–2476`은 returns와 executionOutputs를 구별한다. `dist/blueprint.js:248`은 출력 발행을 결과 분기와 후속 동작보다 앞에 둔다. 이 요구에 맞춰 직접 소유한 동기 ordinary Blueprint 함수의 기존 반환값을 공개 분기와 함께 전달한다. 원본 C#·함수/핀 ID·IO 타입/역할·연결·provider 선택·권한·레이아웃을 재작성하지 않는다.

기존 `IInvoke.Invoke(...) -> T`는 그대로다. 생성 `IExecutionInvoke`의 별도 진입이 기존 인수 뒤의 생성 `out T`로 원래 반환값을 캡처하고 기존 ExecutionResult를 반환한다. 캡처 매개변수 이름은 기존 인수와 충돌하지 않도록 할당한다. Blueprint 호출 노드는 이 값을 기존 return 데이터 포트에 발행한 뒤 공개 분기를 실행한다. tuple/enum으로 사용자 C# 반환문을 바꾸거나 예외를 실패 분기로 치환하지 않는다.

비void 공개 종료점은 `{executionBranch, value}`로 기존 직접 값 연결과 분기 ID를 함께 보존한다. `value:null`은 기존 export-return/미할당 기본값을 사용한다. 공개 계약 전환 후보는 기존 종료점의 데이터 연결을 몰래 변경·누락하면 거절한다. UI 분기 선택·다른 target 선택도 기존 데이터를 보존한다. 공개 분기 전환에서 기존 직접 종료점 데이터는 변경하지 않으며 별도 데이터 편집 UI를 새로 추가하지 않는다. 새로운 반환 배치는 기존 export/default 의미를 사용한다. void/private 종료점의 기존 저장 형태는 유지한다.

## 검증 경계

검증 결과는 최종 동결 코드 기준으로 아래에 기록한다. 이번 사용자 흐름은 int 반환·ref int·out long/string, 직접 종료점 값과 기존 export-return을 함께 사용한다. native 계약 테스트는 반환 캡처 이름 충돌·일반 Invoke·잘못된 값 선택·None/기본값도 확인한다. 이미 지원된 저장/Review/Confirm·복원/receipt·충돌·쓰기 실패·응답 유실·늦은 입력 검증을 이 데이터 흐름에서 실행한다.

구형 parser/생성기는 비void 공개 실행 계약을 이해하지 못하므로 새 데이터를 과거 버전에서 열 수 있다고 보장하지 않는다. 원본·checkpoint·검증 증거와 최신/정상 롤백을 보존하며 자동 migration을 만들지 않는다.

## 유한한 실제 잔여

1. 같은 데이터·분기 전달을 기존 copy/자식 소유/등록 외부 함수 반환 흐름에 적용하고 원래 소유권·readonly receipt 경계를 확인하기.
2. 공개 계약 변경에서 중첩/private의 실제 호출 위치와 등록 외부 import의 관측을 같은 원자 후보에 결합하기.
3. 여러 직접 소유 ordinary provider의 공개 계약·target 반환·명시 caller 대응을 한 후보에 결합하기.

이 목록은 사용자 흐름별이며 타입·ref/out·문맥의 모든 곱을 새 요구로 만들지 않는다. 부모/참조 원본 직접 쓰기·override 공개 계약 변경은 정상 보호다. 구형 profile 자동 승격·독립 새 계약 복제는 필수 범위가 아니다. M11은 구체적 회귀가 없으면 닫힌 상태다.

M4의 동기 호출자 정책은 2026-11-02에 확정됐다. 호출자가 명시적으로 async로 바뀌기 전에는 호환되지 않는 호출을 오류로 표시하고 거절한다. 자동 blocking/await 삽입/caller 변환은 하지 않는다. 실제 async 저장·호출·완료 실행은 다음 고정 M4 구현이며 이번 동기 M12 완료와 구분한다. 3D 이동은 표시 연출이며 실행 조건이 아니고 3D·권한은 별도 팩이다.


## 최종 검증·지속 보관 결과

동결 제품·테스트·harness source는 `e38ba0620d2e62e6f83f250ad55bb6d15e01acf5`다. 이후 커밋은 결과 문서뿐이다. 독립 no-hardlinks LF/CRLF checkout·각각의 home/NuGet·빈 엔진 캐시에서 **신규 LF21·CRLF18·패키지/전체 복원/실패 수명관리6, 총45단계**가 모두 통과했다. 최종 실행의 검사 재사용은 없다. Core/runtime41·소유 경계2씩 **총86개**는 위 단계에 포함되며 양쪽에서 새 실행했다.

- 실제 int 반환·ref int·out long/string 프로젝트에서 원래 직접 종료점 값 연결/export-return·None·return 포트·기존 C# 바이트·입출력과 실행 순서를 확인했다. 일반 IInvoke와 continuation의 반환값 소비도 별도 실제 실행했다. 원래 값 연결 누락/변경·잘못된 분기·낡은 proof는 전체 미반영과 입력 보존을 확인했다.
- 정상·취소/Undo/Redo·쓰기 실패·원문 충돌·Review 이후 경합·응답 유실·늦은 입력·cold 재시작·전체 Review/Confirm을 실제 API/화면에서 새 검증했다. 기존 void/provider import, 복수 target 화면, M11, 원시 읽기 CAS, 등록 외부 새/저장 copy도 새 회귀다. 이 비void Root의 별도 독립 창/프로젝트 왕복은 새 검증하지 않았다.
- 집중 실행의 최종 native/API/UI는 통과했다. 원래의 비void 거절 기대와 잘못된 forwarding fixture, 변경 JS와 resource manifest의 identity 누락을 진단·수정한 실패 로그도 보존했다. 집중 결과를 최종 통과 단계로 재사용하지 않았으며, 최종 동결 blob과 집중 source overlay를 대조했다.
- 새 Windows 교차 패키지의 생성본 normal, 전체 SHA/CRC·파일/디렉터리 모드 복원·복원본 late와 실패/예외 수명관리를 새 검증했다. 실제 Windows apphost/WebView2·모바일 실행·전체 UI/Space/Library 전달 검증은 아니다.

| 구분 | source commit | archive SHA256 | manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `e38ba0620d2e62e6f83f250ad55bb6d15e01acf5` | `c2d877c95f0e36644b816c861cc54df0c3a560170119a6e90de69c958b1a4162` | `08be998131ed4cfa574828e3d75541bbaf978bcd06bad04af1843be4c845cb10` | 51342620 / 2370 / 147 |
| 정상 롤백 | `f43c9caaf3ca823c4d435c3b09dc7c117b4728fd` | `7a3258ec60b3e3882cfc24d849e88660d4e0ef33271da1b077803b60ba086ef1` | `a2ab88e4421d9828dab3f3af960f302c269fe027e3f5780a0f2536b3796adcf4` | 51337618 / 2370 / 147 |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신 생성/실행/복원은 신규 검증이며 롤백 실행은 이전 정상 근거를 재사용하고 archive SHA를 재확인했다. 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/264c3445f34b49d5ad2be3836b3a6364.zip`(SHA256 `244667f14d1d1fe251b905a1067d3f13cc627cac277bccc8534a78d9a18a1d17`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/70b245dc0b8a4ea4a8760847025d82d1.zip`(SHA256 `e97c7eb3a61850f3c4c3b34ba7027cb98b8cc6974cd411e5f3d9451636778d89`)와 입력·로그·프로필·스크린샷·전체 manifest를 지속 보존했다. 자식 종료·보관 무결성·소유권 확인 뒤 이번 두 임시 공간만 정리했다. 승인된 관리 최신/롤백 승격 외의 과거 자료·SDK·원본·사용자 데이터 삭제는 없다.

집중 디스크 여유 1902.99→1902.30MiB(사용 순증가 0.69MiB), 최종 1901.91→1897.39MiB(사용 순증가 4.52MiB)다. 수집 시 여유 1897.39MiB, stage 표본 최소 여유 1901.84MiB, 관측 cgroup memory peak 4142.55MiB다. 기존 persistent144MiB(안전64MiB 포함)·RAM3GiB+512MiB·memory7GiB+1GiB 예산을 낮추지 않았다. 다음 실행의 증가량을 보장하지 않는다.
