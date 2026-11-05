# V2: 새 내보내기·값·수동 실행선 첫 저장 복구

기준은 보관된 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 1236–1250행 `addNode/export`와 기존 native
`outputNodes` 계약이다. 직접 소유 root에서 이미 선언된 출력에 export 하나를 만들고
값을 입력하며 기존 ordinary code의 next 선을 명시적으로 해제한 뒤 새 카드 양쪽을
수동 연결하는 현재 지원 UI를 다룬다. 공개 출력 선언이나 override 계약은 바꾸지 않는다.

## 재현·지원 경계

게시본 `f813c5780de4930feed67e5d62187f3f016de65a`의 생성 프로젝트에서 이 네 입력을
만든 뒤 checkpoint 쓰기를 실패시켰다. live에는 새 노드가 생겼지만 네 개인 입력은
사라졌고 checkpoint·물리 원본·C# bytes는 같았다. 재시작 후 새 노드·값·연결 선택을
모두 잃었다. 원래 실제 .NET 실행, 실패 화면·입력·traffic·cold를 개발 record에 보관한다.

생성 1·새 노드 값 1·기존 code→새 노드 및 새 노드→원래 next 목적지 2를 정확한
네-row `outputNodes` 후보로 직렬화한다. 새 ID·직접 소유 ordinary code·관측한 기존
next 목적지를 확인하고 기존 native ID/출력/값/graph 검증을 후보 안에서 재사용한다.
CAS 체크포인트 저장 성공 뒤 live에 반영한다. 기존 노드의 값/다른 연결·추가 생성·공개
계약·본문·slot/private 소유 권한을 이 허용으로 변경할 수 없다.

응답 유실은 원래 ID와 계획의 receipt로 확인한다. 이미 생긴 노드를 다시 만들거나
실행선을 다시 적용하지 않는다. 미반영·동일 checkpoint·전체 source proof가 확인될
때에만 같은 ID/출력/양쪽 연결을 보존한 새 노드 값 수정의 명시 재시도를 허용한다.
적용 후 늦은 값은 독립 보관하고 기존 값 전용 원자 Save로 넘긴다. 미반영 계획에 다른
노드의 새 입력이 섞이면 모든 입력을 보존하며 거절하고 live 직접 수정으로 우회하지 않는다.

생성 직후의 기존 개인 Undo/Redo, 후속 값/연결 때문에 이전 개인 Undo를 멈추는 보호,
저장 후 전체 묶음의 공유 Undo/Redo를 구분한다. 공개/override 계약·기존 C# 원문/ID·
남은 출력과 profile·권한·부모/외부 원본·Review→Confirm·최종 CAS를 유지한다.
기존 팝오버·레이아웃·문구는 변경하지 않는다. [정확한 delta](v666-export-creation-recovery-delta.json)와
[검증 상태](VALIDATION_V666_EXPORT_CREATION_RECOVERY.md)를 따른다.

## 별도 점검과 한계

현재 실행선 메뉴의 export 자동 배치는 미연결 거절 경계이며 이번에 연결하지 않는다.
이를 새 영구 UX 정책으로 정하지 않는다. 재현에는 지원되는 캔버스 생성·명시적 선 해제와
수동 연결을 사용했다. 자동 배치·다른 생성/구조 혼합·root 핀 정의·혼합 계약 Save는
원본 요구와 현재 지원을 대조할 별도 점검 후보다. 조합마다 새 필수 요구를 추가하지 않는다.
완료 M11/M12/M4를 다시 열지 않는다. 나머지 V2·V3–V9·팩/backend·종류 호환성 결정·
실제 Windows/모바일·전체 UI·Space 전달은 고정 수용 표에 남긴다.
