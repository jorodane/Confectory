# v536 정보 함수: 명시 전체 본문과 값/ref 저장소 첫 단위

고정 6행의 첫 지원 단위다. 직접 소유하고 import가 없는 원래 전체 본문 lift에 사용자가 작성한 C#과 값↔ref 선택을 적용한다. 공개 핀과 다른 native 인자명, 기존 out 인자와 반환, 각 caller의 기존 exact-typed 저장소를 보존한다. 이름·타입·인자 수·out 역할·반환 변경이나 추가 노드/별칭이 있는 전체 본문은 이번 지원 범위에 넣지 않는다. 범위는 [고정 수용 조건](V536_I5_6_ROW6_SCOPE.md)에 기록한다.

기존 C# Script의 매개변수/본문 입력과 호출 계약 갱신 선택창을 재사용했다. CSS·권한·Review/Confirm 경계를 바꾸지 않았다. 본문 자동 치환, 임의 ref 임시 변수, 별칭을 값 스냅샷으로 바꾸는 처리는 없다. [실제 편집 화면](evidence/v536-information-whole-body/code-editor.png)에서 원래 native 인자명과 out, 명시 ref 및 직접 쓴 한글·이모지 본문을 확인했다. 원본 대비 새 배치나 상시 패널은 없다.

서버는 원래 record/hash·경로·구문 경계·정의 hash·context, native/public positional 저장소와 원래 직렬 반환 경로를 재검사한다. 명시 본문만 record에 넣고 함수·구현·graph·code record·모든 직접 caller를 기존 한 후보/CAS에 결합한다. 모드가 바뀐 caller는 현재 연결을 명시적으로 선택해야 한다. ref에 리터럴·계산값을 새 저장소로 추정하지 않으며 지원하지 않는 공유 source 소유자는 거절한다. 직접 본문과 실제 생성기의 entry/members 모두 Roslyn 컴파일 진단으로 검사한다. 코드를 emit/load/Run하지 않는다.

## 검증

현재 Native 빌드 0 warning/0 error, Linux 실제 엔진 빌드 stderr 0. `v536_information_whole_body_native.py` 2건은 명시 후보와 누락/해시/소유권/구문 경계/컴파일/타입/out 역할/외부 source/임의 저장소/공유 source의 전체 거절을 확인한다. 실제 엔진 API의 저장·cold·컴파일 Review/Confirm 3건을 통과했다.

실제 렌더러 기본 창 4건: 취소·불완전 본문/params의 cold 보관·명시 코드/저장소 선택·Undo/Redo, 실제 checkpoint 쓰기 실패의 전체 미적용, 저장 및 receipt 응답 유실 후 cold/결과 조회만으로 복구(재적용 없음), Review 취소 후 재검토/명시 Confirm을 통과했다. 첫 실행은 이 네 제품 흐름 통과 후 Playwright가 종료된 뒤 스크린샷을 시도한 검사 정리 코드만 실패했다. 정리 코드를 고쳤고 동일 검사 전체가 정상 exit 0으로 끝났다. 해당 실패를 제품 결함 해결로 계산하지 않는다.

독립 창 충돌/변경 취소/동일 namespace 프로젝트 전환은 각 2건씩 통과했다. 현재 실제 렌더러는 4시나리오 10 PASS다. 기존 whole-body root 계약 회귀 5건, 혼합 target 순수 후보 2건과 실제 API/컴파일 Review/Confirm 3건도 통과했다. 원래 root modes/legacy3·exact4 source group, native CPP/일반 Blueprint의 명시 편집과 마지막 target 오류 전체 거절을 보존한다. [선별된 검사 근거](evidence/v536-information-whole-body/focused-checks.json)는 토큰/사용자 자료 없이 체크 이름과 격리 fixture 위치만 기록한다. 자기 Confirm 뒤 ref→값 재편집, clean checkout/리소스 및 Windows 교차 패키지는 마지막 결과를 아래에 확정한다.

모든 검사는 임시 fixture 프로젝트/저장소만 사용했다. 사용자 계정·유료 AI·사용자 프로젝트 실행은 없다. 실제 Windows apphost/WebView2, 네이티브 모바일 기기, Library 업로드/전달은 미검증이다. 전체 I5-6/v536 완료나 배포 완료를 뜻하지 않는다. 5·7·8·9행은 기존 별도 잔여다.
