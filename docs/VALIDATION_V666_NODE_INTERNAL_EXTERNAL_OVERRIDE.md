# M11 등록 부모의 관측 영수증과 최종 CAS

고정 v666 ZIP `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의 `blueprint.js` 내부 진입·call/wrapper readonly와 `app.js`의 `localImplementationDraft`/`moduleFunctionDefinition`을 따른다. 공개 override는 원래 함수 ID와 입출력 계약을 유지하고 구현만 바꾼다는 사용자 합의를 보존한다. 원본 카드·팝오버·레이아웃이나 복제/권한 정책을 새로 만들지 않는다.

## 지원과 보호

기존 프로젝트가 이미 등록하고 의존하는 부모 계약을 상속하며 **자기 Blueprint target을 직접 선언한 자식**의 내부 진입·단일 원문 래핑·편집·Save/Review/Confirm을 연결한다. 기존 registry의 namespace-qualified ID·선언 종류·직접 의존성·상속 함수/서명 일치를 그대로 사용한다. 부모와 참조 원본을 자식 소유로 바꾸거나 외부 접근 권한을 발급하지 않는다.

`blueprintOverrideContracts`는 현재 등록 경로를 통해 프로젝트/선택 pack manifest, 정확한 부모 구현 선언 체인과 함수/import 계약 헤더를 관측한다. 부모의 `.csbody`·graph·노드 원문은 읽거나 실행하지 않는다. 경로별 raw-byte SHA와 텍스트 SHA를 보존하고 사이클·파일 수·바이트 예산·링크 경계를 검사한다. 사용자가 준 임의 경로를 권한으로 받지 않는다.

영수증 hash는 기존 내부 흐름 binding에 포함된다. 미리보기 뒤 Save에서 부모가 바뀌면 새 관측으로 묵시적으로 갈아 끼우지 않는다. 원래 영수증은 기존 `nodeFlowOrigin`/원자 그룹·checkpoint에 보관한다. cold 복원은 저장된 증거의 구조·ID·원문 대응을 검증하고 입력을 유지한다. Save·Review·Confirm은 현재 등록 경로로 다시 유도한 관측과 정확히 대조하며 누락·변조·오래된 증거를 거절한다.

Save checkpoint와 Confirm source commit은 기존 파일 lease 안에서 동일 관측을 다시 검사한다. `CommitPlan`의 선택적 `reads`는 정확한 절대 경로/hash의 **읽기 전용** 검사다. 기존 `writes`/`checks`의 소유 상대 경로 제한은 유지한다. `reads`에는 text를 넣지 못하며 외부 파일/lease를 만들지 않는다. 관측 파일의 읽기 공유 handle을 유지한 채 hash를 확인하고, 하나라도 다르면 source/activity/checkpoint를 쓰기 전에 거절한다. 임의 비참여 외부 편집기나 crash에 대한 범용 분산 트랜잭션을 구현했다는 뜻은 아니다.

구현 목록은 등록 부모 헤더를 기존 의존성 규칙으로 관측하여, 이미 함수가 명시한 자식 구현을 부모 미확정으로 막지 않는다. 함수의 명시 구현·기존 대상 선택 규칙은 유지하며 부모 본문을 자동으로 선택하거나 수정하지 않는다.

## 진단 구분

첫 Save에서 관측 JSON을 새 저장 계획에 복제하지 않고 붙이던 노드 소유 오류를 발견해 수정했다. 최초 traceback을 cold 실패로 읽은 설명은 정정한다. 실패는 cold 이전 첫 Save 단계였으며 수정 뒤 첫 Save·cold·동일 요청 재시도를 실행했다. 임시 checkout의 예외 진단 출력은 제거하고 게시하지 않는다. 화면 진입에서 등록 부모 헤더를 목록이 관측하지 못하던 누락도 수정했다. 다중 구현 중 자동 선택을 추가한 것이 아니라 기존 명시 구현의 부모 헤더를 해석하는 연결이다. 다음 단언 실패는 Review가 저장한 checkpoint와 Save 직후 checkpoint를 같다고 가정한 검사 문제였다. Review 직후 기준·물리 graph·저장 입력을 각각 확인하도록 수정했고 실제 거절/컴파일/실행 판정은 유지한다. 실패 증거를 통과와 구분해 보존한다.

## 유한한 종료 경계

이번 단위는 고정 M11의 등록 부모 관측/최종 CAS 누락이다. 직접 소유 Root/private, 원문 보존 ref/out·whole-body·실행 selector/명시 exit, 저장/새 same-contract copy와 자기 소유 override의 기존 지원을 다시 잔여로 세지 않는다. 부모 본문만 상속한 경우·call/wrapper·비소유 원본 직접 쓰기는 정상 보호다. 공개 override 계약 변경·독립 새 계약 복제·legacy 자동 승격을 새 필수 요구로 만들지 않는다. 가능한 C# 조합 전부를 별도 행으로 늘리지 않는다.

다음 기존 독립 항목은 M4 비동기 계약과 M12 루트 실행 분기다. ABI 영향 closure·공유 호출자·고급 타입/표시명, B2 타 사용자/그룹 backend, 정보 종류 C# 표현·사용 중 삭제 대응, 고정 V2–V9와 별도 3D/권한 팩은 원래 ledger의 잔여로 유지한다. 3D 이동은 연출이며 실행 조건이 아니다. 전체 UI·실제 Windows apphost/WebView2·모바일·Library/Space 전달 완료를 뜻하지 않는다.

## 검증과 보관 원칙

`tools/verify_desktop.py --suite node-internal-external-override`로 독립 LF/CRLF·native/소유/copy 회귀·등록 부모 Root/중첩 API와 화면의 Undo/Redo·취소·쓰기 실패·부모 충돌·응답 유실·늦은 입력·cold/프로젝트 왕복·Review/Confirm을 검증한다. 실제 Confirm/CommitPlan 본문에 재검증 이후 부모 변경·소실·잘못된 hash·쓰기 실패를 주입한다. 그 probe의 metadata/컴파일러는 통제된 의존성이며 실제 registry·컴파일·실행은 API/UI에서 별도 검증한다.

신규 교차 패키지·전체 SHA/ZIP CRC/모드 복원·복원본 실행·실패 수명관리를 수행하고 최신/정상 롤백과 입력·로그·스크린샷·manifest를 지속 보관한다. 실행의 소유 임시물만 기존 수명관리로 정리하고 과거 비관리 자료는 삭제하지 않는다. 최종 source·신규/재사용/미실행 수치·보관 SHA·공간 실측은 종료 후 아래에 기록한다.

## 최종 검증 결과

최종 동결 source는 `ccfb03452bb2654153ab510cc399a9f607cb2cad`다. **51단계 전부 신규 실행·통과**했으며 과거 실행/집중 진단의 통과를 재사용하거나 실패/skip을 통과로 집계하지 않았다.

| 검증 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF clone·checkout·restore·Release/MCP/엔진·영향 회귀·API/화면 | 22 | 0 |
| 독립 CRLF의 같은 준비·영향 회귀·API/화면 | 21 | 0 |
| 새 교차 패키지·전체 복원·복원본 실행·실패 수명관리 | 8 | 0 |
| 합계 | 51 | 0 |

양쪽 checkout은 `--no-hardlinks` 독립 clone과 별도 cache/tool home으로 만들었다. 각각 native 분기·중첩·whole-body/ref/out 28개, 상속 본문 소유 보호 2개, 새 최종 read CAS 5개와 기존 owned CAS 4개가 통과했다. 기존 혼합 선언·헤더 이미지·C# 원문 편집·private copy checkpoint, 저장 whole-body copy 및 중첩 ref/out 반복 실행 분기 copy를 영향 회귀로 확인했다. 단위 수는 여러 native 사례를 포함하는 실행 단계 수다.

Root/중첩 등록 부모 API는 실제 실행 7 → 사용자 편집 후 11, 영수증 누락/변조/다른 경로·소유, 부모 파일 소실/읽기 권한 부재/미선언 의존성, Save 전 부모 변경을 확인했다. cold 체크포인트의 누락/변조는 Restore가 사용하는 같은 검증기로 거절했다. 같은 요청의 cold/retry는 중복 저장하지 않았고, 부분 Review 및 Review 뒤 부모 변경의 Confirm·재검토도 거절했다. 이때 부모·자기 원본과 저장된 입력·상대 변경을 보존했다.

화면은 정상·취소·부모 충돌·쓰기 실패 복구·응답 유실·늦은 입력·동일 ID 프로젝트 왕복·Undo/Redo·cold·Review 취소/Confirm·반영 후 재시작을 확인했다. 새 패키지에서 기존 직접 소유 및 이번 등록 부모 화면을 실행하고, 전체 파일 SHA/ZIP CRC/모드 복원 후 새 copy 중첩 ref/out·응답 유실과 등록 부모 늦은 입력을 다시 실행했다. 외부 부모 파일 bytes와 0440 모드는 유지됐다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 실행하지 않았다. 모든 독립 정보 view/타입/target 조합을 이번 신규 검증으로 주장하지 않는다.

별도 집중 실행은 36단계 중 31통과·진단 실패 5건을 그대로 보존했다. 첫 3건은 같은 JSON 노드 소유 오류를 상세화한 실행, 1건은 Review checkpoint 기준을 바로잡은 검사 진단, 1건은 등록 부모 헤더가 목록에서 미확정이던 제품 누락이다. 수정 후 Root/중첩·CAS 및 화면 통과를 보존했으며, 최종 위 51단계는 모두 다시 새 실행했다. 집중 마지막 제품 overlay와 동결 Git blob의 SHA 동등성도 확인했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/6f6c4e41f8c84664b513f8d5edb5c554.json` (`cleaned`, 51/51).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/6f6c4e41f8c84664b513f8d5edb5c554.zip`, SHA-256 `923147e926b1db59f222a791c10fc8e2952c02925aa450679ced90bdeec11ce3`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/e8a666a1731e417d93ce345d5b70b1cc.zip`, SHA-256 `4397bfa544836adbfc7456c8bf9db9c799e8c8e01a499372b22f8931cb565e70`.

## 패키지 보관과 공간 실측

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `ccfb03452bb2654153ab510cc399a9f607cb2cad` | `2b5440224bcb3b39fa5b1e8fec8fbc1b029aba22b60e30d002d1134e118466ae` | 51,279,519 | `5d565f2ba001b740c1d109b79e29c0f90586eb0450b70dd18b547dfa1066da96` |
| 정상 롤백 | `1d9bdf6aeacb798ac603adf79b3c52750cad6ccb` | `6e4b242050277807571b75c7789474b2fdadf5973c9adaba02fe96286134b11e` | 51,269,008 | `fd3ba5118d37185e3f1388face3214ed49b039eb6a513f5ca059f411ecf05597` |

index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 2365파일·147디렉터리, 롤백은 2364파일·147디렉터리다. 최신은 새 생성·전체 복원·복원본 실행을 마쳤다. 롤백은 직전 정상본의 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 유일한 정상본을 먼저 없애지 않는 기존 관리형 승격/회전만 사용했다. 롤백본에는 이번 등록 부모 영수증/외부 read CAS가 없으므로 새 미확정 초안은 검증된 현재 본에서 확정해야 한다. 구버전 Confirm이 같은 보호를 적용하는 호환성을 보장하지 않으며 자동 마이그레이션은 추가하지 않았다.

최종 실행의 디스크 여유는 **1988.97 → 1984.75 MiB**, 순증가 **4.21 MiB**였다. 집중 증거 순증가는 별도 **3.12 MiB**다. 최종 단계 샘플의 최소 여유는 1988.90 MiB, cgroup 메모리 피크는 4574.62 MiB였다. 144 MiB 추가 디스크 예산(64 MiB 안전 여유 포함)과 기존 RAM/메모리 예산을 낮추지 않았다. 미래 단위의 증가량을 보장하는 수치는 아니다.

정상 반복·복사 중 예외·UI 실패·변조 확인 실패에서 예상 오류·증거를 보존하고 각 실행의 소유 복사본만 제거했다. SDK·원본 패키지는 변하지 않았다. 집중/최종 임시 root는 증거 보관·소유 자식 종료 확인 뒤 제거됐고 과거 비관리 자료를 추가 삭제하지 않았다.

검증 후 결과 문서만 추가한 게시 HEAD와 위 source의 차이는 문서뿐임을 확인한다. 보고 commit으로 패키지를 재생성했다고 표현하지 않는다. **원래 고정 M11의 소유 구현 편집·복구 거래는 이번 등록 부모 관측/CAS까지 마감**하며 정상 거절과 미검증 기기/전체 UI를 별도로 유지한다. 다음 기존 독립 구현 우선순위는 M4/M12이고, 다른 고정 ABI/권한/리소스 등의 잔여는 위 유한한 목록대로 남긴다.
