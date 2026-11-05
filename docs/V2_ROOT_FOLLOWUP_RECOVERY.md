# V2: root 정의 저장 뒤 일반 본문 저장의 복원

기존 v666 root 핀 식별자 편집과 일반 C# 동작 편집을 순차로 사용하는 흐름이다.
기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 1196행 식별자 편집과 기존 C# 편집/Save 진입,
native `rootParameters`·`authorBatch`·명시 root 그룹 저장/복원 계약이다.
두 편집을 한 계획으로 합치는 새 기능이나 새 UI를 추가하지 않는다.

## 재현

게시본 `03af2ab3f3135792944c4d83ff19847125b34c3e`에서 입력 이름을 바꿨다가 원래
이름으로 돌아와 Save하면, 변경 파일이 없는 함수·구현·그래프 root 묶음과 receipt가 남는다.
이후 같은 그래프의 일반 C# 본문을 편집하고 Save하면 receipt가 `ownedSource`로 바뀐다.
기존 저장기는 그 그래프와 수정 본문만 내보내고 변경 없는 함수·구현 두 멤버를 빠뜨렸다.
개인 입력은 저장됐다고 처리돼 사라졌고, 재시작은 `Project workspace unavailable`로
실패했다. 물리 원본/C#은 그대로이며 불완전한 checkpoint와 입력·traffic·시작 로그를 보관한다.

처음 생성 fixture의 JSON 공백 차이는 실제 draft 변경이었다. native가 이미 쓰는 동일한
compact JSON으로 fixture만 맞춘 뒤 위 zero-dirty 경로를 재현했다. 의미·프로필·계약·
연결은 바꾸지 않았다. 예전 writer가 만든 실제 저장 형식을 대상으로 하는 검사다.

## 수정 경계

`packs/edit-workspace/Export.csbody`에서 기존에 보관하던 v1 author receipt 판정을
공통으로 사용한다. 같은 11개 flag·blueprint 종류·자기 graph ID 결합을 그대로 유지한다.
그 receipt 때문에 그래프를 보관한다면, 이미 있는 동일 root 그룹의 함수·구현 멤버도
함께 보관한다. 변경 있는 root 그룹을 보관하던 기존 조건은 그대로다.

새 편집/receipt 종류를 허용하거나 unknown ID·경로·외부 원본을 읽어 묶음을 만들지 않는다.
Restore·묶음/소유/경로 검증·원자 checkpoint CAS·Review→Confirm·최종 CAS·Undo 규칙,
타입/호출/override 계약·원래 ID/값/연결·권한·팝오버·문구·레이아웃은 바꾸지 않는다.
원래 C#은 명시적으로 편집한 본문만 Confirm 뒤 반영한다. 다른 C#과 부모/외부 원본은
보존한다.

후속 늦은 본문 검사에서는 cold 복원으로 revision만 달라진 개인 입력이 성공 receipt 뒤에도
이전 proof를 유지하여 다시 저장되지 않는 결함도 재현했다. 직접 소유 root의 단일 일반
C# 노드 source 저장에서만 기존 receipt 복구의 동일 원본 해시 판정을 사용한다. 정확한
저장 시도·두 번의 receipt 확인 뒤, 캡처한 같은 입력/노드/종류와 전체 소스 ID/해시가
일치해야 늦은 본문을 새 proof에 연결한다. peer 본문/누락 소스/다른 입력 proof는 허용하지
않고 private/copy/slot/whole-body 전달·혼합 저장으로 이 규칙을 넓히지 않는다.
화면/문구/레이아웃은 같으며 canonical UI 자산의 크기·SHA만 갱신한다.

정상 후속 저장·반복/변경 없는 저장·원래 본문으로 되돌린 저장 모두 완전한 그룹과 receipt를
복원한다. 누락·다른 그룹·경로/namespace·receipt 변조는 기존 검증으로 계속 거절한다.
이전 버전이 이미 만든 불완전한 checkpoint를 묵시적으로 재구성하는 정책은 추가하지 않는다.
그 증거와 원본을 보존하며, 자동 마이그레이션을 새 필수 요구로 만들지 않는다.

[정확한 delta](v666-root-followup-recovery-delta.json)와
[검증 상태](VALIDATION_V666_ROOT_FOLLOWUP_RECOVERY.md)를 따른다.

## 유한한 별도 점검

다른 root 정의·혼합 계약 Save·직접 배치는 원본 요구와 현재 지원을 대조할 별도 점검 후보다.
가능한 타입/문맥 조합마다 새 필수 요구를 추가하지 않는다. 완료 M11/M12/M4를 다시 열지
않는다. 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정과 실제 기기/전체 UI/Space
전달은 고정 수용 표에 남긴다. 새 권한·계정/외부 접근·live AI 호출은 사용하지 않는다.
