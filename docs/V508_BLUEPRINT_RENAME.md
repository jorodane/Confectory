# v508 내부 함수 표시 이름

사용자가 확정한 규칙은 “표시 이름 자체는 완성 상태에 영향이 없게”다. v508 시안의 `definition.name`/build stamp 연결을 그대로 옮기지 않고, 기존 graph node에 선택적 `displayName`을 저장한다. 이전 자료는 ID를 표시 이름으로 사용하며 읽기만으로 파일·profile을 바꾸지 않는다. 이름은 앞뒤 공백과 제어 문자가 없는 1–256 UTF-16 문자다. 한글을 포함한 일반 문자열을 허용한다.

## 저장과 실행 의미

일반 소유 내부 code/graph 함수의 Rename을 기존 `PackWorkspace.Blueprint` 명령과 전체 관찰 원본 CAS에 연결했다. 참조 함수·전체 본문 context/호출자 저장소 전달 노드의 계약 이름은 이 경로에서 바꾸지 않는다. 이름만 바꿔도 graph의 원문 hash/revision은 바뀌므로, 과거 basis나 동시에 바뀐 graph·본문·계약에 대한 요청은 거부한다. 적용 후 초안 저장과 별도 compiler Review/Confirm으로 프로젝트에 반영한다.

표시 이름은 안정 node/function ID, 인수·출력·분기 순서, 의도 설명, C# 심볼과 ABI에 포함하지 않는다. 중첩 graph의 부모 정의 및 독립 node probe의 graph hash에서도 선언된 node 위치의 `displayName`만 제외한다. 같은 단어를 쓰는 매개변수·local·property·실행 enum 이름은 계속 의미를 가진다. 표시 이름이 없는 기존 graph의 해시는 그대로다.

기존 semantic definition/body/topology와 생성 코드가 같으면 컴파일 artifact를 재사용한다. 새 빌드 영수증은 그때 읽은 실제 파일 hash를 기록하며 raw 관찰 검사를 우회하지 않는다. 이름 변경은 본문 stamp나 완료 기록을 새로 쓰지 않는다. 의도/계약 변경으로 stale이 된 본문, 잘못된 C#은 이름을 바꾼 뒤에도 재검토·컴파일이 필요하다. 구조상 source available과 실제 compilerValidated는 기존과 같이 구분한다.

## 편집 동작

막대를 끌면 기존 private 배치가 움직인다. 이미 선택한 함수의 이름 클릭, F2, 막대의 `Rename · F2` 메뉴로 표시 이름을 편집한다. 최초 클릭은 선택하고, 이동한 pointer gesture는 Rename을 열지 않는다. Enter 또는 ✓는 공유 초안 적용, Escape·×·빈 이름은 해당 이름 입력 취소다. 한글 조합 중 Enter와 keyCode 229는 적용하지 않는다. 반복 클릭/F2는 입력을 초기화하지 않는다.

포커스를 옮기면 미제출 이름을 보존한다. graph/프로젝트 전환이나 재시작으로 자동 적용하지 않는다. 이름 입력은 프로젝트·graph·안정 ID에 귀속된다. 다른 미적용 본문·의도·외부 editor 입력과 함께 있을 때 적용을 거부하고 둘 다 보존한다. CAS 실패도 입력을 유지한다. 현재 원본 읽기 후 ↻ 기준 재검토와 별도 적용이 필요하며, cold 입력은 과거 basis를 재사용하지 않는다.

## 검증

이 단위의 최종 source, 실행 메서드와 로그는 `validation/v508-blueprint-rename.json`에 기록한다. 일반 EditorHome의 실제 Chromium 검사, .NET 컴파일/실행 및 Windows managed 구성·Android export 검사를 구분한다. 실제 Windows OS·Android 기기에서 새 Rename을 실행한 검증은 포함하지 않는다.

main, 원본 ZIP, Android 설정, CSP/권한, overflow, async/wrapper/공개 출력 실행 의미와 기존 parameter 정렬은 이 단위 범위 밖이다.
