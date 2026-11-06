# V3 소유 프로젝트의 3D 보기

사용자가 지정한 v666 ZIP의 `office.js`, `office-world.js`, `office-actors.js`,
`voxel-character.js`, Three.js와 라이선스를 별도 `Confectory.Workspace3D` 팩에 연결했다.
출처는 [고정 수용 목록](V666_ACCEPTANCE.md), 자산별 원본 SHA는
[`UPSTREAM.json`](../packs/workspace-3d/ui/UPSTREAM.json)에 기록한다.
원본의 방/보관함·카메라·지도·보기 전환 조작과 CSS를 재사용한다.

실제 활성 ProjectContext의 기존 local inventory/관계 읽기에서 `owned === true`인 선언만
기존 ID로 표시한다. 분류는 기존 Browser 부모 관계로 연결한다. 지도/방 메뉴의 카테고리
열기는 기존 Browser와 권한 검사를 사용한다. 별도 시연 프로젝트나 Worker를 만들지 않는다.
패널을 기본으로 유지하며 명시적 3D 선택과 카메라/미니맵은 기존 프로젝트별 private
presentation에만 저장한다. 이미 저장된 3D 선택은 새 엔진에서도 복원한다.

표시는 실행·source 저장·Review/Confirm·권한 판정과 독립적이다. 3D 위치·도착을 작업 시작,
완료, 잠금이나 허용 조건으로 사용하지 않는다. 표시 팩에는 작업 dispatch나 ACL 판정 API가
없다. 현재 개인 배치의 canArrange/canWrite는 [후속 private 경계](V3_PRIVATE_ARRANGEMENT.md)를 따르며 source 권한을 부여하지 않는다. canChat은 false다. 이미 공개된 현재 Worker DTO의
표시 일치만 확인하는 `canInspectTask`와 실제 상태 adapter는 [후속](V3_WORKSPACE_WORKERS.md)에
연결했다. 권한 grant를 만들지 않으며 실제 read/stage 완료는 [후속 연결](V3_WORKSPACE_IO.md)을 따른다. 개인 배치는 위 후속으로 연결했다. 별도 권한 팩의 미구현을
allow-all로 대체하지 않는다.

자산은 pack의 고정 manifest와 전체 SHA/크기를 검증하고 LF로 정규화한 bounded inline
WebUI 리소스로 전달한다. 외부 CDN/개인 파일 업로드를 사용하지 않는다. 자산 누락·변조면
선택적 3D bundle을 제공하지 않으며 기존 편집기는 유지한다. WebGL을 사용할 수 없거나
context가 손실되면 기존 패널로 복귀하고 개인 배치/입력을 보존한다. 폐기/다른 프로젝트의
모듈 응답·확대 열기/입력 callback은 현재 방이나 카메라를 변경하지 않는다.

기존 원본 C#·값·설명·부모/외부 source·공개/override 계약·권한·CAS·Undo·Review/Confirm
경계는 변경하지 않는다. 원본의 읽기/쓰기·이동 연출 전체와 자식 Workspace의 모든 배치
조작을 완료로 표시하지 않는다. V3의 진행 중 IO phase 구분과 하위 Workspace의 기존 지원 대조/전체 UI 검증, V4/V5의 신원/가시성,
V6/V7의 자산 저장·미리보기, V8의 실제 Run 화면·오디오는 [기존 목록](V666_ACCEPTANCE.md)에
남는다. 이 WebGL 방 보기는 프로젝트 Run 렌더러나 오디오 backend의 구현이 아니다.

[최종 검증과 보관](VALIDATION_V666_OFFICE_VIEW.md)을 따른다.
