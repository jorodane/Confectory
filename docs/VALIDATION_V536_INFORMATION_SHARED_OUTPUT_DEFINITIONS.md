# v536 공유 호출자의 출력 정의와 void 반환 — 2026-10-25

기존 정보 창의 함수 상세창에서 직접 소유한 여러 함수의 출력 정의를 편집하고
한 번 임시 저장하는 경로를 연결했다. 원본 v536 UI/CSS·창 크기·권한은 변경하지
않았다. 7행의 독립 copy 계약/ID/새 기능 정책은 사용하지 않는다.

## 지원 경계

- 직접 소유 함수 2~8개, 직접 Blueprint leaf의 code/export와 선택한 함수만
  호출하는 call/export caller를 대상으로 한다. 기존 linked source 64개 한도를 유지한다.
- 값 입력과 유지되는 핀의 이름·타입·상대 순서는 고정한다. 기존 scalar out
  추가, 모든 writer를 확인하는 삭제, 삭제/추가 혼합, 반환의 양방향 void 전환을
  기존 `outputGraphs` 계획과 caller outputs의 명시 대응으로 결합한다.
- 새 출력의 값·타입·고유 graph node·삽입 위치·다음 경로를 사용자가 선택한다.
  이미 소비되는 출력을 없애려면 같은 타입의 현재 출력에 명시적으로 대응해야 한다.
  모든 원래 writer/exit와 graph hash를 확인하고, 유지되는 실행 경로를 보존한다.
- 공개 metadata는 기존 공개 출력 중 유지되는 것만 남긴다. 새 출력을 자동으로
  SourceContext 공개 출력으로 만들지 않는다. 공개는 외부 공유 권한이 아니다.
- 내부 C# code 노드의 원래 서명과 사용자가 쓴 본문은 그대로 둔다. 새 graph node는
  기존 내보내기 배치의 노드이며 새 함수/계약/copy ID가 아니다.

각 closure의 선택을 **원래 source에서 먼저 독립 검증**한다. 그 후 기존 내부
overlay에만 합치며, 앞서 확인한 생산자의 출력 대응만 원래 caller graph 복제본에
투영하여 현재 후보와 대조한다. 다른 선택 call의 서명·인자 외에 변화가 있으면
거절한다. 원래 source hash·checkpoint CAS·receipt·Review/Confirm을 유지하고,
중간 후보를 저장하지 않는다. 마지막 함수가 틀리거나 실제 source가 바뀌면 전체 미적용이다.

## 검증 fixture

두 함수 A/B와 공통 Caller를 격리 프로젝트에 만든다. 원래 A 출력은 B 입력에,
B 출력은 Caller 반환에 연결된다. 출력 삭제 fixture는 count writer를 각 graph에
두 개 두어 정의 삭제가 모든 배치를 확인하는지 검사한다.

| 종류 | 선택한 편집 | 소비 대응 |
| --- | --- | --- |
| add | 기존 count 유지, fresh 추가 | 기존 연결 유지 |
| delete | count와 두 writer 삭제 | count → 기존 return |
| mixed | count 삭제, fresh 추가 | count → fresh |
| void | long 반환 삭제 | return → 기존 count |
| fromvoid | void → string 반환 및 명시 writer | 기존 count 연결 유지 |

mixed의 새 값은 A=23, B=`9223372036854775806`이다. fromvoid는 한글과 emoji
문자열을 사용한다. 기존 code/out 매개변수·C# 본문·설명 문자열·선택하지 않은
함수·부모·외부 팩과 Power 기본값의 정확한 64비트 수치를 보존한다.

`tests/web/v536_information_shared_output_definitions_{native,api,ui}.py`가
공통 fixture를 사용한다. 기존 방식대로 REPO, 격리 ENGINE_REPORT,
`mixed-normal` 같은 종류/모드와 선택적인 `view`를 인자로 받는다.

## 집중 검사

19개 실행 흐름에서 48개 체크가 통과했다. 준비·보존 체크를 반복 포함하는 수이며
48개의 새 기능이라는 뜻이 아니다.

- 순수 후보 5종(15체크): 원래 요청 불변, ID당 하나의 원래 hash, 역순 편집의 같은
  결과, source/writer/exit/삽입 위치/값/타입/역할/공개/누락된 소비 대응 거절.
- 실제 API 4회(11체크): mixed 및 양방향 void의 저장·cold·컴파일러 Review/Confirm,
  마지막 함수 오류의 전체 미적용과 caller 물리 파일 경합 차단.
- 실제 화면 10회(22체크): 기본/독립 창, 원본 460px 창, 명시 대응, 취소,
  Undo/Redo, 미저장 cold, checkpoint 실패/재시도, 응답·결과조회 유실 후 receipt 조회,
  peer 수정, 같은 namespace 프로젝트 전환과 오래된 form 차단, 잘못된 마지막
  입력 타입 편집 거절 → Undo → 명시 재시도, Review 취소/Confirm.
- 기존 공유 입력 이름/타입, out 이름/scalar 타입의 영향 회귀 15체크도 통과했다.

첫 conflict 화면 검사는 경고 MutationObserver 대기에서 시간 초과했다.
당시 보존 checkpoint에는 변경이 없었고, 같은 제품 코드 재실행은 통과했다.
최초 시간 초과의 정확한 원인은 확정하지 않았다. 새 검사는 이미 표시된 경고와
이후 변화를 함께 읽으며, 성공한 applySlots 응답이 없고 checkpoint/peer 설명/사용자
입력이 보존되는지 추가로 확인한다. 제품 검사나 CAS는 완화하지 않았다.
보강 후 conflict 검사는 통과했다. 해당 실패 로그·fixture도 보존했다.

run-2는 검사 전 고정 RAM 디렉터리가 이미 있어 종료했다. 기존 RAM 자료를
삭제하지 않고 새 mkdtemp 경로를 사용했다. 그 실행에서 기능 검사는 시작되지 않았다.

Native Release 빌드는 warning/error 0이었다. 집중 실행의 200ms 샘플 기준 최소
workspace 여유는 442,519,552 B, 최대 cgroup 메모리는 17,033,412,608 B였다.
OOM/oom_kill은 0이다. 순간 전체 peak를 보장하는 수치는 아니다. 검사들은 순차
실행했고, 기존 workspace/cache/보관 빌드는 삭제하지 않았다. 새 RAM fixture의
원문·draft/profile·로그·이미지는 재생성 가능한 compiler cache/output을 제외하고
workspace evidence에 보존했다.

원본 화면 구조는 변경하지 않았다. 실제 상세창/대응창/최종 화면을 확인하고,
기존 460px 창과 실제 데이터 표시·삭제된 핀 제거·새 핀 표시를 검사한다.
원문 없는 데모나 대체 일반 폼을 새로 만들지 않았다.

## 잔여

이번 지원 단위와 8행 전체 완료는 다르다. 비void 반환 타입 변경, 입력/출력
동시 타입·값 입력 수/ref/역할/순서, 유지 출력 타입과 정의 변경의 혼합,
C#/mixed target·nested/private/whole/postCall, copy/상속/등록/owner 속성 혼합,
현재 scalar 경계 밖 타입은 별도 잔여다. 정의 편집과 다른 속성 편집 결합도
이번 경계에 추가하지 않는다. 새로운 조합을 추측해 연결하지 않는다.

7행 독립 복제 정책은 사용자 답변 대기다. 9행 named 정보/참조/외부 함수 타입과
표시명/native 식별자 분리도 남았다. I6/B2 및 A4~A6/M4/M11/M12와 Helper의 실제
편집 도구는 별도 후속이다. 실제 Windows/WebView2·모바일 기기 실행 및 Library
전달 완료를 뜻하지 않는다. 사용자 프로젝트·실제 로그인·유료 추론은 사용하지 않았다.

로컬 전체 근거는 `/workspace/scratch/v536-shared-output-definitions/`에 보존한다.
