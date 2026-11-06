# V2: 한 동작의 이름·설명·본문 함께 저장 복구

기준은 보관된 v666 `Confectory-v666/dist/blueprint.js` 1630–1631행의 같은 노드
제목·설명 편집과 기존 직접 C# 작성/Save 흐름이다. 새 UI나 가능한 편집 조합 전체를
필수 요구로 만드는 단위가 아니다. 같은 일반 동작의 세 텍스트 필드를 한 흐름으로
마감하며 이미 끝낸 이름·본문 두 입력도 보존한다.

## 재현

게시본 `5d090e97ad1a1fbf2a80f9f61ee3bd8aeec476c7`에서 같은 직접 소유 root code/next
노드의 이름·설명·본문을 원래 UI로 입력하고 checkpoint 쓰기를 실패시켰다. 개인 입력
3개가 모두 사라지고 live에만 남았으며, cold 재시작 뒤에는 이전 세 값으로 돌아왔다.
checkpoint·물리 원본·기존 caller bytes는 같았다. 생성 fixture와 실제 실패 화면·traffic·
before/after/cold를 보관했다.

## 닫힌 지원 경계

직접 소유 ordinary root의 같은 기존 code/next 노드에서 `rename`, `intent`, `source`
세 종류 중 중복 없는 2–3개 문자열만 기존 원자 후보·checkpoint CAS·receipt·공유 이력으로
저장한다. 두 필드 하위집합도 이 유한한 같은 동작 편집 범위이며 조합별 새 기능을 만들지
않는다. 설명/본문의 기존 native 일반 저장 지원은 유지하고, 이름이 섞인 후보의 닫힌
허용만 보완한다. 기존 단독 편집·다른 이미 지원된 문맥은 유지한다.

다른 노드·실행선·인자/핀·root 계약·생성·네 번째 편집·중복 종류를 이 경로로 허용하지
않는다. private/copy/slot·부모/외부 원본·참조·문맥 전달의 기존 보호와 override 입출력
계약을 유지한다. 기존 이름·설명·본문 검증과 예산, writer·receipt 형식·권한·이력 planner·
Review→Confirm·최종 CAS를 바꾸지 않는다. 기존 설명 변경에 따른 C# 재검토도 그대로다.
본문은 사용자가 입력한 bytes를 저장하며 나머지 원문·ID·타입·핀·값·연결·profile을 보존한다.

실패 후에는 같은 checkpoint·전체 원본 관측과 미적용 결과가 확인된 경우에만 동일한
노드/종류/key의 수정 텍스트로 명시 재시도한다. 실패한 시도는 새 시도가 정착할 때까지
보존한다. 무관한 입력이 추가되면 모두 유지하고 legacy live 변경으로 우회하지 않는다.
응답 유실은 확정 receipt만 회수한다. 늦게 입력한 텍스트는 자신의 캡처 origin·같은
전체 소스 ID/해시와 정확한 확정 요청을 대조한 뒤 별도 저장한다. cold의 process-local
revision 차이를 다른 원본/누락 origin/다른 종류·노드의 허용 근거로 삼지 않는다.

본문을 포함하면 기존 ownedSource receipt와 소스 복구 경계를 사용한다. 이름·설명만
바꿀 때는 기존 일반 receipt 의미를 유지하며 소스 편집 권한을 새로 부여하지 않는다.
원본 UI·문구·레이아웃과 기존 최신/롤백·임시물 수명 정책을 보존한다.

[정확한 delta](v666-node-text-recovery-delta.json)와
[검증 기록](VALIDATION_V666_NODE_TEXT_RECOVERY.md)을 따른다.

## 고정 잔여

다른 root·혼합 저장·직접 배치는 재현을 확인할 후보이며 가능한 조합을 새 필수 항목으로
늘리지 않는다. 완료 M11/M12/M4는 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/backend·
종류 호환성 결정과 실제 Windows/모바일·전체 UI·Space 전달은 별도 잔여다. 생성한
테스트 자산만 사용하며 계정·외부 접근·유료/live AI를 사용하지 않는다.
