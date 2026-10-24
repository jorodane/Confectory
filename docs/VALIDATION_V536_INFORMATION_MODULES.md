# v536 I5: 정보의 모듈 연결과 기본창 구현 편집

이 기록은 I5의 첫 지원 단위다. **정보 자체 기능 생성과 독립 properties 창의 구현 편집은 아직 완료하지 않았다.** 27개 수용 항목에서 I5 전체를 완료로 세지 않는다. 기준은 저장소 `196c605`의 v536 레퍼런스이며 새 사이트의 UI 변경은 포함하지 않는다.

## 연결한 동작

정보 카드에도 기존 원본 기능 영역을 사용한다. 모듈 선택/해제, 상속 모듈의 읽기 전용 표시, 실제 요구 기능의 이름·입출력·기본/소유 구현 상태를 native schema의 `module`/`provide`에 연결했다. 정보의 필드·기본값·상속·기존 provider는 유지한다. 모듈 선택은 실행 권한 부여가 아니다.

기본 정보 창에서는 모듈 기능의 명시적 가져오기, 기본/상속 구현의 비공개 Blueprint 복사, 단독 소유하는 저장 구현의 본문 편집을 기존 선택창과 Blueprint/C# 코드 편집 영역에 연결한다. 저장은 기존 출처·등록·import·wrapper·본문 및 정보 변경을 같은 후보/CAS로 검증한다. 직접 선택한 구현과 다른 정보 입력의 혼합 Save는 아직 차단한다. 새 private copy와 지원되는 정보 기본값의 같은 후보 Save는 허용한다. 원본·상속 구현·등록 팩·다른 target을 복사 대상 대신 수정하지 않는다.

schema 소유 구현의 읽기/쓰기에는 실제 직접 `provide`, 동일 namespace, 현재 source hash/revision과 단독 소유를 요구한다. 다른 object/schema의 assignment, 부모 구현 또는 공유 graph는 원본 편집 권한으로 승격하지 않는다. 잘못된 owner 토큰과 늦은 원본 변경은 전체 거절한다. 기존 object 동작과 계정/동의·Confirm·프로젝트 실행 권한은 유지한다.

독립 정보 창은 모듈 연결/해제와 계약 표시·저장/취소를 지원하지만 구현 가져오기/복사/편집 버튼은 아직 비활성이다. 정보 자체 `＋ 기능`도 미연결로 남는다. `설명으로 작성`의 실제 Helper 작업 연결은 후속이며 성공처럼 처리하지 않는다.

## 수정한 실제 결함

- 모듈 팝오버의 focus 뒤 대기 중이던 문서 scroll이 팝오버를 즉시 닫았다. 원본 anchor가 실제 이동할 때 닫고, 원본 위치 계산과 검색 focus를 보존했다.
- 독립 창의 기능 영역에서 Ctrl+Z를 전역 Workspace 이력이 먼저 가로챘다. 기능 영역의 현재 owner·전체 입력 identity에 묶인 Undo/Redo로 전달한다. 다른 source/창/새 입력을 덮는 재적용은 하지 않는다.
- schema에서 생성한 구현의 원래 소유권·재시작 복원 경로가 object만 허용했다. 구현에 한해서 schema owner를 같은 검증 계약으로 확장했다. object 속성 schema 생성은 여전히 object owner만 받는다.
- 여러 기능 카드의 상세 조회가 하나의 host work 슬롯을 동시에 차지하려 해, 실행되지 않은 조회가 빈 완료 캐시에 남았다. 실제 저장된 import는 정상이지만 같은 창에서 출처가 사라졌다. 조회를 순서대로 처리하고 취소/미실행 기록은 캐시에서 정리한다. 원래 imported call 형태 검사는 완화하지 않았다.
- copy+정보 값의 원자 Save 뒤 다른 기능을 가져오면 새 구현/graph가 이전 검토 그룹에 들어가지 않았다. 후속 Save가 기존 atomic 그룹을 건드릴 때도 기존 동일 후보/proof 병합을 수행한다. 검토 선택 누락 차단을 해제하거나 자동 Confirm하지 않는다.

## 실행한 검사

검사는 격리 fixture의 자체 프로젝트·프로필만 사용한다. 실제 로그인·계정 설정·동의·추론 및 사용자 프로젝트 실행은 없다.

| 검사 | 확인한 결과 |
| --- | --- |
| `v536_information_modules.py` | native 5 PASS. 정보 모듈 편집, 기존 field/default/provider 보존, 상속·외부 metadata 검증·관측 source 보호 |
| 기존 정보 정의 native 회귀 | 5 PASS. 기존 정보 정의/기본값 편집 경계 유지 |
| `v536_information_modules_ui.py normal` | 기본창 4 PASS 및 독립창 4 PASS. 선택/취소, private Undo/Redo, 실제 계약·핀 표시, 임시 Save/cold, unlink 취소, Review 취소·새 명시적 compiler Confirm |
| 위 UI의 `storage/conflict/loss` | 기본/독립창 각각 2/2/1 PASS. 저장 거절·실제 source 변경 전체 미적용, cold 재시도, 성공/조회 응답 유실 후 receipt 확인과 중복 Save 방지·다른 창 입력 보존 |
| 원본 모듈 선택창 대조 | 추적 ZIP의 실제 함수/CSS를 별도 렌더하고 같은 후보 데이터로 6영역의 좌표·치수·색·font/padding 일치. 원본/실제 PNG와 비교 JSON 보존 |
| `v536_information_slots_api.py` | 실제 엔진 6 PASS. 명시적 가져오기, 올바른 owner binding/위조 차단, private snapshot cold, 원본/부모/다른 target·exact64 보존, 저장 본문 편집/cold, 늦은 owner CAS 변경 거절 |
| `v536_information_slots_ui.py` | 실제 엔진/Chromium 4 PASS. private Blueprint 본문+정확한 64비트 기본값 같은 후보 Save/cold, 가져오기와 출처 표시, 저장 copy 재편집/cold, Review 취소와 새 명시적 compiler Confirm·원본 보존 |
| `v536_information_slots_boundaries.py storage/conflict/cancel` | 각각 2/2/1 PASS. 실제 checkpoint 쓰기 거절·재시작 후 명시 재시도, 동료의 실제 저장/CAS 변경 거절·cold 재거절, 미저장 copy snapshot/본문/값 취소·cold와 다른 창 입력 보존. 취소는 자기 private snapshot만 정리하고 기존 source 초안을 유지한다 |
| 위 UI의 `projects` | 3 PASS. 이름·namespace·요소 ID가 같은 실제 A/B 프로젝트의 서로 다른 copy와 peer exact64 입력, Home 전환 뒤 은퇴한 A 가져오기 callback의 B 쓰기 차단, 양방향 재진입·A만 저장·프로세스 cold 분리 복원 |
| 위 UI의 `loss` | 1 PASS. 실제 성공/조회 응답을 유실시킨 뒤 cold에서 `settledSlots` 검증으로 복구. `applySlots`는 최초 한 번뿐이며 중복 copy 생성/재적용 없음, 다른 창 입력/원본 유지 |
| `v536_object_modules_regression.py` | 최종 엔진에서 기존 객체 모듈 UI 3 PASS. 해제/취소·Undo/Redo·원자 Save/cold와 기존 provider 보존 |
| Linux 엔진/리소스 | 변경 native 소스와 pack 본문 컴파일, 경고 0. JavaScript/Python 구문·canonical pins·diff whitespace 검사 통과 |
| Windows 교차 패키지 | 생성 및 73리소스·PE/의존성·손상 거절·별도 cwd·SDK 없는 격리 runtime의 패키지 웹 엔진/최소 Agent 화면 기동 통과. 실제 Windows apphost/WebView2 실행은 하지 않음 |

검사 증거는 `/workspace/scratch/v536-information-modules`에 보존한다. 최종 정상 구현 UI는 `information-slots-ui-8.log`, fixture `confectory-wide-mixed-9qnc66hg`다. 앞선 UI 실패를 통과로 세지 않았다. 잘못된 일반 문서 상태 기대값은 원래 저장 copy의 출처 표시로 바로잡았고, 실제 저장 여부는 cold 이후 본문 비교·원본 불변·명시적 compiler Confirm으로 검증했다.

추가 실패 회귀의 초기 fixture 오류는 독립 창 번호를 두 번째로 가정한 설정, 최신 schema를 읽기 전 비어 있는 snapshot 사용, copy 시도 journal 추가까지 동일 배열로 요구한 기대값, 취소 시 자기 private snapshot 정리까지 checkpoint 바이트 불변으로 요구한 기대값이었다. 사용자 입력/원래 source/권한 검사를 약화하지 않고 실제 창·source와 원문 보존 계약으로 수정했다. 실패 로그는 보존하며 통과 횟수에 포함하지 않는다.

응답 유실 fixture에서는 cold 시 이미 검증 복구되어 비활성인 Save를 클릭하거나, 비동기 조회 도중 비어 있는 native schema cache를 저장 결과로 사용한 기대 오류도 있었다. 최종 검사는 실제 receipt 조회/첫 한 번의 적용/단일 copy와 fresh native schema를 확인한다. 오류 로그는 보존했다.

깨끗한 checkout 재현 결과는 후속 기록에서 구분한다. 전체 UI, C# copy의 모든 문맥, 일반 ABI/모바일 특수 동작, I6/B2/A4–A6/M4/M11/M12 완료로 확대하지 않는다. 원본 전체 pixel equality나 실제 Windows/Android/터치·DPI 수용도 아니다. 로컬 패키지 경로는 사용자에게 첨부/전달했다는 의미가 아니다.
