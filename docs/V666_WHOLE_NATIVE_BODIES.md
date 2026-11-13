# 기존 whole-body와 일반 C# 본문의 공동 저장

고정 8행의 같은 정보 창·한 Save에서 이미 변환한 whole-body C# 함수와 일반 native C#
함수의 본문을 함께 저장한다. 게시 `a50532884c188d6e07aba6206719ebc485467d68`에서
두 단일 명시 계획은 각각 유효하지만 함께 거절되는 것을 재현했다. 이번 단위는 계약 변경을
추측하지 않는 명시 본문 결합이다. private 및 실제 ABI 변경 callee/import 결합은 별도 잔여다.

직접 소유 함수 2~8개, 함수당 하나의 원래 구현/target, 기존 whole-body lift와 일반 native
본문을 선택한다. 공개·native 매개변수 이름·타입·역할·순서·반환·async/공개 실행 계약을
유지한다. 선택된 구현의 import·copy·상속·추가 target은 별도 명시 closure를 요구한다.
새 C#·바인딩·셀·별칭·변환을 생성하거나 기존 원문을 재작성하지 않는다. 기존 공유 호출자도
원래 단일 검증기의 원본 관측과 컴파일 검증을 통과해야 한다.

각 계획을 완전한 원래 관측에서 기존 InformationFunctionContracts로 독립 검증하고
기존 내부 overlay·SlotBatch·checkpoint CAS로 결합한다. 순서에 무관한 한 후보이며 기존
64개 Review member·전체 source/read 240 한도를 유지한다. 원래 whole-body receipt와
root graph를 검증한 뒤, 계약 불변 편집에서는 그래프를 그대로 쓴다. 기존 단일 처리의
불필요한 빈 `exits` → `return: null` 변경도 이 경우에 한해 없앤다. 실제 계약 전환의 기존
명시적 저장·return 처리에는 이 단축 경로를 적용하지 않는다.

기존 version3 slotSaveReceipt에 선택적 `nativeBodyContexts`로 원래 함수 hash와 전체
명시 본문 계획을 보관한다. source/hash/경로·whole graph/return receipt·원래 등록된
소유 source scope를 재검증하고, 조립한 후보도 checkpoint 쓰기 전에 검증한다. cold는
기존 알려진 경로만 다시 읽고 새 원본 기준을 채택하지 않는다. 후속 정보/함수 표시 Save는
원래 계획과 readGuards를 유지한다. 후속 명시 본문 편집은 현재 draft hash를 확인한 뒤
캡처 계획의 text만 갱신하고 원래 source/flow hash는 유지한다. 다른 계약·구조 변경을
섞으면 입력을 보존하며 거절한다. Review/Confirm과 최종 물리 read/source CAS는 기존 그대로다.

변환 뒤 미등록 상태로 남은 원래 `.csbody`는 쓰지 않고 바이트 보존을 검사한다. 이를 새로
관측된 등록 source 또는 CAS 감시 대상으로 주장하지 않는다. 등록된 whole graph/node,
구현·함수·공유 caller·manifest와 나머지 알려진 소유 source는 기존 read/check 범위에 있다.
원래 파일 변경을 새 기준으로 받아들이지 않고, 정확한 복원 후 새 Review로만 계속한다.

완료 조건은 이 사용자 흐름의 순수 후보/거절/순서 독립성, 원래 UI 편집·취소·Undo/Redo,
Save 실패/재시도·cold·응답/조회 유실·반복·프로젝트 경계·늦은 입력과 후속 Save,
Review 취소/Confirm 및 Review 뒤 그래프/node/caller 경합이다. 실제 portable 실행은 원래
40에서 사용자가 명시한 두 뺄셈 본문으로 20이 된다. LF/CRLF restore/build, 새 package와
전체 추출본을 별도로 검증한다. 단일 whole 타입 전환·기존 native 계약·등록 helper·새 소유
자식은 회귀로 포함한다. 개발 실패와 최종 신규·재사용 결과는 별도로 기록한다.

같은 게시 세대의 authoring/runtime을 사용한다. 새 pending receipt를 구 실행기가 검증한다고
보장하지 않으며 migration/downgrade를 수행하지 않는다. 기존 Reference parser 제약을
바꾸지 않는다. Linux 실제 엔진·Chromium 자동화와 실제 Windows/WebView2·물리 기기·
IME/GPU/audio·전체 UI 전수 검증을 구별한다. 과거 초기 빈 화면 원인은 미확정이다.

유한 잔여는 (1) private/독립/retained whole 문맥의 명시 계획 결합, (2) 실제 계약 변경의
callee/import·등록 외부 관측 결합이다. 위 한 흐름의 검증을 마치면 이번 단위를 닫고 가능한
타입/문맥 조합을 새 의무로 늘리지 않는다. 기존 정보별 struct·종류 enum·모듈 interface,
명시 async 전환 전 sync caller 오류·override·권한·배치·원본·백업을 유지하고 main은
사용자의 검토/merge에 남긴다. M11/M12/M4 전체를 다시 여는 작업으로 표현하지 않는다.

이 whole/native 본문 공동 저장 단위의 [최종 신규 41·재사용0 검증과 보관](VALIDATION_V666_WHOLE_NATIVE_BODIES.md)을 마쳤다.
