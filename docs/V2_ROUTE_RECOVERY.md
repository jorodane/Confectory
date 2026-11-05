# V2: 일반 다음 실행선 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 442·526·547–548·778행(실행 핀/연결), 1267·1291행의
명시 저장·검토다. 기존 포트의 키보드 연결을 사용하며 레이아웃이나 새 연결 UI는 추가하지 않는다.

## 재현한 결함과 지원 경계

게시본 `5db09dc`의 생성 프로젝트에서 직접 소유 ordinary root code 하나의 다음
목적지를 바꾸고 checkpoint 쓰기를 실패시켰다. 기존 일반 Save가 live 연결을 먼저
바꾸고 개인 입력을 지워 재시작 시 원래 목적지만 복원됐다. checkpoint와 물리 원본은
그대로였다. 수정 전 입력·실패·traffic·스크린샷·cold 결과를 보관한다.

같은 직접 소유 root의 단일 `next` 입력을 기존 private 후보·checkpoint CAS·receipt와
공유 Undo/Redo에 연결한다. 목적지 변경과 명시 해제는 기존 native route 검증을 그대로
사용한다. 없는 목적지/다른 실행 포트·분기 범위를 임의로 만들거나 기본 경로를 선택하지
않는다. 호출/참조·copy/slot/private/whole-body 및 공개 분기 반환은 이번 새 범위가 아니다.
기존 정상 지원·거절과 구분하며 부모·외부 원본이나 공개/override 계약을 바꾸지 않는다.

실패 시 checkpoint·전체 source proof·물리 원본이 유지되고 이전 시도가 미반영임이
확인된 경우에만 새 목적지로 명시 재시도한다. 응답 유실은 같은 receipt로 판정하며,
저장 중 새 연결은 분리해 보존한다. 변경 없는 반복 Save도 `ownedRoute` receipt를
보관하고 기존 source/name receipt를 유지한다. 가짜 graph/C# 변경은 하지 않는다.
연결 의도를 명시한 실행 변화만 반영하며 ID·핀/출력 계약·C# bytes와 다른 연결은
보존한다. 물리 쓰기는 Review→Confirm과 최종 원본 CAS를 따른다.

관련 V2 실행선 해제 안내 2문구·2곳만 “주십시오”로 정리한다.
[정확한 delta](v666-route-recovery-delta.json)는 로직·문체·canonical asset을 구분한다.
backend의 원문 진단은 전역 번역하지 않는다.

## 별도 점검과 한계

이번 Undo 검증은 저장 뒤 공유 draft history다. 저장 전 일반 연결의 모든 편집 조작과
모든 문맥을 완료로 표현하지 않는다. entry/다른 실행 포트·root 핀/export·혼합
signature/description·서로 다른 입력 혼합 등 다른 일반 Save는 별도 읽기 점검 후보다.
재현 없이 결함/정상 금지/새 필수 조합으로 확정하거나 완료 M11/M12/M4를 다시 열지 않는다.
나머지 V2, V3–V9·기존 팩/backend·종류 호환성 결정, 실제 Windows/모바일·전체 UI·Space
전달은 남는다. [검증 기록](VALIDATION_V666_ROUTE_RECOVERY.md)에 검사·보관·미실행을 구분한다.
