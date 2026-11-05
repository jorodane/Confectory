# v666 일반 설명 저장 복구 검증

개발 중이며 최종 동결 코드 검증·패키지 보관·원격 게시 결과는 아직 확정하지 않았다.
[지원 범위](V2_DESCRIPTION_RECOVERY.md)와 [정확한 delta](v666-description-recovery-delta.json)를 따른다.

기존 게시본 d63e8f7의 세 가지 손실 재현과 기존 공유 Undo 가능 증거를 보존한다.
개발 중 Ctrl+Y 테스트의 Linux textbox redo 가정을 Ctrl+Shift+Z로 수정했고, 초기 원자
후보의 공유 Undo 회귀는 제품에서 기존 기록기를 재사용하도록 수정했다. 함수 Review
검사는 기존 관련 변경 검토 모달을 먼저 통과하도록 보완했다. 실패 증거를 삭제하지 않는다.

초기 동결 2a358c7의 독립 LF 검사에서 API/공유 history/기존 값 회귀를 확인했다. 함수 선언의 Unicode escape 저장은 native 파서로 다시 읽어 비교하도록 수정했고, display-name native 검사 선택을 실제 메서드 이름으로 바로잡았다. 초기 실행은 증거를 보존하고 종료하며, 제품 byte는 바꾸지 않고 새 동결 검사에서 명시적으로 확인한다.
