# V2: 기존 일반 동작의 표시명·본문 함께 저장 복구

보관된 v666 `Confectory-v666/dist/blueprint.js`의 노드 이름 편집(926행 이후)과
C# 편집 진입, 기존 구현의 원래 compact 제목 inspector와 C# 편집기·Save를 함께 사용하는
흐름이다. 새 화면·문법·공개 함수 계약을 추가하지 않는다.

## 재현과 범위

기준 게시본 `47a343450dc448126c0598ec9c12315afcad23ec`에서 직접 소유 root의 기존 일반
next code 노드 하나의 표시명과 본문을 바꾸고 checkpoint 쓰기를 실패시키면 두 개인 입력이
모두 사라졌다. 두 값은 live에만 남고 checkpoint/물리 원본은 같았다. cold 재시작하면
이전 이름·본문으로 돌아왔다. 각각의 단독 저장 완료와 다른 실제 혼합 저장 결함이다.

native 후보의 이전 혼합 거절은 구현 경계였다. 실제 UI가 이 두 입력을 순차 live 변경으로
넘기고 checkpoint 전에 지우던 결함을, 정확히 같은 root/같은 노드의 `rename`·`source`
두 edit로 한정한 원자 후보 연결로 보완한다. 미관측 owner/private/slot/copy·다른 노드·
일반 next가 아닌 코드·추가 계약/분기/실행선은 이 두 편집 허용으로 채택하지 않는다.
기존 property/async/copy 등 이미 지원된 경로와 별도 거절은 유지한다.

기존 ownedSource receipt·원자 checkpoint·소유/물리 원본 대조·공유 소스 이력·최종 CAS를
재사용한다. 새 receipt 형식이나 source 소유권·공개/override 계약·C# 자동 재작성·새 권한은
없다. 실패 뒤 같은 두 key/노드/원래 관측에서 이름·본문을 고친 경우만 native 미적용/
원본 동일 증명 뒤 재시도한다. 다른 입력이 더해지면 저장 시도와 전부 보존하며 live 변경으로
우회하지 않는다. 응답 유실은 정확한 receipt를 먼저 회수하고, 처리 중 늦게 입력한 이름·
본문은 그 원래 관측 출처가 일치할 때에만 별도 후보로 저장한다.

소유 집합과 ID가 같으므로 두 값의 공유 Undo/Redo도 한 이력으로 처리한다. 새 노드 생성의
기존 OWNERSHIP_CHANGED 보호와 구분한다. Review→Confirm 이전에는 물리 원본을 바꾸지
않으며, 최종 반영은 명시한 graph 표시명과 기존 node 본문뿐이다. 나머지 C# bytes·
함수/구현/caller·핀/타입/순서·연결·부모/외부 원본·권한·레이아웃을 보존한다.

[정확한 delta](v666-text-pair-recovery-delta.json)와
[검증 기록](VALIDATION_V666_TEXT_PAIR_RECOVERY.md)을 따른다. 다른 root·혼합 계약·직접 배치
형태는 별도 점검 후보이며 가능한 조합을 새 필수 항목으로 늘리지 않는다. 완료된
M11/M12/M4와 고정 V2 후속·V3–V9·팩/backend·종류 결정·실기기/전체 UI/Space 한계는 유지한다.
