# v536 I5-6: 수식·별칭·exit의 명시적 입력 대응

기존 9행 중 1행의 수식·별칭·exit 하위 단위를 연결한다. 일반 code/call/Set/export의 값 인자, root 별칭의 입력 저장소, exit의 반환/출력 값이 삭제·타입 변경되는 root 입력을 읽을 때 기존 `입력 연결 갱신` 창에서 대체를 직접 고른다. caller 대응과 모든 영향 본문은 기존 한 검증 후보/CAS로 저장하고 최종 반영은 별도 Review/컴파일/Confirm을 거친다. C# 본문을 문자열 치환하지 않는다. 출력 값 바인딩은 포함하지만 출력 타입·추가삭제·반환 **계약** 편집은 3행의 별도 잔여다.

## 의미와 서버 경계

`InformationFunctionInputUses`는 알려진 semantic 위치만 나열한다. 수식의 root 참조는 binary AST의 operands와 직접 input에서만 읽고 constant/문자열/노드·local 참조 안을 임의 검색하지 않는다. 기존 root 입력 이름이 둘 이상 들어간 수식도 전체 기존 JSON과 원래 graph hash/node/argument를 증거로 묶는다. 사용자는 수식 **전체 값**을 대체한다. 일부 피연산자나 C# 문자열을 자동으로 삭제·재작성하지 않는다.

별칭은 local ID·표시명·타입·소비 연결을 유지하고 사용자가 선택한 동일 타입의 현재 root 저장소로만 옮긴다. 직접 값/literal을 저장소로 허용하지 않으며 기존 다른 별칭과 몰래 병합하지 않는다. 일반 local의 constant 초기값은 바꾸지 않는다. Set은 쓰기 대상과 별도 outputLocal 스냅샷을 기존 엔진 의미 그대로 유지한다. node output을 가리키는 별칭은 이 조작에서 재지정하지 않는다.

exit와 export는 원래 위치·출력 타입·경로를 보존한다. 선택한 바인딩을 순수 후보 안에서 분리하고 원래 root 계약을 준비한 직후 새 바인딩을 복원하여 전체 graph/record/source를 검증한다. alias나 exit가 임시로 비워진 중간 상태는 저장·반환하지 않는다. 누락·변조·타입 불일치·다른 위치·실제 동시 변경이면 기존 입력/checkpoint/source를 보존한 채 전체 거절한다. 저장 직전 기존 source 관찰/CAS와 receipt 확인을 사용한다.

지원 call은 기존 동일 프로젝트 소유 callee·typed import·서명이 일치하는 ordinary next/value 범위다. property 수신자, 특수 call, nested/private 경로, 전체 C# 문맥·ref/out 역할, 등록/외부 계약 및 다른 별칭 저장소 역할을 이번 일반 값 대체로 추측하지 않는다. 이 제한을 안전한 거절만으로 완료라고 표시하지 않는다. [고정 9행 목록](V536_I5_6_REMAINING.md)의 다른 행을 추가하거나 새 언어 의미를 만들지 않는다.

## 화면 연결

원본 함수 상세창과 기존 ABI 선택창을 재사용한다. 새 패널이나 CSS 배치는 만들지 않는다. 선택창의 기존 값 영역에 원래 수식 전체 또는 별칭 저장소를 읽을 수 있게 표시하며 typed JSON parser로 64비트 숫자 원문을 보존한다. 별칭에는 같은 타입의 입력 저장소 후보만 표시하고 직접 값 옵션을 제공하지 않는다. 저장된 선택을 변조해 literal을 제출해도 UI와 서버가 각각 거절한다. 선택/취소·미저장 값은 기존 입력 이력·창/프로젝트 문맥과 source별 form 보관을 따른다.

## 검증

격리 fixture의 실제 소유 함수는 code 수식, 별도 소유 callee를 부르는 call 수식, export 수식, root alias, exit 수식의 다섯 위치에서 같은 입력을 읽는다. 독립 local의 정확 64비트 초기값과 별도 callee의 세 원본 파일을 보존한다. 선택 누락, 부분 수식 증거, alias literal/없는 저장소, 잘못된 hash·타입·다른 소유 요청은 전체 거절하는지 검사한다. pure 후보에서는 alias를 사용하는 Set의 쓰기 대상과 별도 결과 스냅샷도 생성된 source와 graph로 확인한다.

원래 작업 트리의 API 11 check(삭제 3·타입 변경 3·다중 target 3·실제 caller 파일 충돌 2)와 실제 UI 14 check(독립 혼합 편집 2·타입 변경 쓰기 실패/재시도 3·저장/조회 응답 유실 2·변경 취소 2·동시 편집 거절 2·거절 후 같은 세션 Undo/새 선택 재시도 3)가 통과했다. pure 후보 3 check는 별칭의 실제 저장소·정확한 독립 초기값·중복 저장소 거절·Set의 별도 outputLocal을 확인했다. 새 값 표시 어댑터 2 check와 기존 Native 계약 7·call 보호 2·call 혼합 API 3·ABI 어댑터 3·원래 별칭 계약 5 check도 통과했다. Native/Linux 빌드는 경고/오류/stderr 0이다. 같은 namespace/요소 ID를 가진 다른 프로젝트 전환과 오래된 form 거절의 기존 UI 회귀 2 check도 통과했다. 따라서 영향 회귀는 22 check이며 새 후보 3·값 표시 2와 별도 집계다. 근거 디렉터리는 `/workspace/scratch/v536-information-value-uses`다. 테스트 fixture의 초기 export 존재 가정과 Describe에 body를 기대한 호출은 실제 계약에 맞춰 수정했으며 제품 보호를 완화하지 않았다. Set의 outputLocal은 기존 임시값을 두 저장소에 대입하는 구현이므로 직접 literal 대입 문자열을 기대한 테스트를 그 실제 스냅샷 계약에 맞췄다.

실제 Windows apphost/WebView2·모바일 기기·사용자 계정/유료 추론·사용자 프로젝트 Run·Library 전달은 이번 검증에 포함하지 않는다. I5-6 전체/v536 전체 완료를 의미하지 않는다.


[원래 전체 값/저장소의 명시 선택](evidence/v536-information-value-uses/picker.png)과 [저장/확정 후 정보 화면](evidence/v536-information-value-uses/saved.png)을 실제 렌더러에서 확인했다. baseline e112ca9 대비 CSS 세 파일은 byte 그대로이며 `layout-evidence.json`에 해시를 기록했다. 기존 모달의 스크롤 안에서 모든 선택과 취소/갱신 버튼이 동작한다. 전체 pixel 일치 또는 실제 Windows 조작 검증이라는 뜻은 아니다.


## 깨끗한 체크아웃·교차 패키지

검증 소스 커밋은 `846532dc6b75aa5f1b658f3304481202270b3804`다. 기존 별도 clean clone을 로컬 origin에서 정상 fetch/fast-forward했고 Native/Linux 빌드가 경고/오류/stderr 0으로 끝났다. 그 체크아웃의 새 runtime으로 다중 target API 3 check와 독립 창 삭제 UI 2 check를 재현했다. Save·Review 취소·컴파일 Confirm·cold와 다른 입력/원문 보존을 포함한다.

실제 CRLF 유지 pull/fresh LF checkout에서 74개 리소스의 canonical/exact 바이트를 확인했다. 내용/UTF-8/BOM/UTF-16/단독 CR/예산/PNG 변조를 거절하고 원본을 보존했다. WebBundle은 바뀐 두 JS의 canonical size/hash만 갱신한다.

Windows x64 교차 패키지는 `/workspace/artifacts/v536-information-value-uses/Windows-x64`다. manifest 2,331파일, SHA-256 `5262af54ee056c99794364a17dcbb646782951f2f066a4fe87301060f72aad02`이며 source/Native DLL/두 JS/WebBundle의 6파일이 검증 소스와 일치한다. 테스트/프로필/로그는 패키지에 없다. 실행 파일은 `Confectory.exe`, 선행 조건은 .NET Desktop Runtime 10.0 x64와 WebView2 Runtime이다. 실제 Windows 실행이나 파일 전달 완료를 의미하지 않는다. `desktop_package.py`는 다른 cwd와 SDK 없는 복사 runtime에서 실제 패키지 엔진의 웹 기동·74리소스·최소 로그인창 렌더를 확인했다. 리소스 변조와 WebView2 의존성 누락을 거절했고, fixture 설정 보존과 명시 override도 확인했다. 실제 Windows apphost/WebView2 실행이나 계정 로그인은 하지 않았다.

이번에 마감한 것은 고정 9행 중 **1행의 수식 전체·root alias/Set·export/exit 입력 대응 하위 단위**다. 9행 전체를 새로 닫았다는 뜻은 아니다. 1행의 property 수신자/특수 호출과 3행 출력 타입·추가삭제·반환 계약, C#/중첩/whole-body/ref·out/등록·복사/여러 함수/고급 타입의 기존 잔여는 고정 목록에 유지한다. 출력 값의 사용처 대응과 출력 계약 자체의 변경을 구분한다.

재현은 `v536_information_value_uses_api.py`에 repo·Linux build JSON·delete/type/multi/conflict를 전달한다. `v536_information_value_uses_ui.py`는 mixed/type-storage/delete-loss/delete-cancel/type-conflict/type-retry 및 독립 창의 마지막 `view`를 사용한다. `v536_information_value_uses_guards.py`는 순수 후보와 생성 source를 검사한다. 테스트 API나 우회 권한은 배포 제품에 추가하지 않는다. 전체 solution/full suite, 실제 Windows/모바일 실행·계정/추론·Library 전달은 수행하지 않았다.
