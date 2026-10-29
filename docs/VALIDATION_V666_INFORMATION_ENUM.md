# v666 정보 종류 정의와 항목

기준은 저장소 `Confectory-Editor-Prototype-v666.zip` SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다. `app.js:1707–1710`의 종류 생성, `3075–3081`의 항목 추가·이름·드래그 순서·아이콘·삭제, `2773–2786`과 `2809–2811`의 항목 참조/기본값을 대조했다. 원본 항목은 `{id,name,icon?}`이고 속성 값은 선택한 항목 ID다. 행 번호는 표시 순서이며 int32 값 편집기가 아니다. 기존 `BlueprintEnumContract`/C# 실행 분기 enum과 연결하지 않는다.

## 이번 지원 단위

- native의 별도 `enum Namespace::Name` 선언과 프로젝트 등록을 사용한다. 전체 정의의 namespace-qualified ID와 내부 항목의 불투명 ID를 구분한다. 항목은 별도 manifest element를 만들지 않으며 UI의 UUID를 한 번 만들고 저장·재시도·cold·Undo에서 유지한다.
- 기존 primitive `value` 문법의 `editorEnumProfile="nominal-members-v1"`와 `editorEnumValues` JSON 문자열에 항목 목록을 보존한다. 무표식 빈 enum은 빈 정의다. 알려지지 않은 profile, 일부만 있는 기록, 중복 ID/이름, 잘못된 이미지, 숫자 `value`/실행 필드 혼입을 거절한다. 항목 256개·목록 1MiB와 기존 source 1MiB 읽기 예산을 유지한다. 항목 이름은 원본과 같은 60자 이내의 비어 있지 않은 서로 다른 표시명이다.
- 원본 작업실의 종류 만들기, 기존 정보 Browser와 선언 창에 연결한다. 원본 `.enum-values`/`.enum-value-row`와 공통 팝오버를 사용하며 새 CSS나 별도 디자인을 추가하지 않는다. 추가·이름·순서·기호/이모지·생성한 로컬 PNG의 정규화 이미지·아이콘 해제·미참조 항목 삭제·Undo/Redo를 지원한다. 타이핑 중 이름도 private 입력으로 보존한다.
- 기존 owner 거래와 직접/독립 선언 창 binding, 원문 hash·프로젝트 문맥·전체 후보·최종 CAS·checkpoint·receipt·Review→명시 compiler Confirm을 재사용한다. 항목/아이콘 때문에 함수·핀·본문·실행 계약·다른 원본을 바꾸지 않는다. 새 정의는 등록과 함께 검토하고 Confirm 전 실제 파일을 만들지 않는다. 미확정 생성의 취소도 등록 그룹과 함께 되돌린다.
- 새 native 종류를 기존 소유 선언 읽기/receipt 및 표시 projection에 추가했다. namespace/ID/hash/binding/경로 검사는 유지한다. 종류에는 원본에 없는 상속·실행/모듈 계약을 추가하지 않는다. Review는 항목 이름·안정된 값 ID·아이콘 변경을 기존 비교 행에 표시하며 긴 이미지 URI를 본문 요약에 노출하지 않는다.

## 경계와 호환성

이 단위는 종류 **정의와 미참조 항목 편집**이다. 속성 타입 선택기의 종류 연결, 실제 항목 값 선택/기본값·소비자 검증, 사용 중 항목의 삭제 대응, 종류 전체의 보관/복구 UI는 다음 원래 흐름으로 남긴다. 정의 생성/편집을 이러한 소비 흐름의 완료로 표시하지 않는다. 기존 ordinary 선언 전체 삭제의 허용 목록을 enum으로 넓히지 않았다. 임의의 문자열·C# 본문을 항목 참조로 추측하거나 조용히 재작성하지 않는다. 함수/C# ABI에서의 종류 타입 표현이나 숫자 변환은 이 단위에서 결정하지 않았다.

새 `enum` 문법은 갱신된 native/백엔드가 필요하다. 이전 패키지의 parser는 새 enum 파일·등록을 읽지 못한다. 기존 프로젝트를 자동 변환하거나 구버전 형식으로 내보내지 않는다. 알 수 없는 profile은 보존한 채 거절하며 자동 마이그레이션하지 않는다. 최신/롤백 패키지의 복원 검증은 각 패키지의 출처 코드에 대한 검증이고, 구버전으로 새 enum 데이터를 읽는 보장은 아니다.

## 집중 검증과 발견 사항

base `442102a`, 집중 기록 `/workspace/artifacts/v536-verification-managed/runs/530882b914d5491aa3e27fdf7fd30d64.json`에 각 overlay·입력·원문·이미지·실패를 보존한다. Core의 종류 전용 검사와 기존 실행 enum 검사 5건이 실제 C# compile-only 검사까지 통과했다. native 후보는 원문 CRLF/주석·큰 정수·등록·원본/참조 파일을 유지하며 생성·정렬·이름·문자/이미지·해제·삭제와 잘못된 owner/profile/ID/이름/숫자 값/이미지 거절을 확인했다.

실제 화면에서 기본/독립 창, 원본 메뉴 생성, 미확정 생성 취소, private Undo/Redo·타이핑 중 cold·순서·항목 삭제/복원·Save·Review 취소·명시 Confirm을 확인했다. 독립 창의 늦은 이름 입력, 응답 유실 후 중복 적용 없는 cold receipt, 저장 실패, 변경 취소, 실제 peer 충돌, 실제 다른 프로젝트 왕복, 잘못된 binding/다른 owner/부모 계약 혼입, 중복 이름의 저장 전 거절·입력 보존·명시 수정도 통과했다. 테스트 자산은 생성 이미지뿐이며 개인 파일이나 외부 자료를 업로드하지 않았다.

첫 UI의 disabled 버튼은 editable projection의 새 종류 누락이었고, 다음 Save 거절은 owner 읽기/receipt 종류 누락이었다. 해당 목록에 enum을 추가하되 기존 소유/버전 검사를 유지했다. Review가 ready인 화면에 없는 추가 확인 체크박스를 기다린 검사 가정은 실제 제공되는 절차로 수정하고 Confirm 활성화 검사는 유지했다. 실패 기록을 통과에 합치지 않는다. 새로운 전체 정의 삭제 수명을 추측해 추가하지 않았다.

## 최종 마감

`tools/verify_desktop.py --suite enum-definitions`는 기존 70단계와 Core/native/UI·신규 생성·패키지/복원 enum 검사 9단계를 합친 79단계다. 정확한 commit의 LF/CRLF 독립 checkout, 새 교차 패키지, 전체 파일 SHA/CRC/모드 복원·실행 UI, 최신/롤백 지속 보관과 임시물 정리 결과를 최종 검증 뒤 기록한다. 공용 SDK/의존성 seed와 이전 정상 롤백 증거의 재사용은 새 실행과 구별한다.

Set 미지원 문맥과 기존 ABI closure·고급 타입/핀 표시명·B2·M4·M11·M12·V2–V9는 이 단위에 포함하지 않는다. 3D/권한 별도 팩, 이동 연출과 실행 분리, 공개 override 원계약 유지 합의는 그대로다. 실제 Windows/WebView2·물리 모바일·전체 UI·Space/Library 전달은 미검증이다. 배율 일시 실패의 원인은 미확정으로 유지한다.
