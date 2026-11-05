# v666 root 반환 핀 표시 순서 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `9902f18f6555b7532f0955d5bd0b9dfe6be0b158`다. 이후 마감 commit은 문서와
수용 표만 바꾼다. [지원 경계](V2_ROOT_OUTPUT_ORDER_RECOVERY.md)와
[정확한 delta](v666-root-output-order-recovery-delta.json)를 따른다.

## 재현·수정

게시본 `b5c31ad7ae1b27128e4a0ad0652253a324e17a34`에서 기존 Alt+화살표 UI로
반환 핀을 이동하고 checkpoint 쓰기를 실패시켰다. live 순서는 바뀌고 개인 입력은
사라졌지만 checkpoint·물리 원본·C#은 같았다. cold 후 원래 순서만 복원됐다.
원래 실제 .NET 실행과 실패 화면·입력·traffic·cold 증거를 개발 record에 보관한다.

out 둘의 상대 순서·이름·타입·mode와 비void 반환 타입을 그대로 유지하는 반환 핀의
표시 위치만 원자 후보·checkpoint CAS·receipt·공유 Undo/Redo에 연결했다.
기존 root 계약 검증을 후보에서 재사용하며 성공한 checkpoint 뒤에 live를 반영한다.
미반영·동일 checkpoint·전체 source proof가 확인된 경우에만 같은 계약의 새 순서를
명시 재시도한다. 실패 뒤 개인 Undo로 취소한 선택을 자동 재적용하지 않는다.
응답 유실은 receipt만 회수하고, 적용 뒤 늦은 순서는 별도 Save로 남긴다.
무관한 새 값이 섞인 미반영 계획은 모두 보존하며 legacy live 경로로 우회하지 않는다.
변경 없는 Save도 receipt와 기존 세-member root 묶음을 함께 보관한다.

원본 C# bytes·실제 `(out int left,out int right) -> int` 호출 계약·ID·타입·값·연결·
profile·부모/외부 원본·권한·Review→Confirm·최종 CAS 및 기존 UI/안내/레이아웃을
보존한다. 다른 root 계약 변경이나 공개 override 계약 변경을 허용하는 단위가 아니다.

## 최종 신규 검사

독립 LF 25·CRLF 25·새 패키지/전체 복원/실패 수명관리
8, **총 58단계: 신규 58·재사용 0** 통과.
Git 객체·실제 줄바꿈·엔진 캐시·NuGet/home을 분리했다. 개발 결과는 최종 수에 합산하지 않는다.
초기 엔진 컴파일의 LINQ Count 호출을 고쳤고, API 거절 fixture가 공유 순서 배열을 바꾸어
후속 정상 요청을 오염시키던 문제는 입력별 깊은 복사로 고쳤다. 개인 Undo 이력이 cold를
넘어 보관된다는 fixture 가정도 고쳐, 실패 직후 Undo/Redo와 수정 순서 cold 복원을 나눴다.
임시 진단 엔진의 양성
저장과 오류 기록을 보관하고, 최종 검사는 진단 출력이 없는 제품으로 수행했다.

- 정확한 제품 delta·canonical JS metadata·문법·기존 완료 문구/레이아웃과 실제 공유
  history inverse/CAS/restart/owner 및 표시명 native 회귀를 확인했다.
- stale checkpoint·위조 source proof·잘못된 origin/소유/private frame·여분 필드·
  다른 계약/본문 혼합·인자 순서/이름/타입/mode/반환 타입 변경·비identity remap·
  중복/누락/없는/nonstring 출력 ID·out 상대 순서 변경을 거절했다.
  정상 후보·같은 요청 멱등 회수·공유 history·cold·위조 receipt 거절을 확인했다.
- 실제 Alt+화살표·개인 Undo/Redo·cold와 checkpoint 쓰기 실패 후 입력/live/원본 보존,
  실패 뒤 Undo 취소가 재적용되지 않음·Redo/수정 순서의 cold 명시 재시도를 확인했다.
  동료 checkpoint 충돌과 무관한 새 값 혼합은 cold/retry 후에도 모두 보존하며 거절했다.
- 응답 유실은 이전 순서를 재전송하지 않고 receipt만 회수했다. 적용 후 늦은 순서는
  새 root 계획만 전송하며 이전 순서와 섞이지 않았다. 공유 Undo/Redo/cold도 확인했다.
- Review 취소·검토 뒤 물리 graph 충돌 거절·새 Review/Confirm·실제 .NET 실행·cold를
  확인했다. 원래/선택/수정 순서 모두 `body` 다음 `17:23:10`, 반환 10이다.
  물리 graph의 outputOrder 외 C# bytes·원래 계약/ID/핀/값/연결/profile과 다른 파일은 같다.
  Confirm 후 변경 없는 재저장은 dirty 0개여도 세-member root 묶음과 receipt를 복원한다.
- 기존 export 생성/삭제/재배정/값·root 반환·entry/source/name/route API를 양쪽에서
  새로 회귀했다. CRLF에서는 기존 export 재배정 실패/새 선택/cold/Undo/Confirm/실행 UI와
  property 관찰·부분 Review·경로/원본 위조·expected-missing·readonly CAS를 확인했다.
- 새 Windows 교차 패키지의 구성/무결성과 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  CRC·전체 SHA/모드로 완전히 복원한 엔진에서 쓰기 실패/새 순서 재시도와 늦은 순서 UI를
  Confirm/실행/cold까지 확인했다. 성공·반복·실패·예외의 증거 보존/복원·자식 종료·
  소유 임시물 cleanup도 통과했다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/b7e62c7786c040c392545e5386a418cd.json`

개발 증거 SHA `0100ae39a4c225bf772d1700ca761fa524524b974e5c15f48497d634ce826a3d`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/e076a2677db34ec1affd97a11693bff1.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/e076a2677db34ec1affd97a11693bff1.zip`

SHA256 `0af6be9a688c5ef749d2c91a5b7b80429fd251e5b8c2ced15238d1b065908f84` (2.78MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `9902f18f6555b7532f0955d5bd0b9dfe6be0b158`, `0879d8252fb0a0dfd98b012aede27c65921b3f05e988335e77b795432935b45a.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `8b66666d4155848c95f1231fa70de51eb29ab77a74955b5f6a542b3a4ca616b5`.

- rollback: 출처 `3473213dfa9df7b2813d09f2e3f5b3cec03815c4`, `310273bdde2e5a0b0d798e7594d1335ccf155bd4c2c50977aaec88986e74a1d4.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `114e70224c43a19427e0c7c1225b7de6585223338301a4facf6e984f19086856`.

최신은 최종 동결 코드와 일치한다. 롤백·증거·원본을 보존하고 archive 검증과 자식 종료 뒤
이번 실행이 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 추가 삭제하지 않았다.
단계 표본 최소 여유 1586.66MiB, 최대 cgroup 메모리 4669.54MiB다.
최종 실행 순증가 4.05MiB, 개발 시작부터 보관 확인까지
5.75MiB, 문서 마감 전 여유 1582.67MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 root 핀 정의/실제 ABI 편집·혼합 계약 Save·직접 배치는 원본 요구/현재 지원과 대조할
별도 점검 후보다. 조합마다 새 필수 요구를 추가하지 않는다. 완료 M11/M12/M4를 다시
열지 않는다. 나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 고정 수용 표에 남긴다.
검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·
모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다.
live AI·자격증명·유료 호출·새 권한/외부 접근은 사용하지 않았다.
