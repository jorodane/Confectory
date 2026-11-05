# v666 기존 root 반환 출력 핀 값 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `0e39dd05d5934bdb89a1f21e6419ceb40931eade`다. 이후 마감 commit은 이 검증 문서와
수용 표만 바꾼다. [지원 범위](V2_ROOT_RETURN_RECOVERY.md), [정확한 delta](v666-root-return-recovery-delta.json)를 따른다.

## 재현과 수정

게시본 `f37c06237eed76bcc674a05a92bc0df3a609553a`의 생성 프로젝트에서 원래 .NET 실행을
확인했다. 기존 `$exit:return` 값 메뉴로 정수 37을 선택하고 checkpoint 쓰기를 실패시키면
live 값은 바뀌고 개인 입력은 사라졌지만 checkpoint·물리 원본·C#은 그대로였다.
재시작 뒤 원래 호출 출력 연결만 복원됐다. 수정 전 원문·입력·실패 화면·traffic·cold와
원래 실행 결과를 개발 record에 보관했다.

기존 직접 소유 ordinary nonvoid root의 단일 반환 값을 원자 후보·checkpoint CAS·receipt·
공유 Undo/Redo에 연결했다. 정확한 exit/`$exit:return`/return/문자열 표현식만 허용하며
기존 값·자료형 검증을 재사용한다. void·실행 분기 종료·return export 작성자·다른 소유/
private 문맥이 이 허용을 빌려 쓰지 못한다. 공개 핀 정의·타입·순서나 새 계약을 만들지 않는다.

미반영과 동일 checkpoint·전체 source proof·원본이 확인될 때만 새 값으로 명시 재시도한다.
응답 유실은 receipt만 회수하며 늦은 새 값은 별도 보관하고 이전 값을 재전송하지 않는다.
변경 없는 반복 Save도 `ownedRootReturn` receipt를 유지하고 원문을 가짜로 바꾸지 않는다.
기존 export binding/value·source/name/route/entry의 보호와 C# bytes·ID·입출력/override 계약·
profile·다른 연결·권한·부모/외부 원본을 보존한다. 물리 쓰기는 Review→Confirm과 최종
CAS 뒤에서만 한다. 새 문구·UI 없이 기존 안내·메뉴·레이아웃을 유지한다.

## 최종 신규 검증

독립 LF 21·CRLF 22·새 패키지/전체 복원/실패 수명관리
8, **총 51단계: 신규 51·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발 통과·실패 단계는 최종 수에
합산하지 않는다.

- 정확한 제품 delta·canonical JS metadata·문법·이전 완료 기능을 대조했다.
  실제 공유 history inverse/CAS/restart/owner와 표시명 native 회귀를 검사했다.
- API에서 stale checkpoint·위조 source closure·잘못된 가상 핀/종료점·owner/slot/frame·
  노드 값/본문/계약/실행선 혼합·여분 필드·비문자열 표현식·반환 자료형 위반을 거절했다.
  실제 void 함수와 기존 return export 작성자 문맥의 허용 차용도 거절했다. 멱등 저장·
  공유 history·cold·receipt hash 위조 거절을 유지한다.
- 기존 값 메뉴 취소·개인 값 cold 복원·checkpoint 쓰기 실패 뒤 새 값/명시 재시도·
  동료 checkpoint 충돌/cold를 확인했다. 응답 유실은 receipt만 회수하며 저장 중 새 값은
  독립 보관한다. 실제 packet이 정확한 새 exit 값이며 새 요청이 존재하는지 확인했다.
  이전 값은 재전송하지 않는다.
- 공유 Undo/Redo/cold·Review 취소·검토 후 Main.graph.json 원본 충돌 거절·새 Review/Confirm·
  실제 .NET 실행을 검사했다. graph에서는 exits.return만 바뀌고 모든 기존 노드/edge/ID/
  profile·다른 파일/C# bytes는 같다. 원래는 반환 10, `callee:1` 다음 `after:10`이다.
  명시 편집 뒤 출력은 그대로이고 반환은 37 또는 41이다.
- 변경 없는 반복 Save도 receipt를 유지하고 cold에서 물리 쓰기 없이 판정한다.
  기존 export binding/value·entry/source/name/route API를 양쪽에서 새로 회귀했다.
  CRLF에서는 기존 재배정 쓰기 실패/새 선택/cold/Undo/Review·Confirm·실행 UI와 property
  관찰·부분 Review·경로/원본 위조·expected-missing/readonly CAS도 새로 확인했다.
- 새 Windows 교차 패키지의 구성·무결성·패키지 엔진 웹 시작과 정상/응답 유실 UI·실행을
  확인했다. CRC·전체 파일 SHA/모드를 검증해 완전히 복원한 뒤 복원 엔진의 쓰기 실패/
  새 값·늦은 값 UI를 최종 Confirm·실행/cold까지 확인했다.
- 성공·반복·실패·예외의 증거 보존/복원·자식 종료·소유 임시물 cleanup도 통과했다.

이번 UI는 기존 root 반환 값 메뉴다. 저장 전 모든 private Undo/Redo·포인터/터치·문맥/
프로젝트 왕복·전체 UI 완료를 주장하지 않는다. root 핀 정의·다른 종료점 문맥·export
생성/삭제·구조 입력 혼합·혼합 계약은 별도 읽기 점검 후보다. 재현 없이 결함·정상 금지·
새 필수 조합으로 단정하지 않는다. 실행 분기 종료나 C# 의미를 자동 변환하지 않았다.

## 증거·보관

개발 record `/workspace/artifacts/v536-verification-managed/runs/9c400a2992174954be3f6efb057aa980.json`

개발 SHA `22075bc0a44a7b458a8ab951ba218912152194d55a2ce2604aa13e959563bea9`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/8b623130e4994cc68b0c03fd6832b71b.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/8b623130e4994cc68b0c03fd6832b71b.zip`

SHA256 `78bbd2e95ec96a1ca1b27a0c764e8ac0df4c201d66d344b5635f6328d0853b68` (2.75MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `0e39dd05d5934bdb89a1f21e6419ceb40931eade`, `75f045b85c0116b58b5df8ca4ec9c74f49256f97ea2088ec9c116355691d437b.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `afc77913f4f96a04f8aab31ae0fe3be53cc7c4efeab0124baac7776e5f89f519`.

- rollback: 출처 `3980f6688107460221ef8cd69bba306f179649ae`, `1002dc94f5aad3abb8c175552dd28b7710c8360b8db00fd11a254da1c8059568.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `13e6602965b4377b871d507c06bcb0c1220f13e1fe02137a054f6c245f322ddb`.

최신은 최종 동결 코드와 일치한다. 정상 롤백·증거·원본을 유지하고 자식 종료와 archive
검증 뒤 이번 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1605.03MiB, 최대 cgroup 메모리
4684.48MiB. 최종 실행 순증가 3.95MiB, 개발 시작부터 보관
확인까지 5.64MiB, 문서 마감 전 여유 1601.15MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 일반 Save와 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 수용 표에
남긴다. 완료 M11/M12/M4를 조합별로 다시 열지 않는다. 검증은 컨테이너 Chromium·
실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·모바일 기기·DPI/IME·
전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다. live AI·자격증명·유료 호출·
새 외부 권한은 사용하지 않았다.
