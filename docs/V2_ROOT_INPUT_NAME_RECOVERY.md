# V2: root 입력 식별자 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 1196행 `offerIdentifier`와 기존 native
`rootParameters`/`blueprintRootContract`의 명시 remap이다. 새 핀 ID 체계를 만들거나
한글 표시명과 C# 식별자의 미정 대응 정책을 정하는 단위가 아니다.

직접 소유한 동기 ordinary root의 값 입력 하나를 같은 타입·위치·mode와 비void 반환
타입을 유지하며 이름만 바꾸는 기존 UI를 다룬다. 호출자는 기존 위치 기반 계약을 유지한다.
본문의 인자명·소스 bytes와 호출자 C#을 다시 쓰지 않고, 원래 root 입력을 가리키던
그래프 참조만 기존 명시 remap으로 바꾼다. private/slot/copy·부모/외부 원본·공개 실행
분기/async·다중 body·다른 구현 공유의 기존 보호와 override 원계약을 유지한다.

## 재현·구현

게시본 `2a553854ad254994c1b361a472c42a0c1ba8bdf8`에서 입력 `amount`를 `units`로
바꾸고 checkpoint 쓰기를 실패시켰다. live의 이름은 바뀌고 개인 입력은 사라졌지만
checkpoint와 물리 원본·C# bytes는 같았다. 재시작 후 원래 이름만 돌아왔다.
수정 전 실제 .NET 실행과 실패 화면·선택·traffic·cold 증거를 개발 record에 보관한다.

args·returnType·완전한 remap·outputOrder 네 필드의 단일 root 입력을 원자 후보·
checkpoint CAS·receipt·공유 Undo/Redo에 연결한다. 입력 추가/삭제·타입/mode/반환 변경·
다른 출력/본문/실행선 혼합을 이 경로로 허용하지 않는다. 이름은 기존 UI와 native 검증을
통과해야 한다. 기존 root 계약 검증을 후보에서 재사용하고 checkpoint 성공 뒤 live를
반영한다. Review→Confirm과 최종 CAS 전에는 물리 원본을 쓰지 않는다.

미반영·같은 checkpoint·전체 원본 proof가 확인된 경우에만 같은 계약의 새 이름으로
명시 재시도한다. 실패 뒤 개인 Undo로 취소한 이름을 재적용하지 않는다. 응답 유실은
receipt만 회수한다. 저장 후 늦은 이름이 생기면, 자신의 원래 요청·확정 receipt·현재
단일 입력 계약을 대조한 뒤 그 명시 remap을 받아들인 이름에서 새 이름으로 잇는다.
동료 변경이나 미확인 receipt를 새 입력의 허용 근거로 사용하지 않는다. 무관한 새 입력이
섞인 미반영 계획은 모두 보존하며 legacy live 편집으로 우회하지 않는다.

같은 이름의 변경 없는 Save도 receipt와 함수·구현·그래프 세-member 묶음을 함께
보관한다. 일반 root 그룹 보관 정책을 바꾸지 않고 이 receipt와 기존 순서 receipt에
한정한다. 기존 팝오버·안내·레이아웃을 보존한다.

[정확한 delta](v666-root-input-name-recovery-delta.json)와
[검증 상태](VALIDATION_V666_ROOT_INPUT_NAME_RECOVERY.md)를 따른다.

## 유한한 별도 점검

다른 root 정의·혼합 계약 Save·직접 배치는 원본 요구와 현재 지원을 대조할 별도 점검
후보다. 조합마다 새 필수 요구를 추가하지 않는다. 완료 M11/M12/M4를 다시 열지 않는다.
나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정·실제 Windows/모바일·전체 UI·Space
전달은 고정 수용 표에 남긴다. 새 계정/외부 접근·live AI 호출은 사용하지 않는다.
