# v536 I5-1 독립 정보 창의 모듈 편집·가져오기

기본 창의 기존 기능 선택창·private copy·import·본문 편집·원자 저장을 독립 properties 창에 연결했다. 새 화면·메뉴·레이아웃·언어 타입이나 실행/Confirm 권한을 추가하지 않는다. 원본/부모/등록 팩을 수정하지 않고 해당 정보의 provide와 새 소유 복사본·wrapper만 편집한다. 공통 target 선택 경로를 사용하며 실제 검증한 common 선택과 다른 target 원본 보존을 모든 target 실행 검증으로 표현하지 않는다.

## 화면과 서버 계약

기존 feature-authoring을 재사용하는 element-author-surface 어댑터가 현재 프로젝트·정보 ID·창 nonce를 확인하고 schema/declaration 조회를 해당 정보 창으로 연결한다. copy 선택·본문·저장 시도 키와 지속 receipt의 UI surface를 창별로 분리한다. 기본 창의 기존 키/기록 형식은 유지한다. 다른 창 입력을 자신의 입력으로 채택하지 않는다.

서버는 bound properties/schema 정보에 한해 기존 슬롯 조회·선택·copy/import·apply/settled/discard 계약을 허용한다. body source/intent/description은 해당 창에서 관찰한 동일 graph ID, 정보 owner, writable 독점 provide의 basis가 있어야 한다. 최종 소스/CAS/참조·원본 경로·등록 계약 검증은 기존 backend가 담당한다. client uiSurface, 위조/누락 nonce, 타 owner/창 basis는 거절하며 기존 별도 Review/Confirm을 유지한다.

모듈 연결·선택 취소 및 C# 편집기의 원래 Undo/Redo를 사용한다. C# 코드 저장 이후 캔버스 Undo가 본문 전체를 되돌린다고 새 의미를 만들지 않았다. source/typed 값·참조·원래 초안과 다른 창 입력을 보존하며 지원하지 않는 기능 가져오기 선택+일반 정보 값 혼합은 기본 창과 동일하게 전체 거절한다. private copy+정보 값/두 copy는 기존 원자 후보/CAS로 함께 저장한다.

## 확인하고 고친 문제

독립 창은 실제 버튼과 서버 입구에서 module 기능을 막고 있었고 primary copy API로 단순 위임하면 입력 키/저장 범위가 섞인다. 창별 surface 어댑터와 서버 binding을 추가했다. 닫힘 nonce는 재사용하지 않고 재시작 복원은 새 현재 창에서 기존 선택/완료 근거를 재검사한다.

활성 module 편집기 복원에 필요한 moduleAuthor 메타데이터가 layout 보관 목록에 없었다. 해당 기존 창 메타를 보관하고 복원/Confirm 후 갱신을 같은 surface 편집기로 전달한다.

private copy 선택 직후 원문 schema가 같으면 독립 정보 창의 stamp가 같아 다시 그려지지 않았다. 미저장 copy와 편집 진입 버튼이 보이지 않는 실제 화면 결함을 재현했고 기본 창과 동일하게 해당 창 stamp를 갱신했다.

기존 fixture는 부유 창을 작업 공간/Blueprint caption 위로 옮겨 클릭을 가렸다. 강제 클릭이나 assertion 삭제 없이 원본 드래그·카드 접기·overview 탐색을 사용하도록 준비를 수정했다. 외부 계약 오류로 schema projection이 unavailable이면 live 정보 원문과 디스크 checkpoint를 직접 검사하여 부분 적용 검증을 유지했다. 실패 로그는 scratch에 보존한다.

## 실행한 격리 검증

실제 엔진·Chromium·compiler와 격리 fixture만 사용했다. 사용자 프로젝트·로그인·새 계정 권한·유료 모델 호출·프로젝트 실행을 하지 않았다. 로그와 격리 프로젝트는 `/workspace/scratch/v536-information-module-views`에 보존한다.

| 검사 | 결과 |
|---|---|
| Linux engine-5 | warnings 0 / stderr 0 |
| 정보 module API | 6 PASS: copy/import·cold·상속 source·저장 본문·CAS와 원본 보존 |
| bound view API | 4 PASS: 누락/위조 nonce, 타 owner/창 basis, receipt surface, 닫기/reopen/cold와 primary 보존 |
| 실제 독립 정보 UI normal | 4 PASS: copy+exact64 Save/cold·import/미지원 혼합 거절·저장 copy 재편집·Review 취소/Confirm |
| 실제 독립 경계 | storage 2, source conflict 2, 응답/조회 유실 cold 1, 취소/cold 1, 프로젝트 A/B 3, 원본 C# Undo/Redo 및 활성 창 cold 2 PASS |
| 등록 C#와 두 슬롯 | 4 PASS: 상속/등록 후보 선택·마지막 계약 오류 전체 거절·두 copy+값의 재시도/Review/Confirm·등록 callable import, 다른 target 불변 |
| 실제 Blueprint 원본 | 별도 4 PASS. 실제 원본 graph/node 파일을 생성해 상속 Blueprint와 등록 C#를 함께 선택하고 계약 변경 전체 거절·재시도·Review/Confirm·등록 callable을 검증 |
| 기존 회귀 | 기본 정보 module UI 4, 기존 자체 함수 독립 body API 7, module 연결/Undo·cold·취소/Confirm UI 4 PASS |
| 원본 v536 module 선택창 | 6영역의 치수/스타일 exact equality; 원본 source에서 추출한 picker와 실제 데이터 어댑터를 비교 |
| 깨끗한 checkout | 게시 전 재현 단계에서 갱신한다. |
| Windows x64 교차 패키지 | manifest 2,327 runtime files. 무관 cwd/runtime-only 관리 엔진 web 기동·74 assets·변조/누락 dependency 거절·fixture profile 보존 PASS |

공통 fixture 준비/회귀/별도 checkout 재현은 고유 사용자 조작 수로 합산하지 않는다. [원본 picker](evidence/v536-information-module-views/information-module-picker-original.png), [실제 picker](evidence/v536-information-module-views/information-module-picker-engine.png), [6영역 수치](evidence/v536-information-module-views/information-module-picker-geometry.json), [등록 기능 연결 후](evidence/v536-information-module-views/registered-module-final.png)를 보존했다. 전체 화면 pixel equality나 실제 기기 검증으로 주장하지 않는다.

로컬 Windows 폴더는 `/workspace/artifacts/v536-information-module-views/Windows-x64`다. 전체 폴더를 함께 두고 `Confectory.exe`를 실행한다. manifest SHA256은 `92163bbf525784bf86b71337a4b8bb252f0daa8b47f3cab1e818d054e6f40e5b`다. 실제 Windows apphost/WebView2·모바일 기기와 Library 전달은 미검증이며 패키지/프로필/로그를 Git에 포함하지 않는다.

## 고정 잔여

[고정 여섯 항목](V536_I5_COMPLETION_CHECKLIST.md) 중 이번 I5-1 지원 경로를 검증하고 I5-4 완료를 유지한다. I5-2 공유/상속/copy의 확장 삭제 수명은 부분 지원, I5-3 삭제 후 새 고유 구현 생성·I5-5 함수 순서·I5-6 연결된 함수 전체 계약은 미완료다. I6/B2, A4~A6/M4/M11/M12 및 Helper 실제 작업은 섞지 않았다. 전체 I5/v536 완료가 아니다.
