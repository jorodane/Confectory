# v666 M12 자식 소유 공개 분기 반환

## 원본과 지원 범위

저장소의 v666 ZIP(SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)만 기준으로 삼았다. `dist/blueprint.js` 969–976의 공개 분기/반환, 718–739의 종료점 선택과 `dist/app.js` 2469–2476의 원계약 유지가 근거다. 기존 원본 팝오버·카드·레이아웃을 재사용하며 CSS/HTML은 변경하지 않았다.

직접 소유 함수의 동기 void·값 입력·선택적인 int out 하나에서 자식이 직접 선언한 ordinary switch Blueprint target(code/export, native context·call·중첩 없는 Root)의 기존 공개 분기/None 반환을 편집·저장·실행한다. 등록 외부 부모는 기존 dependency registry 및 readonly 관측만 사용한다. 상속된 Blueprint 실행도 선언 원본의 source identity를 보존하며, 부모 본문을 자식 locator로 편집하는 것은 거절한다.

공개 입출력/분기 ID·계약, C# 원문, 부모/참조 원본·권한을 변경하지 않는다. 반환 entry/edges/exits만 바꾸고 전체 관측 소스를 원자 Review 그룹과 checkpoint/final CAS에 보존한다. 최신 입력과 Save journal은 최초 외부 부모 관측 해시를 유지한다. 저장 직전 부모 변경을 새 관측으로 대체하던 결함은 이 해시 결합으로 수정했다.

## 최종 동결 소스와 새 검사

제품·검사 코드 동결 커밋은 `758e28ab0c86b7bcc239d289342aaec34581e3cb`이다. 이후 이 결과 문서와 수용 표만 갱신한다. 최종 소스에서 **새 LF 23·CRLF 20·새 교차 패키지/전체 복원/실패 수명 관리 6, 총 49단계**를 모두 통과했다. 실패·생략은 없다. 양쪽 checkout은 Git objects·캐시·SDK home·NuGet 경로를 분리하고 빈 엔진 캐시에서 시작했다.

- 양쪽 신규 Root/Switch/Nested/Conversion/External native 회귀 38개, 선언 소유/타인 node-source 차단 2개씩 통과했다. 이 case 수는 위 stage 수와 중복 합산하지 않는다.
- local/등록 외부 부모 API는 기존 성공·실패·None과 int out 동시 발행, 상속 실행과 부모 locator 편집 거절, 공개 계약/분기/연결/원문 proof 거절, 저장된 origin/group/source/외부 receipt 누락·변조, Save 직전 부모 변경과 Review 이후 부모 변경에 대한 Confirm 거절, cold/반복·확정 후 재진입을 확인했다. LF는 out 없는 함수 API도 새로 확인했다.
- 외부 부모 화면은 LF normal/cancel/storage/conflict와 CRLF loss/late/project를 새로 검사했다. local 부모 화면 normal도 LF에서 새로 확인했다. 기존 분기 정의 readonly·반환 선택/배치/Undo/Redo·선택 취소, 실패 입력 보존과 재시작, 응답 유실 뒤 receipt 조회에 의한 중복 저장 방지, 늦은 입력의 별도 명시 Save, Review 취소/Confirm, 같은 ID의 다른 프로젝트 왕복을 포함한다.
- 공개 반환의 실제 production Review/Confirm/CommitPlan과 제어된 metadata 경계로 local/external의 성공·최종 lease 직전 경합 4개를 양쪽에서 새로 확인했다. 의미/권한/registry receipt는 별도 실제 엔진 API가 검증한다. 기존 copy 읽기 CAS 4개도 양쪽에서 새로 통과했다.
- 저장 copy M12 API와 M11 등록 외부 override 회귀(API LF, late UI CRLF)도 새로 실행했다. M11 기능 범위를 추가한 것은 아니다.
- 새 Windows 교차 패키지 probe·hosted UI normal, 전체 SHA/CRC·파일/디렉터리 모드 복원, 복원본 probe·hosted UI late, 실패 시 수명 관리를 통과했다. Windows apphost/WebView2를 실제 Windows에서 실행한 결과는 아니다.

집중 실행은 24단계이고 진단 실패 3개를 보존했다: `release, override-external-api, bound-ui-normal`. nullable 컴파일 진단은 nonnull 증명으로 수정했다. 외부 부모 Save 직전 변경이 새 관측으로 대체되던 실제 결함은 최초 dependency hash 결합으로 수정했다. 자식 본문 저장을 copy 전용 flag로 검사하던 fixture는 실제 publicBodyOrigin/dependencyHash를 검사하도록 교정했다. runner 들여쓰기 진단은 실행 전 AST에서 수정했다. 집중 결과와 최종 실행 결과를 섞어 통과 수를 늘리지 않았다. 최종 위 검사는 재사용 없이 동결 소스로 새로 실행했다.

## 지속 보관과 공간

| 구분 | source commit | archive SHA256 | 전체 manifest SHA256 | bytes / 파일 / 디렉터리 |
|---|---|---|---|---|
| 최신 | `758e28ab0c86b7bcc239d289342aaec34581e3cb` | `59112a6327a6302e8d08ddbbfa88b96700314b97e953fd59c3d233687fcf7da6` | `dadb04c82ea355d067ea1ee93d0e94d4141a145e7757830f0c4a2cf7227d8ec4` | 51324756 / 2368 / 147 |
| 정상 롤백 | `d6a8aa0e67378dbacf25c9486bf23fb0b2a70581` | `f225cfd28a157d04afa76092e52a5eca9f370637c21468be2e6d4b483885f7f3` | `293719cc0d0552c9221e674f04e3386144a83516189941d8bad9e292128afd5d` | 51320419 / 2367 / 147 |

보관 index는 `/workspace/artifacts/v536-verification-managed/packages/index.json`이다. 최신은 이번 전체 복원과 복원본 실행까지 새 검증했다. 롤백의 실행 근거는 기존 정상 검사에서 재사용하고 압축 SHA는 다시 확인했다. 롤백은 새 자식 공개 반환의 실행 경계를 지원하지 않으므로 최신 초안을 그 이전 엔진에서 실행할 수 있다고 보장하지 않는다. 새 source 문법/원본 C# 자동 migration은 추가하지 않았다.

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/8ea32ce472ab490aa09d4b09bec89286.zip`(SHA256 `524ab0f4f4f0863118f4839eb1b5a68a0cdf113f5478b1029c6744140181cde8`), 집중 증거 `/workspace/artifacts/v536-verification-managed/runs/e5c0c2fc93e444a0b4ca1bb0b7967d02.zip`(SHA256 `e8cecbd7820b5c8322871057410fd88c495e01aa0ff70d88d317423414444ee7`)를 지속 보존했다. 양쪽 RAM 작업공간은 child 종료·보관 확인 후 정리됐으며 현재 존재하지 않는다. 과거 원본/SDK/로그/프로필/산출물의 임의 정리는 없었다.

집중 디스크 1947.69→1944.75MiB(순증가 2.94MiB), 최종 1944.36→1940.19MiB(순증가 4.18MiB), 수집 시 여유 1940.19MiB다. stage 표본의 최소 여유 1944.29MiB, cgroup memory 관측 peak 3988.16MiB다. 기존 추가 persistent 예산 144MiB(안전 64MiB 포함), RAM filesystem 3GiB+512MiB, memory 7GiB+1GiB 기준을 낮추지 않았다. 순증가는 이 실행의 증거/최신·롤백 회전 측정값이며 모든 후속 실행의 보장치가 아니다.

## 잔여와 한계

등록 외부 함수 계약 자체의 반환 편집, 나머지 원래 데이터/호출 문맥과 M4는 별도 잔여다. 공개 override 계약 변경·부모 원본 쓰기는 정상 보호이며 독립 계약 복제/구형 profile 자동 migration은 필수 요구가 아니다. M11은 회귀 검증 대상으로만 유지한다. ABI/고급 타입/표시명·종류 실행 표현/사용중 삭제 대응·B2 권한 backend·V2–V9 등 고정 ledger는 확장하지 않는다.

실제 Windows/WebView2·모바일 기기·전체 UI 및 Space/Library 전달은 이번 Linux hosted UI/CLR와 교차 패키징으로 완료 처리하지 않는다. main과 과거 보관 자료는 보존하며, 이 실행이 소유한 임시물의 승인된 수명 관리와 최신/정상 롤백 두 패키지 보관만 사용한다.
