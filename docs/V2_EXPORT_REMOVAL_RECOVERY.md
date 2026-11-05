# V2: 기존 내보내기 노드 삭제 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 947·1017·1021행의 기존 노드 삭제 UI와 현재
native `outputNodes/remove` 계약이다. 직접 소유 root의 기존 직렬 export 하나를
삭제하는 흐름만 다룬다. 출력 선언 삭제나 새 핀/타입/계약 편집과 구별한다.

## 재현과 구현

게시본 `3b6191591fd920678d4c9e0458f8703deead4277`의 생성 프로젝트에서 기존 삭제
버튼을 누르고 checkpoint 쓰기를 실패시켰다. live 노드가 사라지고 개인 삭제 입력은
지워졌지만 checkpoint와 물리 원본은 같았다. 재시작 후 노드는 돌아오고 삭제 선택은
없어졌다. 원래 실제 .NET 실행, 실패 화면·입력·traffic·cold 증거를 개발 record에 보관한다.

단일 `export-remove`를 정확한 `$exports`/`outputNodes`의 단일 remove 후보로 직렬화하여
checkpoint CAS·receipt·공유 Undo/Redo와 연결한다. 후보에서 기존 native 삭제·graph 검증을
그대로 실행하고 저장 성공 후 live에 반영한다. 기존 export인지와 직접 소유 root 여부를
검증한다. 여분 필드·누락/비문자열 ID·다중 삭제·본문/계약 혼합·slot/private/copy 문맥은
이 허용을 빌려 쓸 수 없다. 노드가 없어진 뒤에도 원래 요청을 같은 형태로 직렬화하므로
응답 유실 시 receipt를 회수할 수 있다. 없는 노드의 새 삭제 요청을 성공으로 바꾸지는 않는다.

미반영 삭제 journal에 다른 새 입력이 생기면 기존 live 직접 수정 경로로 우회하지 않고
두 입력을 보존하며 저장을 거절한다. 새로운 혼합 저장 정책은 정하지 않는다. 삭제가 이미
반영된 경우에는 정확한 receipt 확인 뒤 늦은 입력만 별도 보존·재시도한다. 적용된 삭제는
재전송하지 않는다. 저장 전 개인 삭제 Undo/Redo와 저장 후 공유 Undo/Redo를 구분한다.

기존 삭제의 entry/실행선 우회 규칙과 해당 profile의 out 기본값 의미를 유지한다.
다른 노드·남은 출력값·ID·C# bytes·공개/override 입출력 계약·profile·권한·부모/외부
원본을 보존한다. 물리 쓰기는 기존 Review→Confirm과 최종 CAS 뒤에서만 한다.
원본 팝오버·레이아웃·문구와 완료된 값/재배정/root 반환 저장 복구를 보존한다.
[정확한 delta](v666-export-removal-recovery-delta.json)와 [검증 상태](VALIDATION_V666_EXPORT_REMOVAL_RECOVERY.md)를 따른다.

## 유한한 별도 점검과 한계

root 핀 정의·export 생성/구조 혼합·혼합 계약 Save는 별도 읽기 점검 후보다.
재현 없이 새 필수 조합이나 결함으로 단정하지 않는다. 완료 M11/M12/M4를 다시 열지 않는다.
나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정·실제 Windows/모바일·전체 UI·Space는
수용 표에 남긴다. 이번 검사는 생성한 프로젝트를 사용하며 개인/외부 자료를 업로드하지 않는다.
