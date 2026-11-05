# v666 기존 export 노드 삭제 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `a358bdd9805eb8ef9dc3a975fb5731b4d14839ed`다. 이후 마감 commit은 이 문서와
수용 표만 바꾼다. [지원 경계](V2_EXPORT_REMOVAL_RECOVERY.md)와
[정확한 delta](v666-export-removal-recovery-delta.json)를 따른다.

## 재현·수정

게시본 `3b6191591fd920678d4c9e0458f8703deead4277`의 생성 프로젝트에서 기존 export
삭제 버튼을 누른 뒤 checkpoint 쓰기를 실패시켰다. live 노드와 개인 삭제 입력이 사라졌지만
checkpoint·물리 원본은 같았다. 재시작 후 노드는 돌아오고 삭제 선택은 없어졌다.
원래 실제 .NET 실행, 실패 화면·개인 입력·traffic·cold 증거를 개발 record에 보관했다.

직접 소유 root의 기존 직렬 export 하나를 정확한 remove 후보로 연결했다. 기존 native
삭제·graph 검증을 후보에서 실행하고 CAS 체크포인트 저장이 성공한 뒤 live에 반영한다.
적용돼 노드가 없어져도 원래 요청을 같은 형태로 직렬화해 receipt를 회수한다. 없는 노드의
새 삭제 요청을 성공으로 바꾸지 않는다. 실패한 미반영 삭제에 다른 입력이 섞이면 live 직접
수정 경로로 우회하지 않고 두 입력을 보존하며 거절한다. 이미 적용된 삭제의 늦은 입력은
별도 보존·재시도하고 삭제 자체를 재전송하지 않는다.

공개 출력 선언·C# bytes·ID·핀/override 계약·profile·남은 출력·권한·부모/외부 원본과
기존 삭제의 실행선 우회 및 해당 profile의 out 기본값 의미를 유지한다. 물리 쓰기는
Review→Confirm과 최종 CAS 뒤에서만 한다. 문구·팝오버·레이아웃 변경은 없다.

## 최종 신규 검사

독립 LF 23·CRLF 23·새 패키지/전체 복원/실패 수명관리
8, **총 54단계: 신규 54·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발 단계의 통과/실패는 최종
집계에 합산하지 않는다. 개발 API의 변수 누락과 지연 응답 fixture의 flush 대기를 고쳐 해당 검사만 재실행했다.
중단한 소유 worker의 진단·완료 기록과 증거도 보존했다.

- 정확한 로직 delta·canonical JS metadata·문법·기존 문구/레이아웃을 대조했다.
  실제 공유 history inverse/CAS/restart/owner와 표시명 native 회귀를 검사했다.
- API는 stale checkpoint·위조 source proof·잘못된 가상 origin·없는/비문자열 ID·code
  노드·owner/private frame·여분 필드·다중 삭제·본문/계약 혼합·생성/재배정 허용 차용을
  거절했다. 정상 삭제의 멱등 재요청·공유 history·cold·receipt 위조 거절을 확인했다.
- 기존 삭제 버튼의 저장 전 개인 Undo/Redo와 삭제 선택 cold 복원·checkpoint 쓰기 실패/
  명시 재시도·동료 checkpoint 충돌/cold·응답 유실·지연 중 늦은 값을 확인했다.
  응답 유실은 receipt만 확인하고 삭제를 재전송하지 않는다. 적용 후 늦은 값은 새 값
  요청만 보내며, 미반영 삭제에 새 값이 섞이면 두 입력을 유지하고 live 쓰기를 거절한다.
- 저장 후 공유 Undo/Redo/cold·Review 취소·검토 후 물리 graph 충돌 거절·새 Review/
  Confirm·실제 .NET 실행을 확인했다. 원래 `body` 다음 `17:23:0:False`, 반환 1이다.
  publish만 삭제하면 `body` 다음 `0:23:0:False`, 반환 2이고 늦은 keep 값 29를 별도
  저장하면 `0:29:0:False`, 반환 2다. 삭제 자체는 publish와 기존 규칙에 따른 인접
  실행선만 바꾼다. 늦게 명시한 keep 값 외의 다른 내용·ID·계약·C# bytes는 그대로다.
- root 반환·export binding/value·entry/source/name/route API를 양쪽에서 새로 회귀했다.
  CRLF에서는 기존 export 재배정 쓰기 실패/새 선택/cold/Undo/Review·Confirm·실행 UI와
  property 관찰/부분 Review/경로·원본 위조/expected-missing·readonly CAS도 확인했다.
- 새 Windows 교차 패키지의 구성·무결성 및 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  CRC·전체 파일 SHA/모드를 검증해 완전히 복원한 뒤 복원 엔진의 쓰기 실패/재시도와
  늦은 입력 UI를 최종 Confirm·실행/cold까지 확인했다.
- 성공·반복·실패·예외의 증거 보존/복원·자식 종료·소유 임시물 cleanup도 통과했다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/0806d798721544e08a25229c00cbc72f.json`

개발 증거 SHA `24e7a81d39d95349b14aa72f6b8294f092cb7e2133331364925ba91832ce8988`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/7a7c594742044c33b7ffef0b0c485e1f.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/7a7c594742044c33b7ffef0b0c485e1f.zip`

SHA256 `542333ae9b9bf02106cada1fb6e4890f6685df3a0e4e8fa2abe3c3c4600a8032` (2.66MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `a358bdd9805eb8ef9dc3a975fb5731b4d14839ed`, `6f0c884c8ad2cb3bb28b941386317eb70cf5b23a477a77ffc17e7fa6041fbded.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `fb386063b3359e5aae485de279c30c472f74419a164dc1378af5a9b2b1c9978b`.

- rollback: 출처 `0e39dd05d5934bdb89a1f21e6419ceb40931eade`, `75f045b85c0116b58b5df8ca4ec9c74f49256f97ea2088ec9c116355691d437b.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `afc77913f4f96a04f8aab31ae0fe3be53cc7c4efeab0124baac7776e5f89f519`.

최신은 최종 동결 코드와 일치한다. 롤백·증거·원본을 보존하고 archive 검증과 자식 종료 뒤
이번 실행이 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 추가 삭제하지 않았다.
단계 표본 최소 여유 1599.36MiB, 최대 cgroup 메모리 4651.72MiB다.
최종 실행 순증가 3.88MiB, 개발 시작부터 보관 확인까지
5.49MiB, 문서 마감 전 여유 1595.54MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

root 핀 정의·export 생성/구조 혼합·혼합 계약 Save는 별도 읽기 점검 후보다.
재현 없이 결함/정상 금지/필수 조합으로 단정하지 않는다. 완료 M11/M12/M4를 다시 열지
않는다. 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 고정 수용 표에 남긴다.
검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이며 실제 Windows apphost/
WebView2·모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다.
새 권한·외부 접근·live AI·자격증명·유료 호출은 사용하지 않았다.
