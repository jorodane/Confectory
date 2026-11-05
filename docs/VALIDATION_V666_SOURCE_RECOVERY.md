# v666 일반 C# 본문 저장 복구 검증

개발 중이다. 최종 동결 코드의 LF/CRLF·패키지/전체 복원·보관/게시 결과는 아직 확정하지 않았다.
[정확한 지원 경계](V2_SOURCE_RECOVERY.md)와 [허용 delta](v666-source-recovery-delta.json)를 따른다.

기존 게시본 dfdf043에서 직접 소유 ordinary root next C# 동작의 입력 손실을 실제 쓰기
실패와 cold로 재현했다. 최초 probe는 multiline source를 JSON 직렬화 문자열에서 그대로
찾는 잘못된 fixture 가정을 사용했다. 실제 blueprint cell의 text를 비교하도록 바로잡고
제품 변경 전 손실을 확인했다. baseline·실패·재현 자료를 보존한다.
