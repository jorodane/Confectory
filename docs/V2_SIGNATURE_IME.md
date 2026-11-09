# 함수 상세 편집의 IME Escape 입력 보호

고정 v666 `app.js::openOwnFunctionPopover`의 상세창은 함수 설명·핀 이름/타입의 미확정 복사본을
편집하고 저장에서만 반영한다. 일반 Escape·닫기·취소·바깥 클릭은 복사본을 버리는 원래 의미다.
현재 native UI의 공통 `openFunctionSignatureEditor`는 이 흐름을 직접 소유 기능·정보 함수에
재사용한다. 핀 표시명과 native 계약 식별자의 분리/저장 정책을 새로 정하는 단위는 아니다.

게시 833617c7의 실제 상세창/타입 검색창에서 브라우저 `KeyboardEvent.isComposing`와 legacy
`keyCode=229` Escape를 각각 전달하면 창이 닫히고 미확정 설명·이름 또는 검색어가 사라졌다.
원본/체크포인트는 변경되지 않았지만 조합 취소 키가 전체 편집 취소로 처리됐다.

두 Escape listener에 기존 UI와 같은 조합 중 guard를 추가한다. 조합 중에는 창 취소/포커스
이동을 실행하거나 기본 동작을 막지 않는다. 조합이 끝난 일반 Escape는 타입 검색창을 먼저
닫고 다음 Escape가 상세창을 취소하는 기존 동작을 유지한다. 명시 취소/닫기·저장과 pointer/
scroll/resize·owner/창 수명 검증은 그대로다. 새 컨트롤·CSS·영구 입력/저장 형식은 만들지 않는다.

실제 공통 팝오버에서 설명·핀 이름·타입 검색어 보존, 일반 Escape 순서·명시 취소·반복 열기/
닫기·cold 재진입을 검증한다. 명시 설명 Save/cold·Review 취소/Confirm 및 기존 C# 실행10도
검사한다. 원래 C#·함수/핀 식별자·계약·권한·최종 CAS는 바꾸지 않는다.

이 검사는 실제 Chromium DOM에 생성한 조합/키 이벤트를 전달하는 자동화다. 실제 OS IME·
키보드 드라이버·Windows/WebView2·모바일/터치·전체 UI 수용은 미검증이다. 초기 빈 화면과 과거
Agent 준비 지연의 원인은 미확정으로 유지한다. 다른 고정 ABI/핀 표시명/backend·종류 정책은
별도 잔여이며 M11/M12/M4를 다시 열거나 가능한 조합별 새 필수 범위를 추가하지 않는다.

[최종 신규29단계·재사용0과 보관/검증 한계](VALIDATION_V666_SIGNATURE_IME.md)를 따른다.
