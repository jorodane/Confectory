# v536 I5-2: 소유 copy 등록·본문 아카이브

이 단위는 기존 연결 보관과 구분하여 현재 정보에 직접 연결된 프로젝트 소유 copy의 등록·구현·모든 선언 본문을 복구 가능한 거래로 보관한다. 물리 파일은 삭제하지 않는다. 함수 선언·핀·공유/부모/등록 팩 원본, 다른 사용처·target은 유지한다. 현재 지원 수명의 구현·격리 화면·checkout·교차 패키지 검증을 완료했다. 전체 I5/v536 복원이나 실제 Windows 실행 완료를 뜻하지 않는다.

## 원본 동작과 범위

기준은 `196c605:reference/site-ui/Confectory-Editor-Prototype-v536.zip`의 `Confectory-v536/dist/app.js`다. `deleteFunctionBody`는 선택 정의의 본문·컴파일/가져오기 표시만 지우고, 모듈 행 삭제는 현재 객체의 로컬 method만 제거하여 상위 fallback을 다시 사용한다. 물려받은 구현 자체의 삭제는 비활성이다. donor/부모 객체는 수정하지 않는다. 원본 카드·확인창·버튼·CSS를 재사용한다.

원본 자체 함수 행에는 모듈 copy/import 선택 동작이 없다. 기존 서버 `readImplementationCopy`도 현재 모듈 요구 슬롯을 검증한다. 테스트가 자체 함수만 있는 정보에 그 API를 호출해 거절된 것은 기존 생성 계약을 벗어난 fixture였다. 이 아카이브 작업을 위해 생성 계약이나 권한을 확장하지 않는다. 모듈의 로컬/상속/등록 출처를 선택하여 실제로 만든 copy 수명을 검증한다.

## 후보와 보호

`information-copy-v1`은 기존 정보 연결 증명과 독립적인 bounded closure를 결합한다. 현재 프로젝트의 명시적 provide·유효한 요구 계약·소유 등록·정확한 구현 경로·부모 없는 copy·Blueprint의 출처/target·모든 본문 locator/hash를 확인한다. 임시 creationOwner만 믿거나 ID 이름만 보고 소유를 판정하지 않는다. 확정 후 cold의 등록/본문 출처도 확인한다.

다른 정보의 provide, 상속 구현, import/wrapper/본문 참조 또는 공유 경로가 있으면 closure를 제거하지 않는다. 현재 정보의 연결만 해제하는 기존 안전한 수명을 유지하거나 안전하게 거절한다. donor, 부모와 등록 팩은 후보에 포함하지 않는다. 숨겨진 접근 범위나 Agent/계정/실행 권한을 추가하지 않는다.

등록·연결·closure·receipt·결과 기록을 한 후보/checkpoint CAS로 처리한다. 실패·경합이면 전체 미적용이며 입력과 기존 초안을 보존한다. 불확실한 응답은 기록을 조회하고 apply를 반복하지 않는다. 원본의 Undo/Redo·복구 메뉴·변경 취소·명시적 Review/Confirm을 재사용한다. 복구 취소 후 재복구는 별도 단계다. 새 provider, 바뀐 함수 계약, 다른 창의 새 입력을 이전 archive로 덮어쓰지 않는다. 읽기 검증은 오래된 기록을 보존하며 실제 복구는 현재 계약/디스크 baseline을 다시 확인한다.

## 재현과 수정

첫 후보는 같은 JsonObject graphs를 두 부모에 재사용하여 거절됐다. 각 읽기 요청에 DeepClone을 사용했다. 후보의 내부 연결 증명 토큰에 이전 plan 토큰이 섞여 같은 source의 apply가 거절된 재현도 수정했다. 외부 checkpoint identity와 무관한 내부 증명은 제거한 token을 다시 포함하지 않고 정규화한다. 실제 확정 후 복구는 이전 논리적 binding을 현재 디스크 baseline 위에서 재검사하여 정상 확정을 오래된 파일로 오인하지 않는다.

보관 증명의 retained 목록에서 본문 한 항목을 뺀 Native fixture가 수용된 것을 재현했다. closure의 각 항목에 경로/종류/hash 증명을 필수로 요구하는 거절 회귀를 추가했다. Native-6 재빌드 후 같은 불완전 증명을 거절하고 정상 후보/apply를 유지하는 집중 회귀를 통과했다.

## 검증 현황

격리 fixture, 실제 엔진·compiler·Chromium만 사용한다. 실제 사용자 프로젝트·계정·유료 추론은 사용하지 않는다. 상세 근거는 `/workspace/scratch/v536-information-copy-archive`다.

| 검사 | 현재 결과 |
|---|---|
| Native-5/6 / Linux engine-3/4 | warnings/errors/stderr 0. Native-6은 필수 proof 누락 거절 보완 포함 |
| 실제 생성 copy의 Native 경계 | Native-6에서 4 PASS(누락 proof 거절 포함): closure apply/recover·공유/상속 참조 보존·변조 거절·live 경합/계약 변경 보호 |
| 실제 API 기본 수명 | normal 2, 쓰기 실패 3, live 경합 1, 미확정 copy 2, 등록 팩 출처 2 PASS |
| API 기존 경계 | 모듈 요구 없는 자체 함수 생성 거절 1, 독립 창 nonce/위조/닫힌 창/primary 보존 1 PASS |
| 원본 독립 창 화면 | 3 PASS: 삭제 취소/Undo/Redo, Browser 복구/cold, Review 취소/Confirm·복구 취소/재복구/Confirm |
| 기존 pure 회귀 | 연결 9, 함수 전체 9, 단독 구현 7 PASS |
| 추가 실제 화면 | 기본 창 3, 쓰기 실패/재시도 4, 응답·조회 유실/cold 1(apply 1회), 프로젝트 전환 1, 다른 창 입력/취소 3, 계획 뒤 경합 1 PASS |
| 깨끗한 checkout | 소스 `1d181c1f0edd5dc6cbfc3a015d1f900cf7759dfd`, Native/Linux warnings/errors/stderr 0, 실제 copy API 2 + 독립 창 화면 3 PASS |
| 리소스 checkout | 실제 CRLF pull/fresh LF 및 canonical/exact 74개, 변조/인코딩/BOM/binary/budget 거절 PASS |
| Windows 교차 패키지 | win-x64 PE 2329파일, SDK 없는 runtime-only에서 패키지 엔진 웹 기동·74개 리소스·최소 연결창 렌더·변조/누락 의존성 거절 PASS |

화면 7회 실행 16개 check와 API 12개 check를 통과했다. Native-6의 독립적인 깨끗한 checkout에서 실제 API 2개·화면 3개를 추가 재현했다. 이 5개는 16/12개와 별도 재현 횟수다. 각 수명 검사에는 실제 compiler Review/Confirm과 반복 cold가 포함된다. 이 문서의 검사 수는 시나리오의 check 수이며 서로 다른 기능 수를 뜻하지 않는다. 실제 Windows apphost/WebView2·모바일 기기 실행과 Library 전달은 미검증이다. 이전 af65e36 패키지는 이 copy closure 변경을 포함하지 않는다. 생성 빌드·로그·프로필은 Git에 포함하지 않는다.

화면 근거는 `evidence/v536-information-copy-retirement/{primary,detached,modal}.png`와 `layout-evidence.json`이다. 카드 폭 460px 및 consumer/style CSS의 기준 `af65e36` byte 일치를 확인했다. 원본 레이아웃과 제어를 유지하며 pixel equality를 주장하지 않는다.

## 로컬 패키지

`/workspace/artifacts/v536-information-copy-retirement/Windows-x64`에 Windows 패키지가 있다. Windows에서는 `Confectory.exe`로 시작한다. `confectory-desktop-package.json` SHA-256은 `95125c319ed683b694c690218c2689988b452e32f4d76bcfdb3d8cb1763f4afe`이며 2329파일이다. 소스 커밋은 `1d181c1f0edd5dc6cbfc3a015d1f900cf7759dfd`이고 이후 문서 마감은 실행 파일을 바꾸지 않는다. 현재 소스/Native와 패키지의 핵심 7개 파일 byte 일치를 확인했다. 테스트 스크립트·인증 파일·프로필·로그는 manifest에 없고 제품에 테스트 우회 API를 추가하지 않았다. 이 로컬 경로는 Library 첨부나 사용자 전달 성공을 의미하지 않는다.

## 고정 후속

I5-1 독립 모듈 편집/가져오기, I5-3 삭제 후 새 구현, I5-4 독립 함수 전체 삭제의 기존 지원을 보존한다. I5-2는 원본 v536이 제공하는 현재 지원 수명 범위로 마감한다. 독점 소유를 증명하지 못한 provider/사용 중 copy는 연결만 보관하며 원본을 유지한다. 진행 중 다른 atomic group이나 호환 불가 계약은 먼저 완료하도록 거절한다. 원본에 없는 자체 함수 copy 생성 API를 새로 추가하지 않았다. I5-5 함수 순서 변경과 I5-6 연결된 함수 전체 계약 편집은 이 단위 다음이다. 새 레이아웃이나 새 편집·실행 체계를 만들지 않는다.
