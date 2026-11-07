# V3 진행 중 도구 I/O 관측

원본 v666 `office-actors.js::workerActivity/createWorkerJob`의 실제 access 신호를 기존
명시 배정·현재 보이는 소유 대상에 연결한다. 별도 표시 팩과 이동/도착의 실행 독립성을
유지한다. 실제 DevelopmentTools의 승인된 읽기/inspect 및 초안 stage 호출 중만 표시한다.
`읽는 중`/`초안 처리 중`은 요청 처리 중인 관측이며 성공·최종 원본 쓰기·작업 완료가 아니다.

기존 도구 admission/chat-use 철회·직렬 mutation 잠금·원자 CAS/중복 호출/저장·원문/override
입출력 계약은 그대로다. 기존 Snapshot API도 변경하지 않는다. 새 read-only Observe는
같은 capability들을 즉시 TryEnter로 관측한다. 모두 비어 있을 때만 원래 Snapshot을 읽고,
하나라도 바쁘면 잠금을 기다리거나 부분 초안/provenance를 합치지 않는다. 이때 마지막 초안
관측에는 pending을 명시하고 새 완료 사실로 사용하지 않는다. 별도 immutable 메모리 문자열의
진행 신호만 읽는다. 필수 Review→Confirm·최종 원본 검증은 계속 기존 동기 Snapshot을 쓴다.

실제 소유/명시 target·권한 검사를 지난 read/inspect 또는 stage 경계에서만 진행 신호를
발행하고 finally에서 성공·충돌·예외 모두 해제한다. replay/거절은 새 신호를 만들지 않는다.
ProjectAI는 trusted origin의 project/task/worker와 hash를 대조하고 journal의 동일 이름 필드는
제거한다. 공개 DTO는 projectId/opaque receipt/1–256 ordinal/targetId/kind/phase뿐이다.
capability/call ID·원문·경로·origin hash·자격증명·시작/종료 시각이나 소요시간은 내보내지 않는다.

3D projection도 현재 프로젝트·보이는 Helper·실제 running Worker·명시 배정과 소유 root를
확인한다. 복수 대상은 자동 선택하지 않는다. actor/job snapshot은 불변이고 이동/좌석과
상관없이 실제 phase를 표시한다. 실패·취소·관측 철회/프로젝트 이탈·cold의 신호를 재생하지
않는다. 완료된 읽기/초안 결과는 기존 [마지막 완료 사실](V3_WORKSPACE_IO.md)로 구분한다.

현재 범위는 DevelopmentTools read/inspect·draft-stage 경계다. provider HTTP 대기, 일반
FileStream/사용자 C#·최종 채택/파일 쓰기를 진행 신호로 추정하지 않는다. UI 오류/늦은 입력과
기존 소유·권한·Review/Confirm/CAS는 보존한다. Run HD 이상 전송·GPU/FPS/요소 경계,
신원/권한·자산·참여자/대화, 실기기/전체 UI/Space 전달은 기존 고정 잔여다.
