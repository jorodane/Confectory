# 고정 8행: 전체 C# ref→out과 공유 호출자

기준은 `6a713365cac4a7fc40ef474c14c8b828cc3e8b4e`의 원래 v536 정보/C#/
호출 대응 화면과 I5-6 고정 8행이다. 이번 단위는 기존 단일 closure가 이미
지원하는 직접 소유 whole-body lift의 ref→out 전환을 여러 함수/공유 caller의
한 후보에 연결한다. 입력 이름·위치·타입·핀 수·반환은 유지한다. 순서와 반대
방향, 다른 계약 조합을 새 필수 범위로 늘리지 않는다.

## 원래 조작과 완료 경계

기존 정보 창에서 두 함수의 C# 본문 편집을 열고 밝은 매개변수 영역의
`ref long nativeTotal`을 `out long nativeTotal`로 명시한다. 기존 호출 계약
갱신에서 제거되는 count 입력의 원래 바인딩을 각각 명시 해제하고, 남는 amount
입력과 return 출력 대응을 유지한다. 원래 코드와 return writer/실행 경로,
호출자의 원래 ref 입력 second 선언은 보존한다. count out은 자동 공개하지 않는다.

fixture의 원래 코드는 nativeTotal을 먼저 대입하므로 양쪽 역할에 모두 유효하다.
원문을 자동 수정하지 않으며, out을 대입 전에 읽는 잘못된 C# 원문은 컴파일
검증에서 거절한다. nativeAmount/nativeTotal과 공개 amount/count를 구별한다.
별도 저장된 변환 전 C# 원문 파일도 보존한다.

기본/독립 460px에서 C# 취소/재열기·Undo/Redo·미저장/저장 재시작, 명시 입력
해제·저장/실패·응답 유실·실제 경합/취소·프로젝트 전환·Review 취소/Confirm을
격리 fixture로 확인한다. 정확한 9223372036854775806·기존 설명·다른 입력과
부모/외부 원본을 보존한다.

## 구현과 보호

`InformationFunctionBatch`는 원래/새 선언의 같은 위치·타입·이름·수·반환과
각 핀의 동일 역할 또는 ref→out만 허용한다. 원래 핀 대응을 보존하고 모든 본문
계획과 caller 계획이 있어야 한다. 남는 입력은 기존 바인딩을 유지하며,
해제 목록은 바뀐 ref 핀과 정확히 일치해야 한다. caller 출력은 원래 identity
대응만 받는다. 원래 graph/source/hash와 해제 값은 기존 단일 검증기가 재검사한다.

선택된 callee의 implementationContext는 이 ref→out 단위에 한해 기존
`InformationFunctionRetained.IsLift`의 정확한 code/return 형태와 해당 body
계획이 있을 때만 허용한다. body/native/public 선언·whole receipt·경로·컴파일은
기존 `InformationFunctionWholeBody.Contract`가 검증한다. 추가 노드/지역값·별칭,
copy/private/wrapper·native C# target guard는 유지한다. 사용자 whitelist를
신뢰하거나 일반 root 계약 검사를 완화하지 않는다.

모든 원래 선택을 먼저 검증하고 caller의 명시 출력 대응을 원래 그래프 복제본에
투영하여 내부 overlay를 합친다. 원래 해시·단일 후보/CAS 및 Review/Confirm을
유지한다. `MappingFor`·`ProjectOutputs`·`Merge` 본문과 권한/UI/레이아웃은 같다.
부모나 외부 계약, 함수 ID와 원래 C# 원문을 자동 재작성하지 않는다.

## 검증 기록

변경 전 두 단일 후보가 유효하고 기존 그룹만 거절하는 재현을 통과했다.
영향 래퍼는 최초 runenv 초기화 오류로 제품 검사 시작 전에 종료했다. 이를
수정하며 이전 단위의 ref 이름 UI 1건이 늦은 환경 재설정으로 역할 UI였음을
ZIP의 확정 선언에서 확인했다. 당시 native 이름 검사는 정상이며 원본 증거를
보존했다. 현재 플래그를 먼저 초기화하고 각 실제 실행의 선택 값을 기록해
해당 이름 UI를 정확히 재검증한다. 이전 문서도 범위를 정정한다.
집중 10흐름·25확인, 영향 8흐름·23확인이 통과했다. 정방향/역순 후보와 모든
원래 hash, 전체 caller graph/header/import·native/public out·원문·정확한 값과
기존 경로를 대조했다. 잘못된 타입/역할/순서/수/반환·pin 대응·입력/해제·출력·
본문/receipt/컴파일·copy/다른 문맥 및 실제 source 경합은 전체 미적용이었다.

실제 기본/독립 화면은 C# 취소/재열기·코드/호출 확인 Undo/Redo·미저장/저장 cold·
Review 취소/Confirm을 통과했다. checkpoint 실패/재시도, 저장/조회 응답 유실 뒤
cold receipt 조회와 중복 방지, 취소·peer 경합·프로젝트 분리/오래된 창 제출 차단,
마지막 함수의 불완전 대응 거절과 Undo 재시도도 통과했다.

기존 값/ref·ref 이름·입출력 정의·출력 없는 경로·오버라이드 및 단일 out→ref,
이전 값/ref API를 회귀했다. 올바른 REF_NAMES 플래그의 실제 이름 UI도 통과했고
확정 선언에서 ref 역할 유지를 재확인했다. 이 결과로 이전 UI 범위 정정을 닫았다.
새 증거 ZIP19개의 파일 집합·권한·전체 바이트/SHA-256을 재검증했다.
[집중·영향 근거](evidence/v536-information-shared-ref-out/focused-verification.json)에
래퍼 초기 오류·이전 범위 정정과 실제 플래그를 구분하며 미해결 실패는 없다.
독립 checkout·새 교차 패키지는 이후 별도 기록한다.

## 정확한 잔여

이번 단위와 8행 전체 완료는 별개다. out→ref·값/out 전환, 공개 핀 순서,
기존 바인딩/출력의 다른 명시 재선택과 이 단위 밖 계약 결합은 남아 있다.
일반 retained-storage 그래프·선택 callee 간 의존·C#/native mixed·중첩/private·
whole/postCall·같은 원계약 copy/상속/등록·소유 정보 속성·scalar 밖 타입의
그룹 문맥도 기존 guard/수용 경계로 유지한다.

7행의 같은 계약 copy 편집/배정 잔여와 9행 고급 함수 타입·표시명/native 식별자
분리, I6/B2·A4~A6·M4/M11/M12는 별도다. 오버라이드 원계약 구조 변경 거절은
정상 보호이며 독립 계약 복제는 필수 범위가 아니다. Helper 실제 작업은 UI
다음 단계이고 이미지/협의/렌더 신규 backend는 범위 밖이다. 실제 Windows/
WebView2·모바일 기기 실행과 Library 전달은 managed/브라우저/교차 빌드와 구별한다.

## 독립 checkout·새 교차 패키지 완료

실행 소스는 `90d727a25ba01c2a7c6b84ec861f4c40cbb8c757`다. 기존 독립 checkout을 정상 fast-forward하고
10개 Git blob·기존 LF/CRLF 설정·clean 상태를 확인했다. Native Release 경고/
오류 0, 후보·API·독립 UI·기존 경로·오버라이드 보호 5흐름·13확인이 통과했다.
root solution 및 별도 MCP Release도 경고·오류 0이다.

새 Windows x64 교차 패키지의 manifest 2,343항목/marker 포함
2,344파일, 132,781,224바이트의 집합·전체 해시 및
현재 제품 소스·Native DLL과 7개 Core DLL 일치를 확인했다. manifest SHA-256은
`8daee4d8dee5f029146d25848224b3392b35aa6f2eebacac8b9cbdd7a80f5681`, Native DLL SHA-256은
`a3989b36e4f1e45136f82c44eacb14bfbf069b1e7108fa2c121dd2af0788ae68`이다.

SDK 없는 새 소유 runtime에서 무관한 cwd의 Linux managed 엔진 웹 기동,
74리소스·synthetic profile/명시 override 보존·변조/DLL 누락 거절과 패키지
backend 후보 4확인이 통과했다. 검사 6단계를 순차 수행했으며 OOM/oom_kill은 0이다.
실제 Windows apphost/WebView2·모바일 기기 실행 및 Library 전달과 구별한다.

새 증거 ZIP 26개의 파일 집합·권한·전체 바이트·해시를 재검증하고 전체 manifest와
fixture 증거를 보존한 뒤 이번 소유 임시 RAM 패키지만 종료 cleanup했다.
기존 자료 삭제·압축 변환이나 새 영구 배포 파일 보관·전달은 하지 않았다.
패키지 단계 최저 디스크 여유는 1,886,334,976바이트다. 후속 결과 문서 커밋은
실행 소스를 바꾸지 않는다.
[checkout·패키지 근거](evidence/v536-information-shared-ref-out/package-clean-verification.json)에 단계·소스·해시·검증 한계를 기록했다.
