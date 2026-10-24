# v536 I5-4 독립 정보 창 함수 전체 삭제·복구

원본 정보 카드의 자체 함수 × 삭제, 기존 확인창과 Browser 복구 메뉴를 기본 창과 같은 복구 가능한 거래로 연결했다. 구현만 삭제와 달리 함수 선언/contain 등록과 단독 구현/본문 등록을 함께 작업 사본에서 제외하며 실제 소스 파일은 보관한다. 삭제 및 복구의 최종 반영은 각각 별도 Review/Confirm을 요구한다. 기존 v536 CSS/레이아웃과 계정·프로젝트 실행 권한은 변경하지 않았다.

## 서버와 입력 경계

현재 프로젝트/context·정보 properties 창·정보 ID·창 수명 nonce를 확인한다. 계획은 해당 정보의 단일 자체 함수에 대한 정확한 information selection만 허용하고 기존 native 소유권/참조/원본/CAS 검사를 사용한다. 임의 Browser 삭제나 독립 창의 직접 Confirm 권한을 추가하지 않는다. 거래 token은 서버의 계획/archive/지속 outcome에서 같은 정보 owner와 알려진 수명 모드 및 함수 식별성을 확인한다. 알 수 없는 모드·위조/누락 nonce·다른 창/owner token은 거절한다.

닫힌 창이나 실제 프로젝트 A/B 전환 뒤 은퇴 callback은 새로운 삭제 계획을 만들지 않는다. 같은 정보의 다른 창에 원문/정확한 64비트 입력이 있으면 계획 전에 차단하고 cold 후 입력도 유지한다. 저장 결과가 불확실하면 journal을 보관하고 readonly outcome을 조회하며 mutation을 추측해 재전송하지 않는다. 미확정 생성 함수도 기존 생성 그룹의 복구/명시적 확정 경계를 유지한다.

## 확인한 결함과 수정

독립 창의 변경 취소는 구현만 삭제 모드만 허용했고 일반 함수 archive의 `mode:null`을 발견하지 못해 비활성 상태로 남았다. 알려진 일반 함수 수명도 현재 정보의 pending/restoring archive에 한해 취소하도록 연결했다. 일반 shared-draft 취소를 허용하지 않았다.

초기 연결에서 지속 완료 outcome에 없는 `function` 필드를 검사하면 cold 완료조회가 거절되었다. 살아 있는 계획/archive의 function, 구현-only outcome의 retainedFunction, 전체 함수 outcome의 보관 ID에서 동일한 함수 식별성을 확인하고 기존 native 결과 proof 검증을 유지했다. 실제 전체/구현-only API로 cold 및 닫힘 nonce를 재검증했다. 실패 로그와 fixture는 scratch에 보존한다.

## 실행한 검증

격리 fixture와 실제 엔진/Chromium/compiler만 사용했다. 실제 사용자 자료·계정·유료 모델을 사용하지 않았다. 로그는 `/workspace/scratch/v536-i5-detached`다.

| 검사 | 실제 결과 |
|---|---|
| Linux 엔진 engine-2 | warnings 0, stderr 0 |
| 독립 전체 함수 API + 구현-only API 회귀 | 각각 4 PASS. 위조/타창/unknown mode·닫기/reopen nonce·primary 입력 보존·cold readonly 완료조회 |
| 독립 함수 전체 삭제 정상/미확정 생성 | 각각 5 PASS. 모달 취소/inert·Undo/Redo·변경 취소·Browser 복구·cold·Review 취소·삭제/복구 Confirm·복구 취소 후 재복구 |
| 독립 추가 화면 경계 | 쓰기 거절 1, 실제 source 경합 1, 응답/결과조회 유실+cold 1, 다른 창 exact64 원문 1, 실제 프로젝트 A/B 전환 2 PASS |
| 기존 화면 회귀 | 기본 창 전체 함수 삭제 5 + 독립 구현-only 삭제 4 PASS |
| Windows x64 교차 패키지 및 관리 엔진 web probe | manifest 2,326 runtime files, 무관 cwd/runtime-only·73리소스·변조/누락 dependency 거절·fixture profile 보존 PASS |
| clean checkout `473405911be0307d19e6c9d14b5e6648e54592d4` 재현 | 별도 Linux 빌드 warnings/stderr 0, API 4 + 실제 독립 UI 5 PASS, 실제 CRLF pull/fresh LF·73 canonical 리소스·변조/encoding/BOM/binary/budget 거절 PASS |

구현 snapshot은 `473405911be0307d19e6c9d14b5e6648e54592d4`다. 신규 독립 함수 화면 16건과 기존 화면 회귀 9건은 별도로 센다. 별도 checkout의 API 4/UI 5 재현은 root 결과와 중복 합산하지 않는다. API 4+4는 공통 준비 검사가 있어 고유 조작 수로 합산하지 않는다. native archive 알고리즘은 변경하지 않았다. [460px 원본 카드](evidence/v536-i5-detached/function-before-delete.png)와 [최종 복구 후](evidence/v536-i5-detached/function-after-recovery.png)를 보존했다. 카드·기존 버튼 구조/치수를 확인했으며 전체 pixel equality라고 주장하지 않는다.

## 패키지 및 남은 범위

로컬 패키지는 `/workspace/artifacts/v536-i5-detached/Windows-x64`이며 전체 폴더를 함께 두고 `Confectory.exe`를 연다. manifest SHA256은 `8749d9eade1d235a468a6206537e1acaebfdeec42d09676666591bebcbd7b23d`다. 실제 Windows apphost/WebView2와 모바일 기기 실행 및 Library 전달은 미검증이다. 패키지/프로필/로그는 Git에 포함하지 않는다.

[고정 여섯 I5 항목](V536_I5_COMPLETION_CHECKLIST.md) 중 I5-4 지원 경로만 마감한다. I5-1 독립 모듈 편집/가져오기는 아직 차단되어 있고, I5-2 확장 삭제 수명·I5-3 새 구현 생성·I5-5 함수 순서·I5-6 연결된 함수 계약은 미완료다. I6/B2 및 A4~A6/M4/M11/M12나 Helper 실제 작업은 이번 변경에 섞지 않았다. 전체 I5/v536 완료가 아니다.
