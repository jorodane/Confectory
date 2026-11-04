# M4: 분기선에 만든 동작의 첫 Task 결합

기준은 저장소의 v666 `dist/blueprint.js`다. 완료와 결과 분기를 구분하고,
`await-before-publish-and-branches`·`dispatch-result-then-continue` 순서를 유지한다.
새 동작의 Task 본문은 사용자가 명시적으로 작성하며 C#을 자동 변환하지 않는다.

## 실제 누락과 연결

기존 원본 UI는 완료선·결과선의 새 동작을 같은 `branchOwner`에 만들고 기존 목적지를
명시적으로 다시 연결할 수 있다. 새 동작과 명시 Task의 첫 저장 결합이 `route:completion`·`route:case:`
입력을 제외해 저장을 막던 경계를 연결한다. 화면 배치나 팝오버를 새로 만들지 않는다.

분기 연결은 기존 `route` 후보 검증을 그대로 사용한다. 존재하는 completion/결과 ID,
같은 실행 영역·목적지와 원래 순서를 확인한다. 새 동작·입력/값·연결·명시 C#을 먼저
검증하고 마지막에 선택한 Task를 적용한다. 한 격리 후보와 checkpoint CAS로 저장하며,
실패하면 기존 checkpoint·원본과 개인 입력을 유지한다. Review→Confirm과 최종 물리
CAS를 생략하지 않는다. 새 공개 실행 계약이나 권한 정책은 추가하지 않는다.

## 검증 경계

직접 소유한 기존 async Blueprint Root에서 원문/정체성을 가진 결과 동작의 완료선과
결과선에 새 ordinary C# Task를 삽입한다. 기존 out 출력은 새 Task가 읽으며 완료,
선택된 결과, 다음 실행의 순서와 기존 C# 바이트·계약·분기 ID·목적지를 보존한다.
UI는 원본 줄의 메뉴, 전환 Undo/Redo, 명시 Task 메뉴와 코드 편집기를 사용한다.

잘못된 분기·실행 영역·소유자·ref Task를 묵시 수정하지 않는다. 동기 caller는 명시
async 전환 전까지 오류이며 자동 대기나 전환을 하지 않는다. 비소유 원본/override
공개 IO 변경·legacy 자동 migration은 새 필수 범위가 아니다. 기존 private/copy/
정보 owner/외부 원본 보호를 이 흐름으로 우회하지 않는다.

[최종 검증 기록](VALIDATION_V666_ASYNC_BRANCH_CREATION.md)에 동결 코드, 신규/재사용,
실패/중단/재시작, 패키지/복원과 보관 범위를 확정한다. 실제 Windows·모바일 실행과
컨테이너 Chromium/.NET 실행·교차 패키지를 구별한다.
