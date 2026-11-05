# V2: 기존 함수 시작점 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 442·526·547–548·778행(시작/실행 연결),
1267·1291행의 명시 저장·검토다. 기존 시작 포트와 선언된 노드를 사용하며 UI나
공개 입출력·override 계약을 새로 만들지 않는다.

## 재현과 지원 경계

게시본 `5f3d31e`의 생성 프로젝트에서 기존 직접 소유 root의 시작 노드를 바꾸고
checkpoint 쓰기를 실패시켰다. 일반 Save가 live entry를 바꾸고 개인 입력을 지워
재시작 때 원래 시작점만 복원됐다. checkpoint·물리 원본·C# bytes는 그대로였다.
수정 전 입력·실패·traffic·스크린샷·cold 결과를 보관한다. 원래 시작과 두 명시 선택의
native 실행도 먼저 확인하여 fixture와 기존 C# 의미가 유효함을 검증했다.

entry 전용 입력 하나를 기존 private 후보·checkpoint CAS·receipt·공유 Undo/Redo에
연결한다. 가상 시작점 `$entry`와 문자열 목적지를 가진 정확한 단일 편집만 허용하고,
기존 native entry/프로필 검증을 그대로 사용한다. 선언된 호출 노드도 시작 대상으로
선택할 수 있지만 호출 원본이나 다른 노드의 편집 권한을 부여하지 않는다.
원래 프로필이 허용하는 명시 해제는 빈 entry로 보관하며 임의 시작 노드를 넣지 않는다.
새 함수 생성·slot/copy/private/whole-body 전환·공개 분기/핀 계약·다른 입력과의 혼합은
이 단위의 새 지원이 아니다. 기존 경로의 지원/거절과 구분한다.

실패한 시도가 미반영이고 checkpoint·전체 source proof·물리 원본이 같은 경우에만
새 시작점으로 명시 재시도한다. 응답 유실은 같은 receipt로 판정하고 저장 중 새 선택은
분리해 보존한다. 변경 없는 반복 Save도 `ownedEntry` receipt를 보관한다. 기존 source/
name/route receipt는 유지하며 metadata 보관을 위해 사용자 graph/C#을 가짜로 바꾸지 않는다.
명시한 시작 선택만 실행 순서에 반영하고 ID·원문·핀/출력·다른 연결·권한·부모/외부 원본을
보존한다. 물리 원본 쓰기는 기존 Review→Confirm과 최종 CAS를 따른다.

관련 V2 저장 분리 안내 2문구·3곳을 “주십시오”로 맞춘다.
[정확한 delta](v666-entry-recovery-delta.json)는 로직·문체·canonical asset을 구분한다.
컴파일러의 원문 진단은 전역 번역하지 않는다.

## 별도 점검과 한계

저장 뒤 공유 draft history를 검증한다. 저장 전 모든 private Undo/Redo·포인터/터치·
문맥/프로젝트 왕복을 완료로 주장하지 않는다. root 핀/export·혼합 signature/description·
서로 다른 입력 혼합 등 다른 일반 Save는 별도 읽기 점검 후보다. 재현 없이 결함이나
새 필수 조합으로 확정하지 않는다. 완료 M11/M12/M4를 다시 열지 않는다.
나머지 V2, V3–V9·기존 팩/backend·종류 호환성 결정, 실제 Windows/모바일·전체 UI·Space
전달은 남는다. [검증 기록](VALIDATION_V666_ENTRY_RECOVERY.md)에 검사·보관·미실행을 구분한다.
