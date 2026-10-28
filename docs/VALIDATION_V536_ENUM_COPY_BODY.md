# v536 고정 7행: enum 분기 복사본의 본문 연결

기준 게시 `be6bef7c1f47a69de906e89e11fa9f4ea7919d25`, 원본 UI는 저장소 v536 `196c605`다. 이번 최소 단위는 **같은 공개 계약·선택한 target의 기존 code switch/Result enum Blueprint를 정보 모듈에 복사해 표시하고, 그 복사본의 기존 C# 본문을 편집·저장·확정하는 흐름**이다. 새 함수 계약이나 독립 계약 ID는 만들지 않는다. 새 구현 ID는 기존 명시적 복사 경로가 발급하는 소유 구현 ID다.

## 원래 수용 범위 대조

| 경계 | 실제 근거와 판정 |
|---|---|
| 오버라이드 매개변수·출력 구조 변경, 외부/부모 원문 쓰기, target 자동 선택 | 정상 보호 또는 명시적으로 제외한 확장이다. 원계약을 유지하고 기존 선택 target만 복사한다. 보호 거절을 미구현으로 세지 않는다. |
| native 별칭/import 선언 이름을 새 전용 UI로 바꾸기 | 원본 v536의 기능 가져오기는 공개 이름/입출력 정의를 원본에서 유지하며 본문/Blueprint를 가져온다. native import 별칭 선언의 전용 편집 조작은 확인되지 않았다. 기존 alias/import 보존과 본문 편집은 이미 수용됐으며, 임의 native header+raw/C# 조합을 새 7행 필수 UI로 늘리지 않는다. raw/여러 계약 closure는 기존 8행 경계로 별도 대조한다. |
| legacy bool `control:branch` | 엔진에서 유효할 수 있으나 v536 화면의 Result enum 실행 분기 형식과 다르다. 실제 기존 화면도 노드 미연결 상태로 보존했다. 이번에 별도 bool 시각 분기 시스템을 추가하지 않고 기존 guard를 유지한다. 언어 오류나 오버라이드 정책 위반으로 분류하지 않는다. |
| 기존 code switch/Result enum 본문의 선택·복사·본문 편집 | 원본 기능 가져오기/로컬 구현 복제는 Blueprint와 하위 action을 보존한다. 현재 구현 선택에도 해당 source/target이 표시됐지만 Native copy의 code-next 한정과 화면의 copy 제외 검사로 준비 또는 표시가 막혔다. 이것은 실제 미연결이다. 이번 단위에서 연결한다. |
| copy 문맥의 실행 enum 계약 변경·새 분기, 중첩/private graph copy | 기존 원본 UI 요구의 별도 미연결이다. 이번 source-only enum 본문 연결을 이 계약 편집까지 완료한 것으로 세지 않는다. enum 계약 변경은 같은 후보에서 명시 코드/사용 중 route를 검증해야 하며, nested는 qualified record/context를 보존해야 한다. 새 사용자 설계가 필요하다고 단정하지 않는다. |

원본 `localImplementationDraft`는 정의/Blueprint를 clone하고 내부 action의 compiled owner만 재배치하며, `moduleFunctionDefinition`은 원래 이름/입출력·매개변수·실행 출력을 유지한다. 이 의미를 보존하며 임의의 C# 조합 경우의 수를 필수 요구로 추가하지 않는다. flat whitelist 밖 Set/property 계열도 현재 guard와 실제 원본 copy 진입을 대조할 경계로 남기며 모든 조합을 자동 필수화하지 않는다.

## 수정

`ImplementationCopy`는 기존 code next와 call enum 후처리에 더해 **code switch**만 기존 flat copy 경로로 받아들인다. 기존 `FeatureBlueprint`의 전체 그래프·enum·scope·순환·타입·record 해시 검증, readonly source 관측과 immutable private seed는 유지한다. code branch/graph/Set/property 종류를 일괄 허용하지 않는다. preview는 원래 branchOwner도 그대로 전달한다.

기존 action 카드·미니맵·C# Script 창을 사용한다. copy의 기존 enum·선언·보조 함수는 보호된 문맥으로 표시하고, 사용자가 편집하는 C# 본문만 기존 source 후보로 저장한다. 원래 enum ID·이름·값·순서, branch return/main continuation과 공개 핀 계약을 자동 변환하지 않는다. inline 분기 계약 변경은 현재 이 후보가 지원하지 않아 기존 제어를 읽기 전용/비활성으로 표시한다. 이 한정은 현재 구현 경계이며 새 영구 UX 정책이 아니다.

UI 변경은 `feature-authoring.js`의 복사본 표시/본문 어댑터뿐이다. 나머지 UI73개와 CSS/HTML은 기준 게시와 바이트가 같고, WebBundle은 그 파일의 정확한 canonical size/SHA만 갱신한다. strict resource 검증은 유지한다. Blueprint 850×600, 정보 카드 460px와 원래 제목 드래그·기본/독립 창·popup 조작을 사용한다.

## 검증

집중6흐름·영향5흐름, 총11흐름 56확인을 통과했다. 순수 후보2확인(정상 snapshot 보존과 소유·stale·route·cycle·scope·enum의8거절 경계)은 별도로 구분한다. 기본/독립 창, 미확정/확정 copy, 보호된 enum 선언, 직접 C# 본문 편집, 정확한 값과 donor/다른 target/보조 원문, Undo/Redo·취소·cold·Save·실제 쓰기 실패/재시도·경합·저장/조회 응답 유실 후 중복 방지·다른 창 입력/전역 Review 보호·Review 취소/명시 compiler Confirm을 검사했다. [상세 기록](evidence/v536-enum-copy-body/focused-verification.json)에 명령·체크·SHA와 실패 시도를 구별했다. 독립 checkout과 새 패키지는 다음 결과 기록에서 구분한다.

격리 fixture는 등록 팩의 같은 공개 함수 `(long,out long,out bool)->long`, common Blueprint와 별도 Windows 원문을 사용한다. enum primary/positive ID와 값0/7, 별도 branchOwner 실행 줄/return/main continuation, 공개 출력·반환을 유지한다. copy C#에서 직접 수정한 조건과 일반 본문을 함께 저장하며 원래 보조 함수·donor CRLF·한글/이모지·9223372036854775806 원문과 9223372036854775804 정보 값을 보존한다. 사용자가 편집한 textarea 본문은 LF로 보관되며 수정하지 않은 원본/보조 문자열은 그대로다.

최초 진단의 bool source는 실제 UI 거절을 보여 줬지만 원본 enum UI와 구분해 최종 지원 검사에서 제외했다. 다음 시도의 Native prepare는 성공했고 빈 화면 원인은 backend 거절이 아니라 `show()`의 형식 검사였음을 traffic으로 정정했다. 임시 예외 trace는 원래 Model 파일로 정확히 복원해 제품에 남기지 않았다. UI 어댑터 변경 뒤 WebBundle의 오래된 size/SHA가 기동을 막은 실패도 보존하고 정확한 새 파일 identity로 갱신했다. 이 실패를 통과로 합산하거나 검증을 완화하지 않는다.

## 실제 잔여

7행 전체는 미완료다. 위 copy enum 계약 변경·새 분기와 중첩/private graph copy의 qualified closure가 별도 후속이다. alias/import는 원래 UI 노출과 native/raw 고급 편집을 구분하며 막연한 영구 필수 항목으로 늘리지 않는다. 이미 통과한 외부 root copy 내부 ref→값 ABI, serial/C# copy의 생성/배정/본문, 원계약 오버라이드 보호를 반복 미구현으로 적지 않는다.

8행의 기존 다른 계약/body/private/whole/wrapper closure 결합, 9행 함수 고급 타입·표시명/native 식별자, I6 기호/이모지/사용자 로컬 이미지, B2 실제 배정 작업자 배지, A4~A6/M4/M11/M12는 그대로 별도다. 이미지 생성·협의/승자/공유 Confirm·내장 렌더/FPS 신규 backend는 구현하지 않는다. 전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 완료로 표시하지 않는다.

사용자 프로젝트·유료 AI를 실행하지 않고 fixture만 사용한다. 기존 자료·보관 빌드·로그·스크린샷·사용자 데이터는 삭제하지 않으며, 이번 검사 소유 복사본만 증거 ZIP/해시를 보관한 뒤 승인된 종료 cleanup을 사용한다.

## 독립 checkout·새 교차 패키지 검증

실행 소스 커밋 `f8e23dd8822cfdc88d6ee498e414db28babe536d`에서 기존 독립 checkout을 정상 FF하고 원래 `core.autocrlf=true`를 유지했다. 변경 파일의 Git blob과 clean 상태를 확인하고 Native Release·새 Linux 엔진·실제 기본/독립 창·enum copy 경합·권한/오버라이드 회귀 4흐름 15확인을 통과했다. 루트의 11흐름 56확인과 별도로 구분한다.

restore·솔루션 Release·명시 MCP Release·새 Windows x64 교차 패키징·패키지 probe·실제 패키지 `content/runtime/Confectory.App.dll`의 등록 함수 enum copy 독립 창 UI/컴파일러 5확인까지 6단계가 통과했다. manifest 2345개, 전체 2346개 파일/해시와 링크 부재, 실제 Core/Native DLL 및 변경 제품 소스의 바이트 일치를 확인했다. manifest SHA-256 `0d4969f257d3f211f5a083689aa5d5af44c6415c915fb8715a01471a3af18554`, Native DLL `e99c254a4454141e7f7a1045b8341183c672498726f8223aea104110baec85e3`. SDK 없는 Linux runtime에서 패키지 웹 기동·74 resource·변조/필수 의존 누락 거절·기존 프로필/명시 override 보존은 probe로 구분한다. Windows apphost/WebView2를 실제 Windows에서 실행한 검사가 아니다.

전체 manifest와 fixture ZIP을 보관·무결성 확인한 뒤 이번 RAM 검증 패키지만 정리했다. 이전 보관 패키지/원본/사용자 자료는 삭제하지 않았다. 새 전달용 산출물을 보관하거나 Library에 업로드한 것은 아니다. 기록 시 workspace 여유 1410.6 MiB. [상세 결과](evidence/v536-enum-copy-body/package-clean-verification.json)에 실제 명령·로그·SHA를 남겼다. 이 이후 커밋은 이 검증 문서와 결과 JSON만 추가하며 실행 코드는 위 소스 커밋과 같다.
