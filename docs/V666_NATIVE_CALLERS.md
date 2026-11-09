# 여러 본문 편집에서 C# 호출자 원문 보존

고정 [I5-6 8행](V536_I5_6_REMAINING.md)의 정보 한 창·한 Save에서 여러 함수
본문을 편집하는 흐름이다. 원본 기준은 저장소 v666 ZIP
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의
`app.js` 안 `openOwnFunctionPopover`와 `renderFeatureDefinition`, 기존 native 계약과
`InformationFunctionContracts.Prepare`의 `unchangedConsumer`다. 다른 문맥의 가능한
모든 조합을 새 필수로 만들지 않는다. [기존 로컬 import 본문 그룹](V666_NATIVE_BODY_IMPORTS.md)을
보존하며 원래 8행의 수동 C# source closure 연결 중 현재 재현되는 한 흐름을 닫는다.

게시 `08627e24`에서 직접 소유한 두 C# 본문의 단일 후보는 각각 유효했고, 그대로인
C# 호출자의 실제 프로그램은46을 반환했다. 두 본문을 함께 저장할 때만
`InformationFunctionBodyBatch`의 Blueprint-only caller 제한으로 거절됐다. 기존
원본 계약이 같은 native C# 소비자 유지 경로를 그룹에도 연결한다. 호출자의 C#·
import alias·native/public 매개변수 이름·타입·역할·반환은 자동으로 재작성하지 않는다.
원본 UI의 기존 ‘구현 선택’에서 편집할 **이 기능**의 정확한 target을 선택한다.
호출자도 선택지에 보인다는 사실을 무시하던 첫 검사 시간 초과는 제품 실패와 구분한다.
선택창/코드 편집창·레이아웃·저장 버튼과 client 코드는 변경하지 않는다.

지원 범위는 직접 소유한 단일 native C# target 함수 2~8개를 같은 계약으로 편집하고,
그 함수를 import하는 직접 소유 native C# 호출자 원문을 그대로 유지하는 경로다.
기존 ordinary Blueprint 호출자와 공존할 수 있다. C# 호출자는 모든 원래 target
source가 관측돼 있어야 하며 import는 같은 프로젝트 소유 함수의 정확한 typed 계약이어야 한다. 부모/외부 쓰기, 임의
호출자 편집 계획·누락 source·stale 계약은 기존 검증과 한 후보/CAS에서 거절한다.
새 C# 해석/자동 코드 변환이나 override 입출력 변경·새 권한 정책은 없다.

기존 `informationBodyGroupGuards`는 callee가 import 없는 leaf여도 **C# 소비자가
있으면** 이미 관측한 소유 source 전체의 original read scope를 version3 receipt에
보존한다. Review/cold는 현재 ProjectContext의 알려진 소유 implementation 헤더를
기존 Read로 읽고, 저장한 readGuards의 hash를 재기준화하지 않는다. 기존 Save의
240 read+write/2048 known unit 예산·Review 검증·Confirm 최종 source lease를 그대로
사용한다. 명시한 두 본문과 기존 정보/함수 metadata를 저장하며, 호출자는 읽기 의존성으로 유지한다.

C# 소비자가 없는 구 leaf/ordinary Blueprint 그룹의 빈 readGuards는 기존 범위대로
유효하다. 새로운 receipt 버전·문법·ABI가 없으며 강제 마이그레이션을 만들지 않는다.
새 흐름의 native caller receipt가 빠진 경우는 전체를 보존·거절한다. 구 reader와
모든 checkpoint 교환을 실행한 것으로 과장하지 않는다.

생성한 격리 fixture의 호출자는 CRLF·Unicode 주석·C# 별칭 left/right와 First/Second를
갖는다. imported callee의 원래46→명시 편집26, leaf callee의 원래40→명시 편집20을
실제 Linux 생성 코드로 확인한다. 정상 Confirm 뒤 호출자의 bytes/inode/mode/mtime
보존과 선언·헤더·본문의 Save/Review 이후 peer 변경 거절·입력/cold 복구를 구분한다.
확정 검사와 보관 SHA는 [최종 기록](VALIDATION_V666_NATIVE_CALLERS.md)에 마감한다.

copy/상속/등록·private/whole/wrapper·계약 변경의 실제 다중 closure, 고급 타입/핀
표시명은 기존7/8/9행 잔여다. 종류 CLR/사용 중 삭제와 실제 identity/group backend의
미결 정책을 임의로 정하지 않는다. M11/M12/M4를 근거 없이 다시 열지 않는다.
초기 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·모바일·물리 IME·전체 UI·
사용자 프로젝트·Space/Library 전달은 Linux/Chromium·교차 패키지와 별도 미검증이다.

최종 runtime `6a9b48d2af44eb4fa0227d80b164c24f17bcd164`의 신규41단계·재사용0을 통과했다. 개발24통과/2실패와 클릭 요청 미발행 원인 미확정은 최종 기록에서 구분한다.
