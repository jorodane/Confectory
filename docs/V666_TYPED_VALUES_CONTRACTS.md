# 기존 typed 값과 native 계약·본문 공동 저장

같은 정보 창에서 복합·다중 값, 객체/함수 대상 참조와 종류 값을 편집하고 두 native 함수의 계약·본문·호출 대응을 저장하는 기존 흐름이다. 값 편집과 native 계획이 각각 유효해도 조합만 거절되는 분류 경계를 다룬다.

InformationFunctionBodyBatch의 분류와 기존 native 읽기 증거의 결합을 수정한다. 기존 data/unset 행을 native 함수 계획에서 분리하며, 전체 InformationDefinitions 검증을 그대로 거친다. 종류는 general/compound/reference/function/enum, cardinality는 single/multiple, 기존 경로 한도는1..64다. data의 정확한4키 및 문자열 valueJson, root unset의 정확한3키만 분류한다. 일반 타입은 기존6개 primitive다. 이름·경로/인덱스·실제 원래 계약·기본값·대상 유효성과 출처는 원래 검증기가 증명한다.

전체64행과2..8개 native 계획 제한, 겹치는 경로·알 수 없는 필드·부적합 값 거절을 보존한다. 참조를 따라 다른 소유자를 편집하거나 없는 부모/목록 항목을 만들지 않는다. 필드 정의·정보 타입 생성·구조 전환이나 자동 값 변환을 추가하지 않는다. C#은 사용자가 명시한 원래 계획만 반영하며 native/caller 후보 bytes는 값 행 추가 전후 동일해야 한다.

검증 조작은 Tree.Count, 기존 등록 외부 타입의 ExternalTree.HP, Samples 목록 항목, Peer·Handler 대상과 Mode enum 선택을 원래 UI로 편집하는 한 흐름이다. 두 함수의 명시 out/return·본문·공유 caller 대응과 정보 설명·아이콘을 같은 Save로 보관한다. 정확한64비트 값, 필드 ID/계약과 선택 밖 C#을 유지한다. 외부 정의·선택 참조/enum/provider 원본은 읽기 관측에만 속한다. 새 명시 공동 Save의 기존 version3 receipt에 nativeBodyValues와 nativeBodyValueReads를 보관한다. 원래 값 검증기로 관측 경로를 다시 증명하고 후속 표시 저장에서도 같은 계획/해시를 유지한다. 프로젝트 내부 경로는 기존 readGuards, 이미 등록된 프로젝트 밖 출처는 기존 CommitPlan reads의 최종 읽기 lease로 연결하며 쓰기 대상에 넣지 않는다. 이전 미지원 조합의 receipt를 자동 마이그레이션하지 않는다. 저장 receipt와 후속 표시 저장의 readGuards 및 Review 뒤 최종 CAS 거절을 검사한다.

이 흐름의 정상 저장·실행과 부적합/중복/겹침 거절, 취소·역사 경계·실패/재시도·응답 유실·cold·경합·늦은 입력·프로젝트 분리, LF/CRLF 새 빌드와 패키지/전체 복원을 확인하면 이번 단위를 닫는다. 타입·문맥의 임의 조합을 새 필수 범위로 늘리지 않는다.

고정7/8행의 다른 복합 속성 **구조/정의 변경**, opaque/private 명시 C# 계획, 선택 소유 native callee와 기존 import의 변경 그룹·등록 외부 원본의 읽기 관측 결합은 별도 잔여다. M11/M12/M4는 회귀 없이 다시 열지 않는다. 정보별 struct·종류 enum·모듈 interface, override 계약·권한·배치·Review/Confirm·최종 CAS를 보존한다. 새 grant/credential·과금·migration은 없다.

구 Reference reader downgrade는 보장하지 않는다. 초기 빈 화면 원인은 미확정이며 실제 Windows/WebView2·기기·OS IME·전체 UI 전수 검증을 자동화된 Linux 편집기 검증과 구별한다.
