# v536 정보 함수: 명시 전체 본문과 값/ref 저장소 첫 단위

고정 6행의 첫 지원 단위다. 직접 소유하고 import가 없는 원래 전체 본문 lift에 사용자가 작성한 C#과 값↔ref 선택을 적용한다. 공개 핀과 다른 native 인자명, 기존 out 인자와 반환, 래퍼 없는 일반 Blueprint caller의 기존 exact-typed 저장소를 보존한다. 이름·타입·인자 수·out 역할·반환 변경이나 추가 노드/별칭이 있는 전체 본문은 이번 지원 범위에 넣지 않는다. 범위는 [고정 수용 조건](V536_I5_6_ROW6_SCOPE.md)에 기록한다.

기존 C# Script의 매개변수/본문 입력과 호출 계약 갱신 선택창을 재사용했다. CSS·권한·Review/Confirm 경계를 바꾸지 않았다. 본문 자동 치환, 임의 ref 임시 변수, 별칭을 값 스냅샷으로 바꾸는 처리는 없다. [실제 편집 화면](evidence/v536-information-whole-body/code-editor.png)에서 원래 native 인자명과 out, 명시 ref 및 직접 쓴 한글·이모지 본문을 확인했다. 원본 대비 새 배치나 상시 패널은 없다.

서버는 원래 record/hash·경로·구문 경계·정의 hash·context, native/public positional 저장소와 원래 직렬 반환 경로를 재검사한다. 명시 본문만 record에 넣고 함수·구현·graph·code record·모든 직접 caller를 기존 한 후보/CAS에 결합한다. 모드가 바뀐 caller는 현재 연결을 명시적으로 선택해야 한다. ref에 리터럴·계산값을 새 저장소로 추정하지 않으며 지원하지 않는 공유 source 소유자는 거절한다. 직접 본문과 실제 생성기의 entry/members 모두 Roslyn 컴파일 진단으로 검사한다. 후보 검증기 자체는 코드를 emit/load/Run하지 않는다.

## 검증

현재 Native 빌드 0 warning/0 error, Linux 실제 엔진 빌드 stderr 0. `v536_information_whole_body_native.py` 2건은 명시 후보와 누락/해시/소유권/구문 경계/컴파일/타입/out 역할/외부 source/임의 저장소/공유 source의 전체 거절을 확인한다. 실제 엔진 API의 저장·cold·컴파일 Review/Confirm 3건을 통과했다.

실제 렌더러 기본 창 4건: 취소·불완전 본문/params의 cold 보관·명시 코드/저장소 선택·Undo/Redo, 실제 checkpoint 쓰기 실패의 전체 미적용, 저장 및 receipt 응답 유실 후 cold/결과 조회만으로 복구(재적용 없음), Review 취소 후 재검토/명시 Confirm을 통과했다. 첫 실행은 이 네 제품 흐름 통과 후 Playwright가 종료된 뒤 스크린샷을 시도한 검사 정리 코드만 실패했다. 정리 코드를 고쳤고 동일 검사 전체가 정상 exit 0으로 끝났다. 해당 실패를 제품 결함 해결로 계산하지 않는다.

독립 창 충돌/변경 취소/동일 namespace 프로젝트 전환은 각 2건씩 통과했다. 현재 실제 렌더러는 4시나리오 10 PASS다. 기존 whole-body root 계약 회귀 5건, 혼합 target 순수 후보 2건과 실제 API/컴파일 Review/Confirm 3건도 통과했다. 원래 root modes/legacy3·exact4 source group, native CPP/일반 Blueprint의 명시 편집과 마지막 target 오류 전체 거절을 보존한다. [선별된 검사 근거](evidence/v536-information-whole-body/focused-checks.json)는 토큰/사용자 자료 없이 체크 이름과 격리 fixture 위치만 기록한다. 깨끗한 checkout의 실제 API 4건과 독립 창 UI 2건도 통과했다. API는 자기 Confirm 뒤 현재 record/서명으로 ref→값 재편집을 다시 한 후보에 넣어 native 인자·기존 out·원문·caller 저장소 보존을 확인했다. 정상 cold는 실제 충돌로 오인하지 않고 실제 다른 편집자 변경은 거절한다.

모든 검사는 임시 fixture 프로젝트/저장소만 사용했다. 사용자 계정·유료 AI·사용자 프로젝트 실행은 없다. 실제 Windows apphost/WebView2, 네이티브 모바일 기기, Library 업로드/전달은 미검증이다. 전체 I5-6/v536 완료나 배포 완료를 뜻하지 않는다. 5·7·8·9행은 기존 별도 잔여다.


## 최종 checkout과 Windows 패키지

실행 소스는 `d36a2d74539c1f483fdafd214677f59b01606365`다. root 및 clean Native 빌드는 0 warning/0 error, 두 Linux 엔진 빌드 stderr는 0이다. 실제 Git fast-forward의 보존 CRLF/fresh LF에서 리소스 74개와 내용·인코딩·BOM·binary·budget 변조 거절이 통과했다. 첫 리소스 probe는 명령에서 `CONFECTORY_DOTNET`을 빠뜨려 PATH에 없는 기본 dotnet을 실행하지 못했다. 설치된 .NET10 실행기를 명시해 동일 검사 전체를 통과했고 제품 검사나 코드를 완화하지 않았다.

로컬 Windows x64 전체 폴더는 `/workspace/artifacts/v536-information-whole-body/Windows-x64`, 실행 파일은 그 안의 `Confectory.exe`다. manifest 대상 2,336개/manifest 포함 실제 2,337개이며 manifest SHA-256은 `42c3d9d35b597cf3722933d30e15db110656dc416c0d12807725726cf7b4cae3`다. 모든 manifest hash와 변경된 실행 소스 6개·Native/Core DLL 2개의 root/package 바이트 일치를 확인했다. 최종 문서 보완은 실행 소스를 바꾸지 않는다.

[패키지 근거](evidence/v536-information-whole-body/package-checks.json): Windows x64 PE·전체 구성, 무관한 cwd, 관리 DLL의 SDK 없는 runtime-only 패키지 기동과 74 리소스·최소 로그인 렌더, 변조/의존 DLL 누락 거절, checkout 프로필 재사용/명시 override를 통과했다. 이는 Linux에서 관리 패키지 경로를 검사한 것으로 실제 Windows apphost/WebView2 실행이나 실제 로그인 검증이 아니다. Library 전달은 미검증이며 Git에 생성 빌드·로그·인증정보·사용자 데이터는 포함하지 않는다.

첫 지원 단위만 마감했다. 전체 본문 이름·타입·수·out 역할·반환 변경, 추가 노드/alias의 forwardCallerStorage, whole-body caller/postCall 래퍼는 계속 미구현이다. 5·7·8·9행과 I6/B2·A4~A6/M4/M11/M12는 기존 후속이며 전체 UI 완료로 분류하지 않는다.
