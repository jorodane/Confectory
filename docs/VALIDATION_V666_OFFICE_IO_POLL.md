# V3 passive I/O poll 검증

최종 LF/CRLF·실제 Worker/OS 읽기 스케줄링·오류·기존 편집 보호·새 패키지/전체 복원 검증 진행 중.
기준 31434810의 재현 기록은 `/workspace/artifacts/v536-verification-managed/runs/7dcca433dc3048e8885b13e873b8977b.json`.
원래 코드에서 진행 표시가 갱신되지 않는 실패를 확인했다. 생성 FIFO의 종료 시 삭제 누락은
검사 수명관리 결함으로 구분하고, 자식 종료를 확인한 뒤 해당 실행이 만든 FIFO만 정리했다.
수정 검사는 FIFO inode/소유권·host 종료를 확인하고 삭제하며 접근 제한을 우회하지 않는다.
최종 통과 수와 새/재사용 증거·보관본·공간은 완료 후 확정한다.
