# v666 M12 등록 외부 함수의 소유 provider 반환

## 원본과 실제 사용자 흐름

저장소 v666 ZIP(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `dist/blueprint.js` 969–976 공개 분기/반환, 718–739 종료점 선택 및 `dist/app.js` 2469–2476 원래 입출력·실행 출력 유지에 대응한다. 기존 정보의 명시 provider 편집·공통 팝오버·카드·Review 경로를 사용하며 새 레이아웃을 만들지 않는다.

직접 의존성으로 이미 등록된 외부 공개 함수의 동기 void·값 입력·정수 out 하나(선택) 계약을 로컬 소유 Blueprint provider에서 구현한다. schema에 단독 명시 배정된 ordinary Root(code/export)의 기존 분기/None 반환을 편집·저장·실행한다. 외부 함수 ID·계약·분기 정의·부모/참조 원본·권한은 readonly로 유지한다. 원래 C#·핀/데이터 연결·배정 원문은 보존한다.

기존 callable 등록 경계에서 외부 함수·팩 manifest 두 헤더만 관측한다. local 프로젝트와 구현 등록이 실제 파일과 일치해야 하며, 외부 본문이나 새 권한을 읽거나 부여하지 않는다. 텍스트·원시 파일 hash를 모두 보존하여 BOM만 바뀌어도 이전 관측으로 Save하지 않는다. Snapshot과 최초 입력 dependency hash, local 전체 관측 그룹, checkpoint CAS/복원/Review 및 최종 외부 typed read CAS를 연결한다.

API가 통과하던 화면에서 switch C# 카드가 copy-only 표시 조건으로 중단되던 누락을 수정했다. backend의 기존 반환 편집 허용 신호만 카드 표시에 연결하며 C#·분기 계약 편집 권한을 추가하지 않는다.

## 동결 소스·신규 검사와 재사용

동결 source commit은 `c8c9cfd7f94bc9b9c536f2903dfa6c08c30aa3e0`이며 이후 결과 문서·수용 표만 갱신한다. 새 독립 **LF 16·CRLF 14·새 교차 패키지/전체 복원/실패 수명 관리 6, 총 36단계**가 통과했다. 최종 실행의 실패·생략은 없다. 독립 checkout은 no-hardlinks Git, 별도 home/NuGet·빈 엔진 캐시로 준비했다.

- 신규 양쪽 API는 실제 out/분기/None 실행, readonly 외부 source 제외, 부분 Review 및 계약/연결/proof 거절, snapshot 누락·변조·소유/경로 위조, 등록 철회·파일 누락/읽기 불가·raw BOM 변경, Save/Review 뒤 계약 변경, cold·반복·확정 후 재진입을 확인했다. LF는 out 없는 함수와 기존 등록 외부 부모의 owned-function 회귀도 새로 실행했다.
- 신규 독립 화면 검사는 LF normal/project, CRLF loss 및 독립 정보 창 late를 포함한다. 새 패키지 normal과 전체 복원본의 독립 정보 창 late도 새로 확인했다.
- 집중 정상/취소/저장 실패/경합/응답 유실/늦은 입력/프로젝트 왕복은 최종 제품 파일의 SHA를 동결 Git blob과 대조해 증거를 재사용한다. 기본/독립 창, Undo/Redo·선택 취소, Review 취소/Confirm, cold와 명시 재저장·실제 호출을 포함한다. 집중 23단계와 진단 실패 4개(`registered-api, registered-fixture-fixed-api, registered-ui-normal, registered-final-ui-loss`)를 보존하며 최종 통과 수와 섞지 않는다. 두 fixture ID prefix/import 오류, Review를 위해 닫은 독립 편집기의 자동 복원을 기대한 fixture 오류와 실제 switch 카드 render 누락을 구분했다.
- production Review/Confirm/CommitPlan의 local/external 최종 경합 4개와 기존 copy 읽기 CAS 4개는 양쪽에서 새로 실행했다. 의미·등록/권한 receipt는 별도 실제 엔진 API로 확인한다.
- 변경 없는 Core/native·소유 경계 입력 134개와 같은 SDK/NuGet bytes를 확인했다. 이전 증거 `/workspace/artifacts/v536-verification-managed/runs/8ea32ce472ab490aa09d4b09bec89286.zip`(SHA256 `524ab0f4f4f0863118f4839eb1b5a68a0cdf113f5478b1029c6744140181cde8`)의 LF/CRLF native 38개·소유 경계 2개씩을 재사용하며 신규 실행으로 세지 않는다. M11 기능을 다시 열거나 새 범위로 확대하지 않았다.
- 새 패키지 probe·hosted UI, 전체 파일 SHA/CRC·파일/디렉터리 모드 복원, 복원본 probe·hosted UI 및 실패 수명 관리를 새로 통과했다. 실제 Windows apphost/WebView2 실행을 뜻하지 않는다.

## 보관·수명 관리와 측정

| 구분 | source commit | archive SHA256 | 전체 manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `c8c9cfd7f94bc9b9c536f2903dfa6c08c30aa3e0` | `a98e2b0435289f6c92c53831ea40cfe7f05246a1852fc9c7cf2dd474200052a2` | `8ceee2814a7ebe239ba0ddd488b7eeb71bc6b83792951d80923d9dfddbb941e5` | 51330275 / 2369 / 147 |
| 정상 롤백 | `758e28ab0c86b7bcc239d289342aaec34581e3cb` | `59112a6327a6302e8d08ddbbfa88b96700314b97e953fd59c3d233687fcf7da6` | `dadb04c82ea355d067ea1ee93d0e94d4141a145e7757830f0c4a2cf7227d8ec4` | 51324756 / 2368 / 147 |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 전체 복원/복원본 실행을 새 검증했다. 롤백 실행은 이전 정상 근거를 재사용하고 압축 SHA를 다시 확인했다. 이전 엔진은 새 외부 함수 반환 draft receipt를 지원하지 않으므로 최신 초안의 이전 엔진 복원을 보장하지 않는다. source 문법·원본 C# migration은 없다.

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/e3793bafc53d44ba8be914ff352dd86c.zip`(SHA256 `92a15aa6dcec124f00b6a40e96cd1a907ac0407cd078d96f13ee5dde19b21a30`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/227cb2bcf67f4141b98d52da17a78b57.zip`(SHA256 `c43dc360035466c095081052dc0273ce5fe840d1bff1a04dc4b516e667bd695f`)를 지속 보존했다. child 종료와 보관 무결성 확인 후 이 실행이 소유한 두 RAM 작업공간만 정리했으며 현재 존재하지 않는다. 과거 산출물·캐시·로그·프로필·원본·SDK의 추가 삭제는 없다.

집중 디스크 1940.07→1936.61MiB(순증가 3.46MiB), 최종 1936.28→1933.17MiB(순증가 3.11MiB), 수집 시 여유 1933.17MiB다. stage 표본 최소 여유 1936.23MiB, cgroup memory 관측 peak 4124.80MiB다. 기존 추가 persistent 예산 144MiB(안전 64MiB 포함), RAM 3GiB+512MiB 및 memory 7GiB+1GiB 기준을 낮추지 않았다. 이 순증가를 후속 실행의 보장값으로 쓰지 않는다.

## 유한한 잔여와 한계

외부 함수의 public same-contract copy 반환과 나머지 원래 M12 데이터/호출 문맥은 이 단위의 완료로 표시하지 않는다. 외부 공개 계약 직접 변경·부모/참조 원문 쓰기는 정상 보호이며 새 권한 정책이나 독립 계약 복제·구형 profile 자동 migration을 추가하지 않는다. M11은 기존 완료를 유지하며 회귀 증거만 확인한다. M4와 고정 ledger의 ABI/고급 타입/표시명·종류 C# 표현/사용중 삭제 대응·B2 권한 backend·V2–V9는 기존 범위대로 남는다.

최신·정상 롤백·증거 보관과 이 실행의 소유 임시물 수명 관리만 사용한다. 과거 자료를 추가 삭제하지 않는다. 실제 Windows/WebView2·모바일 기기·전체 UI 및 Space/Library 전달은 교차 패키지/hosted UI 검사와 별도로 미완료다.


## 고정 M12 잔여 대조

| 구분 | 현재 근거와 다음 경계 |
|---|---|
| 실제 미구현: 등록 외부 함수의 public same-contract copy 반환 | `BlueprintPublicCopyReturns.cs`는 기존 owned 함수 source/group을 요구하고, 현재 read의 등록 함수 snapshot은 `copySource` 없는 provider에 한정한다. 기존 명시 copy 선택/배정을 유지하면서 이 읽기 전용 계약을 copy의 기존 출처·첫 Save/후속 Save receipt에 결합하는 것이 다음 최소 후보다. 새 함수 ID나 독립 계약 복제 요구가 아니다. |
| 기존 데이터/호출 지원 경계 | `BlueprintExecutionBranches.SupportsSignature`의 동기 void·값 입력·선택적인 int out 하나 및 `BlueprintRootExecution`의 일반 직접 caller/target 경계는 그대로다. 그 밖의 원래 데이터 타입·반환·wrapper/private/import 영향은 고정 ABI/공유 호출자 행과 함께 관리한다. 동일 조합의 모든 순열을 별도 필수 항목으로 추가하지 않으며 이미 마감한 직접 복수 호출자/target을 다시 미완료로 세지 않는다. |
| 정상 보호·선택 확장 | 부모/참조 원본·외부 공개 계약 직접 쓰기와 override 입출력 변경은 정상 거절이다. 독립 새 계약 복제·새 핀 ID 체계·구형 profile 자동 migration은 새 필수 잔여가 아니다. |
| 다음 독립 고정 항목 M4 | 원본의 `await → 출력 발행 → 완료 분기 → 결과 분기 → 다음 동작`과 ref 제한을 실제 실행 계약에 연결하는 항목은 아직 미구현이다. 이번 등록 함수의 동기 반환 완료로 M4 완료를 주장하지 않는다. |

이번 단위는 새로운 권한이나 미정 설계 결정을 필요로 하지 않았으며 현재 미해결 차단은 없다. M11은 닫힌 상태를 유지하고 다른 v666 고정 행·실제 기기/전체 UI/전달 검증은 별도로 남긴다.
