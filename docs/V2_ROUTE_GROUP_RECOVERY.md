# 여러 next 실행선 저장 복구

원래 v666 Blueprint의 실행선 해제·재연결과 기존 일반 동작 저장을 따른다.
참조 기준은 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 실행 연결 처리이며, 현재 native UI의
자기 자신·순환 거절과 이미 연결된 대상의 명시적 해제 규칙은 유지한다.
새 자동 대상 선택·선 연결·분기 정책을 추가하지 않는다.

## 재현된 결함

기준 `669d6770593468d40de9c1925a986e520ed870f7`에서 직접 소유한 기존 Root의
일반 C# 동작 세 개를 명시적으로 해제·재연결했다. `body → first → second → third`를
`body → second → first → third`로 바꾼 뒤 checkpoint 쓰기를 실패시켰다.
미저장 실행선 세 입력이 모두 사라졌고 live만 새 연결이 됐다. 재시작하면 원래
연결로 돌아왔다. 물리 원본과 C#·계약은 변하지 않았다. 단일 실행선에는 이미
원자 저장 보호가 있었지만 여러 실행선은 legacy 순차 경로로 빠졌다.

## 닫힌 수정 경계

기존 직접 소유 Root에서 서로 다른 일반 `code/next` 동작의 순수 `route` 입력
2–64개를 기존 authorBatch 후보·checkpoint CAS·ownedRoute receipt·공유 이력에
연결한다. 기존 전역 64편집 예산을 재사용한다. 검사 fixture는 세 실행선이다.
각 명시 대상 또는 명시적 해제(`''`)만 적용하며, 출발점/목적지 검증과 기존
저장/완성 검증을 유지한다. 선택한 실행선의 자기 연결·순환은 최종 후보에서 거절한다.
기존 단일 실행선과 불완전 초안 저장 의미는 그대로다.

실패 뒤 같은 키·출발점·종류의 수정은 원래 checkpoint·전체 source proof·물리
원본이 그대로임을 확인한 경우에만 새 시도로 저장한다. 불명확한 응답은 receipt로
확인하며, 저장 도중 생긴 입력은 별도로 보존한다. 무관한 입력이 추가되면 legacy
부분 쓰기로 우회하지 않는다.

공개 입출력·ID·타입·분기·핀·data 연결·원래 C# bytes·caller·profile은 그대로다.
선택한 next 실행선 외 graph 내용을 바꾸지 않는다. entry/branch/completion/call/
export·source/이름/계약 혼합·생성·private/copy/slot·부모/외부 원본 편집 권한을
이 경계에서 추가하지 않는다. writer/receipt schema와 이력 planner·Review→Confirm·
최종 물리 CAS·원본 레이아웃은 그대로다. 이 경계는 현재 안전한 구현 범위이며,
다른 조합을 영구 금지하는 새 UX 정책이나 새 필수 잔여 목록이 아니다.

[정확한 delta](v666-route-group-recovery-delta.json)와
[최종 검증 기록](VALIDATION_V666_ROUTE_GROUP_RECOVERY.md)을 함께 따른다.
