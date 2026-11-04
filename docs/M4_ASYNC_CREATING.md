# M4: 새 ordinary C# 동작의 첫 Confirm 전 비동기 전환

기준은 저장소 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`blueprint.js` 동작 메뉴와 `docs/V666_ACCEPTANCE.md`의 고정 M4 흐름이다.
확정된 직접 소유 Root에 추가한 ordinary C# 동작도 파일을 먼저 확정하지 않고
기존 async 메뉴·코드 편집·Save·Review→Confirm으로 연결한다. 새 디자인이나
C# 자동 변환은 추가하지 않는다.

이번 경계는 기존 직접 소유 함수/구현/graph와 그 graph에 초안으로 추가된 새 leaf다.
기존 생성 API는 파일 없이 `baseline: missing`, 빈 원본과 빈 코드,
0으로 채운 definition hash를 가진 record를 만든다. 이전 async 소유 검사는
모든 `missing`을 거절했으므로 생성 초안을 저장해도 전환 메뉴를 사용할 수 없었다.

이제 기존 graph의 원본 hash·소유 함수, 현재 노드의 정확한 ID·상대 경로,
원본 graph에 그 ID와 코드 경로가 모두 없다는 증거를 검사한다. 새 노드 record만
예외로 허용하며 헤더·graph·이미 존재한 ID/경로에는 적용하지 않는다.
빈 새 record의 placeholder만 현재 정의 hash로 묶고 C#은 비워 둔다.
작성된 원문은 이전 정의와 일치해야 하며 source/helpers를 재작성하지 않는다.

동일한 증거와 `missing` 조건은 전환 영수증, cold 복원, 전체 Review와 최종 CAS에
남는다. 다른 파일이 나타나면 Confirm 전체를 거절하고 상대 파일 및 초안을 보존한다.
물리 파일 생성은 전체 Confirm에서만 수행한다. 사용자 C#은 기존 Task 편집기의
고정 서명을 통해 명시적으로 작성하고 실제 await 뒤 다음 동작을 실행한다.

## 유한한 후속 경계

- 새 함수/구현/graph를 함께 만드는 흐름: 아직 새 헤더까지 이 예외를 적용하지 않는다.
- 직접 소유 private/internal graph의 전환: 현재 Root 전환은 private Task 소유 및
  호출자 연결을 처리하지 않는다. 내부 구현 편집과 공개 override 계약 변경을 구별한다.
- 새 동작의 첫 생성 초안 Save 전 전환 입력을 다른 생성 입력과 함께 다루는 경계는
  현재 UI의 입력 분리 제한이다. 추가 Save를 영구 UX 정책으로 확정하지 않는다.

M11/M12를 다시 미완료로 열거나 legacy 자동 migration, 부모/참조 직접 편집,
임의 타입/문맥 조합을 새 수용 요건으로 늘리지 않는다. 동기 호출자는 명시 async
전환 전까지 오류이며 자동 대기/변환하지 않는다. 원문·권한·팝오버/레이아웃과
최신/롤백/증거 수명은 기존 계약을 유지한다.
