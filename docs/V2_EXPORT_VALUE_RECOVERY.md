# V2: 기존 내보내기 값 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 1015–1017행(내보내기 카드와 값 입력),
1054–1061행(원래 값 편집), 1267·1291행의 명시 저장·완성 검사다.
새 UI를 만들지 않고 기존 직접 소유 root의 기존 직렬 export 값 하나를 다룬다.

## 재현과 범위

게시본 `6b70043`에서 기존 내보내기 카드의 값 메뉴로 정수 37을 선택한 뒤
checkpoint 쓰기를 실패시켰다. 기존 outputNodes 호출은 live 값을 바꾸고 개인
입력을 지웠지만 checkpoint는 갱신되지 않아 재시작 뒤 원래 연결만 남았다.
수정 전 입력·요청·실패 화면·cold 결과를 보관한다. 먼저 사용한 분기 fixture는
기존 실행 영역 검증에서 거절돼 입력이 보존됐으므로 유실 재현으로 세지 않는다.
그 영역 규칙은 이번에 변경하지 않는다.

단일 `argument:value`가 가리키는 기존 직접 소유 root export를 원자 후보/checkpoint
CAS·receipt·공유 Undo/Redo에 연결한다. 전송은 정확한 `$exports`의 outputNodes와
정확한 단일 value 편집뿐이다. 기존 outputNodes의 표현식·선언 자료형·실행 영역·
연결 검증을 그대로 사용한다. C# 노드의 일반 argument 권한으로 export를 우회하지 않는다.
public/override 입출력·아이콘·출력 이름·ID·순서·분기·연결·C# bytes·권한은 그대로다.

실패가 미반영이고 checkpoint·전체 source proof·원본이 동일할 때만 새 값으로 명시
재시도한다. 응답 유실은 receipt로 판정하고 늦게 입력한 값은 분리해 보존한다.
변경 없는 반복 Save도 `ownedOutputValue` receipt를 보관하고 사용자 파일을 가짜로
바꾸지 않는다. 기존 source/name/route/entry receipt는 유지한다. 물리 원본 쓰기는
기존 Review→Confirm과 최종 CAS 뒤에서만 한다.

관련 저장 분리 안내 한 문구·한 지점만 “주십시오”로 정리한다.
[정확한 delta](v666-export-value-recovery-delta.json)는 제품 로직·안내·자산 metadata를
구분한다. backend 원문 진단이나 원본 레이아웃은 전역 변환하지 않는다.

## 별도 점검과 한계

export 생성/삭제/출력 재배정/실행선 혼합, root 핀·export 없는 종료점 값·혼합 계약
및 slot/copy/private/whole-body 문맥은 기존 지원·거절 경계를 유지한다. 이번 단위의
새 지원이나 재현 없는 결함으로 세지 않는다. 저장 전 모든 private Undo/Redo·포인터/
터치·문맥·프로젝트 왕복과 전체 UI를 신규 검증했다고 주장하지 않는다.
기존 완료 M11/M12/M4는 조합별 잔여로 다시 열지 않는다. 나머지 V2·V3–V9·기존
팩/backend·종류 호환성 결정·실제 Windows/모바일·전체 UI·Space는 별도 잔여다.
[검증 기록](VALIDATION_V666_EXPORT_VALUE_RECOVERY.md)에 신규·재사용·미실행을 구분한다.
