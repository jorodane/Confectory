# 저장 copy 실행 분기 동작의 내부 흐름

기준은 저장소의 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)이다. 원본 app.js `localImplementationDraft`는 소유 copy 구현을 준비하면서 공개 입출력 정의를 유지한다. blueprint.js `openInternal(node,false)`는 선택한 동작 정의를 내부 문맥으로 넘긴다. 이미 지원한 ordinary/ref/out copy 진입을 재구현하거나 임의 C# 논리를 그래프로 추론하는 요구로 확대하지 않는다.

## 지원 경계

저장된 same-contract copy가 정보 한 곳에 직접 배정되고 기존 소유 receipt와 완전한 source closure를 검증한 경우, Root 또는 기존 소유 private frame의 C# 실행 enum 선택기를 내부 단일 코드로 감싸고 본문/helpers를 편집·저장한다. 기존 private/switch profile과 native `executionSource` 전달을 사용하며 새로운 공개 계약·핀 ID·자동 target 선택 정책을 만들지 않는다. 정보 종류 Enum/EnumValue의 데이터 타입과 이 실행 분기 계약은 별개다.

바깥 노드 ID·signature·arguments·ref/out 역할/저장소 배정·실행 enum primary/항목 ID/이름/수치/순서·branchOwner·외부 실행선·계속/빈 case/default를 그대로 유지한다. 내부 코드가 계산한 선택값을 한 번 그대로 전달한다. 원래 C# record와 donor/공개 함수/owner/다른 target은 원문 guard로 보존하고 새 leaf만 별도 소유한다. 본문에서 기존 Result를 명시 선택하는 것은 사용자의 C# 편집이며 자동 소스 치환이 아니다.

UI와 저장 경계는 동일한 일반/실행 선택기 조건을 적용한다. 실제 권한은 UI의 boolean으로 부여하지 않고, PackWorkspace가 현재 owner hash/revision·독점 배정·implementation/graph locator·copy provenance·전체 frame/source binding을 검증한 뒤 후보 내부의 제한된 native authority로 전달한다. 소유자 누락·다른 hash·공유 copy·다른 source/frame 또는 불완전한 실행 매핑은 거절한다. 생성 중 copy·whole-body `implementationContext`·상속/참조 전환은 이번에 열지 않는다.

## 저장과 검사

기존 미리보기/Undo/Redo, 동일 프로젝트/slot/frame 입력 키, 단일 authorBatch 후보와 receipt, 체크포인트 CAS, 컴파일 Review→Confirm 및 최종 파일 CAS를 재사용한다. 실패/취소/충돌/응답 유실/cold/늦은 입력에서 활성 원문과 사용자 입력을 보존한다. 별도 창과 프로젝트 왕복은 같은 원본 증거·ID만 복원하고 자동 재배정하지 않는다.

기존 branch fixture에 실제 소유 copy 준비·owner 배정·scoped 호출을 추가했다. 원본 donor와 구분된 copy를 실제 호출해 음수 primary·빈 case·alternate·default·미지정 수치·메인 계속·반복 호출, 반환/out, 별도/동일 ref 저장소를 관측한다. API는 전체 graph(출처와 다른 노드 포함)·모든 원본 파일의 보존, 반복 내부 진입, 잘못된 enum/signature/우회 종료, C# 컴파일 오류 입력 보존·Review 뒤 guard 경합과 최종 CAS를 검사한다. UI는 원본 진입·고정 선언·본문/helpers 취소/편집·Undo/Redo·Root Save·쓰기 실패·원문 충돌·cold·응답 유실·늦은 입력·프로젝트 왕복·Review 취소/Confirm을 확인한다.

`tools/verify_desktop.py --suite node-internal-copy-branches`는 독립 LF/CRLF checkout의 native 분기/중첩/whole-body/ref-out·소유 경계와 기존 직접 소유 branch/ordinary copy 저장소 영향 회귀, 새 교차 패키지 및 전체 SHA/CRC/모드 복원본 실행을 순차 수행한다. 최신/롤백 두 패키지와 로그/합성 입력/프로필/스크린샷/manifest를 지속 보관한 후 이번 실행의 자체 임시 root만 정리한다. 이전 자료 추가 삭제나 검증 수준 축소는 없다.

집중 검사에서 ref/out 전달 copy의 최초 래핑 후 본문 재저장이 기존 private enum guard에 막히는 실제 결함을 발견했다. native에서 파생한 `executionForwarded`와 실행 enum의 정확한 일치를 함께 요구하여, 같은 계약의 본문/helpers만 기존 후보에 적용하도록 보완했다. 임의 ref/out enum 계약 편집을 허용하지 않는다. 수정 후 API에서 같은 계약의 enumCode 거래와 다른 계약 거절을 함께 검사한다. 검사 상태 조회는 하나의 관측 view를 재사용하여 실패 대기 중 임시 view를 과도하게 생성하지 않는다. 초기 fixture의 owner 선택/재선택·copy 상대 경로·private enum source binding 누락·비활성 C# 버튼 선택 오류와 이 제품 결함은 별도로 보존하며 최종 통과에 합산하지 않는다. 최종 LF/CRLF·패키지/복원 검사는 수정 후 동결 코드로 모두 새 실행한다.

## 남은 고정 범위

M11 전체 완료는 아니다. 생성 중 copy의 첫 Save/배정, whole-body copy의 this/재귀/import 소유 문맥, 상속/참조 전환과 기존 private 미지원 profile은 원래 유한한 잔여다. whole-body copy의 receiver/sourceIdentity를 추측해 치환하지 않는다. 공개 override 원계약 변경은 정상 금지이며 독립 공개 계약 복제는 필수 범위에서 제외한다. 가능한 ref/out/분기 조합마다 새 요구를 추가하지 않는다. 내부 종료점 직접 선택의 기존 native/UI는 유지하며 이번 지원과 별도로 새 정책을 만들지 않는다.

B2 다른 사용자/그룹 backend·종류 C# 표현/사용 중 항목 삭제 명시 대응·M4/M12·3D/권한 별도 팩도 기존 고정 잔여다. 3D 이동은 시각적 연출이며 작업 실행 조건이 아니다. 실제 Windows apphost/WebView2·모바일·전체 UI·Library/Space 전달은 교차 패키지 검사와 구분한다. 새 전환 초안을 과거 롤백 UI로 확정하는 호환성은 보장하지 않는다.

최종 코드의 실제 신규/재사용 검사, 패키지 출처·증거와 공간 실측은 아래 검증 결과에 기록한다.
