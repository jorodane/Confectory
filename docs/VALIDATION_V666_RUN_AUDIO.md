# V666 Run PCM 오디오 검증

이번 범위는 [명시적 PCM producer와 로컬 미리듣기](V8_RUN_AUDIO.md)다. 실제
프로젝트 PCM 전송/범위·해시와 Chromium의 실제 AudioContext graph를 검증한다. 물리 스피커,
실제 Windows apphost/WebView2·모바일·실시간 출력 지연·전체 UI·Space/Library 전달은 미검증이다.

진단 단계의 소수점 완전 일치 비교·페이지 생성 API·자연 종료된 buffer의 stop 횟수 가정은
검사 결함으로 구분한다. 재현된 제품 결함인 graph 구성 실패 시 context 잔류는 cleanup을
추가하고 실패 주입 회귀로 검증한다. 진단 실패/수정 과정도 지속 증거에 보존하며 최종 통과
근거로 재사용하지 않는다.

최종 source를 동결하고 별도 Git/SDK 상태·NuGet cache·engine cache의 LF와 CRLF checkout에서
전체 관련 검사를 새로 수행한다. native 소유/범위/변조 PCM·재생/끄기/거절된 시작·반복/Step·
응답 보류/닫기 거절/retired handler·프로젝트 왕복·cold 복원, 기존 해상도와 개발 메뉴를 포함한다.
새 Windows 교차 패키지의 관리형 엔진과 전체 SHA/CRC/모드 복원본에서도 실제 관련 UI를 검사한다.
교차 패키지 검사는 실제 Windows 기기 실행과 다르다.

최종 검사 수·출처 commit·package/evidence hash·순증가와 정리 상태는 검사 완료 뒤 기록한다.
