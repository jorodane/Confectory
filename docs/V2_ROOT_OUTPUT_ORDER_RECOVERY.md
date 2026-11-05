# V2: root 반환 핀 표시 위치 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 700·714행 출력 목록/순서 편집과 기존 native
`rootParameters`/`blueprintRootContract`다. 직접 소유한 동기 root에서 out 둘의 상대 순서는
유지하고 비void 반환 핀을 세 위치에서 이동하는 현재 Alt+화살표 UI를 다룬다.
매개변수·타입·out 순서·반환 타입·실제 C# 호출 계약을 바꾸는 단위가 아니다.

## 재현·구현

게시본 `b5c31ad7ae1b27128e4a0ad0652253a324e17a34`의 생성 프로젝트에서 반환 핀을 이동하고
checkpoint 쓰기를 실패시켰다. live 순서는 바뀌고 개인 입력은 사라졌지만 checkpoint·
물리 원본·C#은 같았다. cold 후 원래 표시 순서만 복원됐다. 원래 실제 .NET 실행,
실패 화면·입력·traffic·cold 증거를 개발 record에 보관한다.

args·returnType·identity remap·outputOrder 네 필드만 있는 단일 root 입력을 원자 후보·
checkpoint CAS·receipt·공유 Undo/Redo와 연결한다. args와 반환 타입은 현재와 같고,
outputOrder는 기존 out 이름 둘의 상대 순서 및 반환 ID를 보존해야 한다. 기존 root 계약
검증을 후보에서 재사용한다. 소유·공유 root/본문·다중 body 등의 기존 거절은 완화하지 않는다.
C# 본문·다른 계약/값/연결·권한·부모/외부 원본을 보존한다. 물리 쓰기는 기존
Review→Confirm과 최종 CAS 뒤에서만 한다. 기존 안내·팝오버·레이아웃을 유지한다.

미반영·동일 checkpoint·전체 source proof가 확인된 경우에만 같은 계약의 새 표시 순서로
명시 재시도한다. 응답 유실은 receipt만 회수하며 적용된 이전 순서를 재전송하지 않는다.
늦은 순서는 별도 입력으로 보관한다. 미반영 저장과 무관한 새 입력/계약 조합은 입력을
보존하며 거절하고 legacy live 편집 경로로 우회하지 않는다. 실패 뒤 개인 Undo로 취소한
입력을 자동 재적용하지 않으며, Redo 뒤 명시 재시도를 유지한다.

변경 없는 반복 Save도 receipt를 보관한다. root receipt만 남고 함수/구현 멤버가 누락되지
않도록 해당 receipt의 기존 세-member root 묶음을 함께 보존한다. 일반 root 묶음의 보관
조건은 그대로이며, 이 표시 순서 receipt에 한정한다. [정확한 delta](v666-root-output-order-recovery-delta.json)와
[검증 상태](VALIDATION_V666_ROOT_OUTPUT_ORDER_RECOVERY.md)를 따른다.

## 유한한 별도 점검

다른 root 핀 정의/실제 ABI 편집·혼합 계약 Save·직접 배치는 원본 요구와 현재 지원을
대조할 별도 점검 후보다. 조합마다 새 필수 요구를 추가하지 않는다. 완료 M11/M12/M4를
다시 열지 않는다. 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정·실제 Windows/모바일·
전체 UI·Space 전달은 고정 수용 표에 남긴다. 새 계정/외부 권한이나 live AI 호출은 사용하지 않는다.
