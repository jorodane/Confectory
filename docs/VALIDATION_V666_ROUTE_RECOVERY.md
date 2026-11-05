# v666 일반 다음 실행선 저장 복구 검증

개발 중이다. 최종 동결 코드의 독립 LF/CRLF·새 패키지/전체 복원과 보관·게시 결과는
아직 확정하지 않았다. [지원 경계](V2_ROUTE_RECOVERY.md)와
[정확한 delta](v666-route-recovery-delta.json)를 따른다.

게시본 5db09dc의 기존 next 실행 포트에서 checkpoint 쓰기 실패와 재시작의 연결 입력
손실을 재현했다. 원본·C#과 checkpoint는 보존됐지만 새 목적지 입력은 사라졌다.
수정 전 fixture·입력·traffic·스크린샷과 cold 결과를 보관한다.
