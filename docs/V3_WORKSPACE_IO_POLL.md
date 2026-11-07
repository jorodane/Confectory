# V3 진행 중 I/O의 passive 상세 갱신

원본 v666의 실제 Worker read/write 표시와 기존 도구 진행 관측을 연결하는 후속이다.
실제 도구 읽기가 공유 EditWorkspace 잠금을 잡은 상태에서 UI 진행 표시가 갱신되지 않음을
소유 OS pipe 읽기 검사로 재현했다. 기존 도구 관측은 pending을 비차단으로 반환했으나
편집기 poll의 상세 창·table·schema 갱신이 같은 잠금을 다시 기다렸다.

현재 선택 프로젝트의 기존 `toolsObservationPending`이 참인 passive poll만 상세 갱신을
미룬다. 이전의 일관된 상세 snapshot은 보존하고, 실제 Worker/진행 신호는 계속 전달한다.
다음 완료/실패 관측에서 원래 동기 갱신을 재개한다. explicit 편집·Review→Confirm·adoption·
CAS는 동일한 코드와 검증을 사용한다. 다른 프로젝트의 pending은 현재 상세를 건너뛰지 않는다.

새 권한/신원·실행 정책·표시 timer·진행률·도착 조건이나 public 계약은 추가하지 않는다.
원본 레이아웃과 C#·override 계약은 유지한다. 빠른 도구 호출은 관측 사이에 끝날 수 있다.
사용자 C#/일반 FileStream·provider HTTP·최종 원본 채택을 도구 진행 신호로 추정하지 않는다.

최종 검증은 별도 문서에 기록한다. 검사 전용 엔진의 두 소유 pack 복사본만 계측해
실제 Tool Read가 실제 EditWorkspace 잠금 안에서 OS FIFO 읽기를 기다리게 한다.
진행/성공 DTO나 UI 응답을 주입하지 않는다. 정상 엔진의 완료/ReviewConfirm 회귀와 구분하며
물리 디스크 지연의 성능 보장이나 모든 I/O 경로 검증으로 확대하지 않는다.
