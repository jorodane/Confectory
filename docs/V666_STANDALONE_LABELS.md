# standalone 함수의 인자 표시명

원본 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`dist/app.js::renderFeatureDefinition`, `functionSignatureFields`,
`renderFunctionSignatureEditor`는 필드 ID와 표시 이름을 구별한다. 같은 원래 상세창을
쓰는 현재 standalone 경로는 정보 카드의 [인자 표시명](V666_ARGUMENT_LABELS.md)에
opt-in하지 않아 native 서명만 편집했다. 게시 `dcb45391`의 실제 UI에서 표시 메뉴가
없고, 한글 이름이 native 서명 입력으로 남아 Save에서 거절되는 것을 재현했다.

직접 소유 standalone 함수의 같은 460px 카드·420px 상세창·이름칸을 사용한다.
우클릭/Shift+F10으로 **표시 이름 편집**, **C# 이름 편집**, **표시 이름 초기화**를
구분한다. 기본 이름칸은 기존 native 편집이다. 카드의 표시는 별칭을 사용하며
실행 서명·C#·기존 인자 이름/역할/순서/ID·호출 연결은 바꾸지 않는다. 고정 반환
슬롯의 별도 표시 이름과 module/caller/graph의 다른 표시는 이번 단위 밖이다.

선택 metadata `editorArgumentNames`는 기존 native 이름→표시명의 JSON **문자열**이다.
정보 카드와 같은 native 정규화·최대64개·trim된 1–60 UTF-16 문자·control 금지·
입출력 쪽 충돌 검사를 재사용한다. 초기화는 해당 metadata만 제거한다. 원본 map의
잘못된 키·형식도 먼저 검사해, 보이지 않는 잘못된 metadata를 조용히 정리하지 않는다.
`constructor`, `toString`, `__proto__` 같은 정상 native 이름에는 자체 JSON 키만
조회한다. JS 기본 객체의 속성을 표시명으로 읽지 않는다. 공통 정보 카드의 같은
조회도 수정하지만 native 이름과 별도 영구 pin ID를 새로 만들지는 않는다.

표시명·설명·아이콘은 최대3개의 기존 owner cell로 결합한다. `readOwnerEdits` →
`applySlots` → 저장 영수증 확인의 한 후보/체크포인트 CAS를 재사용한다. 실패·취소·
cold·응답 유실과 접수 후 새 입력은 기존 journal/receipt로 구별한다. 이전 apply를
재실행하지 않으며, 새 표시명은 접수된 이전 응답으로 지우지 않는다. 같은 함수의
source-only 이력 조건에서만 Undo/Redo를 이어 준다. 단위 수·kind·경로·다른 원문이
그대로인지 확인하는 조건과 다른 ownership 변경의 이력 경계는 유지한다.

표시 편집과 native 계약 변경을 한 popup에서 동시에 제출하는 것은 이 단위에서
거절하고 popup 입력을 유지한다. 표시명이 있는 인자를 기존 standalone 서명 요청에서
없애거나 다른 이름으로 바꿔 별칭을 잃는 것도 거절한다. 필요한 별칭을 먼저 명시적으로
초기화·저장한 뒤 기존 native 계약 편집/본문·호출자 검토를 사용한다. 별칭이 없는 기존
요청과 같은 이름을 유지하는 요청은 보존한다. `functionSignature`는 이를 검사하는
순수 metadata 작업이며 gateway의 기존 소유·revision/hash·전체 후보 검증을 우회하지
않는다. C# 자동 치환이나 암묵적 별칭 대응을 추가하지 않는다.

## 기존 유한 잔여와 호환성

다른 표시 문맥과 고정7/8행은 [기존 재대조](V666_BOOTSTRAP_RECOVERY.md)를 따른다.
ordinary private/frame/wrapper·같은 계약 native 다중 본문과 caller 보존은 이미 지원한다.
실제 forwarded/opaque 영향 source와 여러 함수의 명시 계약/본문 closure 결합은 잔여다.
새 이름/타입/target의 모든 조합을 추가 필수로 만들거나 M11/M12/M4를 다시 열지 않는다.

새 metadata 문법·schema migration·실행 ABI는 없다. 문자열 metadata를 읽는 구 reader와
새 authoring 작업을 지원하는 writer는 구분한다. 구조를 편집할 때는 이번의 별칭 보존
검사가 포함된 같은 게시 세대의 engine/authoring을 사용한다. 구 설치본을 이 변경으로
소급 수정했다고 주장하지 않는다. 타입별 `Confectory.Reference.*`를 모르는 pretyped
reader의 `TYPE` 거절은 별도 호환 제한이며, 거절 코드만으로 데이터 손상이나 구 버전을
단정하지 않는다. 실제 reader 세대와 선언을 확인하고 원문/ID/profile을 보존한다.
일반 값으로 치환·자동 downgrade하지 않는다. 구 바이너리 비교의 보관 근거는
[직전 검사](VALIDATION_V666_ARGUMENT_LABELS.md)를 참고하며 이번 신규 실행으로 세지 않는다.

과거 간헐적 빈 화면 원인은 미확정이다. [의존 module 실패 안내](V666_BOOTSTRAP_RECOVERY.md)는
별도 재현된 경로이며, 이번 최종 코드의 전송 정체 중 실제3D reload 관찰과 구별한다.
실제 Windows/WebView2·물리 기기·OS IME·GPU/audio·전체 UI 전수 검증은 별도다.
최종 신규/재사용·실패·패키지/전체 복원 근거는 [검증 기록](VALIDATION_V666_STANDALONE_LABELS.md)에 남긴다.
