# v666 새 export·값·수동 연결 첫 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `3473213dfa9df7b2813d09f2e3f5b3cec03815c4`다. 이후 마감 commit은 이 문서와
수용 표만 바꾼다. [지원 경계](V2_EXPORT_CREATION_RECOVERY.md)와
[정확한 delta](v666-export-creation-recovery-delta.json)를 따른다.

## 재현과 수정

게시본 `f813c5780de4930feed67e5d62187f3f016de65a`의 생성 프로젝트에서 기존 캔버스
메뉴로 export를 만들고 값 37을 입력했다. 기존 code next 선을 명시적으로 해제하고
양쪽 실행선을 수동 연결한 네 입력의 Save에서 checkpoint 쓰기를 실패시켰다. live에는
새 노드가 생겼지만 개인 입력은 모두 지워졌고 checkpoint·물리 원본·C#은 같았다.
재시작 후 새 노드·값·연결 선택을 잃었다. 원래 실제 실행과 실패 화면·입력·traffic·cold
증거를 개발 record에 보관했다.

생성 1·그 값 1·관측한 code next 목적지 사이의 연결 2를 한 원자 후보·CAS·receipt·
공유 Undo/Redo로 연결했다. 기존 native ID/출력/값/graph 검증을 재사용하고 성공한
checkpoint 뒤에 live를 반영한다. ID가 이미 생겼어도 원래 요청을 같은 형태로 직렬화해
receipt를 회수한다. 미반영·동일 checkpoint·전체 proof를 확인한 뒤에만 같은 ID/출력/
양쪽 연결을 유지한 새 노드 값 수정의 명시 재시도를 허용한다. 적용 후 늦은 값은 별도
Save로 넘기며 생성/연결을 재전송하지 않는다. 미반영 계획에 무관한 입력이 섞이면
모두 보존하고 live 직접 수정 경로로 우회하지 않는다.

공개/override 입출력 계약·C# bytes·기존 ID·다른 값/연결·profile·권한·부모/외부 원본,
Review→Confirm과 최종 CAS 및 기존 안내/팝오버/레이아웃을 보존한다. 실행선 메뉴의
export 자동 배치는 기존 미연결 거절 경계로 남겼다. 영구 UX 정책으로 정하지 않았다.

## 최종 신규 검사

독립 LF 24·CRLF 24·새 패키지/전체 복원/실패 수명관리
8, **총 56단계: 신규 56·재사용 0** 통과.
Git 객체·실제 줄바꿈·엔진 캐시·NuGet/home을 분리했다. 개발 통과/실패는 최종 수에
합산하지 않는다. 초기 fixture의 겹친 미니맵 선택, 기존 선 해제/개인 Undo 보호에 대한
잘못된 가정, read 응답의 valueJson 읽기와 개인 입력/저장 시도 기록 계수를 고쳤다.
제품 UI나 보호를 우회하지 않았다.
초기 실패 기록과 정상 동작을 확인한 수정 검사를 함께 보관했다.

- 정확한 제품 delta·canonical JS metadata·문법·기존 완료 문구/레이아웃을 대조했다.
  실제 공유 history inverse/CAS/restart/owner와 표시명 native 회귀도 확인했다.
- API에서 stale checkpoint·위조 source proof·잘못된 origin·소유/private frame 차용·
  기존/잘못된 ID·불일치 new ID·다중 생성·여분 필드·본문/계약/다른 값 혼합을 거절했다.
  ordinary code와 관측한 next 목적지가 아닌 계획·누락/자기 연결·없는 출력·출력 자료형
  위반·비문자열 값도 거절했다. 정상 후보의 같은 ID 멱등 재요청·history·cold·위조
  receipt 거절을 확인했고 물리 원본은 Confirm 전까지 같았다.
- 기존 생성 메뉴 취소·생성 직후 개인 Undo/Redo·후속 입력을 보존하는 이전 Undo 거절·
  네 입력 cold 복원을 확인했다. checkpoint 쓰기 실패 뒤 live/원본/네 입력이 보존됐고
  같은 ID의 새 값 41을 cold 후 명시 재시도했다. 동료 checkpoint 충돌도 보존하며 거절했다.
- 응답 유실은 receipt만 회수하고 재생성/재연결하지 않았다. 적용 후 늦은 값 41은 새
  value 요청만 보냈다. 미반영 계획에 keep의 무관한 새 값이 섞이면 다섯 입력을 cold
  후에도 보존하고 live 쓰기를 거절했다.
- 공유 Undo/Redo는 새 노드·양쪽 연결을 함께 제거/복원한다. 별도 늦은 값은 별도 history다.
  Review 취소·검토 뒤 물리 graph 충돌 거절·새 Review/Confirm·실제 .NET 실행·cold를 확인했다.
  원래 `body` 다음 `17:23:0:False`, 반환 1이다. 새 export 뒤 `17:23:37:False` 또는
  `17:23:41:False`, 반환 1이다. 명시한 새 노드/값·인접 실행선 외에 기존 node/ID/계약/
  profile·나머지 출력·다른 파일/C# bytes는 그대로다.
- 기존 export 삭제·재배정·값과 root 반환·entry/source/name/route API를 양쪽에서 새로 회귀했다.
  CRLF에서는 기존 export 재배정의 실패/새 선택/cold/Undo/Review·Confirm·실행 UI와
  property 관찰/부분 Review/경로·원본 위조/expected-missing·readonly CAS도 확인했다.
- 새 Windows 교차 패키지의 구성·무결성과 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  CRC·전체 파일 SHA/모드를 검증해 완전히 복원한 뒤 복원 엔진의 실패/값 수정/재시도와
  늦은 값 UI를 Confirm·실행/cold까지 확인했다. 성공·반복·실패·예외의 증거 보존/복원·
  자식 종료·소유 임시물 cleanup도 통과했다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/90d0e686365b415da2a6f1df39b3a329.json`

개발 증거 SHA `698f1844865d7a0f4c40c575a42b68c3ba0d581c17f97e76e036086a8802c801`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/7f7242a9793045afa36e28aa2c3dc7bd.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/7f7242a9793045afa36e28aa2c3dc7bd.zip`

SHA256 `6514894cf5dc4ca3a7f83c2a5499e3ae92955bbacd49be0e47294a2cb75e75d3` (2.75MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `3473213dfa9df7b2813d09f2e3f5b3cec03815c4`, `310273bdde2e5a0b0d798e7594d1335ccf155bd4c2c50977aaec88986e74a1d4.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `114e70224c43a19427e0c7c1225b7de6585223338301a4facf6e984f19086856`.

- rollback: 출처 `a358bdd9805eb8ef9dc3a975fb5731b4d14839ed`, `6f0c884c8ad2cb3bb28b941386317eb70cf5b23a477a77ffc17e7fa6041fbded.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `fb386063b3359e5aae485de279c30c472f74419a164dc1378af5a9b2b1c9978b`.

최신은 최종 동결 코드와 일치한다. 롤백·증거·원본을 보존하고 archive 검증과 자식 종료 뒤
이번 실행이 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 추가 삭제하지 않았다.
단계 표본 최소 여유 1592.47MiB, 최대 cgroup 메모리 4663.38MiB다.
최종 실행 순증가 3.99MiB, 개발 시작부터 보관 확인까지
6.89MiB, 문서 마감 전 여유 1588.54MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

root 핀 정의·다른 생성/구조 혼합·혼합 계약 Save와 export 직접 배치는 원본 요구/현재
지원과 대조할 별도 점검 후보다. 조합마다 새 필수 요구를 만들지 않는다. 완료 M11/M12/M4를
다시 열지 않는다. 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 고정 수용 표에
남긴다. 검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이며 실제 Windows apphost/
WebView2·모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다.
live AI·자격증명·유료 호출·새 권한/외부 접근은 사용하지 않았다.
