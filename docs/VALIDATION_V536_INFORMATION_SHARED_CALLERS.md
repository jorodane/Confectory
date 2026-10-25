# v536 정보 함수 공유 호출자 결합 저장 검증

이 문서는 e827a52의 이름 변경 단위 기록이다. 이후 타입 결합의 현재 상태는 [공유 값 입력 타입 검증](VALIDATION_V536_INFORMATION_SHARED_TYPES.md)과 고정 범위 문서를 따른다.

[고정 8행의 첫 지원 범위](V536_I5_6_SHARED_CALLERS_SCOPE.md)는 같은 정보가 소유한 일반 Blueprint 함수 여러 개의 값 입력 이름 변경이다. 기존 상세창·임시 저장·취소·Review/Confirm을 사용한다. 함수/구현 ID나 원본 v536 HTML/CSS/JS는 변경하지 않았다. 7행의 새 계약으로 독립 복제하는 정책은 답변 대기 상태를 유지하며 이 구현에서 사용하지 않는다.

## 변경

기존 검증은 두 번째 연결된 함수에서 전체 후보를 거절했다. 이제 이 좁은 경계에서는 첫 pure closure의 결과를 내부 overlay에 준비하고 다음 closure가 그 상태를 읽는다. 같은 caller 그래프에 대한 갱신을 한 개로 합치되 최종 제출 해시는 원래 사용자 스냅샷의 해시다. 물리 소스 관측·소유권 검사는 그대로 유지한다. 각 closure를 따로 저장하지 않으며 기존 전체 후보/CAS 및 저장 결과 receipt만 사용한다.

새 `InformationFunctionBatch`는 Native authoring 내부 조정자다. 새 RPC·실행 도구·test API·접근 권한을 노출하지 않는다. 현재 직접 소유 함수 2~8개, 같은 위치/타입의 값 입력 이름, 직접 소유 직렬 code/call/export Blueprint만 허용한다. 타입/역할/출력·반환·C#·copy·상속·중첩·wrapper 또는 다른 속성 변경을 혼합하면 입력을 유지하며 거절한다. 계약이 그대로인 여러 설명 편집과 계약 하나+다른 함수 설명 편집은 기존 native/ref 경로를 유지하도록 별도 회귀를 추가했다. 7행 guard는 제거하지 않았다.

## 집중 검증

두 함수가 같은 caller에 연속 호출되며 첫 호출의 반환이 두 번째 호출 입력에 연결된 격리 fixture를 사용했다. 실제 compiler와 Chromium을 사용하되 프로젝트 실행·사용자 계정·유료 추론은 사용하지 않았다.

| 검사 | 확인한 결과 |
|---|---|
| 순수 후보 4 check | 두 계약/공유 caller의 결합, 중복 ID 없는 원래 해시, 편집 역순의 동일 결과, 마지막 함수 오류/누락 소스/copy·native 문맥의 전체 거절, 계약 불변 설명 편집과 계약 하나+설명 편집의 기존 native/ref 경로 보존 |
| 실제 API 4회 / 11 check | 정상 저장·cold·compiler Confirm, checkpoint 쓰기 실패 후 재시도, live owner 경합, 실제 공유 caller 파일 변경, 두 번째 계약 오류의 전체 미적용 |
| 실제 화면 8회 / 18 check | 기본/독립 창, 상세창 취소, 두 입력 Undo/Redo와 미저장 재시작, 저장 실패/재시도, 저장/결과조회 응답 유실 후 조회만 수행, 변경 취소, 프로젝트 전환 및 오래된 submit 차단, 타입 변경 거절→Undo→정상 재시도, Review 취소/명시 Confirm |

check 수는 각 실행의 반복 공통 준비 단계도 포함하는 관측 문구 수이며 고유 기능 수가 아니다. 영향 회귀 및 clean checkout의 재현 횟수와 합쳐 새 기능 수로 주장하지 않는다. 화면에서 기존 460px 정보 카드와 exact64 기본값을 확인했고 실제 생성 screenshot을 열어 살폈다. UI 소스 파일은 기준 `0f69535` 대비 바이트 불변이다. 전체 pixel equality를 주장하지 않는다.

초기 두 번째 fixture의 node hash는 최종 함수 선언을 기준으로 준비되지 않아 단일 두 번째 함수에서도 stale이 재현됐다. 기존 정상 authoring metadata로 최종 definition hash를 준비하여 fixture를 고쳤으며 검증을 완화하지 않았다. 재시도 화면 검사는 원본 연결 갱신창의 정상 취소를 먼저 수행하도록 고쳤다. 가려진 저장 버튼을 force click하거나 원본 레이아웃을 변경하지 않았다. 실패 로그는 로컬 scratch에 보존한다.

실행별 결과/해시·기본 화면 근거는 [집중 검증 기록](evidence/v536-information-shared-callers/focused-checks.json)에 정리했다. 전체 로그·프로필·fixture·빌드는 Git에 포함하지 않는다.

## Checkout·교차 패키지

최종 실행 코드 커밋은 `070d5a6c87fcd3cd428c352cc4080dcfc086ea2c`이다. 전체 Release 및 MCP Release 빌드는 경고/오류 0건이며 Linux 엔진 빌드도 `tool.ok=true`다. 기존 단일 함수 API 2 check와 상속 원본/위조·경합 보호 3 check를 추가 회귀 확인했다. 기존의 깨끗한 재현 checkout을 해당 커밋으로 fast-forward하여 Native Release를 빌드하고 순수 후보 4·실제 API 3·독립 창 2의 **9 check**를 재현했다. 이는 집중 33 check와 구분한 재현 횟수다.

Windows x64 패키지는 `/workspace/artifacts/v536-information-shared-callers/Windows-x64`에 생성했다. Windows에서는 전체 폴더를 유지하고 `Confectory.exe`를 연다. manifest의 **2,343파일** 해시와 marker를 포함한 2,344파일 집합·symlink 부재를 확인했다. manifest SHA-256은 `9d8f3fa88b1e8c62753ba2fe32228e02aa3be6ef41c34c394a81be15bd42f559`이다. 패키지의 변경 제품 소스 두 파일과 Native DLL은 검증한 현재 소스/Release DLL과 바이트로 일치하며, Core DLL 7개도 모두 현재 Release Core와 일치한다. 패키지에 포함된 Native로 공유 caller 후보 4 check를 추가 실행했다. 이후 검증 문서와 probe 테스트만 바뀌므로 실행 코드 기준은 위 구현 커밋이다. assembly revision 문자열만으로 포함 코드를 판정하지 않았다.

패키지 probe는 SDK가 없는 런타임·다른 작업 경로에서 managed 엔진을 시작하고 74리소스·최소 Agent 화면, 변조 리소스/누락 DLL 거절, 기존 checkout 프로필과 명시 경로 override를 확인했다. 최초 실행에서는 Chromium 탭이 `Target crashed`로 종료됐다. 정확한 원인은 확정하지 않았다. 실패 로그를 보존한 채 새 대형 복제를 만들지 않고, 실패 fixture의 SDK 없는 런타임 전체를 SDK 원본과 대조해 읽기 전용으로 재사용했다. 새 legacy 프로필 fixture는 현재 패키지의 hard link로 만들고 전체 manifest·inode를 대조했다. 이 tree는 변조 검사 이후 읽기 전용 확인에만 쓰고, 종료 후 원본 패키지 해시도 다시 검사한다. 브라우저 임시 파일은 별도 권한이 확인된 전용 RAM 디렉터리에 한정하여 동일 검사를 모두 통과했다. 선택적 fixture 경로와 `CONFECTORY_BROWSER_TMP`는 검사용 저장 위치를 정할 뿐 기존 SDK 부재·변조·프로필·화면 검사를 제거하지 않는다. 이전 패키지는 `.previous-202610251159243430967`로 보관했고 기존 산출물은 삭제하지 않았다.

이는 Linux에서 수행한 교차 패키징과 packaged managed 엔진/Chromium 검사다. Windows apphost/WebView2나 실제 모바일 기기 실행은 아니다. 로컬 패키지 경로는 Library 전달 성공을 의미하지 않는다. [최종 재현·패키지 근거](evidence/v536-information-shared-callers/final-verification.json)에 실행별 로그 해시·파일 해시·공간 사전 측정과 제한을 남겼다.

## 남은 범위

- **7행:** 독립 copy의 새 계약 정책은 사용자 답변 대기다. 새 ID·원본 계약 교체·호출 재연결을 구현하지 않았다. 미확정/다른 함수 ID/다중 target copy, 상이한 native 문맥, 직렬 whitelist 밖 그래프도 기존 잔여다.
- **8행:** 타입·핀 수·순서·ref/out·출력/반환 변경, 사용자가 편집한 C# 본문, private/whole/wrapper 및 copy/상속/등록 문맥의 여러 계약 결합은 미완료다. 이번 지원 이름 변경과 다른 속성 편집의 혼합도 범위 밖이다.
- **9행:** 함수 핀의 정보/참조/외부 named 타입과 표시명/native 식별자 분리가 미구현이다. `Parser.Type`은 현재 기본 CLR 타입/배열만 받고, `FieldTypes.Project`는 속성 정의용 catalogue다. 선택창 항목만 추가해 named 타입을 `object`로 조용히 치환하지 않는다. 이 문법/타입 어댑터 작업은 7행의 새 copy 정책과 별개인 기존 명세의 미구현이다.

전체 I5-6/v536 UI 완료가 아니다. 실제 Windows apphost/WebView2·모바일 기기 입력과 Library 전달도 미검증이다. 원본/외부 팩·main·사용자 데이터를 보존하며 추가 기존 파일 삭제는 하지 않는다.
