# V2: 기존 내보내기 출력 재배정 저장 실패 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 725·748–766행(기존 출력 선택과 연결),
1015–1017행(내보내기 카드), 1267·1291행의 명시 저장·완성 검사다.
기존 직접 소유 root의 기존 직렬 export 하나를 기존 출력에 재배정하는 경로다.

## 재현과 지원 경계

게시본 `c238022`에서 생성한 검증 프로젝트의 원래 실행을 실제 .NET으로 먼저 확인했다.
기존 출력 메뉴에서 left→right를 명시 선택한 뒤 checkpoint 쓰기를 실패시키면
live 대상은 바뀌고 개인 입력은 사라졌지만 checkpoint·물리 원본·C#은 그대로였다.
재시작 때는 원래 left만 남았다. 수정 전 원문·입력·실패 화면·요청·cold를 보관한다.

단일 `export-output`을 기존 원자 후보/checkpoint CAS·receipt·공유 Undo/Redo에 연결한다.
전송은 정확한 `$exports`/outputNodes와 단일 bind다. 원래 선언 출력·자료형·값·영역·
연결 검증을 재사용한다. 원래 값이 있는 정수 export를 bool 출력에 재배정하면 거절하고
명시 선택한 다른 입력은 유지한다. 자동 값 삭제·변환이나 새 출력 선언을 하지 않는다.

미반영과 동일 checkpoint·전체 source proof·원본을 확인한 뒤에만 새 출력 선택으로
명시 재시도한다. 응답 유실은 receipt로 판정하며 늦은 선택은 분리 보관한다. 이전
선택은 재전송하지 않는다. 변경 없는 반복 Save도 `ownedOutputBinding` receipt를
보관하며 원문을 가짜로 바꾸지 않는다. 기존 value/source/name/route/entry receipt와
C# bytes·ID·입출력/override 계약·순서·값·다른 연결·부모/외부 원본·권한을 보존한다.
물리 쓰기는 기존 Review→Confirm과 최종 CAS 뒤에서만 한다.

검증 fixture의 미배정 출력 기본값은 기존 implicit-out 프로필의 원래 의미이며
Core 코드·출력 기본값 정책을 변경하지 않는다. 실제 재배정한 출력에만 17이 발행되고
다른 출력은 원래 프로필의 값을 유지하는지 확인한다.

출력 선택·다른 자료형 거절 안내 2문구·2곳만 문체를 정리한다.
[정확한 delta](v666-export-binding-recovery-delta.json)는 로직·안내·canonical metadata를
구분한다. 원본 메뉴·레이아웃이나 backend 원문 진단을 전역 변환하지 않는다.

## 별도 점검과 한계

완료한 export 값 저장은 재구현하지 않고 회귀를 검증한다. export 생성/삭제·여러
구조 입력 혼합·root 핀·종료점 값·혼합 계약 및 slot/copy/private/whole-body는 별도 읽기
점검 후보다. 재현 없이 결함·정상 금지·새 필수 조합으로 단정하지 않는다. 저장 전
모든 private Undo/Redo·포인터/터치·문맥/프로젝트 왕복·전체 UI 완료를 주장하지 않는다.
완료 M11/M12/M4는 조합별 잔여로 다시 열지 않는다. 나머지 V2·V3–V9·기존 팩/backend·
종류 호환성 결정·실제 Windows/모바일·전체 UI·Space는 별도 잔여다.
[검증 기록](VALIDATION_V666_EXPORT_BINDING_RECOVERY.md)에 신규·재사용·미실행을 구분한다.
