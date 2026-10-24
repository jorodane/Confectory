# v536 정보 자체 함수 삭제·복구

I5의 기본 정보 카드에서 저장된 자체 함수의 기존 ×와 Browser의 기존 `삭제 항목 복구`를 실제 작업 사본에 연결했다. 미확정 생성 함수도 본문 유무에 따라 같은 경로를 사용한다. 정보·함수·등록·단독 소유 구현과 그 구현의 모든 target 본문/graph/node를 함께 보관한다. 원본 파일은 영구 삭제하지 않으며 최종 등록 변경과 복구 반영은 별도의 명시적 Review/Confirm을 요구한다.

원본 v536(`196c605`)의 카드·확인창·메뉴·변경 취소와 함수 pane의 Undo/Redo를 사용한다. CSS/레이아웃을 바꾸지 않았고 실제 정보 카드 폭은 460px이다. [삭제 전](evidence/v536-information-function-retirement/before.png)과 [복구·확정 후](evidence/v536-information-function-retirement/after.png)를 기록했다. 삭제 Undo는 archive 복구이고, Redo는 최신 계획을 읽은 뒤 새 명시적 삭제를 요구한다. 소유권 변경 전에 쌓인 다른 소스 편집 이력은 기존 보호 경계를 유지한다.

## 저장 계약

삭제 계획은 현재 정보/함수 hash, 직접 소유 생성 identity, 정확한 등록 locator, 원래 source baseline 및 전체 workspace 관측에 묶인다. 참조와 소유권은 서버가 실제 선언에서 검사한다. 다른 정보·부모·등록 팩·공유 구현·관련 입력이 남은 다른 창을 추측하여 수정하지 않는다. 알려진 typed import, 함수 값 타입, 모듈 요구, provide 및 기본값 참조는 삭제를 차단한다. 임의 C# 문자열이나 자연어에 있는 모든 사용처를 증명한다는 의미는 아니다.

공통 Save 게이트가 native 순수 후보를 별도 workspace에 구성하고 하나의 checkpoint CAS로 저장한 후 live 상태를 바꾼다. 삭제, 복구, 복구 취소, 정보/Browser 변경 취소가 이 게이트를 공유한다. 쓰기 실패는 전체 미적용이며 기존 초안과 입력을 보존한다. 새로 생성한 source의 `missing` baseline은 생성 소유/locator/파일 부재를 검증하고, 삭제 후보의 빈 `original`을 최종 파일로 쓰지 않는다. 다른 생성·계약 그룹까지 버려야 하는 선택은 거절한다.

제한된 완료 receipt를 checkpoint에 보관한다. workspace·phase·모든 관련 source의 identity/path/kind/hash와 없는 ID를 다시 확인한다. 응답이 끊기면 읽기 전용 `browserArchiveOutcome`로 완료, 원래 기준의 미적용, 확인 불가를 구분한다. 확인 불가를 성공이나 재시도 허용으로 추측하지 않는다. UI의 요청 journal도 재시작까지 보관하고, 다음 명시적 작업 전에 이전 결과부터 확인한다. 실제 새 source/입력은 이전 완료 근거로 덮어쓰지 않는다. 최종 Confirm이나 실행 권한은 추가하지 않았다.

확인한 실제 결함은 변경 취소의 live 복구 후 checkpoint 쓰기 순서와 삭제 후 정보 카드의 오래된 projection이다. 전자는 실패 fixture로 재현한 뒤 공통 원자 Save에 연결했다. 후자는 실제 화면에서 삭제가 저장되어도 함수가 남아 보이던 것으로, 아직 선택된 같은 프로젝트/기본 정보 창만 최신 schema를 읽어 다시 표시한다. 읽기 전용 계획/결과 조회는 source와 전체 version이 동일할 때만 기존 projection을 유지한다.

## 집중 검증

사용자 프로젝트 대신 격리 fixture·실제 엔진·Chromium을 사용한다. 계정 로그인, 권한 부여, 유료 추론, 사용자 프로젝트 실행은 하지 않았다. suite 재실행의 중복 통과는 합산하지 않는다.

| 검사 | 확인 범위 |
|---|---|
| `v536_information_function_retirement.py` | 순수 native 9 PASS. 완전한 여러 target closure, 정확한 64비트 값/주석/미반영 본문, 다른 소유/참조/변조·scope 차단, pending/confirmed 복구 및 새 입력 취소 거절 |
| `_api.py normal/storage/conflict` | 기존 실제 엔진 4/2/2 PASS. 여러 target의 전체 삭제·복구·compiler Confirm, 실제 저장 거절과 source/초안 경합 |
| `_api.py discard-storage/outcomes` | 2/3 PASS. 변경 취소 쓰기 거절의 live/disk 미적용, 복구/취소 완료 receipt·cold·새 입력 보호 |
| `_api.py queries/pending-bare/pending-body` | 3/2/2 PASS. 무쓰기 결과 조회·잘못된 token·확인 불가, 미확정 함수/전체 본문의 삭제·cold·복구·새 Confirm |
| `_ui.py normal/pending` | 각각 5 PASS. 기존 ×/확인창 취소, Undo/Redo, 정보 변경 취소, Browser 복구·cold, 삭제/복구 Review 취소·명시적 Confirm 및 원본 전체 복원 |
| `_ui.py storage/loss/loss-cold/guards` | 각각 1 PASS. 쓰기 실패의 명시 재시도, 실제 성공 응답 변조 유실 후 읽기 조회, 결과 조회까지 유실된 journal cold, 같은 정보의 독립 창 설명/정확한 값 보호 |

실제 renderer 집중 suite는 위 14건과 `_ui.py projects` 2 PASS로 총 16건이다. 프로젝트 검사에서는 같은 native ID를 가진 A/B의 실제 Home 재진입, 은퇴한 삭제 callback 무효, B 삭제의 checkpoint 분리와 양쪽 최종 소스 보존을 확인했다. B fixture의 아직 없는 깨끗한 checkpoint는 fixture의 명시 Save로 준비한 뒤 바이트 보존을 비교했다.

초기 UI fixture는 `sourceConfirmed`를 확인하지 않아 비어 있는 scaffold를 확정본으로 잘못 간주했다. 실제 검증은 `BLUEPRINT_NOT_READY`로 정확히 차단했다. fixture에 유효한 본문을 준비하고 실제 compiler Confirm 성공을 필수로 확인하도록 강화했다. 복구 Confirm 뒤 원래 삭제 상태 바이트가 유지되어야 한다던 잘못된 기대도 원래 등록/소스 전체 바이트의 복원 검사로 고쳤다. 이전 실패 로그를 보존했고 보호 조건이나 실패 assertion을 제거하지 않았다.

게시 전 깨끗한 checkout/회귀 및 Windows 교차 패키지 결과는 완료 후 아래에 기록한다. 현재 문서의 집중 통과 범위를 전체 I5 또는 전체 v536 UI 완료로 해석하지 않는다.

## 남은 범위

- 독립 properties 창의 구현 선택·복사·본문 편집과 함수 삭제는 후속 단위다. 현재 미연결 동작의 차단을 유지한다.
- 함수 자체를 보관 삭제하는 이번 경로와 별개인 구현만 삭제·복구, 자체 함수 순서 변경, 연결된 서명 전체 변경은 미완료다.
- I6 아이콘/B2 실제 배지, A4~A6/M4/M11/M12 및 기존 raw/다른 계획 결합 제한은 각각 기존 목록을 유지한다.
- 실제 Windows apphost/WebView2 및 실제 모바일 기기 실행, 실제 계정 및 Library 첨부 전달은 미검증이다. 로컬 패키지 생성과 전달 성공은 구분한다.
