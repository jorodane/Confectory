# v536 정보 자체 함수의 구현 삭제·복구

기본 창과 독립 properties 창에서 직접 소유하는 자체 함수의 구현을 삭제·복구하는 지원 단위다. 함수 선언·이름·입출력·contain 및 함수 등록은 유지한다. 구현/본문 등록과 해당 정보의 provider 연결만 제외하고 원본 파일과 편집 초안을 보관한다. 최종 반영과 복구의 최종 반영은 각각 별도의 Review/Confirm을 요구한다. 이 작업은 전체 I5 또는 전체 v536 완료가 아니다.

## 지원 경계

첫 지원 범위는 기존에 Confirm한 함수 선언의 원문이 변경되지 않았으며, 해당 정보가 직접 연결한 단독 구현이다. 모든 target의 C#/Blueprint/노드 원문을 하나의 후보·checkpoint CAS에서 처리한다. 다른 곳이 구현을 참조하거나 source/path/기준이 달라지면 부분 적용하지 않는다. 함수 선언 참조는 선언이 남으므로 삭제하지 않는다. 공유·상속 원본과 private copy 출처를 임의 변경하지 않는다.

미확정/편집 중 함수 선언, 상속·copy·공유 구현, 모듈의 새 archive 수명은 이 단위의 지원으로 주장하지 않는다. 기존 모듈 provider 해제 경로는 유지한다. 구현 삭제 후 새 구현을 작성할 때 이전 고정 ID/보관 파일과 새 후보를 분리하는 경로도 아직 미완료다. [정확한 I5 잔여](V536_I5_COMPLETION_CHECKLIST.md)를 별도로 유지한다.

## 서버와 화면

기존 version-2 함수 archive의 기본 수명을 유지하며 명시적 `implementation-only-v1` 모드만 추가한다. 함수 선언 snapshot과 실제 보관 구현의 입출력 계약을 확인하고, 결과 proof에도 남겨 둔 함수의 source/path/kind/hash를 포함한다. 확인할 수 없는 결과나 새 입력을 성공으로 간주하지 않는다.

독립 창은 현재 프로젝트/context, 정보 ID, properties/schema 모드, 창 incarnation nonce와 token의 mode/owner를 서버에서 확인한다. 다른 정보나 닫힌 창의 요청으로 변경할 수 없다. 기존 공용 draft 취소를 일반적으로 허용하지 않고 해당 구현 archive에 한정된 취소만 연결한다. 다른 창의 private 입력과 정확한 값은 보존한다.

원본 구현 삭제 버튼·취소/확인창·Undo/Redo·변경 취소와 기존 Browser 복구 메뉴를 사용한다. Redo에 수명 모드를 보관하여 함수 전체 삭제로 바뀌지 않게 한다. 프로젝트 전환 뒤 은퇴한 callback은 아무 mutation도 만들지 않는다. 새로운 CSS/패널/메뉴나 계정·실행 권한을 추가하지 않는다.

[기본 창 복구 후](evidence/v536-implementation-retirement/primary-restored.png) · [독립 창 복구 후](evidence/v536-implementation-retirement/view-restored.png) · [기존 구현 삭제 확인창](evidence/v536-implementation-retirement/implementation-only-modal.png). 기존 460px 정보 카드와 기존 modal/컨트롤 구조를 사용했다. 전체 pixel equality 또는 네이티브 기기 검증으로 주장하지 않는다.

## 실행한 검증

로그·격리 fixture 경로는 `/workspace/scratch/v536-implementation-retirement`에 보존한다. 반복 시작/준비 단계를 중복 합산하지 않는다.

| 검사 | 실제 결과 |
|---|---|
| Native helper build6 / engine-final Linux | 경고·오류 0 |
| 순수 native 수명/증거 | 새 구현 7 + 기존 함수 전체 archive 9 PASS. source/경로·참조·미확정 선언·동시 수정·복구/취소·변조 계약·완료 proof 보호 |
| 실제 엔진 API normal/storage/conflict | 각각 5/7/2 PASS. 원자 보관·쓰기 거절·cold·중복 조회·별도 compiler Confirm·복구 취소 후 재복구·선언/원본 보존 |
| 실제 엔진 독립 view API | 4 PASS. 누락/위조 nonce·다른 owner/mode/token 거절, 닫기/reopen·cold readonly 조회·primary 선택 보존 |
| 실제 renderer 기본/독립 normal | 각각 4 PASS. 확인창 취소·inert 정리·Undo/Redo·Browser 복구·cold·삭제/복구 Review 취소/Confirm·복구 취소 후 재복구 |
| 실제 renderer 추가 경계 | 기본/독립 쓰기 거절 각각 1, 독립 응답/결과조회 유실+cold 1, 다른 창 원문/exact64 1, 실제 source 경합 1, 기본/독립 실제 프로젝트 A/B 전환 각각 1 PASS. 합계 7 |
| 기존 지원 회귀 | 함수 전체 삭제 UI 5 + 독립 본문 편집 UI 5 + 함수 archive readonly API 3 PASS |
| 깨끗한 checkout `b7f06f3b308c8d6aabb9a6fc6c6a870a885a0088` | native SDK/Linux 엔진 경고·오류 0, 별도 native 16 + view API 4 + 실제 view UI 4 PASS, 실제 CRLF pull/fresh LF와 73리소스·변조/encoding/BOM/binary/budget 거절 PASS |
| Windows x64 교차 패키지·runtime probe | 최종 2,326파일 구성·무관 cwd/runtime-only 엔진 웹 기동·73리소스·최소 로그인 화면·변조/누락 dependency 거절·fixture 기존 프로필 보존 PASS |

새 renderer는 normal 8건과 추가 경계 7건으로 총 15건이며, 기존 회귀 10건은 별도다. fixture만 사용했고 실제 사용자 프로젝트 실행·영구 삭제·로그인·권한부여·유료 추론을 하지 않았다.

## 재현 snapshot과 패키지

구현 snapshot은 `b7f06f3b308c8d6aabb9a6fc6c6a870a885a0088`다. 이 snapshot을 깨끗한 checkout으로 정상 fast-forward하고 native SDK/Linux 엔진을 다시 만들어 새 helper/독립 view 계약/실제 화면을 재현했다. 별도 재현 24건을 root 결과와 중복 합산하지 않는다. 검증 문서 커밋은 runtime에 포함하지 않는다.

로컬 패키지는 `/workspace/artifacts/v536-implementation-retirement/Windows-x64`이며 전체 폴더를 함께 두고 `Confectory.exe`를 연다. manifest SHA-256은 `e651f1b42b7705d902f8367b8ae3c8c9e4914202c1867fd02371fef06a25445b`다. 패키지의 SDK·소스·UI resource가 위 snapshot과 같음을 확인했다. 패키지와 프로필·로그·사용자 자료는 Git에 넣지 않았다.

## 확인하고 고친 결함

복구를 취소한 뒤 cold에서 다시 복구할 때 이전 recover outcome이 정상 재시도를 막았다. 원래 Fn/owner/manifest가 바뀌지 않았고 현재 전체 source를 포함하는 cancel 완료 proof가 맞는 경우에만 명시적 재복구를 허용했다. 실패 기록을 무조건 제거하거나 CAS를 새 기준으로 덮어쓰지 않았다.

독립 창의 변경 취소가 복구 중인 구현을 취소하지 못했다. bound 창의 해당 모드 archive에만 한정된 callback을 추가했고 공용 draft를 취소하는 일반 권한은 확대하지 않았다. 은퇴한 독립 창의 삭제 callback이 프로젝트 전환 뒤 동기 오류를 던지던 경로도 현재 binding이 없으면 mutation 없이 끝나게 수정해 A/B 화면 검사로 확인했다.

보존된 선언 snapshot의 draft/original을 함께 변조하면 다른 반환 타입 증거가 받아들여지는 순수 후보 결함을 재현했다. 실제 보관 구현의 입출력 계약과 일치해야 한다는 검증을 추가하여 거절했다. 타입/전달 방식은 검사하며 매개변수 이름만 다른 정상 계약은 기존 `FunctionSignature.Matches` 의미를 따른다.

첫 primary 화면 검사의 실패는 fixture가 Confirm 뒤 properties 창을 열지 않은 정보를 API로 미리 선택한 채 시작한 준비 오류였다. 기본/독립 모두 다른 기본 대상에서 실제 Browser로 정보 창을 여는 사용자 경로로 준비를 수정했다. 정상 화면 assertion을 제거하지 않았다.

실제 Windows apphost/WebView2, 모바일 기기 및 Library 첨부/전달은 미검증이다. 교차 패키지의 managed 엔진을 Linux에서 여는 검사는 Windows 실행 검증과 구분한다. I6/B2 및 A4~A6/M4/M11/M12는 별도 후속이다.
