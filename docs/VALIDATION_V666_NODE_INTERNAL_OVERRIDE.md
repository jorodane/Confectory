# M11 직접 소유 override 본문과 상속/참조 경계

기준은 고정 v666 ZIP `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의 `blueprint.js:791` (call/wrapper readonly), `openInternal:838`, `app.js:2453` (`localImplementationDraft`) 및 `moduleFunctionDefinition:2469`다. 원본 팝오버·카드·레이아웃을 추가/교체하지 않는다. native `Registry.Effective`의 함수 ID·입출력 계약 일치와 본문 Origin 규칙도 그대로 따른다.

## 대조 결과와 선택한 실제 누락

| 문맥 | 소유/계약 및 수용 경계 |
|---|---|
| 상속받기만 한 부모 본문 | 선언 Origin과 실제 소스 소유자는 부모다. 자식 이름으로 부모 graph/node를 쓰는 것은 정상 거절이다. 이를 새 독립 계약 복제나 자동 마이그레이션 필수 요구로 바꾸지 않는다. |
| call/참조·wrapper 원본 | 원본 UI가 readonly로 표시한다. 참조 연결을 유지하며 다른 원본을 감싸거나 수정할 권한을 주지 않는다. 기존 명시적 copy/참조 열기 기능은 유지한다. |
| 같은 공개 계약을 상속하고 자신의 Blueprint target을 직접 선언한 자식 | runtime에서 정상 실행되는 자기 소유 본문이다. `Parent` 존재만으로 M11 전체를 막던 실제 누락을 재현했고, 해당 소유 본문의 단일 코드 래핑/편집/저장을 연결한다. |
| 공개 override 타입·핀 수·역할·반환 계약 변경 | 사용자 합의와 기존 runtime 상속 계약상 정상 거절이다. 구현만 변경한다. 독립 공개 계약 복제/새 ID 생성은 필수가 아니다. |

## 이번 지원과 보호

현재 프로젝트에서 관측 가능한 소유 부모 선언 체인을 가진 자식의 **직접 선언된 Blueprint target**을 다룬다. Root/기존 소유 private frame의 C# 동작을 같은 pure 래핑으로 감싸며 원래 ID·핀·연결·본문/helpers·profile·공개 계약·활성 target을 보존한다. 부모 본문을 복제하거나 참조를 바꾸지 않는다. body가 자식의 명시 선언에 없거나 Origin이 다르면 거절한다.

현재 자식/부모의 게시 선언과 관측 텍스트를 확인하고 기존 `Registry.Effective`로 동일 함수/서명 상속 계약을 검증한다. 부모 헤더·그 상속 import의 계약을 기존 source closure에 포함한다. parent 영수증 누락/변조·오래된 원문·사이클/예산 위반·비소유 참조·계약 변경은 전체 후보를 거절한다. 기존 일반 C# 편집·registered parent의 읽기 경로를 새 정책으로 차단하지 않는다.

미리보기와 입력은 물리 원문/배정을 쓰지 않는다. 기존 단일 후보·checkpoint CAS·receipt·Review→Confirm·Undo/Redo·취소·재시작·늦은 입력/실패 보존을 사용한다. 부모의 기존 본문/참조·ID·원문 내용·권한은 유지한다. 관측 후 또는 Review 후 부모가 바뀌면 전체 저장/Confirm을 거절하고 상대 변경을 덮지 않는다. 소스 코드의 의미를 추론하거나 자동 재작성하지 않는다.

## 유한한 잔여와 정상 거절

직접 소유/저장 copy/새 copy의 기존 M11 지원은 다시 미완료로 세지 않는다. 이번에는 직접 소유 자식 target의 프로젝트 내 부모 선언 관측 경계를 닫는다. **등록된 외부 부모를 가진 자기 소유 target의 M11 관측/최종 CAS 연동**은 현재 소유 edit-workspace source만으로 영수증이 완결되지 않는 구체적 구현 경계다. 읽기 자체는 기존 registry 경로를 유지하며, 외부 원본 쓰기 금지와 자식 구현 편집 가능성을 구별한다. 이 경계를 영구 UX 금지나 새 권한 정책으로 확정하지 않는다.

부모/참조 원본 직접 쓰기, 공개 override 입출력 변경은 정상 보호다. legacy profile 자동 승격·독립 공개 계약 복제는 필수가 아니며 새 마이그레이션을 추가하지 않는다. M4/M12·B2 타 사용자/그룹 backend, 정보 종류의 C# 표현/사용 중 항목 삭제 대응, 고정 V2–V9와 3D/권한 별도 팩은 기존 별도 잔여다. 3D 이동은 시각적 연출이며 작업 실행 조건이 아니다.

## 검증과 보관

`tools/verify_desktop.py --suite node-internal-override`로 독립 LF/CRLF, 해당 API·화면의 정상/거절·취소/반복/재시작/충돌/응답 유실/늦은 입력/프로젝트 왕복·Review/Confirm, 기존 native/소유/copy 회귀를 검증한다. 새 교차 패키지·전체 SHA/CRC/모드 복원·복원본 실행·실패 수명관리와 최신/롤백·증거 보관을 유지한다. 이번 실행의 소유 임시물만 정리하며 과거 비관리 원본·패키지·캐시·로그·프로필·사용자 데이터는 추가 삭제하지 않는다.

원래 경계의 재현은 부모가 다른 구현을 가지는 실제 실행 가능한 자식 fixture에서 확인했다. 자식 본문은 7을 반환하지만 기존 M11은 Parent 존재만으로 거절했다. 수정 후 Root/중첩 API는 같은 원문을 보존하며 사용자가 지정한 11로 실행 결과를 바꾸고 부모·상속 참조를 보존한다. 누락/위조 ancestry, 상속 본문 소유권 사칭·비소유 ID·계약 변경 및 저장 전/Review 후 부모 충돌도 검사한다. 재현·실패 증거와 최종 통과는 구분한다.

실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 교차 패키지와 별도로 미완료다. 최종 코드의 신규/재사용/미실행 검사와 보관 수치는 아래에 기록한다.

## 최종 동결 코드와 검증 결과

패키지와 모든 최종 실행의 source는 `1d9bdf6aeacb798ac603adf79b3c52750cad6ccb`다. **45단계 모두 신규 실행·통과**했으며 과거 통과를 합산하거나 실패/skip을 통과로 바꾸지 않았다.

| 검증 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF checkout·빌드·API·화면·영향 회귀 | 19 | 0 |
| 독립 CRLF checkout·빌드·API·화면·영향 회귀 | 18 | 0 |
| 새 교차 패키지·전체 복원·복원본 실행·실패 수명관리 | 8 | 0 |
| 합계 | 45 | 0 |

양쪽 checkout은 `--no-hardlinks` 독립 clone과 별도 restore/Release/MCP/새 엔진·cache를 사용했다. 각 checkout에서 native 분기·중첩·whole-body·ref/out 28개와 상속 본문 소유 보호 2개를 새로 통과했다. 기존 혼합 선언·헤더 이미지·원문 편집·private copy checkpoint 및 저장 whole-body/실행 분기 copy도 영향 회귀로 확인했다.

Root/중첩 override API는 부모 영수증 누락·변조, 상속 본문 소유권 사칭, 비소유 ID와 실제 게시 선언의 계약 변경을 거절했다. 관측 후 부모 변경의 전체 Save 거절·입력 보존, 같은 요청 반복의 중복 방지, 부분 Review 거절, Review 후 부모 변경의 최종 Confirm CAS 거절과 상대 원문 보존을 검증했다. 부모의 실제 C# 구현은 자식과 다르게 두었고, 자식 실행 7 → 사용자가 편집한 11을 확인하면서 부모 본문·상속 참조의 bytes와 모드를 보존했다.

화면 검사는 원본 내부 진입·단일 코드 래핑·Undo/Redo·대화상자 취소/적용·Root 왕복·cold 복원을 확인했다. 부모 원문 충돌, 쓰기 실패 후 복구, 응답 유실, 저장 중 늦은 입력의 별도 Save, 동일 ID 다른 프로젝트 왕복, Review 취소/Confirm과 반영 뒤 재시작도 통과했다. 새 패키지에서 기존 직접 소유 및 이번 override 화면을 실행했고, 전체 SHA/ZIP CRC/권한 모드 복원 후 새 copy 중첩 ref/out·응답 유실과 override 늦은 입력 화면을 다시 실행했다. 이 실행은 실제 Windows apphost/WebView2 기기 검증이 아니다.

별도 집중 실행의 19단계도 통과했다. 여기에는 수정 전 실행 가능한 자식 본문을 Parent 존재만으로 거절하던 경계 재현이 포함되며, 최종 45단계에 중복 합산하지 않는다. 집중 실행의 변경된 제품 입력은 최종 Git blob과 SHA로 대조했다. 최종 결과 집계 도우미가 `refused-reference.json`을 `reference.json` suffix로 선택한 오류는 정확한 루트 증거 경로로 수정했다. 제품/검사 실패로 숨기거나 검증을 재실행하지 않았으며 원본 증거 ZIP은 변경하지 않았다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/85363c362e20410484136af561313b56.json` (`cleaned`, 45/45).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/85363c362e20410484136af561313b56.zip`, SHA-256 `680adcfc69d802fbeb0e10c3acf59ba34307bc4b01ea74ec203456d6e14ef0b7`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/71d6a998551546b2a11b6e17c28d8f78.zip`, SHA-256 `d42d7078ec4161829150065f2ce83e2c60d1da5124da280605d0e4c69ea6bdcc`.

## 지속 보관과 공간

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `1d9bdf6aeacb798ac603adf79b3c52750cad6ccb` | `6e4b242050277807571b75c7789474b2fdadf5973c9adaba02fe96286134b11e` | 51,269,008 | `fd3ba5118d37185e3f1388face3214ed49b039eb6a513f5ca059f411ecf05597` |
| 정상 롤백 | `3d91ba6acea42354afdc48b9f0c2a08887e2b8d9` | `067f332da31eb0e6877026b072bf03309408359933165a73f4687f417ba9e074` | 51,266,676 | `841791b87360f67b8338f21cc316825cc8d68a1f52c2c5d77d9e7f35a6b4e62a` |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이며 양쪽 모두 2364파일·147디렉터리다. 최신은 이번 새 생성·전체 복원·복원본 실행을 검증했다. 롤백은 직전 정상본의 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 기존 관리형 원자 승격/회전만 사용했으며 유일한 정상본을 먼저 제거하지 않았다.

최종 실행의 디스크 여유는 **1996.41 → 1992.44 MiB**, 순증가 **3.96 MiB**다. 집중 실행의 증거 증가는 별도 **2.04 MiB**이며 합산해 다음 단위 증가량을 보장하지 않는다. 최종 단계 샘플 최소 여유는 1996.36 MiB, cgroup 메모리 피크는 4576.36 MiB였다. 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함), 기존 RAM/메모리 예산은 낮추지 않았다.

정상 반복·복사 중 예외·UI 실패·변조 확인 실패에서 예상 오류를 그대로 기록하고 증거를 보존한 뒤 해당 실행의 소유 복사본만 제거했다. 원본 패키지/SDK는 변하지 않았다. 집중·최종 실행의 임시 root는 소유 자식 종료와 증거 보관 뒤 제거됐으며 과거 비관리 자료는 추가 삭제하지 않았다.

검증 후 게시할 HEAD와 위 source의 차이는 결과 문서뿐임을 확인한다. 보고서 commit으로 새 패키지를 생성했다는 뜻은 아니다. 이번 지원은 **프로젝트 내 관측 가능한 부모 체인과 직접 선언된 자기 Blueprint target의 편집**이다. 등록 외부 부모의 관측 영수증/최종 CAS 연동은 실제 다음 M11 잔여이며, 부모/참조 원본 쓰기·공개 override 계약 변경·legacy 자동 승격·독립 공개 계약 복제를 새 필수 요구로 만들지 않는다.
