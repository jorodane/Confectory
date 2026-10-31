# 저장 whole-body copy의 내부 흐름

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `localImplementationDraft`와 선택 동작의 `openInternal(node,false)`다. 원본의 소유 구현 복사와 개별 내부 편집 흐름을 기존 native 규칙에 연결한다. C#을 자동 분해하거나 `this`/import/원문을 추측해 치환하지 않는다.

## 기존 의미와 이번 범위

기존 `ImplementationCopy`는 선택한 공통/명시 target 한 개를 별도 소유 구현으로 준비한다. 원본 C#은 그대로 record에 보관하고 원래 파일을 `sourceIdentity`로 유지한다. 이미 Blueprint로 전환된 소스도 자신의 whole-body context만 검증해 copy의 실제 ID·signature·imports로 restamp한다. 원본 부모·donor·다른 target은 바꾸지 않는다. 이번 연결은 이 확정된 native 소유 context를 재사용하며 새 의미를 만들지 않는다.

지원은 저장되어 정보 한 곳에 직접 배정된 same-contract copy의, private graph가 가능한 기존 profile 안 `next` whole-body C# 동작이다. native `DescribeOwned`와 copy ABI receipt가 현재 소유 구현/계약/import/locator/출처/전체 source closure를 검증한 뒤 같은 `BlueprintNodeFlow`를 사용한다. 기존 단독 배정·원문 guard·정확한 frame/source binding·source budget을 유지한다. C#에서 준비된 copy와 기존 Blueprint에서 준비된 copy를 구별해 검증한다.

래핑은 바깥 ID·signature·입력 연결·반환·출구·실행선·metadata를 유지한다. 원래 context와 sourceIdentity를 한 내부 코드로 옮기고 원문 C# 문자열을 그대로 보관한다. native는 같은 구현 클래스의 원래 `Invoke`를 한 번 유지하며 해당 context를 포함하는 ancestor만 같은 instance를 전달한다. 따라서 `this.Invoke` 재귀와 `this.calls`/`IImports`의 명시 scoped import는 copy의 원래 멤버 문맥을 유지한다. ref/out은 바깥 배정과 기존 native 전달 규칙을 사용하며 값 복사·임의 초기화·출력 폐기를 추가하지 않는다. `contextBoundary`는 바깥 공개 계약/alias 편집으로 이 보호를 풀지 못하게 한다.

공통 UI 팝오버·C# 고정 선언·배치 저장·Review→Confirm·최종 CAS·Undo/취소·cold receipt·늦은 입력 처리를 재사용한다. 원래 C# 파일과 copy record는 guard로 보존하고 새 leaf만 따로 소유한다. 잘못된 receiver/import·중복 멤버 context·다른 owner·공유 copy·누락 binding·원문 경합·컴파일 오류는 전체 미적용 및 입력 보존을 유지한다. 물리 반영은 컴파일·명시 Review/Confirm에서만 일어난다.

## 실제 검증 경계

생성한 fixture는 copy와 donor를 같은 실행에서 각각 호출한다. 사용자의 본문 편집은 copy 결과만 바꾸고 donor와 선택하지 않은 target의 결과/바이트는 유지해야 한다. 명시 다른 target이 있는 donor를 복사해도 copy의 target을 자동 확장하지 않는다. public 매개변수 이름과 native 멤버 이름이 다른 경우, object 상태·this 재귀·명시 Scope와 잘못된 기본 provider의 구별·CallerFilePath/CallerMemberName·자신의 IImports 선언 타입·CRLF verbatim literal·ref/out 같은/다른 저장소를 실제 컴파일/호출로 확인한다. qualified probe는 컴파일만 하고 실행하지 않는다.

API는 C#/Blueprint 출처·void·반복 진입·소유/계약 보호·컴파일 오류 입력 보존·최종 파일 CAS·cold를 검사한다. 기본/독립 창은 진입·Undo/Redo·취소/본문 편집·Root Save·쓰기 실패·원문 충돌·응답 유실·늦은 입력·동일 ID 프로젝트 왕복·Review 취소/Confirm·확정 후 재진입/취소를 검사한다. DOM의 같은 local ID를 다른 frame으로 혼동하지 않고 전체 breadcrumb/source binding을 확인한다.

`tools/verify_desktop.py --suite node-internal-copy-context`는 독립 LF/CRLF checkout과 native 분기/중첩/whole-body/ref-out·소유 보호, 기존 직접 whole-body 및 copy branch 회귀, 새 Windows 교차 패키지·전체 SHA/CRC/모드 복원·복원본 실행·실패 수명관리를 순차 실행한다. 최신/롤백과 증거를 지속 보관한 뒤 해당 실행의 자체 임시물만 정리한다. 최종 신규/재사용 검사·패키지 출처와 공간 실측은 검증 후 기록한다.

집중 화면 검사에서 같은 action 카드 속성을 쓰는 일반 graph 진입과 M11 진입을 검사 선택자가 혼동했다. 렌더러에 없는 code/graph class를 가정한 시도도 실패로 보존했다. 정상 저장/실행/cold는 통과했으며, 보존된 확정 copy에서 실제 C# 편집 가능 상태로 frame을 구분하는 재진입/Undo 구간만 분리 검증했다. 최종 LF/CRLF·패키지의 정상 화면 검사는 보강한 선택자로 전체 흐름을 새 실행한다. 제품의 소유/계약 guard나 레이아웃을 완화하지 않는다.

## 고정 잔여와 보호

M11 전체 완료는 아니다. 생성 중 copy의 첫 Save/배정, 직접 상속/참조 내부 진입 및 private를 지원하지 않는 구형 profile은 기존 잔여다. 구형 `implicit`/`ref` profile을 자동 승격하거나 실행/출력 의미를 바꾸지 않는다. 이번 fixture는 기존 property profile의 native 멤버 문맥을 사용한다. 원래 계약을 위반하는 공개 override 구조 변경은 정상 금지이며 독립 공개 계약 복제는 필수 범위가 아니다. 가능한 타입/호출 조합마다 새 필수 항목을 추가하지 않는다.

B2 다른 사용자/그룹 backend, 정보 종류의 C# 표현/사용 중 삭제 명시 대응, M4/M12와 3D/권한 별도 팩도 기존 고정 잔여다. 3D 이동은 표시이며 실행 조건이 아니다. 임의의 stack/reflection 의존 C#을 완전 동등하다고 주장하지 않고 검증한 native 멤버·저장소·실행 계약과 원문 보존을 구분한다. 과거 롤백 UI로 새 초안을 확정하는 호환성은 보장하지 않는다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 교차 패키지 검사와 구분한다.
