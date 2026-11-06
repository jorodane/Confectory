# V1 일반 Blueprint의 읽기 중 창 닫기

고정 v666의 기존 창 닫기·Blueprint 진입 흐름과 native의 숨긴 창 보존 계약을 유지한다.
게시 `54347f19`와 제품 코드가 같은 패키지 `5deb5f28`의 실제 엔진에서 ‘현재 원본 읽기’
성공 응답을 보류하고 창을 닫은 뒤 전달하니 창이 다시 열렸다. 지연은 로컬 검사에서
응답을 보류한 것이며 실제 네트워크 장애나 기기 검증으로 표시하지 않는다.

읽기 시작 시 기존 창의 표시 상태를 캡처한다. 시작 때 열려 있었던 같은 창이 결과
표시 직전에 숨겨져 있으면 기존 읽기 결과로 reveal/show/focus하지 않는다. 이미
실행된 읽기 자체를 취소하거나 source 권한을 바꾸지 않는다. 기존 연결 해제·창 객체
교체·프로젝트 경계도 유지한다. 시작부터 숨긴 창을 사용자가 명시적으로 다시 여는
경로는 계속 현재 원본을 읽고 같은 개인 배치를 복원한다.

제품 delta는 `blueprint.js`의 표시 상태 캡처·완료 guard와 해당 리소스 pin뿐이다.
[정확한 delta](v666-native-read-close-delta.json)로 검사한다. 요청/읽기 retry·source
관측/CAS·원문/C#·계약/ID/핀/연결·부모/외부 원본·권한·Review→Confirm·Undo·배율·
카메라·레이아웃·private 입력 저장은 바꾸지 않는다. 닫기와 동시에 새 기능을 만들거나
새 source 거래를 재시도하지 않는다.

`tools/verify_desktop.py --suite native-read-close`로 LF/CRLF 독립 checkout/build/cache,
실제 생성 프로젝트의 보류된 성공/실패 응답·반복 닫기·명시 재열기·cold 원본 읽기,
기존 읽기 stale 거절/한도와 배율 수명의 관련 회귀를 확인한다. 새 교차 패키지·전체
SHA/CRC/권한 복원본과 임시물 수명관리·최신/롤백·증거를 마감 기록에 연결한다.

실제 Windows/WebView2·모바일·DPI/IME·전체 UI·독립 정보 창의 모든 문맥·Library/Space
전달은 이 단위의 완료가 아니다. V3–V7 실제 backend/packs, V8 실제 영상/오디오 provider,
V9 실제 신원/가시성과 기존 종류 정책 잔여도 유지한다. main은 사용자가 병합한다.

[최종 검증·보관 기록](VALIDATION_V666_NATIVE_READ_CLOSE.md): 29단계, 신규 29·재사용 0.
