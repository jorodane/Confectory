# v666 기존 내보내기 값 저장 복구 검증

최종 제품·검사·도구·delta 동결은 `a8b0dd511dc2a1030cad73d78020b8215a70d28a`다. 이후 마감 commit은 이 검증 문서와
수용 표만 바꾼다. [지원 범위](V2_EXPORT_VALUE_RECOVERY.md), [정확한 delta](v666-export-value-recovery-delta.json)를 따른다.

## 재현과 수정

게시본 `6b70043833a739e875d542c53066b8ac136a90a3`에서 기존 직접 소유 root의 직렬
export 값 메뉴로 정수 37을 선택한 뒤 checkpoint 쓰기를 실패시켰다. live 값은 바뀌고
개인 입력은 지워졌지만 checkpoint·물리 원본·C#은 그대로였다. cold에서는 원래 연결만
복원됐다. 수정 전 입력·요청·실패 화면·cold를 보관했다. 첫 분기 fixture는 기존 영역
검증에서 선행 거절돼 입력이 보존됐으므로 유실 재현으로 세지 않는다.

기존 단일 export 값 입력을 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo로 연결했다.
정확한 `$exports`/outputNodes/단일 value만 허용하며 원래 표현식·자료형·영역·연결
검증을 재사용한다. C# 노드의 일반 argument 권한을 export에 부여하지 않는다.
개발 API 검사에서 잘못된 문자열→정수 후보가 checkpoint에 들어가는 결함도 확인해,
기존 read 진단이 invalid인 outputNodes 후보는 checkpoint 전에 거절하도록 연결했다.
새 자료형 규칙이나 C# 변환은 만들지 않았다.

미반영과 동일 checkpoint·전체 source proof·원본이 확인될 때만 새 값으로 명시 재시도한다.
응답 유실은 receipt만 회수하며 늦은 입력은 별도 보관하고 이전 값을 재전송하지 않는다.
변경 파일이 없는 반복 Save도 `ownedOutputValue` receipt를 보관한다. 기존 source/name/
route/entry receipt·C# bytes·ID·공개/override 계약·profile·다른 연결·권한을 보존한다.
물리 쓰기는 Review→Confirm과 최종 CAS 뒤에서만 한다. 관련 저장 분리 안내 1문구·1곳을
정리했다. UI·레이아웃·공개 .celem 문법은 유지하고 사용자 파일을 가짜로 바꾸지 않는다.

## 최종 신규 검증

독립 LF 19·CRLF 20·새 패키지/전체 복원/실패 수명관리
8, **총 47단계: 신규 47·재사용 0** 통과.
독립 Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 확인했다. 개발의 실패·통과 단계는
최종 수에 합산하지 않는다.

- 정확한 제품·안내 delta와 canonical JS metadata·문법·이전 완료 기능 보존을 대조했다.
  실제 공유 history inverse/CAS/restart/owner와 표시명 native 회귀를 검사했다.
- API에서 stale checkpoint·위조 source closure·가상 origin/없는 export·일반 code·
  owner/slot/frame·출력 재배정/생성/삭제·복수 값/본문/계약 혼합·여분 필드·비문자열
  표현식·선언 자료형 위반을 거절했다. 일반 code argument로 export를 우회하는 경로도
  거절한다. 저장은 멱등이며 cold·공유 history·receipt hash 위조 거절을 유지한다.
- 기존 값 메뉴 취소·개인 값 cold 복원·checkpoint 쓰기 실패 뒤 새 값과 명시 재시도·
  동료 checkpoint 충돌/cold를 검사했다. 응답 유실은 재전송 없이 receipt만 회수하며,
  저장 중 새 값은 독립 보관한다. 실제 packet의 valueJson이 새 값과 정확히 일치하고
  새 요청이 존재하는지 확인했다.
- 공유 Undo/Redo/cold·Review 취소·검토 후 Main.graph.json 충돌 거절·새 Review/Confirm·
  실제 .NET 실행을 검사했다. graph에서는 publish_return의 arguments.value만 바뀌고
  모든 기존 노드/edge/ID/profile·다른 파일/C# bytes는 같다. 출력은 `callee:1` 다음
  `after:10`을 유지하고 반환은 명시한 37 또는 41이다.
- 변경 없는 반복 Save도 receipt를 유지하며 cold에서 물리 쓰기 없이 판정한다.
  기존 source/name/route/entry API를 양쪽에서 새로 회귀했다. CRLF에서는 entry 쓰기
  실패/새 선택/cold/Undo/Review·Confirm·실행 UI와 property 관찰·부분 Review·경로/
  원본 위조·expected-missing/readonly CAS도 새로 확인했다.
- 새 Windows 교차 패키지의 구성·무결성·패키지 엔진 웹 시작과 export 정상/응답 유실
  UI·실행을 확인했다. CRC·전체 파일 SHA/모드를 검증해 완전히 복원한 뒤 복원 엔진의
  export 쓰기 실패/새 값·늦은 값 UI를 최종 Confirm·실행/cold까지 검사했다.
- 성공·반복·실패·예외의 증거 보존/복원·자식 종료·소유 임시물 cleanup도 통과했다.

저장 전 모든 private Undo/Redo·포인터/터치·문맥/프로젝트 왕복·전체 UI 완료를 주장하지
않는다. 이번 실제 UI 조작은 기존 export 값 메뉴이며 안내의 모든 오류 조건을 각각
UI로 주입하지는 않았다. 종료점 값·export 생성/삭제/재배정/실행선 혼합·root 핀·혼합
계약·slot/copy/private/whole-body는 별도 점검 후보다. 재현 없이 미구현·정상 금지·새 필수
조합으로 단정하지 않는다. 원래 분기 영역 검증을 변경하지 않았다.

## 증거와 보관

개발 record `/workspace/artifacts/v536-verification-managed/runs/b5478e834c15416490d58ec7d99efa5e.json`

개발 SHA `190b38766da2d5f198d77f211797c0aabbea7effc1cf6a69e5ed631a3785d367`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/680803d6238645678bd8bc1e2b5699f5.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/680803d6238645678bd8bc1e2b5699f5.zip`

SHA256 `eb7c946b305a777e79a3754422d6ddd90e8ab7db9bffb0b9d3dfb807482450e3` (2.67MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `a8b0dd511dc2a1030cad73d78020b8215a70d28a`, `828b6272e8f93cf856aaedee211deeb08a3d8e05f425fbf9fde4cf4d0a883955.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `8727082657c5630e63b1a664dc6fc93137b676578ced4bfe598c49d69f650ed2`.

- rollback: 출처 `fe44bc6910e7b5da7b1d810c8ef5c9e0703911eb`, `c3e44542905a8d719d2f0b2ed05f1272d52c34a1c59719780e261f10be234580.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `ad18d4f10d16417e5fd464934180360daa5e7184f4a24fda00cf32332912bd7f`.

최신은 최종 동결 코드와 일치한다. 정상 롤백·증거·원본을 유지하고 자식 종료와 archive
검증 뒤 이번 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1615.96MiB, 최대 cgroup 메모리
4672.92MiB. 최종 실행 순증가 3.82MiB, 개발 시작부터 보관
확인까지 5.74MiB, 문서 마감 전 여유 1612.20MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 일반 Save와 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 수용 표에
남긴다. 완료 M11/M12/M4를 조합별로 다시 열지 않는다. 검증은 컨테이너 Chromium·
실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·
전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다. live AI·자격증명·유료 호출·
새 외부 권한은 사용하지 않았다.
