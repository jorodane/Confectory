# M12 same-contract copy의 기존 공개 분기 반환 검증

## 지원 경계

기준은 저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다. `dist/blueprint.js` 969–976행의 공개 분기/반환과 248행의 실행 순서, `dist/app.js` 2469–2476행의 원본 입출력·executionOutputs 보존을 따른다. [현재 M12 계약과 구현 경계](BLUEPRINT_ROOT_EXECUTION.md).

직접 소유 함수 계약을 사용하는 정보(schema)의 단독 소유 same-contract copy에서, 기존 공개 분기 ID 또는 None을 반환 카드에 선택·배치·연결해 저장한다. 함수의 공개 분기 정의/이름/추가/삭제는 읽기 전용이다. 기존 값 입력·선택적 정수 out 하나, 원래 C# record 바이트·ID·IO·caller receipt/연결·donor·copy provenance·권한을 유지한다. 새 함수 계약이나 자동 copy, 부모/외부 원본 쓰기 권한을 만들지 않는다. 새 copy 미리보기의 반환 편집이나 자식 소유 본문·등록 외부 함수 전체까지 완료했다는 뜻이 아니다.

새 구현을 만드는 행위는 기존 명시 copy 생성이며 함수 ID/계약은 같다. 같은 세션의 공개 분기 Confirm → copy 생성·배정 Confirm → copy 반환 편집·Confirm·실제 실행도 지원한다. source layout/CSS/HTML을 바꾸지 않고 기존 사이드바·반환 선택기·배치·private 입력/Undo 체계를 사용한다.

## 실제 결함과 보완

기존 일반 copy 본문 저장 그룹은 변경하지 않는 공개 함수 원문을 최종 파일 CAS에 넣지 않았다. Review 뒤 공백만 바뀌어도 Confirm이 통과하는 것을 재현했다. 반환 편집에서 관측한 소스를 완전한 atomic 그룹/receipt에 보존하고, 저장·복원·Review·최종 파일 lease에서 원계약·명시 owner 배정/hash·source proof·provenance를 검증한다. 공개 함수 원문 경합은 전체 미적용하며 미저장 입력과 외부 수정을 유지한다. receipt/그룹 누락·hash/owner/출처/계약 변조도 거절한다. 관련 public copy가 없는 거래에는 새 metadata 의존성을 요구하지 않는다.

공개 분기 Confirm 후 지속 checkpoint는 정착했지만 live rootContractGroup이 남아, 재시작 없는 다음 copy 생성을 이전 공개 계약 거래의 새 provider로 오인해 막았다. 완전한 공개 루트 그룹이 byte-identical/clean이고 지속 checkpoint CAS가 성공한 뒤에만 그 거래의 live metadata를 종료한다. 활성/불완전 그룹과 다른 기존 거래는 유지한다. 실제 같은 세션의 생성·후속 반환 편집으로 복구를 확인했다.

초기 테스트의 owner 미선택과 copy 정상 상태 문구를 일반 함수의 `저장됨`으로 기대한 실패는 fixture 문제였다. 소유 정보를 먼저 선택하고 미저장 입력 제거·실제 checkpoint·source-ready·원문 보존을 함께 확인하도록 수정했다. 두 실제 제품 결함과 이 두 fixture 실패를 모두 보존했으며 검증 완화로 통과시키지 않았다.

## 최종 신규 검증

동결 실행 source는 **`cf825dcd35122521f4bebe0f5d2dd8c46bd80734`**다. `tools/verify_desktop.py --suite root-execution-copy`의 **48단계가 모두 신규 통과**했다.

| 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF checkout·빌드·native/API/UI·영향 회귀 | 23 | 0 |
| 독립 CRLF checkout의 같은 준비·관련 검사 | 19 | 0 |
| 새 Windows 교차 패키지·probe·패키지 UI·전체 복원·복원 UI·실패 수명관리 | 6 | 0 |
| 합계 | 48 | 0 |

각 checkout은 no-hardlinks 독립 clone과 별도 tool home·NuGet/compiler cache를 사용했다. 각각 native **38개**, 소유 경계 **2개**, 실제 최종 읽기 CAS **4개**가 실패/skip 없이 통과했다. 이 사례 수와 위 실행 단계 수는 별도 집계다. native 범위는 기존 공개 실행 분기·switch·중첩·whole-body/ref/out 회귀다. 새 copy 거래의 guard와 실행은 실제 API/UI 및 같은 세션 생성 흐름에서 별도로 검증한다.

집중 실행 30단계와 진단 실패 4건은 별도 증거다. 최종 48단계에는 이전 성공/실패를 재사용하지 않았다. 집중 최종 제품 overlay와 위 source Git blob의 SHA 일치를 확인했다. 새 패키지는 전체 파일 SHA·CRC·파일/디렉터리 mode·RAM 복원과 복원본 실제 hosted 실행을 검증했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/827a9915730143a292d935e3690b6e00.json` (`cleaned`, 48/48).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/827a9915730143a292d935e3690b6e00.zip`, SHA-256 `3e7c8f09e9f9fe762e9ddba8643c8c375b50604fef3ed4196bf85e2bb1fa4044`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/3b2f8576c611479da4f0ba51b9a15c5f.zip`, SHA-256 `44391750fb9bc92e26ee2fa8252cf54b97f76a68eeb5470cefcc98883cd12a44`.


API는 기존 ID 선택, 잘못된 분기/연결/공개 계약/owner 증거 거절, 한 checkpoint CAS·동일 receipt 재조회·cold, 부분 Review·Review 이후 계약 원문 경합 거절과 정상 재시도를 검사했다. source receipt/atomic 그룹·owner hash·공개 계약·provenance 변조는 Restore와 같은 순수 validator에서 거절했다. 실제 CLR 실행은 copy가 실패를 반환할 때 int out `10`을 먼저 발행하고 caller의 실패 분기와 다음 줄을 실행하며, None은 실패로 바꾸지 않고 다음 줄로 이어짐을 확인했다. 원래 C# 바이트와 명시 배정/공개 계약은 유지된다.

화면은 readonly 정의와 기존 ID 반환 선택/배치·선택 취소·Undo/Redo, 정상·취소·쓰기 실패·충돌·응답 유실·늦은 입력·cold·Review 취소/Confirm·확정 뒤 재시작을 확인했다. 같은 namespace/copy/분기 ID의 다른 프로젝트와 왕복해도 입력을 섞지 않는다. 늦은 입력은 cold에서 이전 receipt만 조회한 뒤 두 번째 명시 Save로 별도 반영한다.

이전 다중 caller/target API(LF)와 응답 유실 UI(CRLF), 단일 out API/UI, 호출자 없는 UI(LF), M11 copy API(LF)·등록 외부 부모 API(CRLF), 혼합 선언·헤더 이미지 및 실제 CAS 회귀도 신규 실행했다. M11을 새 미완료 요구로 열지 않는다. 새 패키지 자체의 정상 화면/실행과 전체 SHA·CRC·mode 복원 뒤의 늦은 입력 화면/실행, 실패 수명관리를 검사했다.

## 지속 보관과 공간

기존 관리형 index `/workspace/artifacts/v536-verification-managed/packages/index.json`에 최신과 직전 정상 롤백을 보관했다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `cf825dcd35122521f4bebe0f5d2dd8c46bd80734` | `017f9bacfbef5e0d73cbdcea038ea3cfe25828170c5709ed35677ca1d8adda31` | 51,314,600 | `2c51f3cc6cc16e5f11f12ab8b003ad83f62d614074f6ac2fda64d6c6527b54be` |
| 정상 롤백 | `500434bcebce0383cd72c76410b8ed991fe0456b` | `a58f1296f831b134cd0518ea9da8afb8e3c057c38efb9eca037e1b2a044f7b64` | 51,308,536 | `82860995943d793c77ec1e08d2a5237162aef370b52dcef7441facbc092e8ab3` |

최신은 이번 최종 source에서 신규 생성·전체 복원·복원본 실행을 마쳤다. 롤백은 직전 정상 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 직전 롤백에서 새 copy 반환 편집/읽기 guard의 검증 수준을 보장하지 않으며 기존 자료의 정상 롤백용으로 보관한다. 최신/롤백 회전은 새 정상본 검증 뒤 기존 관리형 원자 승격만 사용했으며 과거 비관리 산출물·로그·캐시를 삭제하지 않았다. 패키지의 파일/디렉터리 수는 최신 2367/147, 롤백 2366/147다.

최종 실행 여유는 **1962.03 → 1957.59 MiB**, 순증가 **4.44 MiB**였다. 집중 증거 순증가는 별도 **2.92 MiB**다. 최종 stage 샘플 최소 여유는 1961.95 MiB, cgroup 메모리 피크는 4080.51 MiB였다. 추가 지속 공간144MiB(안전64MiB 포함), RAM3GiB+512MiB 및 메모리7GiB+1GiB 예산을 낮추지 않았다. 집중/최종 소유 임시 root는 자식 종료와 검증된 지속 증거 보관 뒤 제거됐다. 미래 단위의 순증가를 보장하는 값은 아니다.

## 고정 잔여와 미실행

저장된 정보 단독 copy의 위 경계를 마감한다. 다음 M12 잔여는 기존 공개 계약을 지키는 자식 소유 본문과 새 copy 미리보기·등록 외부 함수 등 원래 남은 문맥이다. 다른 데이터 계약/고급 타입은 기존 고정 ledger와 구분하고 가능한 조합마다 새 요구를 만들지 않는다. 공개 override 계약 변경·직접 부모/참조 원본 편집·독립 새 계약 복제·legacy 자동 승격은 새 필수 작업이 아니다.

M4 async, 기존 ABI/공유 호출자·타입/표시명, 종류 C# 표현/사용 중 삭제 대응, B2 타 사용자 backend, V2–V9와 별도 3D/권한 팩은 고정 ledger대로 남는다. 3D 이동은 표시 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI/독립 창/프로젝트 왕복·Space/Library 전달은 이 검사와 구별한다. 최종 결과 문서만 추가한 게시 commit은 위 동결 source와 실행 코드가 같으며 보고 commit의 패키지를 다시 만들었다고 주장하지 않는다.
