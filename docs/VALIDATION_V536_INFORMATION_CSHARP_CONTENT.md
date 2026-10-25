# I5-6 4행: 사용자가 직접 편집한 C#과 계약의 결합

v536 원본 정보 함수 상세창·구현 선택창·보호된 `C# Script` 편집기를 사용한다. 기존 CSS와 권한, 저장/Review/Confirm 구분은 유지한다. C# 원문의 자동 재작성 기능이 아니다.

## 이번 지원 경계

직접 소유한 정보 함수 하나의 native C# 구현에서 원래 body ID·target·경로·해시·native 서명과 현재 명시 함수 계약을 함께 보관한다. `코드 저장`으로 사용자가 명시한 본문만 새 후보로 제공한다. 공통/Windows와 같은 여러 C# target, 직접 C# 호출자의 원문과 typed import도 같은 후보·CAS에 담는다. 일반 Blueprint 호출자는 기존 명시 인자/소비 출력 대응을 사용한다. public 핀 이름과 native formal 이름은 구분하며, 같은 타입의 public 핀 순열도 C# 호출자 검토 없이 의미를 바꾸지 않는다.

본문은 기존 실제 코드 생성기의 함수/구현/import 경계와 Roslyn syntax·semantic diagnostics로 검증한다. 후보 검사 중 assembly emit·load·실행·파일 저장은 없다. 보호된 함수 본문 밖의 멤버 삽입은 거절한다. 누락한 target·오래된 원문/서명·다른 계약에서 보관한 본문·공유 물리 경로·외부 소유 본문·구문/타입 오류는 전체 거절한다. 실제 Review 컴파일과 명시적 Confirm은 별도로 유지한다.

편집 중 아직 `코드 저장`하지 않은 본문은 private 입력으로 재시작 복원하며, 이것을 검토된 source 계획으로 자동 승격하지 않는다. 해당 입력이 남으면 전체 저장은 먼저 코드 저장/취소를 요구한다. 기존 function-edit의 Undo/Redo·취소·settlement 조회/CAS를 재사용한다. 응답 유실은 결과 조회 후 복구하며 적용 여부를 추측하여 재전송하지 않는다. 계약이 다시 바뀌면 이전 body 계획을 자동 재동의로 쓰지 않는다.

## 검증 기록

모든 검사는 격리 fixture·실제 엔진/Chromium/컴파일러로 한다. 사용자 프로젝트·계정·유료 AI·실제 프로젝트 Run은 사용하지 않는다. 실행 로그와 초기 실패는 `/workspace/scratch/v536-information-csharp-contract`에 보존한다. check 수는 기능 수/통과율이 아니다.

- 순수 후보: native C# + Blueprint 호출자 2 check, 공통/Windows + 직접 C# 호출자 4 check 통과. 마지막 본문 오류·선택 누락·서명 불일치·공유 파일·동일 타입 순열의 검토 누락, 명시 native ref/out·반환 본문까지 검사했다.
- 실제 API: native C# + Blueprint 호출자 3 check, 공통/Windows + C# 호출자 3 check 통과. Save·cold·원본 보존·실제 compiler Review/Confirm·cold에서 한 거래로 반영된다.
- 실제 화면: 독립 창 정상 2, 기본 저장 실패/재시도 3, 독립 저장/조회 응답 유실 3, 전체 취소 2, 실제 동시 편집 충돌 2 check 통과. 함수·코드 취소, 본문 미저장 cold·입력 원문, Undo/Redo, 명시 코드 저장 및 Review 취소/Confirm을 포함한다.
- 여러 target/직접 C# 호출자를 기존 선택창에서 편집한 독립 화면 2, 동일 namespace의 두 프로젝트 전환·닫힌 코드창의 늦은 저장 차단 2 check도 통과했다. 화면 총 16 check다.
- 기존 Native 함수 계약 회귀 7, 기존 입력/출력 결합 실제 API 3 check 통과. 최종 checkout/리소스/패키지 검사는 마감 후 아래에 기록한다.

초기 화면 fixture는 `직접 작성` 상태를 `편집`으로만 찾거나 보호된 전체 textarea를 fill하려다 실패했다. 원본 버튼 상태와 본문 범위의 실제 키보드 입력으로 fixture를 수정했다. context API의 caller formal 이름 기대도 원래 `first/second`로 바로잡았다. 기존 input/output 회귀 1차는 리소스 변경과 cold가 겹친 canonical mismatch로 멈췄으므로 변경 동결/재빌드 후 3 check 모두 통과했다. 제품 보호나 CAS를 완화하여 통과시키지 않는다.

## 4행 종료 기준과 5~9행

이번 단위는 **직접 소유한 함수 하나의 native C# target들과 명시 편집 C# 호출자/기존 일반 Blueprint 호출자의 결합**이다. 코드/계약/모든 필요한 target·caller의 원래 증거·컴파일·원자 저장·입력 보존·명시적 Confirm을 수용해야 이 지원 단위를 닫는다. 하나의 구현이 Blueprint와 C# target을 섞는 경로는 현재 전체 거절하며 4행의 정확한 잔여다. 이 거절을 전체 4행 완료로 표시하지 않는다.

고정 5행 중첩 private graph 호출, 6행 whole-body/forwardCallerStorage의 ref/out 역할, 7행 등록 callable receipt·상속/copy provenance, 8행 여러 함수의 공유 caller 후보, 9행 고급 핀 타입/표시명은 별도 미완료다. 이번 native ref/out의 직접 명시 본문 후보 검사를 6행 전체 문맥 수용과 혼동하지 않는다. 임의 C# 자동 재작성이나 새 실행 모델을 추가하지 않는다.

I5-6 전체·v536 전체 UI·I6/B2 및 A4~A6/M4/M11/M12·Helper 실제 작업 완료가 아니다. 실제 Windows apphost/WebView2·모바일 기기 실행과 Library 전달은 미검증이며 교차 패키지/웹 렌더와 구분한다. 빌드/프로필/fixture/인증정보는 Git에 넣지 않는다.

[실제 코드창](evidence/v536-information-csharp-content/manual-body-code.png), [프로젝트 문맥](evidence/v536-information-csharp-content/project-context.png), [검사 결과](evidence/v536-information-csharp-content/acceptance.json)를 보관한다. v536 원본 `dist/blueprint.js:959`의 기존 Script editor/backdrop/source/status/error/취소·저장 구조를 사용한다. style/runtime/consumer CSS는 기준 `93636f2`와 byte 동일하다([근거](evidence/v536-information-csharp-content/layout-evidence.json)). 본문의 실제 header/import 문맥 안내를 넣었으며 전체 screenshot pixel 일치를 주장하지 않는다.

## 기존 Blueprint 화면 회귀의 진단

기존 typed-body fixture의 독립 창 검사에서 Blueprint 저장 버튼을 정보 창의 header가 가렸다. 변경 전 `93636f2` checkout·기존 빌드에서도 같은 hit-test를 재현했다([원래 가림](evidence/v536-information-csharp-content/baseline-window-hit.png), [DOM/좌표](evidence/v536-information-csharp-content/baseline-window-hit.json)). 정보 창은 원래 floating layer, Blueprint는 workspace layer였다. 창 z-index나 CSS를 바꿀 이유로 취급하지 않았다.

기본 창 첫 실패는 고정 `.window[data-key=schema]`를 찾지 못했다. 그 실행의 DOM screenshot을 예외 전에 보관하지 못해 최초 실패의 원인을 제품 회귀로 단정하지 않는다. 보완한 fixture는 실제 열린 정보 창을 정확한 제목/단일 인스턴스로 확인하고, 가림이 생기면 원래 title pointer-drag로 정보 창을 빈 영역으로 이동한다. 저장 버튼이 실제 hit-test 대상인지 확인한 뒤 정상 click한다. force click·직접 JS 저장 호출·숨긴 요소 삭제를 사용하지 않는다. 기능/서명/ref·out/원문·저장·명시 compiler Confirm·별도 사본의 실제 scope 호출 컴파일 검사는 모두 유지했다.

보완 후 Browser Enter 기본 창과 `새 창으로 열기` 독립 창을 각각 2 check, 총 4 check로 완주했다([기본](evidence/v536-information-csharp-content/actual-normal-save-control.json), [독립](evidence/v536-information-csharp-content/actual-view-save-control.json)). 원본 사용자 조작에 맞춘 검사 선택·배치 수정이며, 이번 진단에서 제품 데이터/저장 회귀는 재현되지 않았다. 제품 레이아웃 수정은 없다. 영향 회귀는 기존 계약 10 + 기존 본문 화면 4 = 14 check다. 전체 suite나 네이티브 Windows 통과 주장은 아니다.
