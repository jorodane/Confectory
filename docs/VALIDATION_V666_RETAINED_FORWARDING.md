# 기존 forwarded/opaque 호출 원본 검증

제품 동결 `055b5850e4d0e114cf86360032bc540f806f5897`의 [지원 범위](V666_RETAINED_FORWARDING.md)를 **신규 39단계·재사용0·최종 실패0**으로 검증했다.
LF/CRLF 독립 no-hardlinks checkout·격리 HOME/NuGet·빈 엔진 cache의 Release/MCP·실제 엔진,
새 Windows 교차 패키지·구조/무결성·전체 ZIP 복원을 실행했다. 개발과 최종 수는 합산하지 않는다.

- 게시 f56f28fa의 원래 프로그램81은 정상이다. 같은 계약 native 본문 두 개만 선택해도
  공동 후보와 단일 후보가 각각 전달 문맥 제한·opaque 본문 계획 요구로 거절되는 것을
  재현했다. 사용자 원문을 덧셈에서 뺄셈으로 직접 편집한 뒤 실제 프로그램은41이다.
- 단일 후보와 정·역순 공동 후보를 검증했다. 원래 hash·단일 group·native 매개변수 선언과
  공개 계약·함수/본문/노드 ID·전달 프레임·지역값/exact64·실행선·opaque C# source/helpers·
  원래 별칭·import 위치 표기를 유지했다. caller graph/header/record는 새 쓰기 대상이 아니다.
- 바뀐 공개 타입/이름·잘못된 문맥/전달 바인딩·누락/위조 hash·수정된 opaque record를
  전체 거절했다. 기존 ordinary caller의 부적절한 문맥 삽입과 명시 이름/native import,
  private·ref dispatcher를 회귀했다. 새로운 계약·C# 원문을 자동 추측하거나 재작성하지 않는다.
  추가 읽기 전용 순서 대조2건은 stage 수와 별도다. private 경로는 명시 부모 계획을 요구하며,
  순서가 바뀐 opaque 문맥은 definition hash가 달라 읽기 보존 hash 검사를 통과할 수 없다.
- 실제 구현 선택창에서 해당 함수의 native target을 선택했다. 취소·Undo/Redo·미저장/저장
  cold·checkpoint 쓰기 실패/복구·owner 경합·apply/settlement 응답 유실을 검사했다.
  trusted Save 활성화와 실제 거절을 확인하며 발행된 요청을 임의 재시도하지 않는다.
- 기존 version3 readGuards의 누락·hash/path·관측 밖 경로·owner/version 변조를 거절했다.
  Save 전 opaque 헤더 변경, Save 후 cold Review 전 opaque graph 변경, Review 뒤 caller
  헤더·graph·C# record 및 opaque 함수·헤더·graph·C# record의7개 경로 변경은 모두 거절했다.
  peer·checkpoint·두 입력을 보존하고 원문 복원/cold 뒤 새 Review/Confirm은 실행41로 성공했다.
  편집하지 않은7개 원본의 bytes·inode·mode·mtime도 유지했다.
- 저장 성공 응답 지연 중 실제 owner 설명을 입력했다. 반복 Save는 비활성 상태였고 두 본문은
  한 번 저장됐다. 늦은 설명은 cold 후 복원됐으며 후속 명시 Save의 guard는 원래 해시와 같았다.
  Review 취소·새 Confirm·cold는 새 설명과 두 본문·실행41을 확인했다.
- 현재3D 전송 정체/부분 POST·reload8회·단절·child/root·프로젝트 왕복/cold와 패키지 실패
  수명을 확인했다. 초기 간헐 빈 #app의 과거 원인을 확정한 검사는 아니다.

개발은 총 23개 stage이며3개 실패와 후속 수정을 모두 보관했다.
첫 제품 수정 뒤 단일 후보는 opaque 문맥에서 거절됐다. 원래 위치 import 이름 arg0/arg1은
유효하지만 같은 ABI의 공개 이름으로 교체하면 GRAPH_IMPLEMENTATION_CONTEXT_STALE이 되는
순수 대조 증거를 남겼다. 읽기 전용 같은 계약 경로가 원래 import 표기를 유지하도록 고쳤다.
두 번째 실패는 원문 CRLF를 Path.read_text()로 정규화한 fixture 비교였다. raw byte decode로
고쳤다. 세 번째는 기존 구현 선택창을 건너뛴 fixture였다. 보관한 화면/로그에 함수 본문과
opaque caller 선택지가 있고 C# 편집창이 아직 없었다. 실제 함수 target을 명시 선택하도록
검사만 고쳤다. 이 두 검사 수정을 제품 원문 변경/권한 확대로 표현하지 않는다.

최종36단계 뒤 읽기 전용 명령 생성이 exec-server transport disconnected로 실패했다.
환경 상태 표시만으로 복구를 판단하지 않고, 같은 checkout의 실제 읽기 명령·깨끗한055b5850
HEAD와 기존 worker PID/시작 시각·검증 프로세스의 연속 실행을 확인했다. 검사를 재시작하거나
불확실한 수정 명령을 재실행하지 않았다. 전송 복구 증거도 최종 archive에 보관했다.

최종은 위 수정 뒤 코드에서 전부 새로 실행했으며 개발 통과/실패를 최종 단계에 재사용하거나
합산하지 않았다. [기존 구 Reference reader 증거](VALIDATION_V666_ARGUMENT_LABELS.md)는 SHA를
확인해 개발 evidence에 보관한 과거 증거 재사용이며, 이번 최종 단계와 별개다. 같은 게시 세대
reader/authoring/runtime을 사용하며 자동 migration/downgrade·구 profile 삭제는 없다.
기존64-member Review·240 read/write·2048 known source·Tree 예산, 부모/외부 소유권·override
계약·권한·authored layout·Review/Confirm·최종 CAS와 승인된 정리 범위를 유지했다.

| 보관 | runtime source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 055b5850e4d0e114cf86360032bc540f806f5897 | 13ac5274773bbf044232e95849cf66008e8903c9c14296e677e9fd17f0743eb3 | 54077077 |
| rollback | c83e9cae180787323d9d19184d67852b15a72028 | eda7c56ef9b92480821f84eb97a02b68b9c0731e6eede6154a9f89693d75e762 | 54076804 |

최종 record `/workspace/artifacts/v536-verification-managed/runs/5184777e5c0a486f82860abf785800af.json` · evidence SHA256 `5217e91f7440b4c47a28598f9630a381c2adf5031a5ea4c352d0d6fae404bcdd`.
개발 record `/workspace/artifacts/v536-verification-managed/runs/fd6903c560c04087b8f823a3e1335dec.json` · evidence SHA256 `4c3fd0f3805d43ea052325450defdf25bb681766bad6053b087d92c0c316ed2e`.
두 관리 package와 증거 SHA를 다시 확인했다. 기존 latest/직전 정상 rollback2세대 교대와 이번
소유 RAM 임시물 정리만 적용했다. 원래 checkout/main·비관리 자료와 과거 증거는 보존하며
퇴역한 세 번째 관리 ZIP 전체를 계속 보관한다고 주장하지 않는다. 여유 25244082176bytes(23.51GiB)다.

같은 계약의 원본 보존과 실제 계약 변경의 source closure를 구별한다. 공개 이름/타입/역할·출력
변경에 맞춘 forwarded/opaque 원문의 명시 대응, 선택된 native callee 간 의존성 합성·새 import/
alias 편집·등록 외부 관측 결합 등은 원래 고정7/8행 잔여다. 부모/외부 원문 직접 편집 거절은
정상 보호이며 migration이나 선택 조합을 새 필수로 늘리지 않는다. 닫힌 M11/M12/M4를 다시
열지 않는다. 실제 Windows/WebView2·물리 기기·IME·GPU/audio·전체 UI 전수 검증은 Linux
native/Chromium 자동화·교차 패키징과 별도다. 새 credential/grant·라이브 AI/과금·main 변경은 없다.
