# v666 root 입력 식별자 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `68e76080d342ca634b95265cc74c875c9de68d89`다. 이후 마감 commit은 문서와
수용 표만 바꾼다. [지원 경계](V2_ROOT_INPUT_NAME_RECOVERY.md)와
[정확한 delta](v666-root-input-name-recovery-delta.json)를 따른다.

## 재현·수정

게시본 `2a553854ad254994c1b361a472c42a0c1ba8bdf8`에서 기존 입력 이름 UI로
`amount`를 `units`로 바꾸고 checkpoint 쓰기를 실패시켰다. live 이름은 바뀌고 개인
입력은 사라졌지만 checkpoint·물리 원본·C#은 같았다. 재시작 후 원래 이름만 돌아왔다.
수정 전 실제 .NET 실행·실패 화면·입력·traffic·cold 증거를 개발 record에 보관한다.

직접 소유 ordinary 동기 root의 값 입력 하나에 대해 타입·위치·mode·반환·출력 정체성을
유지하는 이름 변경만 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo로 연결했다.
기존 native의 완전한 명시 remap과 root 계약 검증을 재사용한다. 함수·구현 선언의 입력
이름과 root 입력 참조를 바꾸며 본문의 인자·C# bytes·위치 기반 호출자 bytes는 보존한다.
입력 추가/삭제·타입/ref/out·반환/공개 실행 계약 변경·다른 편집 혼합은 허용하지 않는다.
기존 권한/소유/부모외부/override 보호, Review→Confirm과 최종 CAS를 유지한다.

미반영·같은 checkpoint·전체 source proof가 확인된 경우에만 같은 계약의 새 이름으로
명시 재시도한다. 개인 Undo로 취소한 입력을 자동 재적용하지 않는다. 응답 유실은 receipt만
회수한다. 자신의 확정 receipt와 단일 현재 입력 계약이 일치한 경우에만 늦은 새 이름의
remap을 받아들인 이름에서 새 이름으로 잇는다. 동료/미확인 변경을 허용 근거로 쓰지 않는다.
미반영 계획에 무관한 입력이 섞이면 모두 보존하고 legacy live 경로로 우회하지 않는다.
같은 이름의 변경 없는 Save도 receipt와 기존 세-member root 묶음을 함께 보관한다.
원본 팝오버·문구·레이아웃을 보존하며 새 표시명/영구 핀 ID 정책을 정하지 않는다.

## 최종 신규 검사

독립 LF 26·CRLF 26·새 패키지/전체 복원/실패 수명관리
8, **총 60단계: 신규 60·재사용 0** 통과.
Git 객체·실제 줄바꿈·엔진 캐시·NuGet/home을 분리했다. 개발 결과는 최종 수에 합산하지 않는다.

- 제품 변경 네 파일·canonical JS metadata·문법·기존 안내/레이아웃을 정확한 delta로 대조했다.
  실제 공유 history inverse/CAS/restart/owner 및 표시명 런타임 회귀도 확인했다.
- stale checkpoint·위조 전체 source proof·잘못된 origin·소유/private frame 차용·여분 필드·
  입력 추가/삭제·타입/mode/반환 변경·출력 정체성/수 변경·불완전/다른/여분 remap·
  공백/빈/비문자열/길이 초과 이름·본문/다른 계약 혼합을 거절했다.
  정상 후보·같은 요청 멱등 회수·공유 history·cold·위조 receipt 거절을 확인했다.
- 기존 이름 편집·개인 Undo/Redo·cold와 checkpoint 쓰기 실패 후 입력/live/물리 원본 보존,
  실패 뒤 Undo 취소가 재적용되지 않음·Redo/수정 이름의 cold 명시 재시도를 확인했다.
  동료 checkpoint 충돌과 무관한 새 동작 이름 혼합도 cold/retry 후 입력을 보존하며 거절했다.
- 응답 유실은 원래 이름 변경을 재전송하지 않고 receipt만 회수했다. 적용 후 늦은 이름은
  받아들인 이름에서 새 이름으로의 remap만 전송한다. 공유 Undo/Redo/cold도 확인했다.
- Review 취소·검토 뒤 물리 graph 충돌 거절·새 Review/Confirm·실제 .NET 실행·cold를 확인했다.
  원래/선택/수정 이름 모두 `body` 다음 `10`, 반환 10이다. 명시한 세-member root 묶음의
  선언 이름·root 참조·계약 hash 외 C# bytes·node ID/원래 node 인자/연결/값/profile과
  다른 파일은 같다. 변경 없는 재저장은 dirty 0개여도 완전한 묶음과 receipt를 복원한다.
- 기존 반환 핀 표시 순서·export 생성/삭제/재배정/값·root 반환·entry/source/name/route API를
  양쪽에서 새로 회귀했다. CRLF에서는 기존 export 재배정의 실패/새 선택/cold/Undo/Confirm/
  실행 UI와 property 관찰·부분 Review·경로/원본 위조·expected-missing·readonly CAS를 확인했다.
- 새 Windows 교차 패키지의 구성/무결성과 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  CRC·전체 SHA/모드로 완전히 복원한 엔진에서 쓰기 실패/새 이름 재시도와 늦은 이름 UI를
  Confirm/실행/cold까지 확인했다. 성공·반복·실패·예외의 증거 보존/복원·자식 종료·
  소유 임시물 cleanup도 통과했다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/0b72803a1ebb4c448885e1f33eb68919.json`

개발 증거 SHA `ed422564f80efcc70342bfc18a6a9144a7a78e71d1226755eca54aba5d1a6caf`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/26690d44df094c70a8e58545ba4343ad.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/26690d44df094c70a8e58545ba4343ad.zip`

SHA256 `62a0279bf0e2670046bfa663d6ba6465675ba57f3ced7a3cd9c270a15f74efd2` (3.01MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `68e76080d342ca634b95265cc74c875c9de68d89`, `b2eb727d092627398527cd89c61bb70c31ca0d15c6d3f318a85c79c9516d70e3.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `d1fc2cc9d4e3079cbcd062e916cec6672f8131d78e0b0a98202b6d8cba2b41a7`.

- rollback: 출처 `9902f18f6555b7532f0955d5bd0b9dfe6be0b158`, `0879d8252fb0a0dfd98b012aede27c65921b3f05e988335e77b795432935b45a.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `8b66666d4155848c95f1231fa70de51eb29ab77a74955b5f6a542b3a4ca616b5`.

최신은 최종 동결 코드와 일치한다. 롤백·증거·원본을 보존하고 archive 검증과 자식 종료 뒤
이번 실행이 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 추가 삭제하지 않았다.
단계 표본 최소 여유 1580.83MiB, 최대 cgroup 메모리 4697.99MiB다.
최종 실행 순증가 4.35MiB, 개발 시작부터 보관 확인까지
6.05MiB, 문서 마감 전 여유 1576.55MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 root 정의·혼합 계약 Save·직접 배치는 원본 요구/현재 지원과 대조할 별도 점검 후보다.
조합마다 새 필수 요구를 추가하지 않으며 완료 M11/M12/M4를 다시 열지 않는다.
나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 고정 수용 표에 남긴다.
검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·
모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다.
live AI·자격증명·유료 호출·새 권한/외부 접근은 사용하지 않았다.
