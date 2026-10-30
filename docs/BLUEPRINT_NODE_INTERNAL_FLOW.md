# 개별 C# 동작의 내부 흐름 진입

기준은 저장소의 `Confectory-Editor-Prototype-v666.zip`이다. 원본 카드의 `data-function-write-direct` → `openInternal(node,false)` 및 모바일 `data-flow-internal` 연결을 따른다. 원본 `dist/blueprint.js`의 `openInternal`(838행 부근), `api.internal`(1472행 부근), 개별 동작의 C# / 내부 흐름 버튼(1630행 부근)은 선택한 동작 정의를 내부 문맥으로 넘긴다. C#을 의미 단위로 분석하거나 완전한 그래프로 역변환한다는 계약은 아니다.

현재 지원은 **이미 private graph를 지원하는 profile의 저장된 직접 소유 Root 및 중첩 graph에 있는 일반 `next` C# 동작**이다. 내부는 원문을 그대로 담은 코드 노드 하나와 기존 반환 내보내기로 시작한다. 원래 바깥 노드 ID, 입출력 signature, 값 연결, 실행선, 아이콘/표시명/설명을 보존한다. 자동 분해·본문 치환·타입 변환·새 공개 계약이나 핀 ID 발급은 하지 않는다.

진입은 창별 미리보기다. 코드 대화상자의 기존 고정 선언 보호를 유지하며 선택한 새 내부 코드 본문을 편집할 수 있다. 미리보기에서는 구조 및 다른 조상 코드 편집을 잠그고, 최초 Save 후 기존 M3 내부 graph 편집으로 이어간다. 모든 정확한 조상과 Root 왕복도 같은 미리보기 후보를 사용하며 그 위치에서 Save할 수 있다. 저장 전 Undo/Redo와 코드 대화상자 취소는 물리 소스나 공용 체크포인트를 쓰지 않는다. cold 복원은 동일 프로젝트와 원본 전체 closure/체크포인트를 확인한 뒤 미리보기를 다시 준비한다.

중첩 진입은 물리 Root·전체 private 경로·local node·qualified source ID·정의/원문 해시를 함께 묶는다. 같은 local ID의 다른 frame으로 저장 대상을 바꾸지 않으며, 입력 키도 전체 private 경로를 사용한다. 새 내부 graph는 선택한 frame의 profile을 유지한다. 새 깊이 제한은 추가하지 않고 기존 엔진의 깊이/노드/경로 예산을 그대로 적용한다. 예산 초과는 부분 변경 없이 전체 거절한다. 기존 Root 초안은 frame이 없는 이전 창 메타데이터도 Root로 해석하되 중첩 요청에는 명시적 source binding이 필요하다.

Save는 기존 `authorBatch` 격리 후보와 최종 체크포인트 CAS를 사용한다. 새 내부 leaf는 `nodes/internal_<nonce>.node.json`에 따로 소유하며 원래 C# record 파일을 덮어쓰거나 지우지 않는다. 원문 문자열·보조 함수는 새 record로 그대로 옮기고 새 위치에 맞는 definition receipt만 다시 계산한다. 바깥 graph의 `retainedCode`는 원래 정의·source ID·텍스트 SHA-256을 기록하는 표시/출처 자료이며 파일 접근 권한을 부여하지 않는다.

미반영 전환의 원본 source guard와 graph/새 leaf/기존 계약은 하나의 atomic group이다. 부분 Review, 원문 변경, 경로 충돌 및 불완전한 cold 그룹을 거절한다. 원래 파일의 보호는 Review와 최종 Confirm에서 다시 검사한다. 실제 소스 반영은 기존 컴파일·Review→Confirm에서만 일어난다. Review 취소는 물리 원본을 보존하고 이미 저장한 초안은 유지한다. 응답 유실은 같은 시도의 receipt를 조회하며 새 래핑을 추측해 반복하지 않는다. 원래 checkpoint와 소스가 미적용 상태임이 증명될 때만 실패한 시도의 수정 입력을 새 시도로 저장한다. 수락 뒤 늦게 입력한 본문은 삭제하지 않는다.

소유 멤버십이 바뀐 Save 뒤 일반 공유 Undo 이력을 넘지 않는 기존 ownership barrier는 유지한다. 저장 전 전환 Undo와 저장 후 내부 노드의 통상 편집 Undo를 구분한다. 원래 C# 파일은 Confirm 뒤에도 보존되지만, 별도 편집된 graph를 버리고 그 파일을 자동으로 다시 활성화하는 양방향 전환은 이번 단위가 아니다.

## 남은 경계

M11 전체 완료는 아니다. 기존 whole-implementation `implementationContext`/`this`/import 문맥, ref/out 저장소, next 밖의 분기 제어·실행 enum/switch, copy/상속/참조 문맥의 노드 전환은 이번 진입에서 원본을 보존하며 거절한다. 구형 profile을 자동 승격하여 암시적 종료/반환 정책을 바꾸지도 않는다. 이 제한은 현재 구현·검증 경계이며 새 영구 UX 정책이 아니다. 기존 whole-body C# 변환 및 native M3 graph 편집 경로는 유지한다. Root 첫 단위와 [중첩 지원 검증](VALIDATION_V666_NODE_INTERNAL_NESTED.md)은 구분한다.

사용자 C# 원문을 유지하는 것과 모든 관측 가능한 C# 의미가 동일함을 증명하는 것은 다르다. 생성된 메서드 위치/호출 경로가 달라질 수 있으므로 caller-info·stack/reflection 등에 의존한 임의 본문의 완전한 동등성을 주장하지 않는다. 자동 추론으로 보정하지 않으며 실제 지원 fixture의 컴파일·호출 결과와 원문 보존을 따로 검증한다.

B2 다른 사용자·그룹 권한 backend, 종류 C# 실행 표현·사용 중 항목 삭제 대응, M4/M12 및 3D·권한 별도 팩은 별도 고정 잔여다. 3D 이동은 표시 연출이며 실제 실행 선행 조건이 아니다. 교차 패키지는 실제 Windows/WebView2·모바일 기기 실행이나 Library/Space 전달을 뜻하지 않는다.

최신/정상 롤백 실행 패키지를 지속 보관한다. 구버전 실행 파일이 이번 미반영 전환의 `nodeFlowOrigin` 보호를 동일하게 적용하는 호환성은 검증하지 않았으며, 해당 초안의 확정은 검증된 현재 코드 기준으로 제한한다.
