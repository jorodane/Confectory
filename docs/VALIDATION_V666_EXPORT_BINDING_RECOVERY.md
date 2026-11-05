# v666 기존 내보내기 출력 재배정 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `3980f6688107460221ef8cd69bba306f179649ae`다. 이후 마감 commit은 이 검증 문서와
수용 표만 바꾼다. [지원 범위](V2_EXPORT_BINDING_RECOVERY.md), [정확한 delta](v666-export-binding-recovery-delta.json)를 따른다.

## 재현과 수정

게시본 `c2380222c3cf179e613c81e7a709036c5ba8a671`의 생성 프로젝트에서 원래 실행을
실제 .NET으로 먼저 확인했다. 기존 export 출력 메뉴에서 left→right를 고르고 checkpoint
쓰기를 실패시키면 live 대상은 바뀌고 개인 입력은 사라졌지만 checkpoint·물리 원본·C#은
그대로였다. cold에서는 원래 left만 복원됐다. 수정 전 원문·입력·실패 화면·traffic·cold와
원래 실행 결과를 개발 record에 보관했다.

단일 기존 export의 출력 재배정을 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo에
연결했다. 정확한 `$exports`/outputNodes/단일 bind만 허용하고 기존 선언 출력·자료형·
값·영역·연결 검증을 재사용한다. 값이 있는 정수 export를 기존 bool 출력에 재배정하면
거절하며 원래 선택과 값을 보존한다. 새 출력 선언·자동 값 삭제/변환·C# 재작성은 없다.
기존 value 저장과 source/name/route/entry의 보호를 유지한다.

미반영과 동일 checkpoint·전체 source proof·원본이 확인될 때만 새 선택으로 명시 재시도한다.
응답 유실은 receipt만 회수하고 늦은 선택은 분리 보관하며 이전 선택을 재전송하지 않는다.
변경 없는 반복 Save도 `ownedOutputBinding` receipt를 보관하고 원문을 가짜로 바꾸지 않는다.
C# bytes·ID·입출력/override 계약·profile·값·다른 연결·권한과 부모/외부 원본은 보존한다.
물리 쓰기는 Review→Confirm과 최종 CAS 뒤에서만 한다. 기존 출력 선택·자료형 거절 안내
2문구·2곳을 정리했다. 원본 메뉴·레이아웃과 공개 .celem 문법은 유지한다.

## 최종 신규 검증

독립 LF 20·CRLF 21·새 패키지/전체 복원/실패 수명관리
8, **총 49단계: 신규 49·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발 통과·실패 단계는 최종 수에
합산하지 않는다.

- 정확한 제품·안내 delta·canonical JS metadata·문법·이전 완료 기능을 대조했다.
  실제 공유 history inverse/CAS/restart/owner와 표시명 native 회귀를 검사했다.
- API에서 stale checkpoint·위조 source closure·가상 origin/없는 export·C# code·
  owner/slot/frame·값 혼합·생성/삭제·복수 재배정·본문/계약 혼합·여분 필드·미선언 출력·
  비문자열 출력 식별·기존 값과 다른 자료형을 거절했다. 일반 code argument로 export를
  우회하는 경로도 거절한다. 멱등 저장·cold·공유 history·receipt hash 위조 거절을 유지한다.
- 기존 출력 메뉴 취소·개인 선택 cold 복원·다른 자료형 선택 거절과 기존 입력 보존·
  checkpoint 쓰기 실패 뒤 새 선택/명시 재시도·동료 checkpoint 충돌/cold를 확인했다.
  응답 유실은 receipt만 회수하며 저장 중 늦은 선택은 별도 보관한다. 실제 packet의 bind
  대상이 새 출력과 정확히 같고 새 요청이 존재하는지 확인했다. 이전 선택은 재전송하지 않는다.
- 공유 Undo/Redo/cold·Review 취소·검토 후 Pair.graph.json 원본 충돌 거절·새 Review/Confirm·
  실제 .NET 실행을 검사했다. graph에서는 기존 publish의 output만 right 또는 spare로
  바뀌고 값 17·모든 기존 노드/edge/ID/profile·다른 파일/C# bytes는 같다. 원래 실행은
  `body` 다음 `17:0:0:False`, 반환 1이다. 재배정 뒤에는 `0:17:0:False`/반환 2 또는
  `0:0:17:False`/반환 3이다. 미배정 출력의 기본값은 원래 implicit-out 프로필의 기존
  의미이며 Core나 기본값 정책을 바꾸지 않았다.
- 변경 없는 반복 Save도 receipt를 유지하고 cold에서 물리 쓰기 없이 판정한다.
  기존 export value/source/name/route/entry API를 양쪽에서 새로 회귀했다. CRLF에서는
  기존 export 값 쓰기 실패/새 값/cold/Undo/Review·Confirm·실행 UI와 property 관찰·
  부분 Review·경로/원본 위조·expected-missing/readonly CAS도 새로 확인했다.
- 새 Windows 교차 패키지의 구성·무결성·패키지 엔진 웹 시작과 정상/응답 유실 UI·실행을
  확인했다. CRC·전체 파일 SHA/모드를 검증해 완전히 복원한 뒤 복원 엔진의 쓰기 실패/
  새 선택·늦은 선택 UI를 최종 Confirm·실행/cold까지 확인했다.
- 성공·반복·실패·예외의 증거 보존/복원·자식 종료·소유 임시물 cleanup도 통과했다.

이번 UI는 기존 출력 메뉴 경로다. 저장 전 모든 private Undo/Redo·포인터/터치·문맥/
프로젝트 왕복·전체 UI 완료를 주장하지 않는다. 안내의 모든 오류 조건을 각각 UI로
주입하지는 않았다. export 생성/삭제·구조 입력 혼합·root 핀·종료점 값·혼합 계약·
slot/copy/private/whole-body는 별도 읽기 점검 후보다. 재현 없이 결함·정상 금지·
새 필수 조합으로 단정하지 않는다.

## 증거·보관

개발 record `/workspace/artifacts/v536-verification-managed/runs/0402b32396bd498685657556f92d7926.json`

개발 SHA `7dce8f164d781d9a06b09afd808c570e15c3b7686f6bf7c87afe8d1c2eb10910`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/cb44596a68ee4043a5a758ec829019dc.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/cb44596a68ee4043a5a758ec829019dc.zip`

SHA256 `4b174c3531ebdf9015207e324efbd13a903a3cf7b663161b45ff72a0cf17727e` (2.52MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `3980f6688107460221ef8cd69bba306f179649ae`, `1002dc94f5aad3abb8c175552dd28b7710c8360b8db00fd11a254da1c8059568.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `13e6602965b4377b871d507c06bcb0c1220f13e1fe02137a054f6c245f322ddb`.

- rollback: 출처 `a8b0dd511dc2a1030cad73d78020b8215a70d28a`, `828b6272e8f93cf856aaedee211deeb08a3d8e05f425fbf9fde4cf4d0a883955.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `8727082657c5630e63b1a664dc6fc93137b676578ced4bfe598c49d69f650ed2`.

최신은 최종 동결 코드와 일치한다. 정상 롤백·증거·원본을 유지하고 자식 종료와 archive
검증 뒤 이번 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1610.47MiB, 최대 cgroup 메모리
4646.56MiB. 최종 실행 순증가 3.66MiB, 개발 시작부터 보관
확인까지 5.25MiB, 문서 마감 전 여유 1606.87MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 일반 Save와 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 수용 표에
남긴다. 완료 M11/M12/M4를 조합별로 다시 열지 않는다. 검증은 컨테이너 Chromium·
실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·
전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다. live AI·자격증명·유료 호출·
새 외부 권한은 사용하지 않았다.
