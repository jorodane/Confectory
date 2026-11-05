# v666 기존 함수 시작점 저장 복구 검증

개발 중이다. 최종 동결 코드의 독립 LF/CRLF·새 패키지/전체 복원과 보관·게시 결과는
아직 확정하지 않았다. [지원 경계](V2_ENTRY_RECOVERY.md)와
[정확한 delta](v666-entry-recovery-delta.json)를 따른다.

게시본 5f3d31e의 기존 시작 포트에서 쓰기 실패와 재시작의 입력 손실을 재현했다.
원본·C#·checkpoint는 보존됐지만 새 entry 입력은 사라졌다. 원래 시작과 두 명시 선택의
native 실행을 먼저 검증했으며 수정 전 fixture·입력·traffic·스크린샷·cold 결과를 보관한다.
