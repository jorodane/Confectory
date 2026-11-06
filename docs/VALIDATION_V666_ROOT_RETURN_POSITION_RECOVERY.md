# V666 root 반환 핀 표시 위치 저장 복구 검증

제품·검사·도구·delta 동결은 `e4c39322b2730ef37528838aba905a68b2d8932e`이다. 이후 마감 commit은 문서만 바꾼다.
[닫힌 지원 범위](V2_ROOT_RETURN_POSITION_RECOVERY.md)와
[정확한 delta](v666-root-return-position-recovery-delta.json)를 따른다.

## 실제 결함과 수정

게시본 `ddd2c7b1a058f4627a182dc323ce854d0b02a3b7`의 원래 출력 이동 UI에서 값 입력
하나·out 셋·int 반환을 가진 root의 반환 핀만 두 칸 옮겼다. 실제 호출은 기존대로
17·23·29를 out으로 받고 10을 반환한다. checkpoint 쓰기 실패 뒤 개인 입력 하나가
사라지고 live에만 선택이 남았으며 cold에서 이전 위치가 복원됐다. checkpoint·signature·
C#와 caller bytes는 같았다. baseline JSON SHA는
`0ed90cebac0054845849d99615d2de30273f664417ae21ff55f78420fe0893ff`다.

기존 1–64개 전체 매개변수의 이름·타입·mode·위치, 반환 타입과 모든 인자의 identity
remap이 동일한 반환 표시 이동을 기존 원자 후보/receipt에 연결했다. out 하나 이상과
nonvoid 반환이 필요하며, 모든 out과 return을 정확히 한 번 포함하고 out 상대 순서를
보존해야 한다. 기존 유효한 value/ref 입력을 변경하지 않는다. 새로운 ref/out 의미나
UI를 추가하지 않는다. 현재 UI의 out끼리 이동은 args도 바꾸므로 실제 ABI 변경이며
계속 거절한다. 이 동작을 새 필수 migration으로 늘리지 않는다.

writer·receipt 형식·root 그룹/이력 planner·권한·Review→Confirm·최종 CAS·레이아웃은
변경하지 않았다. 다른 계약/이름/타입/mode/순서/추가삭제, private/copy/slot/async/실행
분기/native 문맥과 공유 root의 기존 보호, 공개 override 입출력 계약을 유지했다.
원래 C#·caller bytes·노드 ID·값·연결·profile·본문·설명은 그대로다.

## 최종 검증

독립 LF 17·CRLF 17·새 교차 패키지/전체 복원/실패 수명관리
8, **총 42단계(신규 42·재사용 0)** 통과했다.
개발 결과는 이 수에 합산하지 않는다. Git 객체·실제 EOL·NuGet/home·엔진 캐시를 분리했다.

- 정확한 세 runtime 경로와 canonical 자산 SHA/크기, 실제 JS guard·root/source proof,
  기존 값 입력 이름·같은 노드 텍스트 복구, 공유 이력/컴파일 probe와 JS 문법을 확인했다.
  1·2·3·64개 out, 기존 value/ref 혼합의 불변 args와 첫/중간/마지막 반환 위치는 실제
  guard로 검사했다. 실제 API/UI 실행 fixture는 value 하나·out 셋이다. 모든 ref 조합의
  native 실행을 검사했다고 주장하지 않는다.
- API에서 stale checkpoint·변조된 전체 원본 proof·잘못된 origin·미관측 owner/private,
  새 public 출력·본문·mode·이름·타입·반환/인자 순서/개수 변경, 누락/추가/잘못된 remap,
  중복/누락/알 수 없는/비문자 출력, out 상대 순서 변경과 다른 편집 혼합을 거절했다.
  쓰기 실패에서 live/checkpoint/물리 원본을 보존하며 정확한 baseline만 재시도 대상으로
  인정했다. 정상 적용·멱등성·전체 세 멤버 root 묶음·cold receipt와 변조 receipt 거절을 확인했다.
- 실제 출력 이동 UI의 단계별 local Undo/Redo와 private 입력 cold 복원, 쓰기 실패 뒤
  Undo 취소/빈 Save/Redo/수정 위치/cold 재시도를 확인했다. 무관한 표시명이 더해지면
  두 입력과 실패한 시도를 보존하며 legacy live 변경으로 우회하지 않았다.
- 동료 root checkpoint의 저장 충돌은 재시작/재시도 뒤에도 덮어쓰지 않았다. 응답 유실은
  확정 receipt만 회수하고 중복 authorBatch를 만들지 않았다. 응답 보류 중 선택한 새 위치는
  이전 응답으로 지우지 않고 cold 뒤 별도 저장했다.
- 공유 root Undo/Redo/cold는 함수·구현·graph를 함께 보관했다. Review 취소·Review 후
  물리 graph 변경의 최종 CAS 거절·새 Review→Confirm·실제 Linux .NET 실행·최종 cold를
  확인했다. 기존 `body` 및 `17:23:29:10` 출력과 exit 10을 유지하며 물리 변경은 graph의
  반환 표시 위치뿐이었다. 반복 no-op 위치 Save와 뒤이은 unchanged 일반 C# Save에서도
  zero-dirty 전체 root 묶음과 receipt를 cold 복원했다.
- 이전 out 둘의 반환 표시 위치 및 여러 값 입력 이름 API, 이전 반환 위치/같은 동작
  텍스트의 늦은 입력 UI를 현재 엔진에서 새로 회귀했다. 다른 완료 기능의 기록은 해당
  기존 증거에 남기며 신규 단계로 합산하지 않는다.
- 새 Windows 교차 패키지의 구조/무결성과 패키지 엔진의 정상/응답 유실 UI를 확인했다.
  전체 SHA·압축 CRC·권한 모드로 모두 복원한 엔진에서 쓰기 실패 복구와 늦은 위치의
  Confirm/실행/cold를 확인했다. 성공/반복/실패/예외 수명관리·증거 보존·자식 종료·소유
  임시물 정리를 검증했다. 실제 Windows apphost/WebView2·모바일 실행은 아니다.

## 개발 검사 수정과 증거

첫 late UI는 반환 핀을 두 칸 이동한 뒤 Undo 한 번으로 모두 취소된다고 가정했다.
실제 실패 입력은 정상적인 한 칸 중간 위치였고 제품은 단계별 이력을 보존했다.
검사만 원래 이동 횟수만큼 Undo/Redo하고 각 끝 위치를 대조하도록 수정했다. 같은 제품의
late/normal UI가 통과했고 해당 실패·중간 입력·화면·traffic은 별도 개발 증거에 보존했다.
제품 실패나 최종 통과 수로 합산하지 않았다.

첫 최종 LF 실행의 13단계는 통과했지만 쓰기 실패 Undo 검사가 보존용 author-attempt
기록까지 사라져야 한다고 가정해 중단됐다. 실패 입력에는 typed 편집이 없이 immutable
재시도 기록만 남아 있었다. 제품은 바꾸지 않고 취소 위치·원본/체크포인트·기록 보존을
대조하고 빈 Save에 authorBatch가 없어야 한다고 검사했다. 해당 실패 증거를 보존한 뒤
검사 수정 후 최종 전 단계를 새로 실행했다. 첫 13단계를 최종 수에 중복 합산하지 않았다.

첫 최종 시도 record `/workspace/artifacts/v536-verification-managed/runs/18ae5f99826b4597be5ac9b85d2ea582.json`, 증거 SHA `ddd636e694cd807c80d6ec15d082ee6da8ea58f4fbe84f4375ce598905a26049`.

개발 record `/workspace/artifacts/v536-verification-managed/runs/a89eea490b6a4af78a932d6e66bd6447.json`

개발 증거 SHA `2cb14a214fc1a6d144e9a2d37b5a8259ee3f5ea51e1f3ca02e4476d3e32651e8`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/acd6ad4382a241e5abd50189c3a8b279.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/acd6ad4382a241e5abd50189c3a8b279.zip`

SHA `bc4158db32a5577cafcdbad285f3d9cd920ebfa342927493f1895578134617d4` (2.47MiB).

## 보관·공간·남은 범위

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `e4c39322b2730ef37528838aba905a68b2d8932e`, `fe70b41845932113a00dbb88ab47fc4a5bd46f10cbbb6455842b68a4b2d2fb68.zip`, 49.14MiB, 파일 2381·디렉터리 147, 전체 manifest `63b9830db2f34ee0e9e550ac9d759ca789f8e6e4bc5bf8168d6ed6015268f061`.
- rollback: 출처 `7cf9aaa875e9f038a8b316cc1716087e3a12b6ee`, `3c3fa47440113d1aad7cdb4337043d6b007aa597637a3d4fbf474847ee68663f.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `7cf513eb2e8228b9f8dfcbc9e3fb4f3685bcb87a9c6d86014b8cc2569a4d4f16`.

최신은 동결 코드와 같고 이전 정상 최신본을 rollback으로 보관했다. 전체 SHA/manifest와
복원 가능성을 확인한 뒤 이번 실행 소유 임시물만 승인 수명대로 정리했다. 다른 과거 자료·
원본·로그·프로필·SDK·캐시 삭제나 보관 정책 변경은 없다.

최종 단계 표본 최소 디스크 여유 1542.09MiB, 최대 cgroup 메모리
4732.40MiB. 최종 실행 순증가 3.48MiB, 개발 시작부터
보관 확인까지 5.52MiB, 문서 마감 전 여유 1538.65MiB다.
다음 단위의 고정 증가량을 보장하지 않는다.

다른 root 정의·혼합 저장·직접 배치는 재현 기반 점검 후보이며 조합별 새 필수 항목을
늘리지 않는다. 완료 M11/M12/M4를 다시 열지 않는다. 고정 V2 후속·V3–V9·팩/backend·
종류 호환성 결정과 실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·
전체 UI·Space 전달은 별도 잔여다. 3D/권한 별도 팩·이동 연출/실행 분리·동기 caller의
명시 async 전환 원칙을 유지했다. live AI·실제 계정/키·유료 호출·새 외부 접근은 없다.
main은 사용자 검토/병합용으로 보존한다.
