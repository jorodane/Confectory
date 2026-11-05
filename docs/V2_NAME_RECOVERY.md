# V2: 일반 동작 표시명 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 926–943행(노드 이름 편집), 1267·1291행의 저장·검토다.
이번에는 native의 기존 작은 화면 카드 inspector에 노출된 직접 소유 ordinary root
code 동작 하나의 표시명 입력을 다룬다. 데스크톱 F2/클릭 이름 편집의 새 구현이나
소유 graph/copy/참조·외부 문맥, 이름과 계약/본문을 섞는 기능을 추가하지 않는다.

## 확인한 결함과 변경

게시본 `98a3098`의 생성 프로젝트에서 표시명을 입력하고 checkpoint 쓰기를 실패시켰다.
기존 일반 Save는 live 이름을 먼저 바꾸고 개인 입력을 지웠다. checkpoint와 원본은
보존됐지만 재시작하면 새 이름이 사라졌다. 수정 전 입력·실패·cold 결과를 보관한다.

이름 전용 입력 하나를 기존 private 후보·checkpoint CAS·receipt·공유 Undo/Redo로
연결한다. 표시명은 식별자나 C# 계약이 아니다. ID·원문·signature·핀/연결을 보존하며
물리 원본 쓰기는 기존 Review→Confirm과 최종 CAS를 따른다. 실패한 시도가 미반영이고
동일 checkpoint·전체 source proof·물리 원본이 확실히 유지된 경우에만 새 이름으로
명시 재시도한다. 응답 유실은 같은 receipt로 판정하고 이전 이름을 재전송하지 않는다.
변경 없는 반복 Save도 `ownedRename` receipt를 보존한다. 이 내부 metadata를 위해
graph나 사용자 코드를 가짜로 바꾸지 않는다. 기존 `ownedSource` 복구는 유지한다.

같은 소유 문맥에서 이름 Save 응답을 기다리는 동안의 새 이름 입력만 private 상태로
보존한다. 작업 시작이나 권한을 바꾸지 않는다. 다른 busy 동작/비소유 문맥의 기존
차단을 넓히지 않는다. 권한·부모/참조/외부 원본·override 계약은 유지한다.

관련 V2 공통 저장·확정 후 안내 3문구/3곳만 “습니다” 문체로 맞춘다.
[정확한 delta](v666-name-recovery-delta.json)는 문구와 로직·canonical asset 변경을
분리하며 backend의 원문 오류를 번역하지 않는다.

## 잔여와 한계

route/root 핀/export·혼합 signature/description·이름과 다른 입력의 혼합 등은 별도
읽기 점검 후보이며 재현 없이 결함이나 새 필수 조합으로 세지 않는다. 이미 완료한
M11/M12/M4를 다시 열지 않는다. 나머지 V2, V3–V9·별도 팩/backend·종류 호환성 결정,
실제 Windows/모바일 기기·전체 UI·Space 전달은 남는다.

[검증 기록](VALIDATION_V666_NAME_RECOVERY.md)에 실제 native/.NET·반응형 Chromium,
최종 LF/CRLF·새 패키지/전체 복원·보관과 미실행 범위를 구분한다.
