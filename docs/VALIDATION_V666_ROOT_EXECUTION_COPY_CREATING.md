# M12 새 정보 copy의 첫 저장 전 공개 분기 반환

## 지원 경계

저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`, `dist/blueprint.js` 969–976행의 공개 분기/반환 및 248행의 실행 순서, `dist/app.js` 2469–2476행의 원계약·executionOutputs 보존을 기준으로 한다. [기존 M12 경계](BLUEPRINT_ROOT_EXECUTION.md).

직접 소유 정보(schema)의 명시 선택된 새 same-contract copy에서 첫 Save 전에 기존 공개 분기/None 반환 카드를 선택·배치·연결한다. 일반 switch Root·값 입력·선택적 정수 out 하나를 다루며 정의 이름·추가·삭제는 읽기 전용이다. 첫 Save가 생성·등록·정보 배정·반환을 한 후보/checkpoint에 저장한다. 생성 후 아직 미확정인 본문의 반복 편집, 응답 유실/cold receipt 조회와 늦은 새 입력의 별도 명시 Save도 연결한다. 기본/독립 정보 창의 기존 소유·프로젝트 경계와 권한을 사용한다.

함수 ID/IO·IInvoke/실행 결과 인터페이스, 호출 연결, 원래 C#·donor와 부모/외부 원본은 유지한다. 함수 계약 복제·새 permission 정책·자동 대상 선택이나 C# 재작성은 추가하지 않는다. 새 copy 구현 ID는 기존 명시 생성 기능의 ID이며 새 함수 계약 ID가 아니다. CSS/HTML 및 원본 팝오버/레이아웃은 바꾸지 않는다.

## 확인한 결함과 보완

첫 생성이 관측한 함수·donor 원문을 최종 Confirm 파일 CAS까지 보존하지 않아, Review 뒤 원문 공백 변경도 통과하는 것을 재현했다. 해당 소유 공개 copy의 원문 관측을 첫 저장의 원자 그룹/영수증·복원·Review·최종 읽기 CAS에 연결했다. 새 hash를 추정하거나 원본을 다시 쓰지 않는다.

아직 미확정인 copy의 두 번째 반환 편집은 최초 생성 영수증의 본문 hash와 충돌했다. 생성 출처/배정·원래 물리 baseline은 유지하고, 후속 소유자 연결 author 영수증으로 최신 본문 관측을 검증하도록 결합했다. 그룹·읽기 검사·source proof·출처 누락/변조를 거절하며 원래 source lease를 자동 갱신하지 않는다.

독립 창의 기존 요청 허용 목록에는 root 반환 계획이 없어 후속 Save가 거절됐다. 서버에 연결된 같은 정보 소유자/author binding 아래 정확한 반환 계획만 전달한다. 공개 계약 편집·다른 소유자·다른 node·계약 추가 필드·클라이언트의 서버 surface 위조는 거절한다. 최종 소유·독점 배정/출처 증명은 기존 PackWorkspace 후보와 CAS가 계속 검증한다.

집중 진단의 nullable 컴파일 오류는 수정했고, 재시작 전 Undo를 cold 뒤에도 기대한 검사·성공 receipt 정착 뒤 입력 목록 전체 동일성을 기대한 검사·떠 있는 창의 가림·독립 창의 잘못된 Review 진입은 fixture를 기존 사용자 동작에 맞췄다. 강제 클릭이나 제품 레이아웃 변경 없이 창을 이동하고 정보의 관련 변경 검토로 진입한다. 입력/원문 보존과 실제 실행 검증은 유지했으며 실패 증거를 보존했다.

## 최종 신규 검증

동결 실행 source는 **`d6a8aa0e67378dbacf25c9486bf23fb0b2a70581`**다. `tools/verify_desktop.py --suite root-execution-copy-creating`의 **50단계가 모두 신규 통과**했다.

| 묶음 | 신규 통과 | 재사용 |
|---|---:|---:|
| 독립 LF checkout·빌드·native/API/UI·영향 회귀 | 24 | 0 |
| 독립 CRLF checkout·같은 준비·관련 검사 | 20 | 0 |
| 새 Windows 교차 패키지·probe·패키지 UI·전체 복원·복원 UI·실패 수명관리 | 6 | 0 |
| 합계 | 50 | 0 |

각 checkout은 no-hardlinks 독립 clone과 별도 tool home·NuGet/compiler cache를 사용했다. 각각 native **38개**, 소유 경계 **2개**, 실제 최종 읽기 CAS **4개**가 실패/skip 없이 통과했다. 이 사례 수와 위 실행 단계 수는 별도 집계다. 기존 공개 분기·switch·중첩·whole-body/ref/out native와 저장 copy API·같은 세션의 생성/후속 편집·다중 caller/target·호출자 없음·단일 int out·혼합 선언·헤더 이미지 회귀도 신규 실행했다. M11은 LF의 새 copy whole-body/ref API와 CRLF의 중첩/ref 분기 copy·독립 창 응답 유실 UI로 확인했다.

집중 실행 39단계와 진단 실패 8건은 별도 보존했다. 수정 전 실패나 이전 성공을 최종 50단계 통과로 재사용하지 않았다. 집중 workspace 최종 제품 overlay와 위 source Git blob의 SHA도 일치한다. 새 패키지의 기본 화면/실행, 전체 SHA·CRC·파일/디렉터리 mode 복원 및 복원본 독립 창의 늦은 입력/권한 거절/실행을 검증했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/fabbfc41eca542bab359fd7756a3f307.json` (`cleaned`, 50/50).
- 최종 증거: `/workspace/artifacts/v536-verification-managed/runs/fabbfc41eca542bab359fd7756a3f307.zip`, SHA-256 `acd21008b1c676ac61360f87293088c439d31ef6beafd73b577863c4ce0a090b`.
- 집중 증거: `/workspace/artifacts/v536-verification-managed/runs/15518a3ad14a47649eaf25e89df1e3df.zip`, SHA-256 `e94547d47ece5fd5c043de50b5200826470d3752973a25382ff5e15e72046cc4`.


API는 기존 분기/None 선택, 미등록 분기·추가 계약 필드·잘못된 실행선/다른 frame·중복 계획 거절, 첫 Save 전 원문 경합, 한 후보 저장과 cold/동일 receipt, 관측 그룹/읽기 hash/source proof·출처 변조, 미확정 copy의 반복 None→실패 반환 저장 및 부분 Review/최종 원문 경합 거절을 확인했다. 정상 Confirm과 실제 CLR 실행에서 int out을 먼저 발행하고 선택 분기와 다음 줄을 실행하며 원래 C#·계약/ID·donor를 보존했다.

화면은 기존 정의의 readonly 표시·반환 선택/배치·Escape·Undo/Redo, 첫 Save 전 cold, 명시 취소, 쓰기 실패·원문 충돌·응답 유실·늦은 입력, 동일 ID의 다른 프로젝트 왕복, 기본/독립 창과 Review 취소/Confirm·확정 후 cold를 확인했다. 독립 창은 허용된 반환 편집과 권한/계약 거절을 함께 확인했다. 늦은 입력은 자동 저장하거나 새 copy를 재생성하지 않고 명시 Save만으로 기존 소유 본문에 별도 반영한다.

## 지속 보관과 공간

관리형 index `/workspace/artifacts/v536-verification-managed/packages/index.json`에 최신과 직전 정상 롤백을 지속 보관했다.

| 보관본 | source commit | ZIP SHA-256 | bytes | manifest SHA-256 |
|---|---|---|---:|---|
| 최신 | `d6a8aa0e67378dbacf25c9486bf23fb0b2a70581` | `f225cfd28a157d04afa76092e52a5eca9f370637c21468be2e6d4b483885f7f3` | 51,320,419 | `293719cc0d0552c9221e674f04e3386144a83516189941d8bad9e292128afd5d` |
| 정상 롤백 | `cf825dcd35122521f4bebe0f5d2dd8c46bd80734` | `017f9bacfbef5e0d73cbdcea038ea3cfe25828170c5709ed35677ca1d8adda31` | 51,314,600 | `2c51f3cc6cc16e5f11f12ab8b003ad83f62d614074f6ac2fda64d6c6527b54be` |

최신은 이번 source에서 신규 생성·전체 복원·복원본 실행을 마쳤다. 롤백은 직전 정상 실행 증거를 재사용하고 archive SHA를 다시 확인했다. 롤백의 이전 지원을 새 첫 저장/읽기 guard 검증 완료로 표시하지 않는다. 새 정상본 검증 뒤 기존 관리형 원자 승격/실패 복구만 사용했으며 과거 비관리 자료·원본·로그·캐시·사용자 데이터를 삭제하지 않았다. 파일/디렉터리 수는 최신 2367/147, 롤백 2367/147다.

최종 실행 여유는 **1952.41 → 1947.82 MiB**, 순증가 **4.59 MiB**였다. 집중 증거 순증가는 별도 **3.56 MiB**다. 최종 stage 샘플 최소 여유는 1952.35 MiB, cgroup 메모리 피크는 4127.06 MiB였다. 추가 지속 공간144MiB(안전64MiB 포함), RAM3GiB+512MiB 및 메모리7GiB+1GiB 예산을 낮추지 않았다. 집중/최종 소유 임시 root는 자식 종료와 검증된 지속 증거 보관 뒤 정리됐다. 이후 단위의 순증가를 보장하는 값은 아니다.

## 잔여 및 호환성

이번 정보 copy 첫 저장 경계를 마감한다. 자식 소유 본문·등록 외부 함수, 다른 원래 데이터/호출 문맥의 M12 결합과 M4 async는 고정 ledger의 별도 잔여다. 가능한 조합마다 새 요구를 추가하지 않으며 공개 override 계약 변경·부모/참조 원본 직접 편집·독립 새 함수 계약 복제·legacy 자동 승격은 요구로 늘리지 않는다. M11은 실제 회귀 외 새 미완료로 열지 않는다.

공개 문법이나 IInvoke ABI는 바꾸지 않았다. 보강 전 미확정 공개 copy checkpoint에 원래 관측 그룹/읽기 영수증이 없으면 이를 추정해 자동 승격하지 않고 원본을 보존하며 복원을 거절한다. 자동 폐기/마이그레이션을 이번에 구현하지 않았다. 기존 종류 문법 등 과거 parser의 별도 비호환 제한은 그대로다.

기존 ABI/공유 호출자·고급 타입/표시명, 종류의 C# 표현/사용 중 삭제 대응, B2 타 사용자 backend, V2–V9·별도 3D/권한 팩은 고정 ledger대로 남는다. 3D 이동은 표시 연출이며 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·DPI/IME·전체 UI와 Space/Library 전달은 미검증이다. 최종 결과 문서만 추가한 게시 commit은 검증 source와 실행 코드가 같으며 보고 commit의 패키지를 다시 만들었다고 주장하지 않는다.
