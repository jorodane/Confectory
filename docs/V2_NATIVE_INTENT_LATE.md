# V2 일반 Blueprint 적용 중 새 입력 보존

고정 v666의 설명 편집과 native의 기존 ‘적용’·private 입력/공유 초안 경계를 유지한다.
게시 `493a18a4`와 제품 코드가 같은 패키지 `bd4d65d0`의 실제 엔진에서 설명 적용이
성공한 응답을 보류한 뒤 원래 관측 값으로 돌아오는 input callback을 전달했다.
이전 코드는 원래 값이라는 이유로 새 입력을 지워, 응답 후 이전 제출값으로 덮었다.

처리 중 입력 비활성화는 정상 보호이며 유지한다. 늦은 input 검사는 이미 대기 중인
callback을 통제해 전달한 것으로, 비활성 UI에 실제 키보드 입력이 가능하다는 뜻이 아니다.
일반 `bindInput`에서 Apply 시도는 현재 관측 데이터 객체에 연결한 private WeakMap으로 추적한다.
같은 원본의 컨트롤 remount에도 시도를 기억하며 새 source 관측에는 이전 시도 상태를 이식하지 않는다.
Apply 시도가 시작된 뒤에는 원래 관측 값도 새 private 입력으로
보관한다. 시도 성공/오류 후 현재 source를 다시 관측해 새 컨트롤이 연결되기 전까지
이전 원래 값이 현재 공유 초안과 같다고 추측하지 않는다. 성공 후에는 정확히 제출했던
입력 객체만 정리한다. 새 문자열이 같아도 새 입력 객체를 지우지 않는다. 폐기된 컨트롤·이전 관측/프로젝트의
input callback은 현재 입력을 덮지 못한다. 이 상태는 저장하거나 권한으로 복원하지 않는다.

서버 요청·basis/hash·권한·변경 재시도·source 저장·C# bytes·ID/IO/핀/연결·부모/외부
원본·Review→Confirm·최종 CAS·Undo는 바꾸지 않는다. 새 private 입력을 자동 rebase/
Apply하지 않으며 현재 source 읽기와 명시 기준 재검토/입력 취소의 기존 의미를 유지한다.
제품 변경은 [정확한 공통 helper delta](v666-native-intent-late-delta.json)와 리소스 pin뿐이다.

집중 수용은 직접 소유 일반 Blueprint 설명의 원래 값 복귀·같은 문자열 ABA·응답 유실·
명시 재관측/기준 재검토·공유 Undo/Redo·private cold 복원이다. helper를 사용하는
모든 인수·연결/type 조합까지 UI 검증 완료로 늘리지 않는다. `--suite native-intent-late`의
독립 LF/CRLF·새 패키지·전체 SHA/CRC/권한 복원·수명관리 결과는 마감 기록에 연결한다.

실제 Windows/WebView2·모바일·DPI/IME 이벤트·전체 UI·Library/Space 전달은 미실행이다.
V3–V7 실제 backend/packs·V8 실제 영상/오디오·V9 신원/가시성과 기존 종류 정책은 남는다.
M11/M12/M4의 실행 의미나 main은 변경하지 않는다.

[최종 검증·보관 기록](VALIDATION_V666_NATIVE_INTENT_LATE.md): 31단계, 신규 31·재사용 0.
