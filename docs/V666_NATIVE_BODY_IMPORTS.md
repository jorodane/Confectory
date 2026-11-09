# 여러 C# 본문의 기존 로컬 import 보존

고정 [I5-6 8행](V536_I5_6_REMAINING.md)의 정보 한 창·한 Save에서 여러 함수
본문을 편집하는 기존 흐름이다. 기준은 저장소 v666 ZIP(SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의
`Confectory-v666/dist/app.js` 안 `openOwnFunctionPopover`,
`renderFunctionSignatureEditor`, `renderFeatureDefinition`과
[기존 같은 계약 본문 그룹](VALIDATION_V536_INFORMATION_SHARED_BODIES.md)이다.
원본은 소유 함수의 본문 편집과 정보 저장을 제공한다. import 편집기나 새 화면을
만드는 요구가 아니다. 게시 `8feef782`에서 기존 로컬 함수를 호출하는 두 native
본문의 단일 후보는 각각 유효했지만 그룹 Save는 `native leaf targets`로 거절됐다.
원래 프로그램은 실제 Linux 생성 코드로 컴파일·실행하여 46을 반환했다.

이번 범위는 직접 소유한 함수 2~8개, 각 단일 C# target의 기존 직접 로컬 함수
import, 공개/native 서명과 핀 identity를 유지하는 명시 본문 편집이다. import는
같은 프로젝트 소유 함수이고 부모가 없으며 원래 typed signature와 정확히 같아야
한다. 기존 단일 후보의 검증과 합성·원래 hash/CAS를 재사용한다. ordinary Blueprint
공유 caller와 미선택 helper/선언/import/주석·CRLF·64비트 값은 그대로 보존한다.
본문 두 개만 명시적으로 바꾼 뒤 같은 프로그램의 실제 결과는 26이다.

검사 중 실제 결함도 발견했다. Save 시 관측한 helper가 Review 뒤 바뀌어도 기존
비copy receipt에는 읽기 CAS가 없어 두 본문이 Confirm될 수 있었다. 원래 실패 입력과
물리 쓰기 증거를 보존했다. 이제 이미 읽은 소유 source snapshot을 **쓰기 대상과
분리한 기존 version3 `readGuards`**에 저장한다. Review/cold에서 소유 구현 원문과
완전한 경로·hash 범위를 재검증하고 기존 Confirm의 최종 source lease로 전달한다.
선택 본문 외 helper/호출자를 쓰거나 외부 접근권한을 추가하지 않는다. 새 receipt
버전·문법·공개 ABI·code generation·권한 정책·레이아웃 변경은 없다.

한 그룹의 기존 read+write 합계240 예산을 지킨다. 새 guard 계산은 알려진 unit2048 안으로 제한한다.
범위 누락/변조·이전 Review 뒤 원문 변경은 저장 입력을 유지하며 거절한다. 정확한
원문을 복구한 뒤 명시적으로 재검토할 수 있다. 구형 leaf 그룹의 빈 readGuards는
이 새 import 요구에 해당하지 않는다. 구 reader와 실제 checkpoint 교환은 별도
실행하지 않았으므로 호환 완료로 표현하지 않는다. 기존 version3 필드/최종 lease를
재사용한다는 소스 대조와 구 leaf 후보 회귀를 구분한다.

외부/부모/copy·private/whole/wrapper·계약 변경의 다중 소스 closure는 기존 고정
7/8행 잔여이며 이번 지원으로 자동 완료되지 않는다. 한 Save의 모든 선택 타입·문맥
조합을 새 필수 요구로 늘리지 않는다. 고급 함수 타입·핀 표시명/native ID의 9행,
실제 identity/group 권한 backend와 종류 CLR 표현/사용 중 삭제의 미결 정책은 별도다.
M11/M12/M4의 닫힌 범위를 다시 열지 않는다. 초기 빈 화면의 원인은 미확정이다.

검증 상세와 보관 해시는 [최종 기록](VALIDATION_V666_BODY_IMPORTS.md)에 마감한다.
이 단위의 실제 UI는 Linux Chromium과 native engine의 격리 생성 fixture이며 실제
Windows/WebView2·모바일·물리 IME·전체 UI·사용자 프로젝트/계정 검증은 아니다.

최종 runtime `2897f3709cd44cf10c954ed9dd6a578dd421ec3d`의 신규13·동등재사용25, 유효38단계를 통과했다. 개발23통과/4실패·첫 최종33통과/패키지 경로1실패와 증거 재사용 근거는 최종 기록에서 구분한다.
