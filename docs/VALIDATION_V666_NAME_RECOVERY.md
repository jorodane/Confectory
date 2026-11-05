# v666 일반 동작 표시명 저장 복구 검증

개발 중이다. 최종 동결 코드의 독립 LF/CRLF·새 패키지/전체 복원 및 보관·게시 결과는
아직 확정하지 않았다. [지원 경계](V2_NAME_RECOVERY.md)와
[정확한 delta](v666-name-recovery-delta.json)를 따른다.

게시본 98a3098의 기존 작은 화면 카드 이름 UI에서 checkpoint 쓰기 실패와 재시작의
입력 손실을 재현했다. 원본/C#과 checkpoint는 그대로였으나 새 이름은 사라졌다.
재현 fixture·개인 입력·traffic·스크린샷·cold 결과를 보관한다.
