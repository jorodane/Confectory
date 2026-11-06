# V2: 위치 기반 계약을 보존하는 root 반환 핀 위치 저장 복구

기준은 보관된 v666 `Confectory-v666/dist/blueprint.js` 700·714행의 출력 표시 순서와
현재 `feature-authoring.js`의 root 출력 이동 UI다. 이미 마감한 out 둘의 반환 핀 위치
복구를 재구현하지 않는다. 같은 표시 작업에서 매개변수 수·혼합 입력 때문에 기존
복구 경로에 들어가지 못하는 실제 누락을 마감한다.

## 실제 재현

게시본 `ddd2c7b1a058f4627a182dc323ce854d0b02a3b7`에서 값 입력 하나·out 셋·int 반환을
가진 직접 소유 동기 root를 생성했다. 기존 C# 호출은 17·23·29를 out으로 받고 10을
반환한다. 원래 UI에서 반환 핀만 두 칸 올린 뒤 checkpoint 쓰기를 실패시키면 개인
root-parameters 입력 하나가 사라지고 live 화면에만 선택이 남았다. cold 재시작에는
이전 위치로 돌아왔다. 실제 함수·호출자 실행과 checkpoint·signature·물리 원본 bytes를
대조한 생성 fixture, 화면, traffic, before/after/cold를 보관한다.

## 닫힌 지원 경계

직접 소유한 동기 ordinary root에서 **매개변수 전체가 동일한 반환 핀 표시 이동**만
기존 원자 후보·checkpoint CAS·receipt·공유 이력으로 연결한다. 기존 1–64개 매개변수,
out 하나 이상, nonvoid 반환이 대상이다. 모든 이름·타입·mode·위치와 반환 타입이
같아야 하며 모든 인자의 identity remap을 명시해야 한다. outputOrder는 모든 기존
out과 return을 각각 한 번 포함하고 out 사이 상대 순서를 보존한다. 기존에 유효한
value/ref 입력이 함께 있어도 이를 변경하지 않는다. 새 ref/out 타입 의미를 만들지 않는다.

현재 출력 이동 UI는 out끼리 순서를 바꾸면 args의 out 위치도 함께 바꾼다. 따라서
그 동작은 단순 표시 이동이 아닌 실제 호출 ABI 변경이며 이번 복구에서 계속 거절한다.
핀 ID 재설계·자동 caller 변경·원문 재작성·새 마이그레이션을 추가하지 않는다.
추가/삭제·이름/타입/mode/반환 변경, 다른 private 입력과의 결합도 이 경로로 허용하지 않는다.

private/copy/slot·공유 root·부모/외부·참조·async·실행 분기·native 문맥의 기존 검증과
소유/권한 경계를 유지한다. 공개/override 계약과 원래 C#·caller bytes·node ID·값·연결·
profile·본문·설명은 보존한다. UI 레이아웃이나 writer·receipt 형식·그룹/이력 planner,
Review→Confirm·최종 CAS·원본 파일 저장 시점을 바꾸지 않는다.

실패 뒤 같은 checkpoint·전체 원본 관측과 미적용 상태가 확인돼야 수정한 위치로 명시
재시도한다. Undo는 취소한 위치를 저장하지 않고 Redo/수정·cold 뒤에도 같은 입력을
보존한다. 무관한 입력이 더해지면 둘 다 보존하며 legacy live 저장으로 우회하지 않는다.
응답 유실은 확정 receipt만 회수하고 중복 저장하지 않는다. 보류 중 바꾼 위치는 이전
응답으로 지우지 않고 별도 저장한다. 기존 함수·구현·graph의 전체 root 묶음을 유지하며
no-op Save·후속 일반 C# Save·cold에서도 그룹과 receipt를 복원한다.

[정확한 delta](v666-root-return-position-recovery-delta.json)와
[검증 기록](VALIDATION_V666_ROOT_RETURN_POSITION_RECOVERY.md)을 따른다.

## 고정 잔여

다른 root 정의·혼합 저장·직접 배치는 재현 기반 점검 후보이며 가능한 조합 전체를
새 필수 기능으로 늘리지 않는다. 완료 M11/M12/M4는 다시 열지 않는다. 고정 V2 후속·
V3–V9·팩/backend·종류 호환성 결정과 실제 Windows/모바일·전체 UI·Space 전달은 별도다.
3D/권한 별도 팩·이동 연출과 실행 분리·동기 caller의 명시 async 전환 원칙을 유지한다.
생성 fixture만 사용하고 live AI·계정/키·유료 호출·새 외부 접근을 사용하지 않는다.
