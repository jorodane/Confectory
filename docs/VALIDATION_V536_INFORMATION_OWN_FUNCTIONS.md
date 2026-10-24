# v536 정보 자체 함수: 정의 편집 첫 단위

I5는 아직 부분 지원이다. 기준은 저장소 v536(`196c605`)이며 새 사이트나 레이아웃을 도입하지 않았다.

정보 카드의 기존 `＋ 기능`과 inline 이름·설명, 상세 입출력 popover를 실제 `contain function` 선언에 연결했다. 표시 이름과 native 함수 ID는 분리한다. 새 함수는 기본 `() -> void`에서 시작하며 현재 문법의 기본형·배열·out/return 계약으로 편집할 수 있다. 기존 ref 계약은 읽고 보존한다. 새 함수의 저장 전 삭제, 영역 Undo/Redo, 미저장 cold 복원도 연결했다.

정보·함수·등록·기본값은 한 후보/CAS로 임시 저장한다. 저장된 자기 함수의 이름·설명은 정확한 함수 source hash와 현재 정보 proof를 확인한다. 미연결 함수의 핀 계약도 편집할 수 있다. 구현·typed import·모듈 계약·다른 제공자가 이미 연결된 서명 변경은 조용히 재매핑하지 않고 전부 거절한다. 직접 소유하지 않는 contained 함수는 읽기 전용으로 표시한다. 원래 주석·정확한 정수·다른 선언과 상속 원본을 보존한다.

저장 도중 새 이름/설명이 생기면 성공 receipt의 실제 함수 hash와 결부한 후속 편집으로 보관한다. 응답이 없다는 이유로 같은 함수를 다시 생성하지 않는다. 재시작의 내부 revision만 바뀐 경우에도 원래 hash와 identity 근거를 유지한다. 함수 metadata만 바뀐 거래도 정보 owner revision을 갱신하여 같은 창에서 새 Review가 가능하다.

서버의 첫 구현 생성도 별도 검증했다. 새/이미 확정된 bare 함수 모두 정보 owner·함수·등록의 명시적 proof가 필요하다. 구현은 해당 정보의 직접 `provide`이며 함수 자체의 전역 기본 구현으로 승격하지 않는다. 함수·정보·새 구현/graph/node·등록을 완전한 검토 그룹으로 묶는다. 원본 선택은 정보에 유지한다. 다른 owner, 오래된 proof, owner 없는 우회, 기존 구현/부모 덮어쓰기는 차단한다. 이 첫 구현의 **화면 버튼은 아직 활성화하지 않았다**.

## 실제 검사

| 검사 | 결과 |
|---|---|
| `v536_information_own_functions.py` | native 7 PASS. 순수 후보·typed 추가/재편집·source 관측·오래된 hash/잘못된 owner·연결 계약 차단, 파일 쓰기 없음 |
| `v536_information_own_functions_api.py normal / published` | 각각 실제 엔진 7 / 8 PASS. 생성 그룹·cold·위조/중복/오래된 owner 차단·첫 본문 Save/Review/Confirm, 별도 fixture 사본의 정보 scope 호출 compile. 프로젝트 실행 없음 |
| `v536_information_own_functions_ui.py` 기본 창 | 실제 엔진/Chromium 7 PASS. inline 생성·한글 입력·저장 전 삭제·Undo/Redo·핀 편집/취소·cold·Save·Review 취소/명시 Confirm·확정 후 재편집·읽기 전용 공유 함수 |
| 위 UI 독립 properties 창 | 6 PASS. 생성·핀/이름·cold·Save·Review/Confirm·같은 창의 확정 후 metadata 재편집. 구현 본문 편집은 포함하지 않음 |
| `v536_information_own_functions_boundaries.py` | storage 2, conflict 2, cancel 1, loss 1, late 2 PASS. 격리 checkpoint 쓰기 거절·동료 실제 변경·전부 미적용·cold 명시 재시도·원문 보존·응답 유실 receipt 조회·중복 생성 방지·늦은 이름/설명 보존 |
| `v508_feature_contracts.py` | 기존 전역 함수 계약 API 3 PASS. module 요구 보호·배열/ref/out/반환·잘못된 타입/중복 핀 거절 |
| 원본 정밀 대조 | 원본 함수와 CSS로 별도 DOM을 렌더해 카드 12영역의 상대 위치·크기·font·padding 일치. 원본 source는 실행/편집 권한이 없는 시각 oracle로만 사용 |
| 빌드·패키지 | native C# 및 Linux 엔진 경고/오류 0. Windows x64 교차 패키지 구성과 runtime-only 환경의 패키지 엔진 웹 기동 검사 통과. 실제 Windows apphost/WebView2 실행은 하지 않음 |

실패 로그도 보존했다. 초기 테스트는 출력 목록의 마지막 행을 고정 반환 행 대신 이름 편집 가능한 out 행으로 고르지 못했고, 실제 문법에 없는 function 안 import를 fixture에 넣었으며, Review 취소 뒤 invalidate된 state.schema를 바로 읽었다. 각각 실제 UI/문법/최신 읽기 경로로 바로잡았다. 중복/충돌/원문/Confirm assertions를 제거하거나 보호를 완화하지 않았다. 함수 텍스트 병합이 object/schema 전용 helper에 막히던 실제 구현 오류는 동일 function identity에 한정한 원문 보존 병합으로 수정했다.

[엔진 화면](evidence/v536-information-functions/engine-card.png), [원본 화면](evidence/v536-information-functions/original-card.png), [12영역 측정](evidence/v536-information-functions/card-geometry.json).

## 미완료 경계

- 저장된 함수 삭제·복구 및 구현 삭제, 자체 함수 순서 변경은 미연결이다. 저장 전 함수 입력 삭제만 지원한다.
- 자체 함수 `직접 작성`의 첫 구현/본문 UI 연결과 정보 소유 함수의 연결된 서명 전체 변경은 아직 미완료다. 서버/compile 검증을 화면 구현 완료로 세지 않는다.
- 독립 properties 창의 모듈/자체 함수 구현 선택·복사·본문 편집은 계속 차단한다. 창별 private 입력과 소스 proof 연결이 남았다.
- 원본의 복합 entity/참조 핀 선택 의미를 현재 primitive/object/배열 native 함수 문법으로 임의 치환하지 않았다. 현재 선택창은 기존 native 기본형 범위다.
- Helper의 `설명으로 작성` 연결·권한 확장, I6 아이콘·B2 실제 배지, A4~A6/M4/M11/M12는 이번 단위에 포함하지 않는다.

실제 Windows/모바일 기기·실제 계정·유료 추론은 검증하지 않았다. 로컬 Windows 패키지는 `/workspace/artifacts/v536-information-functions/Windows-x64`이며 Library 업로드/사용자 전달 성공을 뜻하지 않는다. 생성 빌드·로그·계정 정보·사용자 프로젝트는 Git 게시에서 제외한다.

## 게시 전 체크아웃 재현

구현 커밋 `8da384cbcbfb29b4456fa7427cf3b6846d548ef0`을 별도 clean checkout에 fast-forward한 뒤 native와 Linux 엔진을 새로 빌드했다(경고/오류 0). 그 엔진과 해당 checkout 소스에서 자체 함수 UI **7**, 기존 정보 모듈 copy/가져오기/본문 UI **4**, 전역 함수 생성 UI **6**을 모두 통과했다. 동일 원본 카드 12영역 대조도 포함한다. 기존 정보 모듈의 혼합 선택+값 미지원 차단과 소스 보존/Review/Confirm을 유지한다.

실제 Git CRLF attribute pull과 fresh LF checkout의 73개 리소스, 인코딩/BOM/바이너리/크기 한도 및 변조 거절 검사도 통과했다. Windows 패키지는 위 구현 snapshot의 runtime으로 교차 생성·구성 검사·managed 웹 엔진 기동까지 확인했다. 이 뒤 검증 기록만 갱신했으며 runtime 소스는 바꾸지 않았다. 네이티브 Windows 실행과 Library 전달은 여전히 미검증이다.
