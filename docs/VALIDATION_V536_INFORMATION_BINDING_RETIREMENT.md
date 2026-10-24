# v536 I5-2: 정보의 구현 연결 보관·복구

기존 `구현 삭제`에서 현재 정보가 직접 연결한 provide만 보관하고 복구한다. 공유 구현·부모 구현·등록 팩·저장 copy의 구현/본문/등록은 유지한다. 이 문서는 `af65e36`의 연결 보관 단위이며 copy 자체의 등록·본문 아카이브와 구분한다. 당시 분리한 후속 단위는 VALIDATION_V536_INFORMATION_COPY_RETIREMENT.md에 기록한다. 이 두 수명 단위를 전체 I5/v536 복원 완료로 표시하지 않는다. I5-5 함수 순서와 I5-6 전체 계약 편집은 후속이다.

## 변경과 보호 경계

`information-binding-v1` 후보는 현재 프로젝트의 정보 ID·실제 로컬 provide·선언된 자체 함수 또는 모듈 요구·유효한 제공 계약을 확인한다. shared/parent/copy의 원문을 삭제하거나 다른 사용처를 수정하지 않는다. 상위에서 물려받은 연결만 있는 행은 삭제할 수 없다. 로컬 override를 해제하면 실제 상위 provider가 다시 표시된다.

정보 자체 함수의 기존 단독 구현 아카이브는 유지한다. 공유 참조·상속·copy 때문에 원본을 분리해야 하는 경우에만 검증된 연결 보관 후보로 전환한다. 자체 함수의 확정된 선언·핀과 원문 보존 조건도 유지한다. unknown mode, 잘못된 owner/구현, 다른 프로젝트와 독립 창의 누락·오래된 nonce는 거절한다. 이 토큰은 에디터의 로컬 초안 거래 근거이며 Agent/계정/실행 권한을 부여하지 않는다.

기존 삭제 확인창·Undo/Redo·Browser 복구 메뉴·변경 취소·Review/Confirm을 사용한다. 같은 후보와 checkpoint CAS 안에서 저장하며 실패가 나면 입력과 기존 초안을 유지한다. 성공 여부가 불명확하면 기록을 조회하고 apply를 반복하지 않는다. 다른 provider나 제공 계약/본문이 바뀌었으면 이전 기록으로 덮어쓰지 않는다. 오래된 기록은 읽을 수 있지만 복구 동작은 현재 근거를 다시 검증한다.

아직 확정하지 않은 copy가 이미 작업 사본에 있으면, 그 기존 구현과 본문도 명시적인 검토 묶음에 남긴다. 연결을 해제했다는 이유로 생성된 원문이 Review에서 빠지거나 부분 반영되지 않는다. copy를 제외한 불완전 Review는 거절한다. 여기서 새 copy를 생성하거나 자동 확정하지 않는다.

모듈의 삭제 이벤트는 캡처한 프로젝트, 연결된 DOM 행, 현재 원문 revision/hash를 확인한다. 닫힌 A 프로젝트의 행이 같은 이름의 B 프로젝트에 동작하지 않도록 한다. 기존 HTML/CSS·카드·버튼 배치는 바꾸지 않았고 삭제 설명만 연결 보관의 실제 범위에 맞췄다.

## 재현해서 고친 결함

완료 기록만 남고 변경 항목이 없는 재시작에서는 owner가 아직 lazy 상태일 수 있다. 완료 기록의 경로/identity 검증이 불필요하게 로딩된 draft를 요구해 프로젝트 열기를 막았다. 읽기 전용 locator 검증과 실제 동작의 source 검증을 분리했다. 실제 엔진의 삭제·복구·확정 뒤 cold를 다시 통과했다.

미확정 copy를 연결 해제하면 기존 동적 생성 묶음이 provide를 따라 찾지 못해 copy가 Review에서 빠졌다. 이미 소유한 생성 원문을 명시적인 reviewIds/reviewCreation에 포함하고 Changes/Accept가 전체 묶음을 확인·정리하게 했다. 전체 반영, 불완전 검토 거절, 복구 취소와 재시작을 실제 엔진에서 확인했다.

실패한 명령은 live 원문은 남기면서 캐시된 투영이 없을 수 있다. 검사는 투영이 있다고 가정하거나 새로고침으로 상태를 고치지 않고, 정확한 live provide와 화면·checkpoint를 확인한 뒤 원래 재시도 버튼을 사용한다. 열려 있는 확인창의 정상 inert와 닫힌 뒤 남는 inert도 구분한다. 실패 로그와 fixture를 보존하며 assertion을 삭제해 통과시키지 않았다.

## 확인한 범위

격리된 실제 엔진·Chromium·compiler만 사용한다. 실제 사용자 자료·계정 로그인·유료 추론은 사용하지 않는다. 증거는 `/workspace/scratch/v536-information-binding`에 남긴다. 검증된 연결 수명을 copy 자체 아카이브나 모든 UI 기능 완료로 확대해 표현하지 않는다.

| 검사 | 결과 |
|---|---|
| Native build-6 / Linux engine-4 | warnings 0 / errors 또는 stderr 0 |
| 새 pure 후보 | 9 PASS: 공유/상속 슬롯·저장 copy·공유 자체 함수, 변조/경합, 복구 취소·새 provider/본문 변경 차단 |
| 기존 pure 회귀 | 함수 전체 아카이브 9 + 단독 구현 7 PASS 유지 |
| 실제 API | 공유/상속 2, 미확정 copy 3(불완전 Review 포함), view 경계 1, 쓰기 실패 3, 등록 소스 2, 공유 자체 함수 2, 확정 copy 2, 경합 1 PASS |
| 기본/독립 실제 화면 | 각각 3 PASS: 원래 카드/확인창, 삭제 취소·Undo/Redo, fallback, 기존 복구 메뉴, cold, Review 취소/Confirm, 복구 취소 후 재복구 |
| 화면의 쓰기 실패 | 4 PASS: live/disk 미적용, 원래 버튼의 명시 재시도 후 전체 정상 흐름 |
| 화면의 성공 응답·조회 유실 | 독립 창 1 PASS: journal/cold/읽기 결과 조회·복구, apply 1회 |
| 화면 프로젝트 전환 | 독립 창 1 PASS: 같은 namespace의 A/B 전환에서 닫힌 A 행 이벤트는 거절하고 B의 명시 삭제만 B checkpoint에 반영 |
| 화면 취소·다른 창 입력 | 독립 창 3 PASS: Undo/Redo·복구 메뉴·cold·변경 취소 동안 다른 창의 설명과 exact64 입력 2개를 보존 |
| 화면 동시 입력 | 독립 창 1 PASS: 계획 뒤 peer 원문은 유지하며 연결·checkpoint 전체 미적용. DSL의 한글 JSON escape는 파싱해서 확인 |
| 화면 미확정 copy·공유 자체 함수 | 독립 창 각각 3 PASS: 기존 원문/등록 보존, 완전 Review/Confirm·취소·cold·복구 흐름 |
| 깨끗한 checkout 재현 | 소스 `2d0f3e58c4310fabab03e2966e5fbb6106ca0bda`, Native/Linux build warnings·errors 0, 미확정 copy 실제 API 3 + 독립 창 공유 자체 함수 실제 화면 3 PASS |
| 리소스 checkout | 실제 CRLF 유지 후 pull 및 fresh LF, canonical/exact 74개·내용/인코딩/BOM/binary/budget 거절·원래 byte 보존 PASS |
| Windows 교차 패키지 | win-x64 PE 구성 2328파일, 패키지 엔진 runtime-only 웹 기동과 74개 리소스·최소 연결창 렌더 PASS; Windows apphost/WebView2 실행 미검증 |
| 영향받는 실제 API 회귀 | I5-1 창별 module basis 4, I5-3 삭제 후 새 구현 4, I5-4 함수 전체 삭제 4 PASS |

실제 API 16개 check, 실제 화면 9회 실행의 22개 check를 통과했다. 회차/fixture가 다른 중첩 시나리오의 검사 수이며 서로 다른 기능 수를 뜻하지 않는다. Windows x64 교차 패키지 생성과 구성 검사, SDK가 없는 runtime-only 환경에서 패키지 엔진의 실제 web 기동·74개 리소스·기존 프로필 재사용·변조/누락 의존성 거절을 통과했다. 현재 소스/Native와 패키지 7개 핵심 파일의 byte 일치를 확인했다. 별도 깨끗한 checkout의 재빌드·실제 API 3개 및 화면 3개 재현도 통과했다. 이 6개는 앞선 16/22개 회귀와 별도 재현 횟수다. 실제 Windows apphost/WebView2, 실제 모바일 기기와 Library 전달은 미검증이다. 생성 빌드·로그·프로필을 Git에 포함하지 않는다. 패키지 manifest에 이 작업의 테스트 스크립트·인증 파일·프로필·로그가 없음을 확인했고, 테스트 전용 우회 API를 제품에 추가하지 않았다.

## 로컬 패키지와 화면 근거

패키지: `/workspace/artifacts/v536-information-binding/Windows-x64` (`Confectory.exe`는 Windows에서 시작). manifest `confectory-desktop-package.json`의 SHA-256은 `a9a54cd12006cb36ac24c49d7b2b2f0d3ed531dd6d1179f758ef738a464f12f1`, 파일 수는 2328개다. 생성물은 Git에 포함하지 않았다. 이 로컬 경로는 Library 첨부 또는 사용자 전달 성공을 의미하지 않는다.

화면 증거는 `evidence/v536-information-binding/{primary,detached,modal}.png`, 측정은 `layout-evidence.json`이다. 카드 폭 460px, 기존 consumer/style CSS는 기준 `943e4d8`과 byte 동일하다. 기존 HTML/제어를 유지하고 삭제 설명만 변경했으며 pixel equality를 주장하지 않는다.

## 고정 잔여

이 문서는 `af65e36`의 연결 보관 단위를 기록하며 당시 copy closure 아카이브는 미구현이었다. 후속 소유 copy 등록·본문 수명은 [VALIDATION_V536_INFORMATION_COPY_RETIREMENT.md](VALIDATION_V536_INFORMATION_COPY_RETIREMENT.md)에 기록한다. 공유/부모/사용 중 copy는 이 문서의 연결 수명을 계속 사용하며 원문과 등록을 유지한다. 영구 삭제·새 레이아웃·권한 확장은 포함하지 않는다.
