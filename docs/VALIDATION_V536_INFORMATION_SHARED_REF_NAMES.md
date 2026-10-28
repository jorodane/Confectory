# 고정 8행: ref 계약의 핀 이름과 기존 본문 검토 결합

기준은 `4f2836ad5335733e37383d87621ef3109fd194bb`의 v536 상세창·C# 편집/
호출 확인 UI와 기존 단일 함수 closure다. 이번 단위는 ref를 포함한 직접 소유
함수 둘의 값/ref 핀 이름을 명시 대응으로 바꾸면서 원래 타입·역할·수·순서·
반환과 실제 저장소를 유지하는 경계다. 원래 본문 검토가 필요한 저장소 전달
노드는 명시 C# 원문·native 매개변수·출력/graph receipt를 제출해야 한다.
새 UI/레이아웃·새 역할 모델·계약 ID·권한이나 자동 C# 재작성을 만들지 않는다.

## 원본 조작과 종료 기준

원본 정보 상세창은 이름·타입·추가/삭제를 제공하며 값/ref/out 전달은 기존
C# 편집 경로에서 다룬다. 정보 상세창에 순서 드래그/전달 방식 제어를 추가하지
않는다. 기본 ref 구현은 `forwardCallerStorage`를 사용한다. 본문 검토 없이
그 계약을 바꾸는 요청은 단일 함수에서도 정상 거절되며 미구현 결함으로 세지 않는다.

- normal: 두 함수의 `long amount, ref long count`에서 값/ref 이름을 각각
  left/rightAmount와 left/rightCount로 변경한다. C# 원문·형식 매개변수 이름
  amount/count는 그대로 명시 검토한다. 두 호출은 같은 caller ref 입력 second를 유지한다.
- mixed: 첫 함수는 ref, 둘째 함수는 값 전달을 유지한다. 두 함수 이름을 함께
  바꾸되 각 원래 역할과 바인딩을 유지한다. 값 역할을 ref로 승격하지 않는다.

기본/독립 460px 화면에서 상세 편집 취소, C# 검토 취소/재열기·원문 코드 저장,
기존 호출/출력 확인, 마지막 함수 전체 Undo·Redo, 미저장/저장 재시작,
저장 실패/재시도·응답 유실/결과 조회·충돌/취소·프로젝트 전환과 Review/Confirm을
격리 fixture로 검증한다. Power의 정확한 9223372036854775806과 원문·다른 함수/
부모/외부 원본은 보존한다.

## 구현 경계

`InformationFunctionBatch.Begin`에서 ref가 포함된 그룹은 모든 행의 원래
위치별 타입·역할·핀 수·반환 및 명시 이름 대응을 고정한다. caller 계획이 있으면
원래 입력 이름만 선택하고 해제/출력 재선택을 허용하지 않는다. 실제 selected
callee의 code/next 저장소 전달 노드에 해당하는 본문 검토가 있을 때만 기존
단일 retained-body 검증으로 넘긴다. before/native/public 서명·본문 hash·graph
receipt·출력 대응과 컴파일 검증은 기존 단일 closure가 전부 반복한다.

copy/private/implementationContext/postCall·native target·지역/별칭·callee 간
의존 문맥은 기존 그룹 차단을 유지한다. 원래 요청 전체를 먼저 검사한 뒤 내부
callee/caller overlay를 합성하고 원래 source hash로 한 번의 후보/CAS를 저장한다.
`MappingFor`·`ProjectOutputs`·`Merge` 본문과 원래 CAS 보호는 바꾸지 않는다.
공유 원본/오버라이드 계약을 변경하거나 새 독립 계약을 만들지 않는다.

## 실제 검사 기록

초기 조사에서는 본문 검토를 생략한 요청이 단일에서도 정상 거절됐다. 검토를
포함한 before-2의 normal/mixed 2흐름·4확인으로 단일 후보 유효/기존 그룹만
거절됨을 재현했다. Native Release 경고·오류 0이다.

초기 fixture는 이름 변경 후 contractHash를 원래 값으로 기대했다. 기존 생성기는
새 선언에 맞춰 hash를 갱신하므로 native featureBlueprintNodes의 독립 계산/
검증과 대조하도록 수정했다. 이미 구현이 있는 선언을 새 선언 scaffold에 넣던
검사도 기존 생성 경계를 우회하지 않고 같은 native 검증으로 바로잡았다.
화면에서는 본문/호출 확인이 추가된 Undo 이력을 고정 2회로 가정한 검사를
보완했다. 마지막 함수 전체가 사라지고 첫 함수만 남는지, Redo가 전체 입력을
복구하는지 검사하며 제품 동작/검증을 약화하지 않는다. 실패/조사 로그·ZIP은 보존한다.
집중 13흐름·34확인, 영향 6흐름·20확인이 통과했다. 두 후보/역순·원래 hash·
잘못된 타입/역할/순서·caller 재선택·본문 누락/구문/서명/receipt/출력 오류와 실제
source 충돌의 전체 미적용을 확인했다. ref/ref 및 ref/값 API의 원자 저장·cold·
Review/Confirm과 물리 source 경합도 통과했다. 실제 기본/독립 창의 명시 C# 검토·
취소/재열기·호출 확인·전체 Undo/Redo·저장/미저장 cold·검토 취소/Confirm,
checkpoint 실패/재시도·저장/조회 응답 유실/receipt 중복 방지·실제 peer 경합·
프로젝트 전환/오래된 창 제출 차단·불완전 마지막 매핑/Undo 재시도를 통과했다.
초기 조사/fixture 실패와 수정 근거를 구분하며 미해결 실패는 없다.

기존 입력/출력 정의·void 결합, 입력 정의/반환, 입력 타입/출력 정의, 이름 편집,
오버라이드 보호 및 이전 출력 없는 경로도 영향 회귀했다. UI 74리소스+WebBundle
75파일은 82e2676와 바이트가 같다. 새 증거 ZIP25개의 집합·권한·전체 바이트·
SHA-256을 재검증했다. 기존 자료 삭제·변환은 없다.
[집중·영향 근거](evidence/v536-information-shared-ref-names/focused-verification.json)에 기록했다.
독립 checkout·새 교차 패키지는 이후 별도 기록한다.

## 정확한 잔여

이 단위는 ref 역할·타입·수·순서·반환 변경이나 I5-6/8행 전체 완료가 아니다.
기존 직접 함수의 그런 조작은 해당 명시 본문/저장소 대응을 결합할 후속 경로로
남긴다. 오버라이드의 원계약 구조 변경은 정상 금지며 미구현으로 분류하지 않는다.
독립 계약 복제는 필수 범위에서 제외한다.

8행의 남은 계약 혼합·순서/역할과 함수 간 의존·C#/중첩/private·whole/postCall,
같은 원래 계약 copy/상속/등록·소유 정보 속성 및 scalar 밖 타입 결합은 별도다.
9행 정보/참조/외부 함수 타입·표시명/native 식별자 분리, I6/B2·A4~A6·
M4/M11/M12는 유지한다. Helper 실제 작업 도구는 UI 이후 별도이며 새 이미지/
협의/렌더 backend는 이번 범위 밖이다. 실제 Windows/WebView2·모바일 기기
실행과 Library 전달은 브라우저/managed 검증과 구별한다.

## 독립 checkout·새 교차 패키지 완료

실행 소스는 `bba95dcb1ac94737b7e793a5897f5100cd3604d6`다. 기존 독립 checkout을 정상 fast-forward하고
9개 Git blob·기존 LF/CRLF 설정·clean 상태를 확인했다. Native Release 경고/
오류 0, 후보·API·독립 UI·기존 경로·오버라이드 보호 5흐름·13확인이 통과했다.
root solution 및 별도 MCP Release도 경고·오류 0이다.

새 Windows x64 교차 패키지의 manifest 2,343항목/marker 포함
2,344파일, 132,775,000바이트의 집합·전체 해시 및
현재 제품 소스·Native DLL과 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`3f6033bc95e512ad6fb15a302d5781ff637079bbc1b111d7d39bd1942cab4bb0`, Native DLL SHA-256은
`e989c13950f4f39698e9cac9ae5d29f8fd7cec0aa7cb57c522540e035c734075`이다.

SDK 없는 새 소유 runtime에서 무관한 cwd의 Linux managed 엔진 웹 기동,
74리소스·synthetic profile/명시 override 보존·변조/DLL 누락 거절과 패키지
backend 후보 4확인이 통과했다. 검사 6단계를 순차 수행했으며 OOM/oom_kill은 0이다.
실제 Windows apphost/WebView2·모바일 기기 실행 및 Library 전달과 구별한다.

새 증거 ZIP 32개의 파일 집합·권한·전체 바이트·해시를 재검증하고 전체 manifest와
fixture 증거를 보존한 뒤 이번 소유 임시 RAM 패키지만 종료 cleanup했다.
기존 자료 삭제·압축 변환이나 새 영구 배포 파일 보관·전달은 하지 않았다.
패키지 단계 최저 디스크 여유는 1,960,943,616바이트다. 후속 결과 문서 커밋은
실행 소스를 바꾸지 않는다.
[checkout·패키지 근거](evidence/v536-information-shared-ref-names/package-clean-verification.json)에 단계·소스·해시·검증 한계를 기록했다.
