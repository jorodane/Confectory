# v536 공유 호출자의 비void 반환 타입 — 2026-10-25

같은 정보 창의 함수 둘 이상에서 비void 반환 타입을 편집하고 한 번 임시 저장하는
경로를 연결했다. 원본 함수 상세창·타입 선택기·호출 계약 갱신창을 재사용하며
UI/CSS·권한·C# 본문·함수/계약 ID를 변경하지 않는다.

## 이번 경계

- 직접 소유 함수 2~8개의 scalar 비void 반환 타입 변경만 하나의 그룹으로 받는다.
  인자 전체의 이름·타입·위치·수·mode를 고정한다. 입력/out 타입 변경, 정의 추가/삭제,
  void 전환, 수동 본문 편집과 섞은 그룹은 별도 검증 전 거절한다.
- 기존 typed 출력 계획으로 모든 원래 반환 writer/exit의 hash·before·새 값을
  확인한다. caller의 모든 원래 출력마다 같은 타입의 현재 출력 대응을 명시한다.
  소비 중인 값을 조용히 버리거나 캐스팅하지 않는다.
- 기존 독립 code/export leaf와 선택 함수만 호출하는 call/export caller 경계를
  유지한다. 원래 source에서 모든 선택을 먼저 검증한 후 내부 overlay에 합친다.
  앞서 검증한 생산자 출력 대응만 원래 graph 복제본에 투영하며, 선택된 호출과
  나머지 graph를 대조한다. 원래 source hash·단일 후보/CAS·receipt를 유지한다.
- 유지 out·코드 노드의 원래 서명·C# 원문·값·설명·제어 흐름·부모/외부 원본은
  그대로다. 공개 출력 이름도 그대로이며 반환 필드의 타입 snapshot만 갱신한다.
  공개는 외부 공유 권한이 아니다. 새 함수/복사본/계약 ID를 발급하지 않는다.

fixture는 원래 A.return → B.amount, B.return → Caller 반환의 long 연결을 사용한다.
두 반환을 double로 바꿀 때 writer는 기존 Root.real(double)을 명시 선택하고,
기존 long 소비는 각 함수의 유지 out count(long)로 명시 대응한다. 반환을 자동으로
long으로 변환한 것이 아니다. C#의 `return amount`와 count 계산은 원문 그대로다.
공개 count/return의 이름을 유지하면서 return의 타입만 double로 바뀌는지 확인한다.
bool/한글·emoji string 반환과 명시 literal도 순수 후보로 검사한다.

## 재현과 수용 검사

`tests/web/v536_information_shared_return_types_{native,api,ui}.py`에 REPO,
격리 ENGINE_REPORT, `normal`/`source`/`storage`/`loss`/`cancel`/`conflict`/
`projects`/`retry`, 선택적인 `view`를 전달한다. 실제 사용자 프로젝트나 계정을
사용하지 않는다. Source/profile/draft/로그/화면 근거는 로컬 scratch에 보존한다.

순수 후보는 요청 불변, 원래 hash 하나씩, 역순 편집의 같은 결과, 원문 보존,
정확한 caller 연결, 공개 타입 snapshot을 검사한다. 중간 hash 재사용, 원래
writer/binding 불일치, 잘못된 값/타입/역할, 소비 대응 누락, 인자/본문/구조와의
혼합 및 실제 caller source 변화는 전체 미적용이어야 한다.

실제 API/화면은 저장·미저장 cold·저장 후 cold·취소·Undo/Redo·checkpoint 실패와
재시도·물리/live 경합·응답/결과조회 유실 후 receipt 조회만 복구·동일 namespace
프로젝트 전환과 오래된 form 차단·잘못된 마지막 입력 거절 후 Undo 재시도·
Review 취소/Confirm을 확인한다. Confirm 후 실제 파일에서도 signature/writer/
caller/공개 metadata와 C# 원문을 다시 읽는다. 원본 460px 창과 반환 핀 `결과`의
타입 `실수`, 기존 정확한 Power 값 `9223372036854775806`을 확인한다.

Native Release 빌드와 집중 검사 결과, clean checkout 및 새 교차 패키지의
추가 결과는 아래 최종 검증 기록과 evidence JSON에 기록한다. 체크 수에는
반복 준비/보존 검사가 포함되며 새 기능 수를 뜻하지 않는다.

## 고정 잔여와 다음 복합 문맥

반환 타입 단위는 8행 전체 완료가 아니다. 반환/입력/out/구조의 동시 편집,
값 입력 수·ref/역할/순서, C#/mixed target·nested/private/whole/postCall,
copy/상속/등록/owner 속성 혼합 및 현재 scalar 밖 타입은 남아 있다.

기존 single closure와 `BlueprintCompilation`에는 구현의 imports/manifest 관측 및
변경하지 않는 호출 계약을 검증하는 기반이 있다. 다음 최소 복합 문맥은
선택 외 **고정 local import를 보존하는 기존 code/export callee**를 먼저 분리해
검증할 수 있다. Batch의 leaf/선택 외 imports guard는 아직 유지하며, 선택 함수 간
callee 교차 의존·등록/상속/copy와 공유 C# 최종 본문은 섞지 않는다. 이는 조사한
후속 경계이며 구현 완료가 아니다. 공유 C#은 하나의 사용자가 편집한 최종 본문을
모든 최종 계약과 함께 검증해야 하며 자동 재작성이나 무조건 hash 갱신은 하지 않는다.

7행의 독립 copy 새 계약/ID/기능 정책은 여전히 사용자 답변 대기다. 이 구현은
그 결정을 사용하지 않는다. 9행 named 정보/참조/외부 함수 타입과 표시명/native
식별자 분리, I6/B2 및 A4~A6/M4/M11/M12, Helper 실제 편집 도구도 별도 후속이다.
실제 Windows/WebView2·모바일 기기 실행과 Library 전달은 완료로 간주하지 않는다.

## 집중 결과

집중 11흐름 27체크(순수4 + API5 + UI18), 기존 다섯 공유 경로 영향 회귀
18체크가 통과했다. 모든 검사 순차 실행, Native Release warning/error 0.
200ms 샘플 workspace 최소 411271168 B,
cgroup memory 최대 16892190720 B였다.
OOM/oom_kill 0이며 샘플은 순간 전체 peak 보장이 아니다. 이전 자료는 삭제하지
않았고 새 RAM fixture의 source/profile/draft/로그/이미지를 보존했다.
실제 화면을 열어 원본 대응창과 최종 반환 핀을 확인했다. 이번 실행의 실패는 없었다.
근거: `docs/evidence/v536-information-shared-return-types/focused-verification.json`,
전체 로컬 `/workspace/scratch/v536-shared-return-types/`.
