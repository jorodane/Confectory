# v536 I5-6: 연결된 정보 함수의 첫 계약 편집 단위

원본 정보 함수 상세창에서 바꾼 핀을 기존 ID로 대응하고, 프로젝트 소유 callee 구현·실제 caller·필요한 import/require·graph/record를 기존 한 후보와 checkpoint CAS에 결합했다. C# 본문은 자동 재작성하지 않는다. 이 문서는 첫 지원 단위이며 I5-6 전체 완료 증거가 아니다. 정확한 잔여 조작은 [V536_I5_6_REMAINING.md](V536_I5_6_REMAINING.md)에 고정했다.

## 기존 화면과 서버 계약

`openFunctionSignatureEditor`는 원본 상세창의 기존 행 ID로 원래 signature/각 인자의 명시 대응을 캡처한다. 여러 번 편집한 pending 대응도 원래 기준으로 합성한다. Undo/Redo·취소·저장·복원은 기존 입력 Map과 owner 저장 흐름을 사용한다. HTML/CSS나 레이아웃, 계정·Agent·실행·Confirm 권한은 바꾸지 않았다.

서버가 `SlotContext.guards`로 전체 읽기 기준을 구성한다. 클라이언트가 임의 units나 권한을 지정하는 계약을 추가하지 않는다. `InformationDefinitions`는 직접 소유 contained 함수의 ID/경로/hash와 명시 before/args 대응을 확인한다. 옛 요청에 대응 정보가 없으면 기존 연결 계약 거절을 유지한다. Native helper가 만든 linkedUpdates만 종류·ID·경로·원래 hash를 검사하여 stage한다. graph/record/source 검증과 compiler Review/Confirm은 기존 경계를 그대로 사용한다.

일반 Blueprint 루트는 입력 바인딩을 명시적으로 옮기고 내부 code 매개변수와 C# 내용을 유지한다. caller의 typed import/입출력 연결도 함께 검사한다. C# 구현의 안전한 순열은 공개 함수와 구현의 자체 매개변수 이름을 구분해 보존한다. 모듈 require와 모든 target도 같은 후보에 포함하며, 불명확한 C# wrapper/본문 변환은 거절한다. 부분 저장이나 연결 자동 삭제를 허용하지 않는다.

## 확인한 결함과 수정

동일 token 수의 `ref`/쉼표 재배치가 기존 병합에서 `longcount`처럼 두 단어를 붙이는 것을 재현했다. 단어/구두점 경계가 달라질 때 제한된 clause 구조 교체를 사용하고, 버릴 수 없는 inline 주석은 거절하도록 고쳤다. import/body/blueprint/require/default의 선언 identity를 보존하는 제한된 `MergeContract`를 추가했다.

외부에서 caller graph 파일을 바꾼 뒤에도 새 저장 후보가 수용되는 실제 API 재현을 찾았다. 물리 파일은 최종 Confirm 전에 보호되지만 저장 시점 차단이 늦었다. 원래 raw baseline/원문과 실제 파일을 대조하고, 기존 원자 Save의 source guard를 이 계약 경로에서도 stage 전·checkpoint 저장 직전에 재검사하도록 연결했다. 최신 파일을 새 기준으로 삼는 자동 덮어쓰기 재시도는 하지 않는다.

첫 UI 충돌 fixture는 화면이 stale 입력을 서버 요청 전에 거절했는데 `applySlots` 응답을 기다려 실패했다. 실제 오류 표시와 요청 미발생, 입력/peer 원문/checkpoint 불변을 함께 검증하도록 수정했다. 첫 후처리 fixture의 profile도 기존 명세인 `sync-acyclic-methods-v1`로 맞췄다. 검사를 제거하거나 보호를 완화하지 않았다.

## 검증 기록

격리 fixture와 실제 엔진/Chromium/compiler를 사용했다. 사용자 프로젝트·실제 계정·유료 추론은 사용하지 않았다. 상세 로그는 `/workspace/scratch/v536-information-function-contracts`다. 수는 각 시나리오의 check 수이며 기능 수나 통과/실패 비율이 아니다.

| 검사 | 결과 |
|---|---|
| Native SDK / Linux | Native-6 / Linux engine-5 warnings/errors/stderr 0 |
| Native 순수 후보 | 7 PASS: 안전한 C# 순열/구현 이름 보존·stale/중복 대응 거절, C# 다중 target/module require, Blueprint callee/caller/모든 target/후처리와 원문 보존 |
| 실제 API | normal 2, 쓰기 실패/재시도 3, live 충돌 1, 다중 target/후처리 2, 정보 provide에 scope를 둔 실제 호출 2, 위조/권한/다른 프로젝트 1, caller 물리 변경 거절 1 PASS. 최종 source guard 보완 후 caller 거절/다중 target/정보 scoped 호출을 재검증했다 |
| 실제 화면 | 기본 2, 독립 2, 취소 2, 쓰기 실패/재시도 3, live 충돌 2, 응답·조회 유실/cold 2, 거절→Undo 재시도 3, 동일 namespace 프로젝트 전환 2 PASS. 8회 실행 18 check. 최종 source guard 보완 후 응답 유실 2/Undo 재시도 3을 추가 재현했다 |
| 기존 회귀 | raw owner 5, I5-5 순서 4, 자체 함수 7, 함수 전체 삭제 9, 구현만 삭제 추가 7 PASS. 구현 검사 안의 기존 함수 9는 중복 합산하지 않음 |
| 원본 화면 | style/consumer/runtime CSS는 c370e5a와 byte 일치. 기존 정보 상세창과 기본/독립 창을 사용. 새 폼/패널/레이아웃 없음 |
| 교차 패키지 | 최종 source guard 보완 후 win-x64 PE 2330파일. SDK 없는 runtime-only에서 실제 패키지 엔진 웹 기동·74개 리소스·최소 연결창 렌더·변조/누락 의존성 거절 PASS |
| 깨끗한 checkout/리소스 | 소스 `19931e6ab0f5360c2f6b2f564333ea6ab1f93324`: Native/Linux warnings/errors/stderr 0, 실제 다중 target API 2 + 독립 창 화면 2 PASS. 실제 CRLF pull/fresh LF 및 canonical/exact 74개, 변조/인코딩/BOM/binary/budget 거절 PASS |

기본 [화면](evidence/v536-information-function-contracts/primary.png)과 독립 [화면](evidence/v536-information-function-contracts/detached.png), CSS 근거 `layout-evidence.json`을 남겼다. 전체 화면의 pixel 일치나 native 조작을 검증했다는 뜻이 아니다.

## 배포와 제한

로컬 패키지 경로는 `/workspace/artifacts/v536-information-function-contracts/Windows-x64`, 진입점은 `Confectory.exe`다. 마지막 source guard 수정 후 다시 만든 패키지를 검사했다. manifest SHA-256은 `76d88adfb9b228c3fcf4649ee3753cedf7273dc3051ee5231209ad05c1cf8a51`이며, 바뀐 source 9개와 Native DLL의 패키지 byte 일치를 확인했다. 테스트/인증/프로필/로그 경로는 manifest에 없다. 로컬 경로는 Library 첨부 전달 성공을 뜻하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 생성 빌드·프로필·로그·인증 자료를 Git에 포함하지 않는다. 실행 source는 `19931e6ab0f5360c2f6b2f564333ea6ab1f93324`에 대응하며 이후 문서 마감은 실행 파일을 바꾸지 않는다.

한 직접 소유 함수의 검증된 계약 변경을 지원한다. C# 재작성·nested consumer·전체 본문 문맥/저장소 전달, 등록/복사 출처의 이 경로 수용, 연결된 출력의 전체 편집과 여러 함수 동시 후보는 미완료 또는 명시 거절이다. 공개 출력은 호출 후 SourceContext 의미이며 프로젝트/외부 공유 권한으로 확장하지 않는다. I5-1~5를 보존하며 나머지 UI 범위를 이번 변경에 섞지 않았다.
