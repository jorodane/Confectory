# V3 개인 3D 작업실 배치

사용자 지정 v666 ZIP의 `dist/app.js`는 원본 배치 버튼, `owner:()=>workspaceRecord()`와
`workspaceId:()=>activeWorkspaceId`를 제공한다. `dist/office.js`의 배치 카탈로그·Confirm/
취소·30개 지역 Undo/Redo·충돌 검사를 별도 표시 팩과 기존 private presentation에 연결한다.
버튼은 원본 SVG/문구와 검색 다음 순서를 사용하며 CSS·방/가구 형상은 변경하지 않는다.
팩 README의 첫 읽기 전용 연결 배경보다 현재 지원이 넓으며, 현재 변경 경계는 이 문서와
정확한 제품 delta를 우선한다.
배치 중 dock/확대에 따른 라벨 숨김도 원본대로 유지한다.

공유 선언이나 실행 데이터의 편집이 아니다. 현재 활성 ProjectContext의 개인 Workspace가
복구 완료 상태일 때만 배치를 열며, 소유 선언과 renderer의 고정 표시 대상의 geometry만
다룬다. bridge의 canArrange/canWrite는 개인 표시 배치 검사이며 source 쓰기나 ACL grant를
뜻하지 않는다. prototype의 demo projectAccess나 권한 팩 부재를 source allow-all로 채택하지
않는다. 기존 native 개인 presentation의 프로젝트 정체성·view/revision·크기 검사·원자 쓰기를
그대로 사용하고, C# 원문·공개/override 계약·연결·부모/외부 원본·source 권한·Review→Confirm/
CAS와 기존 입력/공유 Undo 계약은 변경하지 않는다. Worker 실행/승인 API를 추가하지 않는다.

카탈로그에서 가구를 고르고 실제 바닥에 놓아 충돌을 검사한다. 같은 배치 모드에서 원래
Undo/Redo·취소·배치 확정을 사용한다. Confirm/Cancel 후 지역 이력 초기화도 원본 의미다.
개인 배치 확정은 source Review/Confirm을 대신하지 않는다. 방/가구/표지판 등의 원본 도구는
private officeLayout만 변경하며, 원래 ID와 별개인 개인 가구 ID를 source ID로 등록하지 않는다.

편집 중 원본 renderer는 메모리의 geometry를 바꾸므로, 다른 자동 저장에 미확정 배치가
섞이지 않도록 최종 snapshot을 분리했다. 편집 중에는 arrangeSnapshot, 개별 변형 미리보기는
actionHandle.before의 rooms/stations/storages/decorations/signs/cleaners/props만 저장 후보에
덮는다. 카메라·다른 개인 metadata/편집 입력은 최신값을 유지하며 현재 메모리나 원래 snapshot을
변경하지 않는다. 확정 이후만 새 geometry를 저장하고, 쓰기 실패는 확정 메모리와 기존 파일을
보존해 재시도한다. 미확정 배치의 crash/cold draft 복원을 약속하지 않으며, 명시 저장한 확정
geometry만 복원한다. 기존 source 입력 복구와 별도다.

같은 Workspace의 패널 전환은 원본처럼 메모리 배치를 잠시 보존하되 저장에서는 제외한다.
다른 Workspace/프로젝트로 바꾸거나 renderer를 폐기하면 미확정 geometry를 원래 확정값으로
되돌리고, 이전 Confirm/색상/문구 callback은 현재 owner를 변경하지 못한다. root와 child의
officeLayout은 각각의 실제 private record에 귀속한다. 같은 프로젝트의 방 읽기는 원본처럼
프로젝트 선언을 사용하며 하위 Workspace 생성·모든 포털/창 편집을 새로 구현했다고 세지 않는다.

이동·도착과 Worker snapshot/실행은 계속 분리한다. 이미 완료된 [실제 Worker 관측](V3_WORKSPACE_WORKERS.md)
과 [읽기 전용 3D 기반](V3_WORKSPACE_VIEW.md)을 보존한다. 별도 권한 팩·공유 신원/세션 backend,
개별 read/write 신호, 리소스 저장/미리보기·Run 영상/오디오 backend와 그 밖의 고정 잔여는
[수용 목록](V666_ACCEPTANCE.md)에 남는다. 가능한 가구/모양/문맥마다 새 필수 기능을 늘리지 않는다.

[최종 검증·보관·실제 검증 한계](VALIDATION_V666_OFFICE_ARRANGEMENT.md)를 따른다.
