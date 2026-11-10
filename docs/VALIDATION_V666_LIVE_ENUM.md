# 실제 객체 enum 접근 검증

[지원 경계](V666_LIVE_ENUM.md)의 제품·검사를 고정한 뒤 `live-enum` 전용 suite로
최종 검증한다. 현재 결과 문서는 최종 실행 후 확정한다. 개발 재현을 최종 통과나 실제
Windows/모바일·전체 UI 완료로 합산하지 않는다.

게시본 `059111512c8c9444a98292072eb083f086b4ca0e`에서 enum C# 타입 자체는 생성되지만
실제 ObjectModel.Create/Access가 해당 필드를 거절함을 실제 CLR로 재현했다. primitive
객체 descriptor와 숫자 매핑 없는 enum 필드의 기존 descriptor를 golden 입력으로 보관하며,
수정 후 byte-for-byte 비교한다. golden 입력과 과거 실행 증거 재사용을 구별한다.

새 native 검사는 caller-owned 객체, 서로 독립인 상속 객체, 실제 Blueprint Read→Set→Read,
반복 호출과 이전 enum 출력 보존을 확인한다. raw ID/정수/다른 enum/정의 밖 값/null,
잘못된 배열·비vector 배열, source hash와 mutable enum ref 거절도 검사한다. 배열 참조와
이전 배열 출력, 호출자가 직접 잘못 바꾼 배열의 Read 거절·명시 복구를 확인한다. 멤버
이름·순서 변경은 숫자·필드 hash·contract 산출물을 유지하고, 실제 멤버 계약 변화는
pinned property node를 거절한다. 정확한 원문 복원이 원래 key와 실행을 회복한다.

UI는 기존 속성 editor·resource 검색·모바일 값 선택과 실제 engine/checkpoint/compiler를
사용한다. 새 읽기·receiver·소비 binding·실행 attachment를 한 후보로 Save하고 cold 복원한다.
저장 실패·enum source 충돌, 응답/receipt 유실의 중복 apply 없는 복구, 늦은 별도 입력,
기존 C# 본문의 취소·저장 실패·후속 Save, 반복 Review/명시 Confirm·최종 CAS를 확인한다.
기존 enum 지역값 초기화 문법은 확장하지 않고 fixture의 명시 C# 숫자 변환을 사용한다.

최종 계획은 독립 LF/CRLF·빈 engine cache·공개 SDK/기존 NuGet seed, 기존 primitive/ref
runtime·authoring·동기/async 속성 UI·module·정보 배열 회귀다. 새 Windows 교차패키지의
구조/무결성·패키지 engine 실행·전체 ZIP 복원과 실패 수명관리를 구별한다. 최종 SHA·
증거·latest/rollback·정리·공간·신규/재사용 결과는 실행 후 이 문서에 확정한다.
