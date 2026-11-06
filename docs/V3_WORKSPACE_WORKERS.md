# V3 실제 Worker 상태 표시

사용자 지정 v666 ZIP의 `dist/office-actors.js`는 Worker 신호로 작업 snapshot을 만들고,
`dist/office.js`는 작업 상태와 캐릭터 동작을 별도로 표시한다. 원본 주석도
“Walking, reporting and seat availability never advance it.”라고 명시한다.
[기존 3D 보기](V3_WORKSPACE_VIEW.md)의 별도 표시 팩에 기존 B2 공개 관측을 연결했다.
팩 README의 첫 지원 단계 이후 현재 상태는 이 문서를 우선한다.
새 실행·배정·권한 정책이나 시연 Worker를 만들지 않는다.

활성 ProjectContext의 `assignmentWorkers`와 기존 `visibleParticipantHelpers()`를 사용한다.
기존 프로젝트 소속/Agent 가시성 필터를 통과한 Helper의 ID와 이름만 전달하며 personality,
개인 기억·연결 자격증명은 전달하지 않는다. 공개 관측의 프로젝트/Helper/Worker ID와
정상 상태를 다시 확인하고, 다른 사용자/프로젝트·가려진 Helper·잘못된 기록은 표시하지 않는다.
native 관측의 전체 64자리 ID를 actor key와 갱신 식별에 보존하며 화면 이름만 짧게 표시한다.

| 기존 native 상태 | 작업 표시 |
|---|---|
| ready | 배정 대기 |
| dispatching | 실행 준비 중 |
| running | 작업 중 |
| awaiting-verification | 완료 검증 대기 |
| completed | 완료 |
| cancelled | 취소됨 |
| interrupted | 중단됨 |
| error | 오류 |

기존 `needsCheck`는 `실행 확인 필요`로 표시한다. 실행 완료 시각과 진행 중 IO phase는
추정하지 않는다. 마지막 실제 read/stage 완료는 [후속 연결](V3_WORKSPACE_IO.md)을 따른다. 내부 시각 분류가 여러 native 상태를 묶어도 원래
상태/ID와 위 문구는 보존한다. `assignedNode`/`assignedSourceIds`가 같은 직접 소유 root를
가리킬 때만 기존 대상 이름과 방을 연결한다. 복수 대상이나 외부/알 수 없는 대상에서
이름 추측·자동 대상 선택·외부 경로/원문 읽기를 하지 않는다.

작업 snapshot은 불변이며 이동/도착·자리와 독립적이다. Helper 도착 전에도 실제 Worker
상태를 표시하고 3D를 끈 동안에도 기존 실행은 계속된다. 이 연결은 레거시 window 활동
이벤트를 실제 관측으로 채택하지 않는다. `canInspectTask`는 이미 공개된 현재 DTO의 표시
일치를 확인할 뿐 native 권한을 부여하지 않는다. 개인 배치의 canArrange/canWrite는 [후속](V3_PRIVATE_ARRANGEMENT.md)에 연결하며 source 권한을 부여하지 않는다. canChat은 false다.
실제 배정·승인·실행·Review→Confirm·채택·취소는 기존 경로만 사용한다. source·C# bytes·
계약/override IO·CAS/Undo/입력 보존이나 작업 journal 저장 코드는 변경하지 않는다.

현재 관측의 내용/가시성이 바뀌면 열린 상세 메뉴를 폐기하고, 철회된 actor의 추적도 해제한다.
일부 journal을 읽을 수 없으면 기존 부분 관측만 표시하고 안내한다. 읽기 때문에 owner를
열거나 journal을 복구/재저장하지 않는다. 홈/다른 프로젝트/폐기한 화면에는 이전 신원을
남기지 않으며, 새 엔진의 중단 기록도 기존 native 읽기 의미대로 표시한다.
Helper 상세는 실제 객체형 Worker와 원본 배열형을 모두 읽고, 확인된 작업 수와 실제 상태를
표시한다. 움직이는 actor의 원본 메뉴·레이아웃을 유지하며 기존 버튼의 키보드 조작도 사용한다.

마지막 실제 read/stage 완료 신호는 위 후속에 연결했다. 진행 중 IO phase는 native 제공
경계가 없어 완료 사실과 구분한다. 개인 배치·확정 전
snapshot 분리·root/child 격리는 위 후속으로 연결했다. 자식 Workspace의 다른 원본 조작은
기존 지원 대조/검증 대상이며 조합마다 새 필수 기능을 늘리지 않는다. 없는 신호를 쓰기 연출로 대체하지 않는다. V4/V5의 별도 신원/권한·가시성
backend, V6 자산 저장과 V7 미리보기, V8 Run 영상·오디오 backend 및 V9 참여자/대화 연결은
각 고정 행에 남는다. M11/M12/M4는 새 회귀 없이 재개하지 않는다. 실제 Windows/모바일·
전체 UI·Space/Library 전달 완료를 뜻하지 않는다.

[검증·패키지·공간 기록](VALIDATION_V666_OFFICE_WORKERS.md)을 따른다.
