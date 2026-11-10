# 모듈 요구 함수의 정보·종류·interface 계약

사용자가 확정한 정보별 struct·종류 enum·모듈 interface를 기존 모듈 require 계약에
연결한다. [고정 정보 편집9행](V536_I5_6_REMAINING.md)과 [첫 enum/interface 기반](V666_NAMED_CLR.md)의
같은 타입 생성 흐름이다. 기존 `Registry.Signature`/`Planner.Module`은 요구 함수의 정확한
입력·역할·반환을 검증한다. 원본 v666의 모듈은 필요한 기능과 기본 구현의 묶음이며 타입
선택은 정의를 가리킨다. 이를 primitive로 바꾸거나 요구 함수를 생략할 근거는 없다.

`module-interface-nominal-v1`은 동기 일반 요구 함수의 정보 struct·종류 enum·다른 모듈
interface 입력/반환과 배열·ref/out 역할을 그대로 C# 메서드 선언에 투영한다. 기존 전체
ID별 타입명과 함수 ID별 메서드명은 유지한다. nominal 값의 숫자/필드/형태를 임의 변환하지
않으며 공개 함수/override 계약을 바꾸지 않는다. default는 정확한 implementation 계약인지
검증하며 타입 생성에서 provider를 선택하거나 호출하지 않는다.

메서드 서명에 실제 사용한 타입부터 정보의 깊은 자식·enum·다른 interface까지 같은
source/shape closure를 추적한다. 해당 타입의 ID·CLR 이름·shape hash를 모듈 shape에
포함한다. 깊은 필드 변경은 모듈과 의존 함수/DLL/link를 갱신하고 표시명/아이콘 변경은
값 shape를 바꾸지 않는다. 기존 pack별 타입 assembly와 전이 compiler/reference DLL을
그대로 사용한다. 모듈 경유로 도달한 다른 모듈에도 기존 `Planner.Module` 검증을 적용해
그 모듈 자체의 require/default/dependency 검사를 우회하지 못한다. 각 요구 함수의 원래
namespace에서 명시한 타입 dependency를 확인한다. 등록 자체를 권한으로 간주하지 않는다.

primitive-only `module-interface-basic-v1`은 생성 source·profile·shape·메서드를 그대로
유지한다. 실제 게시본 bafdbb35에서 얻은 Basic descriptor와 수정본을 byte-for-byte
비교한다. 새 저장 문법이나 별도 module metadata migration은 없다. 기존 primitive/compound/
enum 타입 생성도 같은 기존 이름과 source를 유지한다. 새 nominal 모듈은 직전 compiler가
`MODULE_CLR_PROFILE`로 거절하므로 새 전체 source 재컴파일이 필요하다. 기존 C# 원문을
자동 재작성하거나 이전 보관본/DLL을 고쳐 호환되는 것처럼 만들지 않는다. 첫 정보 타입
이전 parser의 generated name 제한과 enum v2의 구 reader 비호환도 계속 유지한다.

같은 계약의 직접 소유 C# 본문 후보도 동일한 모듈 메서드 타입 closure를 사용한다. 모듈
선언과 CLR 이름이 같아도 깊은 정보만 변경되면 원래 read guard로 Save와 Review 뒤
Confirm을 거절한다. 정확 복원·cold·새 명시 Review/Confirm은 원래 입력과 계약을 유지한다.
관측하지 않은 정의를 추정하지 않고 기존 source/known-unit·원자 저장·Review/CAS·Undo·
실패/취소/재시작·늦은 입력·부모/외부 원본·override와 권한 경계를 그대로 따른다.

현재 interface 상속/includes는 요구 메서드를 평탄화한다. 별도 CLR interface 상속·자동
upcast/실행 객체 생성은 추가하지 않는다. async/공개 실행 분기 요구는 원래 실행 계약을
버리지 않도록 계속 명시 거절한다. 선택된 nominal 타입 dependency 순환은 현재 profile에서
`INFORMATION_CLR_CYCLE`로 거절한다. C# interface 자체가 순환할 수 없다는 뜻은 아니다.
pack DLL 순환은 기존 `INFORMATION_CLR_PACK_CYCLE` 경계를 유지하며 assembly를 임의로
합치거나 새로운 migration을 필수 항목으로 늘리지 않는다.

함수 상세 타입 선택 UI는 아직 기본형 목록이다. 기존 nominal 계약을 읽고 C# 본문을
편집하는 UI와 새 타입을 선택/계약 대응하는 UI를 구별한다. 이번 단위는 기존 본문 편집의
실제 UI/저장 검증이며 전체 타입 선택 UI를 완료로 세지 않는다. 참조 속성은 객체 ID/$ref이고
`RuntimeObjectContracts`는 호출자가 제공한 살아 있는 객체의 계약을 설명한다. 구조체 값
복사로 치환하거나 선언 ID로 runtime 객체를 자동 생성/등록/조회하는 정책을 만들지 않는다.
타입 선택 UI·참조의 실제 접근/수명·multiple/함수 필드·고급 Blueprint 대응과 모듈의
기존 고급 실행 계약은 같은 고정9행 잔여다. M11/M12/M4를 새 회귀 없이 재개하지 않는다.

최종 검증·보관은 마감 기록에서 구분한다. Linux native/Chromium·Windows 교차 패키지와
실제 Windows/WebView2·모바일·물리 GPU/audio/IME·전체 UI를 구별한다. 초기 빈 화면 원인은
미확정이며 이번 모듈 연결로 원인이 해결됐다고 표현하지 않는다.
