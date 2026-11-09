# 정보 정의별 C# 구조체 기반

사용자 결정은 “정보 참조 핀은 정보 정의마다 별도의 C#타입 생성이 맞아. 그거 구조체
만들라는 뜻이었어”다. 공통 값/참조 타입과 정보별 타입 중 선택은 답변 대기가 아니다.
고정 [정보 편집9행](V536_I5_6_REMAINING.md)과 [함수 고급 타입](V666_ACCEPTANCE.md)의
타입/컴파일 기반을 먼저 연결한다. 원본 근거는 저장소 v666 ZIP SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`app.js::renderFeatureDefinition`/타입 선택기와 기존 정보 정의 ID·필드 계약이다.
직전 게시본 Parser는 기본형/배열 native 함수 계약만 허용하여 정보 타입은 실제 컴파일되지
않았다. 이 단위는 정보 선택 UI 전체 완료를 의미하지 않는다.

`information-struct-v1`은 정보 namespace와 전체 ID를 기존 `Generation.Symbol`로
각각 변환한 `Confectory.Information.<pack symbol>.<information symbol>`의 public
struct를 만든다. 정보 이름·표시명·필드 표시명과 CLR 정체성을 분리하며 같은 필드라도
서로 다른 정보 ID는 다른 타입이다. 상속 정보는 기존 유효 필드의 평탄한 값 구조체다.
부모로의 암묵적 CLR 상속/변환은 만들지 않는다. 필드 ID가 C# 멤버이며 키워드는 @로
표기한다. ASCII C# 식별자로 표현할 수 없는 기존 ID는 자동 개명하지 않고 거절한다.
빈 정보와 단일 bool/int/long/float/double/string 필드를 지원한다. 복합·reference·함수·
종류·multiple 필드는 생략하거나 object로 바꾸지 않고 명시적으로 거절한다.

선택된 정보만 pack별 Information contract DLL/ref DLL로 생성하고 함수 interface·구현·
최종 링크와 공개 linkage catalog에 연결한다. readonly `informationStruct` 질의로
타입명·필드 ID/소유 출처·shape hash·C# source와 관측 파일 해시를 확인한다. 질의는
본문 실행·새 파일/객체·배정·권한을 만들지 않는다. 이미 등록된 locator라도 명시 dependency
없이는 거절한다. 미선택 비지원 정보가 있다는 이유로 기존 기본형 프로젝트를 변환하지
않는다. 별도 정보 타입이 없는 함수의 기존 generated source/contract cache key는 유지한다.

필드의 ID/타입/원본이나 부모가 바뀌면 생성 shape와 의존 함수·구현 산출물을 다시
검사한다. 표시 metadata만 바뀌면 구조체 shape와 함수 계약 산출물은 같다. 새 필드는
일반 C# 기본값이며 editor 기본값을 자동 주입하지 않는다. 기존 C# bytes나 서명·핀·
연결을 재작성하거나 사용자 저장 데이터/기존 DLL을 묵시적으로 migration하지 않는다.
새 소스 전체를 다시 컴파일하며 불호환 C#은 오류로 거절한다. 스키마 복원은 원래
산출물과 실행을 복구한다. hot replacement/serialization migration 정책은 정하지 않는다.

직접 소유한 같은 계약 native C# 함수의 본문 후보는 관측한 정보 정의에서 동일 struct
source를 만들어 검사한다. 단일 정보 타입 함수도 기존 native source read scope·version3
receipt·원자 checkpoint를 재사용한다. Save 전 또는 Review 뒤 필드가 바뀌면 CLR 타입
이름이 같아도 원래 source hash/CAS로 거절한다. cold·명시 재검토·Confirm도 원래 정보
snapshot을 유지한다. 기존 64-member/240 read-write/2048 known-unit 예산·권한·소유·
부모/외부 원본·override 계약은 유지한다. 등록 외부 정보의 compiler 읽기는 기존 dependency를
따르며, 후보 편집에서 읽지 않은 외부 정보는 추정하지 않고 정확한 원본 관측을 요구한다.

기존 schema `reference` 속성은 객체 ID/$ref와 현재 객체를 가리키는 의미다. 이를 struct
값 복사로 치환하지 않는다. 본 단위는 native 함수의 정보 **값** 계약 기반이다. 정보/참조
타입 선택 UI, 복합·배열 필드와 참조의 저장/수명 연결, 종류의 CLR, 고급 Blueprint 리터럴·
pin mapping, 기존 서명에서 정보 타입으로 바꾸는 명시 계약 편집은 같은 고정9행의 후속
범위다. 별도 optional 타입/문맥 행을 계속 추가하지 않는다. 참조를 값과 동일시하거나
원본에 없는 소유/권한 정책을 확정하지 않는다. 생성 타입을 쓰는 새 함수 선언은 구 parser가
읽지 못한다. 기본형만 쓰는 기존 선언·원본 C#·이전 보관본은 그대로 보존한다.

최종 검증·보관은 마감 기록에서 구분한다. 초기 빈 화면의 모든 간헐 원인은 미확정이다.
Linux native/Chromium 격리 검증과 실제 Windows/WebView2·모바일·물리 IME/GPU/audio·
사용자 프로젝트·전체 UI 검증은 구분한다. 교차 패키지는 실제 Windows 실행이 아니다.
