# v536 객체의 직접 소유 속성 아이콘

기준은 게시 `b429c0a`와 저장소 `196c605`의 v536 ZIP이다. 원본 객체 화면의
자체 `renderFields` 행은 `data-property-icon`에서 기존 `editIconValue(..., true)`를
연다. 이번 최소 단위는 **객체의 기존 직접 소유 속성 → 기호/이모지·아이콘 없음 →
기존 Save → 재시작·Review/Confirm**이다. 새 메뉴·레이아웃·핀 ID·계약 복제는 없다.

## 소유와 저장 경계

현재 native 모델의 객체 속성 정의는 직접 `use schema`로 배정한 정보 선언에 있다.
기존 이름·타입 편집과 같은 소유 스키마 갱신 후보에 `schema-icon`을 연결한다.
객체 설명/값과 직접 소유 스키마의 `editorFieldIcon_<field>`는 한 후보·기존 최종 CAS로
처리한다. 같은 정의를 사용하는 다른 객체의 표시에도 해당 스키마 metadata가 적용되며,
인스턴스별 비공개 아이콘을 임의로 새로 만들지 않는다. 개별 값·부모 구현·외부 원문은
보존한다. 실제 fixture는 두 객체가 사용하는 같은 소유 정의와 별도 부모 정의를 갖는다.

후보는 한 단계 경로·원래 타입/필드·직접 사용 관계·namespace·스키마 원문 해시를
확인한다. 원문이 바뀌거나 마지막 glyph가 잘못되거나 삭제와 충돌하면 설명/값/metadata
전체를 미적용한다. 부모에서만 사용하는 정의, 외부·미배정 선언, 중첩 경로는 이 갱신의
소유 대상이 아니다. 참조된 정의를 현재 값 화면에서 임의 편집하도록 넓히지 않는다.

성공 응답을 기다리는 동안 추가한 glyph는 기존 receipt를 조회하고, 저장된 소유
스키마의 새 해시·필드 계약·수락 glyph와 객체 source hash를 확인한 뒤 별도 입력으로
보존한다. 재시작 후 새 명시 저장만 이를 적용한다. 이전 정보 전용 receipt와 생성 초안의
후속 아이콘 입력도 유지한다. 응답 유실 시 중복 적용하거나 CAS를 완화하지 않는다.

원본 팝오버·문자 Undo·속성 Undo·취소·명시 해제·닫기·초점과 CSS를 유지한다.
로컬 이미지·개인 파일·외부 자산·AI 호출·실행 권한은 이번 단위에 없다.

## 검증과 남은 원래 범위

명령·종료코드·확인 수·제품 SHA·원본 handler·예산/최소 공간·리소스 검사는
`evidence/v536-object-property-glyph/focused-verification.json`에 기록한다.
실제 엔진/렌더러/Compiler Confirm은 격리 fixture만 사용한다. 원문·화면·로그·프로필
증거는 scratch에 보존하고 Git에 게시하지 않는다. 이번 실행이 직접 만든 임시 복사본만
기존 승인 수명관리로 정리하며 보관 빌드·캐시·SDK·사용자 자료는 삭제하지 않는다.

I6의 기존/새 직접 정보 루트 속성과 이번 객체의 기존 직접 소유 속성을 구별한다.
새 객체 속성의 저장 전 아이콘, 자체 중첩 정의, 함수/서명 핀, 다른 요소 팝오버와 로컬
PNG/JPG/WebP 자산 선택·저장·복원은 아직 미완료다. 이들은 원래 목록의 부분 범위이며
새 조합 요구로 늘린 목록이 아니다. 연결 정보의 하위 값·상속/외부 정의의 정상 읽기 전용도
구별한다. forwarded 부모·opaque/import 영향 결합, 8행 여러 함수 문맥과 9행 고급 타입/
표시명, B2 실제 작업자 배지, M4 async/M11 C#→graph/M12 Root 실행 분기는 별도 잔여다.
전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 계속 미완료다.

집중 8흐름 59확인, 순수 후보 4확인, 기존/새 정보 속성·객체 요소 glyph·정보 편집·생산 final CAS 영향 회귀 27확인이 통과했다. 원본 팝오버 10영역의 치수/위치/스타일과 74개 리소스의 바이트/해시를 확인했다. 스키마 실제 경합·쓰기 실패·취소·Undo·응답 유실 조회·늦은 입력·다른 창 보존·compiler Confirm을 분리 검증했다.

첫 새 교차 패키지 생성 뒤 구성 검사는 WebBundle raw string의 원래 줄바꿈이 빠져 manifest 정규식을 읽지 못했다. 검사기를 바꾸지 않고 원본 source envelope를 복원했다. JSON 리소스 목록·해시와 모든 JS/Native 실행 의미는 같으며, 최초 실패 source/로그를 보존했다. 집중 회귀의 원래 source SHA와 형식 복원 후 SHA를 evidence에 구별하고, 최종 독립 checkout·새 교차 패키지로 후속 검증한다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `a1b1b43ca1da201360150f6ebb2f0fcdfb45d374`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 객체/정보 정의의 native field ID·타입·값과 부모/외부 원본을 보존했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진, 객체의 기존 직접 소유 속성 아이콘·소유 스키마·늦은 입력/다른 창 보호의 독립 창 11확인 및 생산 final CAS 4확인, 이전 형식/객체 스키마 receipt 보호 3확인이 통과했다. 새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 속성 아이콘 UI 11확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 제품 소스 바이트를 확인했다.

manifest SHA `30de8dd0cb6aad7042f09157e65899f586d2c33358c07cbac220fe9e77a88143`. 전체 manifest와 fixture/로그/프로필 증거 보관 뒤 이번 실행의 임시 패키지만 정리했고 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달 및 전체 UI는 계속 미완료다.
