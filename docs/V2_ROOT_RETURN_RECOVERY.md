# V2: 기존 root 반환 출력 핀 값 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의 root 출력 핀과
값 메뉴(`dist/blueprint.js` 1015–1017·1054–1061·1267·1291행), 기존 native
`v508_feature_serial_engine.py`의 `$exit:return` 값 선택·저장 경로다.
기존 직접 소유 ordinary nonvoid root의 반환 출력 핀 값 하나를 다룬다.
공개 핀 정의·이름·타입·순서·override 계약을 편집하는 단위가 아니다.

## 재현과 범위

게시본 `f37c062`의 생성 프로젝트에서 원래 실행을 실제 .NET으로 확인한 뒤, 기존
반환 값 메뉴로 정수 37을 선택하고 checkpoint 쓰기를 실패시켰다. live 값은 바뀌고
개인 입력은 지워졌지만 checkpoint·물리 원본·C# bytes는 그대로였다. cold에서는
원래 호출 출력 연결만 복원됐다. 수정 전 입력·실패 화면·traffic·cold·실행을 보관한다.

단일 `exit`/`$exit:return` 입력을 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo로
연결한다. 정확한 return 이름과 문자열 표현식만 허용하며 기존 반환 값·자료형 검증을
재사용한다. ordinary nonvoid root이며 return 종료점이 있고 return export 작성자가
없는 문맥만 새로 연결한다. void·실행 분기 종료·export 작성자·slot/copy/private 문맥이
이 허용을 빌려 쓰지 못한다. 원래 지원/거절은 그대로이며 새 정책으로 확대하지 않는다.

미반영과 동일 checkpoint·전체 source proof·원본이 확인된 경우에만 새 값으로 명시
재시도한다. 응답 유실은 receipt만 회수하며 늦은 입력은 별도 보관한다. 이전 값은
재전송하지 않는다. 변경 없는 반복 Save도 `ownedRootReturn` receipt를 보관하고 원문을
가짜로 바꾸지 않는다. 기존 export binding/value·source/name/route/entry의 보호를 유지한다.

반환 값만 명시 선택대로 바꾸며 C# bytes·ID·핀 정의/타입/순서·공개/override 계약·
profile·다른 연결·권한·부모/외부 원본을 보존한다. 물리 쓰기는 기존 Review→Confirm과
최종 CAS 뒤에서만 한다. 새 문구나 UI를 추가하지 않고 기존 안내·값 메뉴·레이아웃을
유지한다. [정확한 delta](v666-root-return-recovery-delta.json)는 로직·canonical metadata를 구분한다.

## 별도 점검과 한계

root 핀 정의·다른 종료점 문맥·export 생성/삭제·구조 입력 혼합·혼합 계약 저장은 별도
읽기 점검 후보다. 재현 없이 결함·정상 금지·새 필수 조합으로 단정하지 않는다.
저장 전 모든 private Undo/Redo·포인터/터치·문맥/프로젝트 왕복·전체 UI 완료를 주장하지
않는다. 완료 M11/M12/M4를 조합별 잔여로 다시 열지 않는다. 나머지 V2·V3–V9·기존
팩/backend·종류 호환성 결정·실제 Windows/모바일·전체 UI·Space는 별도 잔여다.
[검증 기록](VALIDATION_V666_ROOT_RETURN_RECOVERY.md)에 신규·재사용·미실행을 구분한다.
