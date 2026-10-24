# v536 정보 자체 함수: 기본 창 본문 편집

I5의 기본 정보 창에서 자체 함수의 기존 `직접 작성`·`편집`을 실제 정보 소유 구현에 연결했다. 저장소 v536(`196c605`)의 카드·본문 편집 화면을 재사용하며 CSS나 레이아웃을 변경하지 않았다. 표시 이름과 native identity를 분리한다. 독립 properties 창의 본문 편집과 저장된 함수 삭제·복구는 아직 미연결이므로 I5 전체 완료는 아니다.

첫 구현을 열기 전에 해당 정보의 미저장 정의·이름·핀·기본값을 기존 임시 저장 경로로 보관한다. 정보·함수·등록의 현재 proof와 실제 source baseline을 확인하여 정보의 직접 `provide`, 구현, graph/node 전체를 같은 checkpoint 후보/CAS로 저장한 뒤 화면을 연다. 함수 자체의 전역 기본 구현, 부모·다른 정보·다른 target을 바꾸거나 자동 Confirm하지 않는다. 이 준비 동안 현재 정보의 입력만 잠깐 보호하고 종료·실패·프로젝트 변경 시 정리한다. 앱 전체에 inert를 걸지 않는다.

직접 소유하고 단독 배정한 schema 구현의 C# source·노드 설명·구현 설명 저장은 기존 authorBatch/settledAuthorBatch에 한정해 연결했다. 원래 checkpoint, 전체 source identity/hash, 소유 경로·실제 source baseline과 링크 검사를 통과해야 한다. staged 후보의 각 편집은 fresh CAS를 사용하며 디스크 checkpoint 저장이 확인된 다음 live 상태와 private 입력을 정리한다. 공유·복사 provenance·구조/ABI 등 다른 경로를 이 plain 저장 계약으로 허용하지 않는다.

성공 응답이 유실되면 같은 attempt/plan/checkpoint/owner와 전체 source receipt를 조회한다. 적용 여부를 추측해 재생성하거나 입력을 지우지 않는다. 재시작으로 바뀌는 process-local revision만 동일 전체 source 근거로 복구하고 실제 source/checkpoint 변경은 거절한다. 저장 도중 늦게 생긴 설명은 확인된 성공 source proof에만 결부해 남긴다. 저장 직전에 창을 닫으면 완료 콜백이 창을 다시 열지 않으며 원래 입력·저장 기록은 다음 진입에서 확인한다.

본문만 재편집한 경우에도 정보의 검토 상태를 갱신하고 정보·함수·구현·본문의 완전한 기존 검토 그룹을 보존한다. 최종 원본 반영은 새 Review와 사용자의 명시적 Confirm을 요구한다. 원래 코드·주석·정확한 long 값, 다른 프로젝트/창의 입력과 계정·Agent 승낙/실행 권한은 그대로 보존한다.

## 실제 검사

다음은 서로 다른 집중 suite의 총 **27 PASS**다. 중복 실행의 이전 통과를 더하지 않았다. 실제 엔진·Chromium 및 격리 fixture를 사용했으며, 사용자 프로젝트 실행·실제 계정·유료 추론은 하지 않았다.

| 검사 | 결과 |
|---|---|
| `v536_information_own_bodies_ui.py` | 6 PASS. 미저장 정의부터 첫 구현, 빈/작성/미저장 본문 cold, C# 취소, Save, Review 취소·명시적 compiler Confirm, 확정 후 재편집 |
| `v536_information_own_body_boundaries.py body-storage / body-conflict` | 각각 2 PASS. 실제 쓰기 거절/실제 source 변경에서 live·disk 전체 미적용과 입력 보존, cold·명시적 재시도 또는 동료 원본 보존 |
| 위 `body-loss / body-close` | 각각 2 PASS. 성공 응답 유실과 늦은 설명 보존, 저장 성공 직전 닫기·재열림 방지, receipt cold 복원·중복 없는 후속 저장 |
| `v536_information_own_body_save_api.py` | 4 PASS. owner 누락/위조/다른 소유/범위 밖 action 거절, 본문+설명 원자 저장, receipt 재전송·변조 거절, cold 복구와 실제 peer 변경 차단 |
| `v536_information_own_body_typed.py` | 2 PASS. long/ref/out/반환 본문 UI·명시적 Confirm·격리 사본의 실제 정보 scope 호출 compile, 경고 0. 프로젝트 실행 없음 |
| `v536_information_own_body_projects.py` | 3 PASS. 동일 native ID의 A/B 프로젝트 입력·checkpoint 분리, 은퇴 callback 무효, 실제 Home 재진입·Save·상대 원본 보존 |
| `v536_information_slots_ui.py` 회귀 | 4 PASS. 기존 정보 모듈 copy/import·본문 재편집·exact64 값·cold·Review/Confirm |

첫 구현 경계는 별도 `storage/source/loss/close` 각각 2 PASS, 기존 own-function API는 normal 7 / published 8 PASS로 확인했다. 이는 위 27건에 합산하지 않는다. Linux 최종 엔진 compile은 경고/오류 0이고 변경 JS 3개의 canonical pin 및 총 73개 resource 계약이 일치한다.

실패 근거도 보존했다. 실제 본문 Save가 live source 적용·private 입력 삭제 후 checkpoint 쓰기에 실패하던 결함을 원자 저장으로 수정했다. 프로젝트 재진입 시 모든 source ID/hash가 같은데 technical revision만 달라 거절되던 경우를 기존 완전한 source 복원 검사에 연결했다. 확정 후 본문만 수정하면 정보의 Review 표시가 갱신되지 않던 결함과, 저장 응답 직전 닫은 창이 다시 열리던 결함도 실제 UI로 재검증했다. 한 응답 유실 fixture의 자체 대기 교착은 응답을 보류한 채 `busy` 종료를 기다리는 flush를 호출한 테스트 오류였으며, 이를 수정해 재실행했다. 보호 조건이나 실패 assertion을 없애지 않았다.

[검증된 정보 카드](evidence/v536-information-own-bodies/engine-card.png). 기존 [카드 12영역 원본 대조](VALIDATION_V536_INFORMATION_OWN_FUNCTIONS.md)를 보존했고 깨끗한 checkout의 정의 UI 회귀에서도 다시 일치를 확인했다. 본문 편집기 전체의 새 정밀 대조를 전부 실행했다는 뜻은 아니다.

## 게시 전 재현 및 한계

소스 snapshot은 `53974d08df71dddb06569b3f2510e657ca64188e`이다. 해당 커밋의 깨끗한 checkout에서 Linux 엔진을 경고/오류 0으로 다시 컴파일했다. 실제 엔진/렌더러 본문 UI 6, 저장 후보 API 4, 저장 중 창 닫기·cold 복구 2, 기존 자체 함수 정의 UI 7 PASS로 재현했다. 마지막 suite는 원본 카드 12영역의 위치·치수·font·padding 일치도 다시 검증했다. source/checkpoint/입력/명시적 Confirm assertion은 유지했다.

같은 checkout에서 실제 retained CRLF 속성 pull과 fresh LF의 73개 canonical/exact snapshot, content·encoding·BOM·binary·byte-budget 거절 검사를 통과했다. 원래 checkout 바이트를 변경하지 않았다.

Windows x64 교차 패키지는 `/workspace/artifacts/v536-information-own-bodies/Windows-x64`에 생성했다. runtime 2,322개 파일 구성, 변조 asset/누락 dependency 거절, 무관한 cwd와 SDK가 없는 격리 runtime에서 패키지 엔진 웹 기동·73개 리소스 제공·최소 로그인 화면 렌더를 확인했다. 기존 fixture checkout 설정 재사용과 명시적 storage override도 검사했다. 패키지 runtime 내용은 위 source snapshot과 같다. 문서 후속 커밋이나 검증 fixture를 배포 파일로 넣지 않는다.

**Windows apphost/WebView2·실제 모바일 기기 실행은 미검증이다.** 실제 계정 로그인·권한 부여·유료 추론·사용자 프로젝트 실행은 하지 않았다. 로컬 패키지 생성과 Library 첨부/사용자 전달은 별개이며 전달 성공을 주장하지 않는다.

- 저장된 자체 함수 삭제·복구·구현 삭제와 순서 변경, 독립 properties 창의 구현 선택·복사·본문 편집은 계속 차단한다.
- 연결된 서명 전체 변경과 원본 복합 entity/참조 핀 선택의 나머지 의미는 기존 I5 잔여 목록대로다. 이번 plain 저장에 구조/ABI 의미를 임의 추가하지 않았다.
- 설명 없는 첫 scaffold의 기존 영문 intent fallback은 별도 관측 항목으로 남긴다. 기존 함수 원문/본문을 자동 변경하지 않았다.
- Helper `설명으로 작성`, I6/B2 및 A4~A6/M4/M11/M12는 후속 범위다.

후속 기본 창 자체 함수의 비파괴 삭제·복구는 [별도 검증 단위](VALIDATION_V536_INFORMATION_FUNCTION_RETIREMENT.md)로 연결했다. 위 본문 편집 단위 당시의 미연결 기록과 검증 수를 소급하여 바꾸지 않는다. 독립 창 본문 편집 및 구현만 삭제는 계속 후속이다.
