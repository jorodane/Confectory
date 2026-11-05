# v666 기존 동작 표시명·본문 함께 저장 복구 검증

제품·검사·도구·delta 동결은 `302d8ae2c833a569d5ba6b0ce3e9a63005adf06d`이며 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V2_TEXT_PAIR_RECOVERY.md)와 [정확한 delta](v666-text-pair-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `47a343450dc448126c0598ec9c12315afcad23ec`의 기존 일반 next 동작에서 원래 제목
inspector와 C# 편집기를 사용해 표시명·본문 두 입력을 만들었다. checkpoint 쓰기를 실패시키면
`consumer_error`와 함께 개인 입력 둘이 모두 사라지고 두 값은 live에만 남았다. checkpoint와
물리 원본은 같았으며 cold 재시작하면 이전 값으로 돌아왔다. 각각의 단독 저장 완료를 다시
미완료로 분류한 것이 아니라 실제 혼합 Save의 유실이다.

원래 native 후보는 ordinary root의 이 두 edit를 함께 허용하지 않았다. 같은 직접 소유 root·
같은 기존 code/next 노드의 정확한 rename/source 두 문자열만 후보로 허용하고, 기존 source
소유/역할 검증과 원자 checkpoint·ownedSource receipt·공유 이력·최종 CAS를 재사용했다.
추가 계약·다른 노드·분기/실행선·owner/slot/private/copy 권한을 채택하지 않는다.
기존 이름 단독 API의 이전 혼합 거절은 이 닫힌 지원 범위에 맞춰 참조 call의 source 혼합 거절로
갱신했고, 새 API에서 서로 다른 노드/세 번째 편집/계약/실행선 거절을 확인했다.

실패 후 같은 두 key/노드/원래 관측을 유지한 이름·본문 수정만 native 미적용/원본 동일 관측
뒤 새 시도로 저장한다. 추가 입력이 섞이면 기존 시도와 모든 입력을 보존하며 live 변경으로
fallback하지 않는다. 정착된 정확한 receipt를 먼저 회수한 뒤 그 원래 출처의 늦은 이름·본문만
별도 후보로 저장한다. process-local revision 차이는 전체 소스 ID/해시와 입력 origin이 같은
이 경계에서만 허용한다. 다른 바이트/누락 origin/비소유 문맥을 새 관측으로 승격하지 않는다.

새 receipt 형식·소유 ID·공개 또는 override 입출력 계약·C# 자동 재작성·부모/외부 편집·
권한 정책 변경은 없다. 원래 UI/문구/레이아웃과 source writer·Restore/Export·이력 planner·CAS는
그대로다. 반영은 명시한 graph 표시명과 기존 node 본문뿐이며, 편집한 본문은 입력 bytes로
보존하고 나머지 C#·함수/구현/caller·핀/타입/순서·값/연결·원본을 보존한다.

## 최종 검증

독립 LF 18·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리 8,
**총 43단계: 신규 20·재사용 23** 통과했다.
개발 검사는 이 수에 합산하지 않는다. Git 객체·NuGet/home·엔진 캐시와 실제 LF/CRLF checkout을 분리했다.

- 정확한 UI/native 후보 허용·실패 복구 delta와 canonical 자산 SHA/크기만 대조했다.
  실제 JS guard·receipt/proof helper·JS 문법과 공유 이력/컴파일 probe 회귀를 확인했다.
- API에서 stale checkpoint·변조 closure·서로 다른 노드·미관측 owner/private·추가 계약/
  실행선/설명·빈 이름·제어문자·길이 초과를 거절했다. 쓰기 실패 시 live/checkpoint/원본을
  보존하고, 원래 checkpoint/전체 closure/물리 원본이 같을 때만 baselineUnchanged를 인정했다.
  원자 적용·동일 요청 멱등성·cold receipt와 receipt 그래프 해시 변조 거절도 확인했다.
- 원래 compact 이름 inspector 입력과 C# 편집기의 고정 선언·취소·Undo/Redo, 두 private 입력의
  cold 복원, 쓰기 실패 후 두 값을 수정한 명시적 재시도, 동료 checkpoint 충돌을 확인했다.
  root 값이 더해지면 세 입력/시도를 cold 뒤에도 보존하고 순차 live 변경으로 돌아가지 않았다.
- 응답 유실은 receipt만 회수하고 이미 적용한 두 값을 재실행하지 않았다. 응답 보류 중
  이름·본문을 모두 바꿔도 두 늦은 입력을 별도 저장했다. 두 값의 공유 Undo/Redo/cold는
  한 이력으로 움직이며 같은 ID/계약/연결과 물리 원본을 유지했다. 생성의 기존
  OWNERSHIP_CHANGED 경계는 별도이며 새 생성 전체 공유 역연산을 추가하지 않는다.
- Review 취소·Review 후 물리 graph 변경의 최종 CAS 거절·새 Review/Confirm·실제 .NET 실행·
  최종 cold를 확인했다. 결과는 명시한 본문에 따라 `body`와 11 또는 12를 출력하고 같은 값을
  반환한다. 같은 두 값을 다시 Save한 zero-dirty receipt와 반복 빈 Save/cold도 확인했다.
- 잘못된 C# 본문과 표시명은 draft에 함께 보존되며 Confirm의 CS0103 진단/심벌은 원문대로
  전달됐다. checkpoint/원본을 보존하고 명시적 본문·이름 수정 뒤에만 다시 Confirm했다.
- 기존 이름 단독·본문 단독 API와 새 일반 동작 생성 API/늦은 입력 UI는 최초 최종 동결
  651bf51에서 새로 회귀했다. 아래 검사 문자열 수정 후에는 같은 제품·선택 코드 경로의
  봉인 근거를 재사용했다. 다른 root/전체 기능의 이전 근거는 해당 기록에 유지하며
  이번 신규 수로 재합산하지 않았다.
- 새 Windows 교차 패키지 구조·무결성 및 패키지 엔진의 정상/유실 UI를 확인했다. 압축 CRC·
  전체 파일 SHA·권한 모드로 완전히 복원한 엔진에서 실패 후 두 값 수정/재시도와 늦은 두 값의
  Confirm/실행/cold를 확인했다. 실패/예외/반복 수명관리·증거 보존·자식 종료·소유 임시물
  정리도 통과했다. 실제 Windows apphost/WebView2 또는 모바일 실행 검증은 아니다.

## 개발 증거와 검사 경계

첫 baseline 명령은 입력한 LF 문자열과 에디터가 유지한 CRLF 문자열을 그대로 비교하는
검사 끝단에서 exit 1이었다. 이미 저장된 before 두 입력→after 빈 입력, live의 새 두 값,
동일 checkpoint/원본과 cold의 이전 두 값 관측을 읽기 전용으로 다시 대조해 유실을 확인했다.
이 줄바꿈 비교 실패를 제품 실패의 추가 사례나 최종 통과로 합산하지 않는다. 원래 C#과
편집기 CRLF 의미를 바꾸지 않았고 새 fixture는 그 실제 문자열을 기준으로 검사한다.

최초 최종 동결 `651bf516468a32c191877528bc5130a278bc1c49`은 34단계 통과 뒤 compiler
UI에서 새 prefix를 CRLF라고 예상해 실패했다. 실제 private 입력에는 새로 입력한 첫 LF와
기존 본문의 CRLF가 함께 보존돼 있었다. Save 전에 두 입력이 모두 남아 있는 관측을 보존했다.
검사 prefix 예상만 LF로 고쳤으며 제품·입력 보존·CS0103 진단·Confirm 거절 조건은 바꾸지 않았다.

최초 최종 record `/workspace/artifacts/v536-verification-managed/runs/fe8a50dc15524814a5fd0931f8dcc565.json`,
증거 SHA `18663bd307ec71161500645d50c1748aa9822c6e118cf2d1384a9782bef2665c`를 보존한다.
동일 제품/선택 검사·SDK/의존성/설정·양쪽 EOL·정규화된 호출을 대조하고 통과한 검사 22개만
재사용했다. 정확한 compiler-mode 한 문자열 변경과 다른 mode의 해당 분기 미실행도 확인했다.
실패한 검사는 재사용하지 않았다. 수정한 compiler UI는 같은 최종 동결 코드에서 통과했다.
그 뒤 출력 대기 도구가 중단되며 driver stdout 파이프가 닫혀 Broken pipe로 종료됐으나,
Windows 패키지 생성/구조 probe까지 총 37단계의 완료 근거와 오류를 봉인했다.
이 중 compiler 통과 1개도 같은 최종 소스/호출/의존성으로 대조해 총 23검사를 재사용했다.
원본 또는 패키지 제품 실패로 분류하지 않으며 최종 driver 출력은 지속 로그 파일로 보존했다.

출력 중단 record `/workspace/artifacts/v536-verification-managed/runs/2564fa7f72de43fa87b7de03974e6b55.json`,
증거 SHA `88cdd4a2d0d35d56837792942456fea392bcb553afb2631aa70986fa23e1be9f`를 보존한다.
생성한 runtime 패키지/임시 빌드는 오류 수명대로 정리됐고 raw runtime은 그 증거의 보관
대상이 아니므로 양쪽 독립 빌드 준비 12단계와 새 패키지 생성/검사·전체 복원·실패 수명관리
8단계를 다시 수행했다. 완료된 UI/API 검사는 반복하지 않았다. 재사용 증명과 driver 자체를
최종 증거에 보관했다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/83e8097157a7473d96cea60fcd0dd680.json`

개발 증거 SHA `ea2580458dccea9cf8553300d2479a1b678c819c8d4414e3c6d72fb3a668c76b`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/d7136a9174c542fda7b0d05abc2dfc4f.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/d7136a9174c542fda7b0d05abc2dfc4f.zip`

SHA `469479d6718cb14b5afcff0a88089a0cfc93192ec29ddf1973a353dfac94484e` (1.45MiB).

## 보관·공간·남은 범위

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `302d8ae2c833a569d5ba6b0ce3e9a63005adf06d`, `dee03d74bc5eb80817ef66dcb0d2f711c3554a7c8818e9b3bbd99e037a2a8989.zip`, 49.14MiB, 파일 2381·디렉터리 147, 전체 manifest `91b191ea36d3cf0fcbdcaf431c164669aabb23d4704aee3408e694788ff3d52f`.

- rollback: 출처 `d2204f103d22170fedb48d3efafd2a9258425f8c`, `9736227508ad82f34d2a9ff9c074a5f01218713386a909c710fc8c01f69343a9.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `712377aaba66a04e6f87adfccfbdab0c3e4d18861f2d5687651d8d094df5345a`.

최신은 동결 코드와 같으며 이전 정상 최신본을 롤백으로 보관했다. 전체 manifest와 복원
가능성을 검증하고 이번 실행의 소유 임시물만 승인 수명대로 정리했다. 다른 과거 자료·
원본·로그·프로필·캐시의 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1557.21MiB, 최대 cgroup 메모리
4740.62MiB다. 최종 실행 순증가 2.22MiB, 개발 시작부터 보관
확인까지 6.64MiB, 문서 마감 전 여유 1555.02MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

같은 기존 일반 동작의 표시명·본문 두 입력 흐름을 마감했다. 다른 root 정의·혼합 계약·
직접 배치 형태는 원래 요구/현재 구현을 대조할 별도 점검 후보이며 조합마다 필수 항목을
늘리지 않는다. 완료 M11/M12/M4와 고정 V2 후속·V3–V9·팩/backend·종류 호환성 결정,
실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달의
미완료 경계를 유지한다. live AI·실제 AI 계정/키·유료 AI 호출·새 외부 접근/권한은 사용하지 않았다.
