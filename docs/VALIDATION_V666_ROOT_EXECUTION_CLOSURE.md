# M12 복수 호출자·target 원자 계약 검증

## 지원 범위

기준은 저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다. `dist/blueprint.js` 969–976행의 공개 분기·반환과 248행의 실행 순서, `dist/app.js` 2469–2476행의 원계약 보존 의미를 따른다. [현재 계약과 실제 구현 경계](BLUEPRINT_ROOT_EXECUTION.md).

직접 소유 동기 void 함수의 기존 값 입력/선택적 int out 하나를 유지하며, 저장된 일반 switch-profile target 전부와 직접 Blueprint 호출 위치를 한 후보·checkpoint CAS·Review 그룹으로 결합한다. 같은 그래프의 반복 호출과 여러 호출자/target을 다루고 모든 호출 위치를 직접 선택한다. 다른 target의 반환도 기존 공개 ID 또는 None으로 명시 대응한다. 누락/중복·추정 배정은 거절하며 대상 자동 선택은 추가하지 않았다. Blueprint 호출자가 없는 공개 정의도 저장하며 기존 C# IInvoke 소비자를 재작성하지 않는다.

현재 slice는 private/copy/상속 body 편집이나 다른 import가 섞인 호출자·복수 provider 계약 변경을 일반화하지 않는다. 물리 파일을 공유하는 target은 초안 소유권이 모호해 현재 거절하며 영구 UX 정책/새 필수 마이그레이션으로 확정하지 않는다. 오버라이드 입출력·권한·부모/외부 원본·ID/값·핀/데이터 연결·본문 바이트와 원래 CSS/HTML을 보존한다.

## 확인한 결함과 회귀

Confirm 후 rootContractGroup이 4개 멤버이면 whole-body 전용 그룹이라고 추정하던 코드가 작은 공개 분기 그룹의 기준본 정착을 막았다. 첫 Confirm·실행은 성공해도 cold 뒤 반복 Save가 낡은 baseline 때문에 실패했다. 멤버 수에 따른 추정을 제거하고 공통 RootGroup 검증을 통과한 전체 멤버만 정착하도록 수정했다. 기존 whole-body context 검증은 같은 공통 validator에서 유지한다. 호출자 없는 API의 Confirm→cold→이름/순서 재편집→재저장/실행과 화면을 신규 통과했다.

집중 검사 중 fixture 선언에 기존 provide 문을 잘못 전달한 실패, 화면이 Linux target을 편집했는데 portable 실행선도 바뀌어야 한다고 기대한 실패를 별도 보존했다. 두 경우 테스트 자산/기대 target을 수정했고 제품 검증을 완화하지 않았다. 실제 기준본 결함 진단 실패와 수정 후 통과를 구분해 보관했다. 통과 개수에 진단 실패를 포함하지 않는다.

## 최종 검증

동결 실행 source는 **`500434bcebce0383cd72c76410b8ed991fe0456b`**다. `tools/verify_desktop.py --suite root-execution-closure`의 **45단계가 모두 신규 통과**했다.

| 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF checkout·빌드·native/API/UI·영향 회귀 | 21 | 0 |
| 독립 CRLF checkout의 같은 준비·관련 검사 | 18 | 0 |
| 새 Windows 교차 패키지·probe·패키지 UI·전체 복원·복원 UI·실패 수명관리 | 6 | 0 |
| 합계 | 45 | 0 |

각 checkout은 no-hardlinks 독립 clone과 별도 tool home·NuGet/compiler cache를 사용했다. 각각 native **38개**, 소유 경계 **2개**, 실제 최종 읽기 CAS **4개**가 실패/skip 없이 통과했다. 이 사례 수와 위 실행 단계 수는 별도 집계다. 새 native 사례는 선택하지 않은 target의 opaque C# body가 있으면 부분 공개 provider 계약을 만들지 않고 거절하며 원문을 보존한다.

집중 실행 25단계와 진단 실패 4건은 별도 증거다. 최종 45단계에는 이전 성공/실패를 재사용하지 않았다. 집중 최종 제품 overlay와 위 source Git blob의 SHA 일치를 확인했다. 새 패키지는 전체 파일 SHA·CRC·파일/디렉터리 mode·RAM 복원과 복원본 실제 hosted 실행을 검증했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/9b60d5cb6c0a4ca68a875611bc166a8d.json` (`cleaned`, 45/45).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/9b60d5cb6c0a4ca68a875611bc166a8d.zip`, SHA-256 `d071035007af9a0361a00582b94c3338961baf7fa8d74415191909cac00c35b6`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/1f36438847a54cf19c1b9f93f3f9bde7.zip`, SHA-256 `b00d563af4546df5b66b15c3aabae03d1e4ca8ff34d94490faa0a61421bd4cbf`.


모든 호출자/target의 명시 대응, 호출 위치 누락/중복·target 누락/추가·마지막 target 오류·낡은 증거 거절, 다른 호출자의 물리 경합, 부분 Review 거절, Review 이후 다른 target 원문 변경의 최종 CAS 거절을 확인했다. 후보 전체는 한 checkpoint로 저장하고 receipt 재조회/cold가 부분 적용·중복 저장을 만들지 않는다. 실제 CLR 실행에서 common/Linux target과 별도 Peer 호출자를 검사하고 공개 분기보다 먼저 int out을 발행했다. 다른 target에서 이름/순서를 다시 편집해도 ID/값과 원래 C# 바이트를 유지했다.

화면 정상·Undo/Redo·취소·쓰기 실패·물리 충돌·응답 유실·저장 중 늦은 입력·cold 복원·Review 취소/Confirm·반영 후 재시작을 확인했다. 직접 선택한 target의 분기 연결만 바뀌고 다른 target의 원래 다음 줄은 실행된다. 호출자 없는 화면도 허구의 호출자를 만들지 않고 같은 저장/확정 경로를 통과했다. 이전 단일 int out API/화면과 M11 종료점/등록 외부 부모, 혼합 선언/헤더 이미지 회귀를 신규 실행했다. M11을 새 잔여로 열지 않는다.

## 보관과 공간

기존 관리형 index `/workspace/artifacts/v536-verification-managed/packages/index.json`에 최신과 직전 정상 롤백을 보관했다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `500434bcebce0383cd72c76410b8ed991fe0456b` | `a58f1296f831b134cd0518ea9da8afb8e3c057c38efb9eca037e1b2a044f7b64` | 51,308,536 | `82860995943d793c77ec1e08d2a5237162aef370b52dcef7441facbc092e8ab3` |
| 정상 롤백 | `d29168242410d1a96f523057f53ba62756de4648` | `3ef0a0eaceaa210ac1f77db04c5263862be2306c9b8d5c90e56522d5a8484c67` | 51,306,144 | `67e4a3ec8bbf7b17594822bb99a3504a839526f910f2b9dcabde2a15b8086dca` |

최신은 이번 최종 source에서 신규 생성·전체 복원·복원본 실행을 마쳤다. 롤백은 직전 정상 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 직전 롤백은 새 복수 target/호출자 checkpoint의 편집을 보장하지 않으며 기존 자료의 정상 롤백용이다. 최신/롤백 회전은 새 정상본 검증 뒤 기존 관리형 원자 승격만 사용했으며 과거 비관리 산출물·로그·캐시를 삭제하지 않았다. 패키지의 파일/디렉터리 수는 최신 2366/147, 롤백 2366/147다.

최종 실행 여유는 **1969.11 → 1965.41 MiB**, 순증가 **3.70 MiB**였다. 집중 증거 순증가는 별도 **2.10 MiB**다. 최종 stage 샘플 최소 여유는 1969.03 MiB, cgroup 메모리 피크는 3931.43 MiB였다. 추가 지속 공간144MiB(안전64MiB 포함), RAM3GiB+512MiB 및 메모리7GiB+1GiB 예산을 낮추지 않았다. 집중/최종 소유 임시 root는 자식 종료와 검증된 지속 증거 보관 뒤 제거됐다. 미래 단위의 순증가를 보장하는 값은 아니다.

## 남은 고정 범위와 미실행

다음 M12 잔여는 same-contract copy/자식 소유 본문에서 기존 공개 분기를 반환하는 연결, 나머지 원래 데이터/호출 문맥이다. ref/비void 등의 표현을 이번에 임의 확정하지 않았다. 가능한 문맥 순열마다 새 요구를 만들지 않는다. 공개 override 계약 변경·비소유 원본 편집·독립 새 계약 복제·legacy 자동 승격은 새 필수 요구가 아니다.

M4 async, 기존 ABI/공유 호출자·고급 타입/표시명, 종류 C# 표현/사용 중 삭제 대응, B2 타 사용자 backend, V2–V9 및 별도 3D/권한 팩은 고정 ledger대로 이어간다. 3D 이동은 표시 연출이며 실행 선행조건이 아니다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI/독립 창/프로젝트 왕복·Space/Library 전달은 이번 신규 실행에 포함하지 않는다. Linux hosted UI·CLR 실행과 Windows 교차 패키지를 실제 기기 검증으로 표현하지 않는다. 검증 뒤 문서만 추가한 게시 commit은 위 동결 source와 실행 코드가 같으며 보고 commit으로 패키지를 다시 만들었다고 주장하지 않는다.
