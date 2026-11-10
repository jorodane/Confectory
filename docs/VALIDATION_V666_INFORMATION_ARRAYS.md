# 정보 구조체 배열 필드 검증

[지원 경계](V666_INFORMATION_ARRAYS.md)의 제품·테스트를 고정한 뒤 `information-arrays`
전용 suite로 최종 검증한다. 이 파일의 결과란은 최종 실행·보관 후 확정한다. 개발 결과를
최종 통과로 합산하거나 실제 Windows/모바일·전체 UI 수용으로 표시하지 않는다.

개발 재현에서는 게시본 `acbdc08fa7139d45dc51b06b2a39b4e11b8b5ad2`의 실제 생성기가
multiple 필드 C# ABI를 `INFORMATION_CLR_FIELD`로 거절하고 원본을 보존함을 확인했다.
같은 게시본에서 얻은 primitive·compound·enum·기본/nominal 동기 module의 source/hash/profile
5개를 golden 입력으로 보관한다. 최종 검사 때 새로 생성한 descriptor와 비교하며,
golden 입력 사용은 과거 실행 증거의 재사용이 아니다.

실제 native 실행은 long/bool/string·중첩 struct·enum 배열, exact64 숫자, Unicode/null,
기본 배열 null 및 일반 C# struct/배열 대입 규칙을 확인한다. 이미 지원하는 동기 module
interface 구현은 fixture의 명시 C# Reflection.Emit 객체다. provider 선택이나 제품의
새 live-reference 객체 생성/접근 정책으로 표현하지 않는다. 배열 원소 shape 변경의 key
무효화, 배열→scalar와 다른 nominal 원소의 C# 불일치, 미선언 dependency, reference/함수
필드·구조 순환 거절과 정확한 복원도 실제 compiler로 검사한다.

UI는 원래460px 정보 본문 편집기와 실제 엔진·checkpoint·compiler를 사용한다. 본문 편집,
취소·Undo/Redo·미저장 cold 복원, 원자 Save, 중복 Save 금지, 저장 실패, apply/receipt 응답
유실과 중복 apply 없는 cold 정산, 응답 중 늦은 이름의 후속 Save를 검사한다. schema 원소
변경 전 Save 거절/Review 뒤 최종 CAS 거절, 등록 read guard 누락·추가·native proof 변조의
cold Review 거절 및 등록 원문 변경 후 Confirm 거절을 구분한다. 실패와 peer 원문을
보존하고 정확한 원문 복원·새 Review 후 실제 결과31을 실행한다.

최종 계획은 독립 LF/CRLF checkout·공개 SDK/NuGet seed·빈 engine cache에서 실행하고,
기존 scalar 정보/compound native/module API·module UI·선언/헤더 receipt 회귀를 포함한다.
새 Windows 교차패키지의 구조·무결성, 패키지 안 engine의 실제 Linux/.NET UI 실행,
전체 ZIP 복원 뒤 동일 계약·수명 흐름과 package 실패 수명관리를 별도로 확인한다.
main·기존 checkout·latest/rollback·증거 및 cleanup 한도를 유지한다.

최종 결과·SHA·증거 archive·package/latest/rollback·공간: 실행 후 이 문서에서 확정한다.
