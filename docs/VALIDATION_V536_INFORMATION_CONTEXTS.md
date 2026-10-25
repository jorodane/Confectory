# I5-6 6행: 전체 본문 호출자의 명시 C#·import 갱신

이 단위는 프로젝트 소유 callee를 import하는 직접 소유 전체 본문 caller다. 함수 상세창의 현재 callee 계약과 기존 구현 선택창의 `호출자` C# Script를 사용한다. caller 자신의 public/native 서명·매개변수·return writer·노드/연결·저장소는 유지하고 사용자가 직접 쓴 호출 본문을 보관한다. callee 계약·callee 본문·caller 본문/record·현재 import/context를 한 후보/CAS·Review 그룹에 결부한다. 자동 C# 재작성, 다른 소유 원본 변경, 새 UI/CSS/권한/자동 Confirm은 없다.

원래 source/record hash·graph receipt·native/context/import를 먼저 확인하고 caller 자신의 ABI를 바꾸는 요청은 거절한다. 원래 graph나 source가 달라지면 이전 명시 편집을 재사용하지 않는다. 모든 본문과 실제 생성된 entry/members·현재 import 인터페이스를 Roslyn으로 검사한다. 컴파일 검사는 실행이나 유료 모델 호출이 아니다.

## 확인한 결함과 수정

첫 실제 저장 검사는 `consumer_error`로 거절됐다. 저장 후보의 import 서명을 선언문으로 직렬화하면 native import 인자 이름이 무명 인자 표기로 저장되고, 재파싱 시 `arg0` 같은 원래 문법의 이름이 된다. 준비 중 public 인자명으로 만든 context와 실제 저장·재로딩 context가 달라 `GRAPH_IMPLEMENTATION_CONTEXT_STALE`이 발생했다. 저장할 **동일 선언문을 재파싱한 import 계약**으로 context를 구성하도록 수정했다. stale 검사를 완화하지 않았다. 순수 후보에서 실제 저장될 선언을 다시 읽는 검증과 실제 저장·cold·compiler Confirm을 모두 확인한다.

## 집중 검증

- 순수 후보 2 check: callee·caller 원문/import/context의 일관성·caller own ABI 유지, 명시 source 누락·record/graph hash·own ABI·callee contract·컴파일 오류 거절.
- 실제 엔진 API 3 check: 거절 시 checkpoint 불변, 한 후보 저장·재시작, Review/Confirm·재시작의 원문·서명 보존.
- 실제 렌더러 13 check: 기존 C# 편집창의 취소·불완전 입력 재시작·Undo/Redo·callee/caller 편집과 저장 장치 오류·응답/receipt 유실 후 결과 조회·재시도·명시 Review/Confirm을 검증했다. 독립 창 정상 저장·cold·Review/Confirm 3, 기본 창 정상/실패/응답 유실 4, 충돌 2, 변경 취소 2, 동일 namespace 두 프로젝트 전환 2를 통과했다. 두 프로젝트의 입력은 분리되고 닫힌 코드창의 오래된 저장 동작은 차단된다.
- 영향 회귀 7 check: 이전 whole-body 계약 pure 2, 동일 함수의 연결된 두 호출 pure 2 및 실제 API·cold·compiler Confirm 3을 통과했다.

총 집중 검증은 **25 check**다. 같은 검사의 재실행은 추가 count로 합산하지 않는다. [선별된 결과](evidence/v536-information-contexts/focused-checks.json), [실제 호출자 편집창](evidence/v536-information-contexts/manual-caller.png), [CSS/원본 Script 구조 근거](evidence/v536-information-contexts/layout-evidence.json)를 보관한다. 확인한 caller fixture는 공통 target이며 자신의 ABI를 유지한다. 이 단위가 모든 target·소유/출처 조합의 완료를 뜻하지 않는다.

## 고정된 잔여와 한계

이 단위로 6행 전체가 완료되지는 않는다. 고정 잔여는 (1) 추가 callee 노드·locals/별칭이 있는 native/public 계약 변경, (2) 별도 `forwardCallerStorage` 저장소 대응, (3) serial After/execution-enum postCall의 명시 source/helpers 갱신이다. caller 등록/상속/copy receipt는 7행, nested/private path는 다음 5행이다. 새 조합을 덧붙이지 않는다.

원본 `196c605` v536 Script 편집기의 구조와 현재 CSS를 유지한다. 실제 Windows apphost/WebView2·모바일 기기, 사용자 로그인·계정/권한 설정·유료 AI·사용자 프로젝트 실행 및 Library 전달은 수행하지 않았다. Windows 교차 패키지는 실제 Windows 실행과 구별한다.

## checkout·리소스·Windows 교차 패키지

검증한 실행 소스 커밋은 `612a40913498abb8225af43fb280029d871cc018`이다. 깨끗한 checkout에서 Native Release 0 warning/0 error, Linux 빌드 stderr 0, 실제 API 3 + 독립 창 렌더러 3 check를 재현했다([기록](evidence/v536-information-contexts/clean-checks.json)). root의 집중 25 check에 같은 검사의 재실행 수를 더하지 않는다.

실제 Git retained CRLF→속성 pull과 fresh LF에서 74개 canonical/exact 리소스를 기동했고 내용/인코딩/BOM/binary/budget 변조를 거절했다. 원래 checkout 바이트는 바꾸지 않았다.

로컬 Windows 패키지는 `/workspace/artifacts/v536-information-contexts/Windows-x64`이며 실행 진입점은 `Confectory.exe`다. manifest 2,336개(자기 manifest 포함 실제 2,337개)의 모든 해시와 변경 소스 5개·Native/Core DLL 2개의 root 바이트 일치를 확인했다([기록](evidence/v536-information-contexts/package-bytes.json)). manifest SHA-256은 `b2fca70b91320ad343ade4204826fa0280900243d758ae4c2d7729b51c2c2fd7`다.

패키지 검사는 SDK 없는 격리 runtime·관계없는 작업 디렉터리에서 managed 엔진 기동·74 리소스·최소 로그인 화면, 변조/의존성 누락 거절과 기존 fixture profile/명시 override 보존을 통과했다([기록](evidence/v536-information-contexts/package-probe.json)). 실제 Windows apphost/WebView2나 실제 로그인을 실행한 검사가 아니다. 사용자에게 첨부로 전달하지 않았다. 이 결과를 기록하는 후속 문서 커밋은 실행 소스를 변경하지 않으므로 위 패키지와 실행 코드가 같다.
