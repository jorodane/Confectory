# 추가 노드·별칭·저장소·postCall 결합 검증

고정 지원 경계는 [V536_I5_6_RETAINED_SCOPE.md](V536_I5_6_RETAINED_SCOPE.md)다. 기존 v536 UI 구조·CSS와 사용자 C# 원문·실제 저장소/별칭·입력·권한을 유지한다. 수정은 직접 소유 후보와 기존 한 거래/CAS·Review/Confirm에 한정된다.

## 집중 검증

- 순수 후보 8 check: context/별도 storage 코드와 추가 ref 인자 코드·live root 별칭·독립 local, serial After/enum source/helpers의 네 고정 경로를 검증했다. 추가 노드/경로·이름·C# 원문과 `9223372036854775806`을 유지한다. 누락된 alias/native 출력/현재 root 출력 대응, stale graph/source, 잘못된 C#과 wrapper receipt/copy provenance는 전체 미적용이다.
- 실제 API 6 check: context+serial, storage+enum 각각 3. 오류 시 checkpoint 불변, 한 후보 저장/cold, 실제 compiler Review/Confirm/cold와 source/helpers·셀·별칭·다른 소스를 확인했다.
- 실제 렌더러 16 check: 기본 serial 3, storage+enum 정상/장치 오류/응답·receipt 유실 4, 충돌 2, 변경 취소 2, 두 프로젝트 전환 2, 독립 창 storage+enum 3을 통과했다. native/public 매개변수와 추가 그래프 입력·native 출력·root 출력·caller를 기존 매핑창에서 직접 고른다. 후처리·보조 함수의 취소·불완전 입력 재시작·코드 저장, Undo/Redo·임시 저장·Review 취소/재검토/명시 Confirm을 확인했다.
- 별도 forwarded call: 실제 UI와 같은 `blueprintPrepareCall`이 만든 import를 사용해 callee ABI/원문과 positional cell을 보존한 root 이름 변경 및 불호환 타입 거절을 검증했다. 실제 저장/cold/compiler Confirm도 통과했다. 직접 화면에서도 함수 상세창의 root 입력/출력 이름 변경·Undo/Redo·저장·명시 Review/Confirm을 완료했다([화면](evidence/v536-information-retained/forward-call-ui.png)).
- 영향 회귀 14 check: 이전 C2 2, 이전 whole-body 모드 2, 연결된 두 호출 pure 2/API 3, 자동 출력/After 변환 차단 2, 기존 live alias·Set 스냅샷 3. 통과한 검사는 무관하게 반복하지 않았다.

앞의 순수/API/화면 및 forwarded call을 포함한 집중 결과는 **47 check**다. 마지막 copy guard 보강 뒤 Native Release 0 warning/0 error와 serial/enum 후보·copy 거절 4 check를 재확인했으며 같은 검사의 재실행은 합산하지 않는다. [선별된 결과](evidence/v536-information-retained/focused-checks.json)에 안전한 check 이름과 격리 fixture 경로만 남겼다.

## 재현과 수정

첫 fixture는 local의 잘못된 `value` 필드와 새 record의 이전 `node` ID 때문에 초기 검증이 거절됐다. 기존 문법의 `initial.constant`와 실제 `extra` record ID로 고쳤다. forwarded call fixture도 임의 `Leaf` import alias가 실제 generator의 alias와 달라 CS1061이 발생했다. 실제 UI operation이 생성한 import로 수정했다. 이어 실제 API fixture의 누락된 schema 조회를 보완했다. 추가 UI 검사는 기존 고급 Review 확인 단계를 빠뜨려 Confirm이 비활성으로 유지됐다. 원래 고급 검토를 열고 확인한 뒤 정상 click으로 완주했으며 버튼 활성화나 보호를 우회하지 않았다. 이 오류를 사용자 제품 결함으로 보고하지 않는다. 회귀 스크립트의 존재하지 않는 파일명도 바로잡고 이미 통과한 8 check는 반복하지 않았다.

후보 구성에서 prepared graph를 이미 부모가 있는 JsonNode로 다시 넣으면 거절되는 결함을 발견하여 명시 복제 후 사용하도록 수정했다. 보호나 CAS를 완화하지 않았다. 전체 그래프·source 원문·원래 의미 위치의 증거를 검증한 뒤 현재 대응만 적용한다.

[본문 화면](evidence/v536-information-retained/native-code.png), [serial 후처리](evidence/v536-information-retained/post-call-code.png), [enum 후처리](evidence/v536-information-retained/enum-post-call.png)와 [원본 구조/CSS 근거](evidence/v536-information-retained/layout-evidence.json)를 보관한다. 원본 Script/backdrop/source/status/error와 구현 선택/매핑을 재사용한다. 전체 screenshot pixel 일치는 주장하지 않는다.

고정 6행의 위 직접 소유 C1~C4 지원 경계에서 남은 실제 미연결 조작은 없다. 아래 clean checkout·교차 패키지·게시 검증을 통과한 뒤 지원 경계 마감으로 기록한다. 다음 구현은 고정 5행이며 전체 I5-6/v536 UI 완료와 구분한다. 실제 Windows apphost/WebView2·모바일 기기·사용자 로그인/권한·유료 AI·사용자 프로젝트 실행·Library 전달은 수행하지 않았다.
