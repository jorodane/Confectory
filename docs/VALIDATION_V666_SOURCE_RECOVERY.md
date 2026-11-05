# v666 일반 C# 본문 저장 복구 검증

개발 중이다. 최종 동결 코드의 LF/CRLF·패키지/전체 복원·보관/게시 결과는 아직 확정하지 않았다.
[정확한 지원 경계](V2_SOURCE_RECOVERY.md)와 [허용 delta](v666-source-recovery-delta.json)를 따른다.

기존 게시본 dfdf043에서 직접 소유 ordinary root next C# 동작의 입력 손실을 실제 쓰기
실패와 cold로 재현했다. 최초 probe는 multiline source를 JSON 직렬화 문자열에서 그대로
찾는 잘못된 fixture 가정을 사용했다. 실제 blueprint cell의 text를 비교하도록 바로잡고
제품 변경 전 손실을 확인했다. baseline·실패·재현 자료를 보존한다.

초기 동결 254ea89에서 LF 17단계와 CRLF native/API/설명 회귀는 통과했다. 다음 property guard 호출의 engine report 인자가 빠져 fixture 초기화 전에 IndexError로 종료됐다. 기존 호출 예와 같이 인자만 추가하며 제품/검사 byte는 그대로다. 봉인된 동등 통과 10개만 SHA·전체 manifest·Git·SDK/NuGet·명령/EOL 일치로 재사용하고, 실패한 관측 검사·checkout/빌드·새 패키지/복원은 새로 실행한다.

응답 유실/cold에서 실제 추가 결함을 발견했다. source-only의 graph draft text가 원문과 같아 Export가 graph receipt를 checkpoint에서 제외했다. C#은 이미 저장됐지만 재시작 후 settled 판정이 불가능해 입력 복구가 막혔다. owned source receipt만 명시적으로 보존하고 현재 C# 본문 일치도 검증한다. No-op Save·위조 receipt 거절을 추가하며 제품 변경 때문에 최종 영향 검증은 모두 새로 실행한다.
