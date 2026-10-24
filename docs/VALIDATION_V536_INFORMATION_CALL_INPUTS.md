# v536 I5-6: 일반 call 인자의 직접 입력 대응

정보의 직접 소유 함수 하나에서 입력을 삭제·타입 변경할 때, 본문의 일반 call 인자가 그 root 입력을 직접 읽는 사용처도 기존 `입력 연결 갱신` 선택창에 연결했다. caller의 값/저장소 대응, 함수·구현·typed import·모든 영향 본문은 기존 한 후보/CAS와 별도 Review/컴파일/Confirm을 사용한다. C# 매개변수·본문, 레이아웃과 권한은 변경하지 않는다. 전체 I5-6 완료를 뜻하지 않는다.

## 연결과 보호

`InformationFunctionInputUses.Read/Detach`가 기존 code 노드에 더해 ordinary `call/next`의 value 인자를 받는다. 직접 소유한 같은 프로젝트 함수가 callee이고 부모가 없으며, 기존 구현의 typed import 하나와 실제 callee·call node의 서명이 정확히 일치해야 한다. 재귀 호출, wrapper, 전체 구현 문맥, caller 저장소 전달, ref/out·등록/외부/상속 callee는 이 경로에 포함하지 않는다.

graph/node/argument ID, 원래 graph hash와 바인딩 원문, 명시한 새 값 또는 정확한 타입의 현재 root 입력을 기존 선택 증거로 사용한다. 임시로 분리한 연결은 순수 후보 안에서 즉시 복원하고 전체 graph/record/source를 재검증하며 중간 상태는 저장하지 않는다. 실제 source 관찰/CAS와 저장 receipt는 기존 경계를 유지한다. callee의 선언·구현·본문은 변경 대상이 아니며 실제 선언의 동시 변경은 저장 전체를 거절한다. 알 수 없거나 빠진 사용처도 전체 거절한다.

## 고정된 다음 입력 사용처 분류

현재 소스의 `BlueprintRootContract.Inputs`, `FeatureBlueprint.Binding`, `FeatureBlueprint.Locals/AliasLocals`, `BlueprintAliases`를 대조했다. 아래는 기존 I5-6 첫 행의 위치 구분이며 새 기능 목록이 아니다.

| 사용처 | 기존 의미와 필요한 연결 | 이번 상태 |
|---|---|---|
| 일반 code/call 인자의 직접 root 값 | 정확한 기존 바인딩을 명시 값/다른 현재 입력으로 대체 | 지원 범위 |
| 수식·복합 바인딩 전체 값 | 기존 AST/타입 검증을 재사용할 수 있다. 전체 기존 JSON 증거와 전체 값의 명시 대체가 필요하며 보이지 않는 부분식을 자동 삭제하지 않는다 | 미연결 |
| 별칭 | root/node **저장소**를 가리킨다. 기존 alias API는 저장소 재지정을 단순 rename으로 허용하지 않는다. 타입·저장소 식별자·전체 사용처를 함께 명시해야 한다 | 별도 계약 결합 필요; 값 대체로 치환하지 않음 |
| 일반 local | 초기값은 constant 전용이므로 root 입력 직접 사용처가 아니다. 관련 Set 값 등 실제 인자 위치는 해당 쓰기 대상/출력 스냅샷 계약을 보존하며 연결해야 한다 | 현재 일반 call 지원에 포함하지 않음 |
| exit/내보내기 | 출력 타입과 경로/여러 할당의 식별성을 포함한 위치별 증거와 명시 대체가 필요하다. 기존 root 계약은 미대응 사용을 거절한다 | 미연결 |

위 의미는 기존 엔진 계약으로 판단 가능하며 사용자에게 새 언어 설계를 요구하는 항목이 아니다. 중첩/전체 본문/ref·out/출력 계약 변경 등은 [고정 I5-6 목록](V536_I5_6_REMAINING.md)에 유지한다. 그 문서에 우선순위와 전체 종료 기준도 기록한다.

## 검증 범위

격리 fixture의 실제 엔진·Chromium·컴파일러를 사용한다. fixture의 root 입력을 읽는 실제 `inner` call과 별도 소유 callee/typed import를 만들고 call 결과가 기존 code/내보내기로 이어지게 했다. 원래 C#과 별도 callee의 세 파일이 보존되는지 검사한다. 테스트 launcher는 기존 원자 저장 수용 검사를 재사용하며 제품에 테스트 API나 권한을 추가하지 않는다.

근거 디렉터리는 `/workspace/scratch/v536-information-call-inputs`다. 원래 작업 트리의 API 12 check(삭제 3·타입 변경 3·두 target 3·실제 callee 선언 충돌 1·caller 파일 충돌 2), 순수 후보 보호 2 check가 통과했다. 누락/변조/타입 불일치/다른 소유 선택을 거절하고 원문·기존 checkpoint를 보존한다. 실제 UI 14 check(독립 창 혼합 편집 2·타입 변경 쓰기 실패/재시도 3·저장/조회 응답 유실 2·기본 창 변경 취소 2·동시 편집 거절 2·잘못된 선택 거절→같은 세션 Undo→새 명시 선택 재시도 3)도 통과했다. 저장/Review 취소/Confirm/cold 복원과 정확 64비트 값·다른 입력·callee source 보존을 포함한다. Native 계약 회귀 7·ABI 선택 어댑터 3·기존 code 입력 혼합 저장 API 3 check가 통과했다. ABI 어댑터의 최초 실행은 필수 repo 인자를 빠뜨려 테스트 진입 전에 실패했고, 인자를 바로잡아 3 check를 확인했다. 기존 프로젝트 전환 실제 UI 회귀 2 check도 통과했다. 같은 namespace/요소 ID의 다른 프로젝트 및 오래된 form은 입력을 분리하고 source를 변경하지 않는다. 실제 Windows apphost/WebView2·모바일 기기·계정 로그인·유료 추론·사용자 프로젝트 Run·Library 전달은 이번 검증이 아니다. 전체 solution/full suite를 실행했다는 뜻도 아니다.


[실제 연결 선택창](evidence/v536-information-call-inputs/picker.png)과 [저장/확정 후 정보 화면](evidence/v536-information-call-inputs/saved.png)을 확인했다. CSS 3파일과 element-functions/call-abi-remap/WebBundle의 baseline `e46395e` byte 일치는 `layout-evidence.json`에 기록했다. 화면을 재설계하거나 원본 v536 대비 전체 pixel 일치/네이티브 조작을 검증했다는 뜻은 아니다.


## 깨끗한 체크아웃과 Windows 교차 패키지

검증 소스 커밋은 `33c39a901b71e39e0261371ee4f80a2915754daf`다. 별도 기존 clean clone을 로컬 origin에서 정상 fetch/fast-forward했다. 그 체크아웃의 Native 컴파일·Linux engine 빌드가 경고/오류/stderr 0으로 끝났고, 새로 생성한 runtime으로 API 다중 target 3 check와 독립 창 삭제 UI 2 check를 재현했다. 정상 Save/Review 취소/컴파일 Confirm/cold 복원, C#·callee 파일과 다른 입력 보존을 포함한다. 기존 프로젝트 전환을 포함한 영향 회귀는 15 check(Native 7·ABI 3·code API 3·project UI 2)이며 신규 API 12·UI 14·순수 후보 보호 2와 별도 집계다.

원래 작업 트리의 `web_resource_checkout.py`는 실제 CRLF 유지 pull/fresh LF checkout에서 74개 canonical/exact 리소스를 확인했다. 내용/UTF-8/BOM/UTF-16/단독 CR/예산/PNG 변조를 거절하고 원본 바이트를 보존했다.

Windows x64 교차 패키지는 `/workspace/artifacts/v536-information-call-inputs/Windows-x64`다. `Confectory.exe`가 시작 파일이며 .NET Desktop Runtime 10.0 x64와 WebView2 Runtime이 필요하다. 패키지 manifest는 2,331파일, SHA-256 `316e9c083d8f3eb93b20c2f8a91d76ef5c9390b73e8b1044b443ef22da16e672`다. 바뀐 두 Native source·Native DLL·기존 element-functions/call-abi-remap/WebBundle의 6파일이 검증 소스와 일치하고, 테스트/프로필/로그는 패키지에 없다.

`desktop_package.py`는 별도 cwd와 SDK 없는 복사 runtime에서 패키지 실제 엔진의 웹 기동·74리소스·최소 로그인창 렌더, 변조/의존성 누락 거절, fixture 설정 보존과 명시 override를 확인했다. 격리 fixture 외 사용자 자료는 사용하지 않는다. 이 결과는 **Windows apphost/WebView2 실행, 사용자 로그인/유료 추론, 모바일 기기 또는 Library 첨부 전달 성공을 뜻하지 않는다**. 전체 I5-6 및 v536 UI는 [고정 잔여 목록](V536_I5_6_REMAINING.md)대로 미완료다.

재현: `v536_information_call_inputs_api.py`에 repo·Linux build JSON·delete/type/multi/callee-conflict/conflict를 전달한다. `v536_information_call_inputs_ui.py`는 동일 인자와 mixed/type-storage/delete-loss/delete-cancel/type-conflict/type-retry, 독립 창은 마지막 `view` 인자를 사용한다. `v536_information_call_inputs_guards.py`는 실제 파싱한 원래 자료의 순수 후보만 검사한다. 기존 code 입력 suite를 공통 사용하되 새로운 call fixture가 실제 use-site를 바꾼다. 패키지·빌드·프로필·실행 로그는 Git에 포함하지 않는다.
