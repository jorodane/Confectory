# v666 일반 설명 저장 복구 검증

개발 중이며 최종 동결 코드 검증·패키지 보관·원격 게시 결과는 아직 확정하지 않았다.
[지원 범위](V2_DESCRIPTION_RECOVERY.md)와 [정확한 delta](v666-description-recovery-delta.json)를 따른다.

기존 게시본 d63e8f7의 세 가지 손실 재현과 기존 공유 Undo 가능 증거를 보존한다.
개발 중 Ctrl+Y 테스트의 Linux textbox redo 가정을 Ctrl+Shift+Z로 수정했고, 초기 원자
후보의 공유 Undo 회귀는 제품에서 기존 기록기를 재사용하도록 수정했다. 함수 Review
검사는 기존 관련 변경 검토 모달을 먼저 통과하도록 보완했다. 실패 증거를 삭제하지 않는다.

초기 동결 2a358c7의 독립 LF 검사에서 API/공유 history/기존 값 회귀를 확인했다. 함수 선언의 Unicode escape 저장은 native 파서로 다시 읽어 비교하도록 수정했고, display-name native 검사 선택을 실제 메서드 이름으로 바로잡았다. 초기 실행은 증거를 보존하고 종료하며, 제품 byte는 바꾸지 않고 새 동결 검사에서 명시적으로 확인한다.

설명 단독 Review에는 additionalChanges가 없어 acknowledgement가 렌더되지 않는다. 자동화의 무조건 checkbox 기대를 렌더 조건에 맞게 수정했다. 제품은 동일하며, seal/전체 SHA와 Git diff·의존성·명령 일치를 확인한 통과 LF 4개만 재사용한다. 실패한 함수 검사·빌드/독립 checkout·패키지/복원은 새로 실행한다.

늦은 응답 검사에서 의도적으로 응답을 멈춘 뒤 busy 해제를 기다리는 flush를 호출한 fixture 교착을 확인했다. 입력만 바꾼 뒤 응답을 해제하고 flush/보존/cold를 검사하도록 고쳤다. 이미 통과한 함수 entry는 해당 pause를 쓰지 않아 sealed 동일성 검증 후 추가 재사용한다. 제품은 변경하지 않는다.

LF/CRLF의 34단계 통과 후 새 패키지 구조 검사도 통과했다. packaged UI는 보조 검사 스크립트를 package content에서 찾는 fixture 경로 오류로 시작 전에 실패했다. 보조 스크립트는 __file__ 기준 checkout에서 읽도록 수정한다. checkout 검사에서는 두 경로가 동일하므로 sealed 동등 증거를 재사용하고 새 패키지/복원은 모두 다시 실행한다. 제품 및 패키징 byte는 변경하지 않는다.
