# v536 소유 슬롯 호출 ABI 검증

다중 구현/C# 묶음은 `0aa3e3ce31dd196875c86a4930d680f028827bbe`로 별도 게시했다. 이 문서는 그 다음 호출 ABI 묶음이며 전체 v536 복원 완료 기록이 아니다. 지원/차단 문맥은 `V536_CALL_ABI_SCOPE.md`에 고정했다.

## 변경

- 기존 슬롯의 안전한 Blueprint 읽기에서 값↔ref 갱신 가능 여부를 확인한다. 소유자가 같은 실제 연결이며 갱신 가능한 ABI만 있는 경우 기존 편집 버튼과 `계약 확인 필요` 배지를 제공한다. 일반 계약 오류를 유효한 연결로 표시하지 않는다.
- 기존 계약 갱신 버튼의 입력을 슬롯별로 보관한다. owner/hash/revision을 batch 및 저장 결과 확인에 전달하며 결과 증거도 같은 슬롯 요청에 결부한다. 다른 종류의 슬롯 batch는 이 경로에서 허용하지 않는다.
- 단일 호출의 서명과 typed import를 기존 원자적 checkpoint에 함께 저장하고 기존 Review/명시적 compiler Confirm을 유지한다. callee·다른 구현·객체를 자동 편집하지 않는다. 복사본 provenance가 있으면 owner 생략 요청도 갱신 가능으로 표시하거나 처리하지 않는다.
- CSS/원본 ZIP/원본 카드·모달·버튼 배치는 바꾸지 않았다. UI 두 파일의 리소스 해시를 갱신했다.

## 검사

`tests/web/v536_slot_call_abi.py`는 자체 임시 프로젝트/프로필을 생성한다. 실제 엔진의 객체 A→Caller 슬롯, 객체 B→Other, 별도 callee를 사용하고 실제 프로젝트 Run/사용자 계정/추론은 하지 않는다. 단일 common/windows 대상의 순수 준비와 비호환 타입·이름·out·반환·다중 본문/동일 호출 중복 차단을 별도로 구분한다. 화면에서는 최초 ABI 진입, 명시적 갱신, cold 복원, 잘못된 슬롯/hash/비ABI 요청 차단, Save, cold/Review 취소, compiler Confirm 및 연결 변경 후 오래된 Save의 입력 보존을 확인한다. 최종 actual7 실행 exit0: 총8건(순수 준비1 + 실제 엔진/화면7), 근거 `/tmp/confectory-slot-call-abi-0784zciw/evidence.json`. controlled 슬롯 렌더러10건도 exit0(`/tmp/confectory-slot-editor-renderer-nfwm_cz7`). 생성 Linux build3 exit0, JS 두 파일/Python 구문과 diff 검사 통과. 원본 프레임850×600의 실제 캡처를 확인했으며 전체 pixel/모든 문맥 수용으로 확대하지 않는다.

집중 검사 중 fixture 준비가 기존 provide를 포함해 준비 API에서 거절된 것과, offscreen 노드를 원본 지도에서 선택하지 않은 클릭, 영문 예외 대신 안전한 한국어 slot 오류 코드를 반환하는 기대 차이를 수정했다. 저장된 화면 상태는 임시 basis를 제거하지만 author-attempt cells에는 남기는 기존 계약도 검사에서 구분했다. 텍스트·proof·node/type·입력 키는 그대로 비교하고 추가 기록은 같은 graph/cells의 단일 저장 시도임을 확인했다. 서버/원본 레이아웃을 완화해 통과시키지 않았다.

실제 Windows apphost/WebView2·네이티브 입력은 미검증이다. 등록 callable·복사본·다중 target 본문·일반 ABI 재매핑은 구현되지 않았으며 자동 추정하지 않는다. Library 업로드는 기존 discovery 네트워크 실패에 새 복구 근거가 없어 재시도하지 않았다. 로컬 패키지는 전달 완료를 의미하지 않는다.

## 교차 패키지

`/workspace/artifacts/Confectory-v536-slot-call-abi/Windows-x64/Confectory.exe`: Windows x64 교차 생성 exit0, 선언 파일2305개와 UI 리소스66개. `desktop_package.py` exit0(`/tmp/confectory-desktop-package-1qtf7jcl`): 구성·누락/변조 거절·SDK 없는 packaged 웹 시작·다른 cwd·프로필 재사용과 명시 override·최소 로그인 화면 확인. Windows apphost와 WebView2 실행은 하지 않았다. .NET Desktop Runtime10.0 x64 및 Edge WebView2 Runtime이 필요하며 자동 설치하지 않는다. Git에는 패키지/로그/프로필을 넣지 않는다.
