# v536 다중 구현과 C# 변환 문맥 검증

2026-10-23, `work/current` `b4afc88` 이후. 기준은 사용자 지정 main `196c605`의 원본 v536이다. 새 화면·전역 구현 ID 입력창·권한을 만들지 않고 기존 객체/모듈 슬롯과 전역 기능의 원본 진입점을 연결한다. 전체 v536 복원 또는 Windows 실기기 수용 완료 문서는 아니다.

## 원본 의미와 이번 유한 범위

원본 `functionNodeMarkup`/`resolveModuleFunctionImplementation`/`openFunctionAuthoring`은 객체·모듈의 선택된 기능 구현을 편집한다. 같은 global function의 임의 implementation IDs 전용 전역 picker/추가 폼은 원본에서 확인되지 않았다. 이 의미를 발명하지 않는다.

이번 실제 UI fixture에는 같은 Calc 기능의 **객체 A→Alpha Blueprint, 객체 B→Beta Blueprint, 전역 명시 provide→Default C# common**이 공존한다. Default에는 다른 Windows C# 본문도 있다. 기존 `featureBodies`/readConversion/convertBody와 owner-bound graph basis를 그대로 사용한다. 선택은 원본의 객체·슬롯/기능 열기로 명시하며 첫 구현을 임의 선택하지 않는다. 본문/target별 private key와 source/owner CAS, 검토·명시적 compiler Confirm은 유지한다.

## 수정

1. 실제 A→B 전환에서 이미 열린 객체 창이 이전 Blueprint 뒤에 남아 슬롯 편집 버튼을 가렸다. 명시적인 `act(select)`의 schema 열기에서 해당 창을 focus한다. 배경 projection/복원 갱신에 무조건 focus를 주지 않는다.
2. `openInWork`가 같은 기능의 직전 `blueprintGraph`를 전역 재진입 문맥으로 재사용했는데, 그것이 객체 슬롯/복사 편집의 graph인지 구분하지 않았다. 전역 선택 기록은 같은 프로젝트·기능의 **전역 문맥만** 재사용하며 `slotOwner`/`copyDraft`는 제외한다. 저장된 슬롯·복사 입력은 삭제하지 않는다.
3. 재사용 기능 창의 title/aria-label을 현재 기능으로 갱신한다. 기존 이름 input의 tooltip에는 선택한 owner/implementation/body target을 표시한다. 화면 영역/버튼/크기는 그대로다. 로딩 중에는 이전 body/owner DOM 표식을 비우고 server 확인 후 새 표식을 채운다. 테스트는 이전 창의 enabled 버튼을 로드 완료로 오인하지 않고 이 표식과 실제 RPC/내용/저장 결과를 함께 확인한다. DOM 표식은 권한 또는 서버 검증의 대체물이 아니다.

4. 마지막 실패 재시도 검토에서 추가 결함을 재현했다. 슬롯 뒤 전역 목록 조회가 실패하면 `loading`이 owner는 지우고 예전 graph는 남겨, 다음 전역 재시도가 해당 슬롯 graph를 선택할 수 있었다. 초기화는 오래된 graph를 지우고, 명시적으로 선택한 전역 body/슬롯 graph는 비동기 조회 전에 해당 문맥에 기록한다. 실패·presentation 복원 뒤에도 그 정확한 body만 재검사하며 다른 구현으로 fallback하지 않는다. 새 권한이나 자동 동의는 없다.

변경은 UI 어댑터와 리소스 hash뿐이며 backend 읽기/쓰기/소유권/변환/Confirm 계약을 변경하지 않았다. CSS와 원본 ZIP을 수정하지 않았다.

## 실제 엔진 + Chromium 통합: 9건, 전체 exit 0

`tests/web/v536_multiple_implementations.py`, 증거 `/tmp/confectory-multiple-implementations-jw73x92g`:

1. 실제 A/B 슬롯 선택·전환과 Script 취소가 Alpha/Beta의 두 비공개 본문을 분리 보존한다.
2. 슬롯 편집 후 전역 진입은 슬롯 graph가 아닌 명시 provide Default C# common의 비공개 미리보기를 연다.
3. 실제 프로세스 재시작 후 세 문맥을 다시 선택해 미저장 한글/emoji와 본문을 복원한다. 원본 BOM/CRLF, Windows 대상·소유 객체는 유지된다.
4. A/B 입력을 둔 변환 Save의 **실제 서버 완료 후 응답 유실**을 격리 renderer에 주입한다. UI 실패와 서버 저장 결과를 구분하며 입력·원본·다른 구현을 보존한다.
5. 유실 뒤 실제 cold 복원·명시 재시도는 같은 conversion origin을 확인해 중복 graph/node를 만들지 않는다. Save 응답 대기 중 추가한 새 본문도 남긴다.
6. 늦은 입력은 다음 별도 Save에서만 Default/common에 저장하고 A/B private input을 보존한다.
7. 전환 Review 취소는 소스를 반영하지 않는다. 새 Review token과 명시적 실제 compiler Confirm만 Default 선언·새 graph/node를 반영한다. 원본 C# 파일/Windows/A/B는 byte-identical이다.
8. Alpha/Beta를 실제 UI에서 각각 Save/Review/compiler Confirm한다. 각각 선택한 node 파일만 변경하고 다른 구현·함수·모듈·객체·전역 전환 결과를 보존한다.
9. 다른 편집자가 B의 provider를 바꾼 뒤 오래된 슬롯 Save는 거절한다. 새 private33/확정 Beta22와 다른 모든 소스·입력은 보존한다. mismatch를 자동 승인하거나 새 provider에 적용하지 않는다.

fixture는 자체 선언·graph·node·profile/registry만 만든다. Main은 세 구현을 참조해 compiler 검증에 포함하지만 프로젝트 실행은 하지 않는다. 실제 사용자 프로젝트/계정/인증파일·유료 inference는 사용하지 않는다. 생성 fixture의 파괴적 변경은 사용자 자료로 전파되지 않는다.

개발 중 첫 실제 실행은 창 가림을 재현했고, 다음 실행은 슬롯 graph가 전역 기본값으로 재사용됨을 확인했다. 이후 테스트에서 cold 창 포커스와 비동기 선택 완료 대기를 실제 UI 동작에 맞췄다. Save를 보류한 route 내부에서 presentation flush를 재귀 대기하지 않도록 장애 주입 helper도 수정했다. 이 과정의 부분 PASS를 전체 통과로 계산하지 않고 최종 위 9건/exit0만 최종 결과로 사용한다.

## 영향 회귀

`v508_module_slot_renderer.py`: **10건, 전체 exit 0**, 통제 provider와 실제 renderer를 사용한다. 두 객체 슬롯, A/common·B/common·B/windows 본문별 입력 분리/명시 복원, 알 수 없는 대상 거절, 정확한 source 증명에 한정한 legacy 입력 이관, 슬롯 외 입력 보존과 저장 payload를 확인한다. 증거 `/tmp/confectory-slot-editor-renderer-k9f61u6h`. 추가 2건은 실제 renderer에서 목록 조회 실패 후 슬롯의 전역 승격 차단, 명시 body 읽기 실패 뒤 같은 target 복원/재시도를 확인했다. 추가 결함을 수정한 최종 코드에서 위 실제 엔진9건도 다시 전체 exit0을 확인했다. 실제 backend 성공 증거와 controlled provider 결과는 구분한다. 기존 단일 C# 전환 검사를 의미 없이 반복하지 않았다.

생성 Linux 엔진 build 통과. 구문·리소스 hash·diff 검사를 수행한다. Windows 교차 package/clean checkout/정상 게시 결과는 최종 기록에 구분한다. 실제 캡처 `three-implementation-contexts.png`를 열어 확인했으며 원본 레이아웃/CSS와 같은 기존 frame을 유지한다. 이 캡처가 모든 화면의 pixel equality 증거는 아니다.

## 한계와 다음 ABI 작업

- 원본에 없는 전역 임의 구현 ID picker/추가 화면은 만들지 않았다. 전역은 명시 provide·실제 실행 target/common 또는 확인된 기존 전역 body 문맥만 사용한다. 미해결/모호한 여러 구현은 기존 안전 차단을 유지한다.
- 객체 슬롯의 C#/여러 실행 대상·상속/등록 원본은 기존 명시적 **복사 편집** 경로와 그 소유권 계약을 유지한다. 이번에 이를 원본을 직접 수정하는 일반 변환 권한으로 확대하지 않았다. 외부 등록 source 직접 편집·범용 언어 변환 backend를 구현한 것이 아니다.
- 실제 UI 엔진 검사는 위 세 구현/common 문맥이다. Windows 본문은 보존을 확인했고 대상별 입력 분리는 controlled renderer로 확인했다. Windows target의 실제 native 실행/OS 창/DPI/IME나 모든 다중 View 조합을 새로 수용한 것은 아니다.
- 실제 계정/Agent 동의/Helper 권한/다른 프로젝트/최종 Confirm·프로젝트 실행 권한은 변경하지 않았다. Library의 이전 `tools/list` 네트워크 장애에 새 복구 근거가 없어 이번 작업에서 재호출하지 않았다. 이전 ZIP은 전달 성공 상태가 아니다.

다음 고정 단위는 나머지 호출 ABI다: 먼저 기존 단일 소유 호출의 값↔ref 외에 원본이 요구하는 호출 형태와 **소유 슬롯/복사본/등록 callable/target 문맥** 목록을 고정한다. 기존 typed import·호출 signature·공개 SourceContext 출력 계약을 같은 명시 갱신에서 검사하고, 지원 backend와 단순 UI 미연결을 분리한다. 비호환 핀을 추측해 바꾸거나 지우지 않으며 취소/저장/cold/Review·명시 Confirm과 소유권 보호를 확인한다. 아직 이 후속 ABI 구현을 시작하지 않았다.

## 패키지와 게시 검토

Windows x64 교차 package **2,305 선언 파일+marker**, UI canonical/exact resources **66개**를 생성했다. `desktop_package.py` 전체 exit0: apphost/런타임/packs/UI 구성, 누락/변조 거절, 설치 SDK 없는 runtime-only 환경의 다른 cwd에서 실제 packaged managed 웹 시작, 최소 로그인 화면·기존 profile 재사용/명시적 override를 확인했다. 증거 `/tmp/confectory-desktop-package-_q1daq7e`. **Windows apphost와 WebView2는 실행하지 않았다.**

로컬 exe는 `/workspace/artifacts/Confectory-v536-multiple-implementations-final/Windows-x64/Confectory.exe`다. 전체 폴더를 함께 두고 실행하며 .NET Desktop Runtime 10.0 x64 및 Edge WebView2 Runtime이 필요하다. 사용자 PC에 자동 설치하지 않았다. marker SHA-256 `5dca693077a97c761d36d51030f2841cbe464823a53ca964f74099a678618e36`, 전체 파일 목록 checksum `0077f0c358194b997ca29b5a96769b2b8676e8035f9d52cfc79b76e4e58fde03`. 로컬 경로는 Library 전달 완료를 뜻하지 않는다.

검토 대상은 구현4·테스트2·문서3 = **9파일**, 비밀정보 탐지0이다. 생성 빌드/로그/사용자 데이터/인증정보는 Git에 넣지 않는다. 원본 v536/v508 ZIP hash와 CSS·Android 설정은 그대로다. 승인된 `https://github.com/jorodane/Confectory.git`의 `work/current`에 정상 commit/push만 수행한다. 커밋 후 clean checkout의 솔루션/생성 엔진/일반 CRLF·LF 리소스 검증 및 direct remote SHA 결과는 완료 체크포인트에 기록한다. main을 merge/reset하거나 수정하지 않는다.
