# V3 실제 도구 완료 신호

저장소 v666 ZIP `dist/office-actors.js`의 `workerActivity`/`createWorkerJob`은 Worker의
access 신호와 작업 snapshot을 표시하고 이동·도착을 실행 조건과 분리한다. 이 연결은
[실제 Worker 상태](V3_WORKSPACE_WORKERS.md)의 기존 표시 팩에 실제 native 도구 결과를 더한다.
원본의 명칭/위치 문자열이나 시연 활동을 실행 증거로 채택하지 않는다. 원래 UI/CSS/메뉴·
배치와 source/override 입출력 계약은 그대로다.

실제 DevelopmentTools 호출이 기존 project/namespace/소유·node source hash·권한을 통과하고
성공했을 때만 마지막 완료 결과를 capability의 메모리 model에 기록한다.

| 실제 결과 | 기존 상태 문구에 추가하는 표시 |
|---|---|
| workspace_read/inspect 성공 | 최근 읽기 완료 |
| workspace_stage CAS 성공·내용 변경 | 최근 초안 변경 확인 |
| workspace_stage CAS 성공·동일 내용 | 최근 초안 동일 확인 |

stage는 공유 **초안**의 변경이며 최종 source 파일 쓰기를 뜻하지 않는다. 실제 원본 채택은
기존 명시 Review→Confirm·컴파일/최종 CAS를 계속 거친다. 거절·CAS 충돌·실패/불확실 결과나
중복 call ID replay는 새 완료 신호를 만들지 않는다. 기존 마지막 성공 사실은 유지할 수 있으나
현재 작업 성공이나 진행 중인 IO로 표현하지 않는다. list/changes/create와 최종 채택은 이
read/stage 완료 연결의 신호로 추정하지 않는다.

ProjectAI는 실제 열려 있는 Worker capability의 project/task/worker와 불변 origin hash를
확인한다. bind 이전의 읽기를 나중에 배정된 Worker에 소급 귀속하지 않는다. Task journal에
같은 이름의 필드를 넣어도 실시간 사실로 사용하지 않는다. 공개 관측은 현재 보이는 Helper,
실제 Worker, 명시 assignedNode/semanticTargets와 정확히 같은 target만 허용한다. 최종 3D
projection에서도 현재 프로젝트의 보이는 소유 root를 확인한다. 복수 배정의 하나를 신호로
자동 선택하거나 새 권한을 부여하지 않는다.

공개 DTO는 projectId, 64자리 opaque receipt, bounded ordinal, targetId, kind/outcome만
전달한다. capability/call ID·원문·origin hash·자격증명·외부 경로는 신호에 넣지 않는다.
job snapshot은 불변이고 시작/완료 시각을 만들어내지 않는다. 원본의 기존 상태 문구만
갱신하며 이동·도착과 실행은 계속 독립적이고 3D를 꺼도 실제 작업은 계속된다.

현재 도구는 동기 잠금 경계 안에서 호출된다. 따라서 이 기능은 **마지막 완료 사실**이며
별도 진행 중 읽기/쓰기 phase나 duration이 아니다. journal/provenance에서 신호를 재생성하지
않고 새 capability/새 엔진에서는 비운다. 프로젝트/Helper 철회와 홈 이탈은 기존 생명주기를
따른다. 오래된 native 성공 사실이 현재 source 내용의 작성자임을 주장하지도 않는다.

V3의 진행 중 IO 신호는 실제 runtime 제공 경계가 없는 상태로 남으며 시간 추정/연출로
대체하지 않는다. 하위 Workspace의 다른 원본 조작과 전체 UI는 기존 지원 대조·검증 대상이고
조합별 필수 작업을 늘리지 않는다. M11/M12/M4는 회귀가 없으면 재개하지 않는다. V4/V5의
별도 신원/권한·가시성, V6/V7 자산 저장·미리보기, V8 Run 영상/오디오 backend 및 V9 참여자·
대화의 고정 잔여는 별도다. /dev/snd가 없는 현재 환경의 작업실 software WebGL 검사를 Run
영상/오디오나 실제 기기 완료로 표현하지 않는다.

[검증·보관·공간 기록](VALIDATION_V666_OFFICE_IO.md)을 따른다.
