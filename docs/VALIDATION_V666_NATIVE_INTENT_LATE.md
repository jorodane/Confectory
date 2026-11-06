# V666 일반 Blueprint Apply 중 새 설명 입력 보존 검증

제품·검사·도구 동결 `1ee505504ff79c29daa099b19db00fcdd9273c72` 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V2_NATIVE_INTENT_LATE.md)·[정확한 delta](v666-native-intent-late-delta.json)를 따른다.

## 실제 재현·변경

고정 v666의 설명 편집과 기존 일반 Blueprint ‘적용’의 private 입력/공유 초안 경계를
유지한다. 게시 `493a18a4`와 제품 코드가 같은 패키지 `bd4d65d0`를 전체 SHA/manifest로
복원했다. 생성 프로젝트의 실제 Linux managed engine/Chromium에서 설명 A 적용이
실제 공유 초안에 반영된 성공 응답을 보류했다. 원래 관측 값으로 돌아오는 input
callback을 전달하고 응답을 풀자, 새 private 입력이 사라지고 A로 덮였다.

처리 중 필드 비활성화는 유지한다. 이 검사는 대기 중인 input/선택 callback을 직접
전달한 통제 검사이며 비활성 UI에서 실제 키보드·IME 입력이 가능하다는 뜻이 아니다.
공통 `bindInput`은 현재 관측 데이터 객체에 연결한 WeakMap/Set으로 Apply 시도를
기억한다. 같은 관측의 컨트롤 remount에도 시도를 유지하고 새 source 관측/프로세스에는
그 상태를 이식하지 않는다. 시도 후 원래 값으로 돌아온 새 입력도 보존하며 성공한
응답은 정확히 제출했던 객체만 정리한다. 폐기된 컨트롤/이전 source·프로젝트의
input callback은 현재 입력을 덮지 않는다.

제품 delta는 이 입력 추적·정리·현재 컨트롤 확인과 canonical 리소스 pin뿐이다.
RPC/변경 재시도·basis/hash·권한·원문/C#·ID/IO/핀/연결·부모/외부 원본·source 저장·
Review→Confirm·최종 CAS·Undo·UI 잠금/레이아웃은 미변경이다. 새 입력을 자동 Apply/
rebase하거나 실제 source 취소/되돌리기로 해석하지 않는다.

## 최종 검사

**31단계(신규 31·재사용 0)**, 모두 exit 0이다.
독립 LF 12·CRLF 12·새 패키지/전체 복원/실패 수명관리
7로 구성한다. Git 객체·EOL·NuGet/home·빈 엔진 캐시를
독립시켰다. 초기 재현·실패와 과거 통과는 이 합계에 넣지 않는다.

- 실제 설명 Apply의 결과 보류 중 원래 관측 값으로 돌아온 새 입력과 같은 문자열 ABA를
  보존했다. 같은 source 선택 callback으로 컨트롤을 remount해도 비활성화를 유지했고,
  이전 disconnected input callback은 새 private 입력을 바꾸지 않았다. 보류한 첫 Apply는
  제출한 설명 A만 한 번 반영했고 물리 fixture source는 byte 단위로 보존됐다.
- 실제 반영 후 update 결과만 `transport-interrupted`로 바꿔 전달한 경우에도 새 입력을
  유지하고 변경을 자동 재시도하지 않았다. 이전 basis로 새 입력을 Apply하면 기존 CAS가
  거절했다. 사용자가 현재 source를 읽고 명시적으로 기준 재검토한 뒤에만 새 값이 적용됐다.
- 명시 재검토/Apply 뒤 실제 공유 Undo/Redo에서 A/새 값이 왕복했다. private 입력의
  명시 Reset도 기존 의미를 유지했다. C# bytes·ID/계약/원래 source는 미변경이었다.
- private cold는 보존한 문자열을 복원했으나 basis와 Apply 시도 상태를 복원하지 않았다.
  현재 원본 읽기 후에도 명시 기준 재검토 전 Apply는 거절되고 입력을 유지했다. 이 cold는
  보류 응답 처리 후 수행했으며 실행 중 강제 프로세스 중단을 시험한 것으로 표시하지 않는다.
- 일반 Blueprint의 늦은 read 성공/닫기·명시 재열기·300%/개인 입력·cold, 기존 stale
  읽기 한도/명시 retry·팝오버 수명의 관련 실제 엔진 회귀도 수행했다. 다른 필드/타입/연결의
  가능한 모든 조합이나 source Confirm 충돌을 새로 검증한 것으로 계상하지 않는다.
- 새 Windows 교차 패키지 구조/무결성과 packaged managed engine에서 정상 입력 보존을
  확인했다. 전체 SHA/CRC/권한 복원본에서 응답 유실/명시 재검토·Undo/Redo와 private cold를
  다시 확인했다. 실제 Windows apphost/WebView2·모바일 실행은 아니다.
- 기존 소유 임시물의 성공/반복 성공·실패/예외·자식 종료·증거 보존/정리가 통과했다.
  최신/롤백·증거는 지속 보관했고 다른 과거 자료나 보관 정책을 변경하지 않았다.

첫 LF의 remount fixture는 비활성 버튼에 `click()`을 호출해 callback이 실행되지 않아
중단됐다. 제품 잠금은 정상 동작했으며 대기 중인 선택 callback을 직접 전달하도록
fixture만 수정했다. 제품 코드 변경은 없고 앞선 임시 빌드는 승인된 실패 수명으로
정리됐다. 최종 검사/패키지는 새 독립 빌드이며 앞선 통과를 재사용하지 않는다.
실패 record `/workspace/artifacts/v536-verification-managed/runs/7d2cfec4785f489a951fd65f4e6fc132.json`, 증거 SHA `b4f03d7042cc817e78ba05c78422b9b8e88cf08ac859aadcddda2f5a4313270a`.

재현 record `/workspace/artifacts/v536-verification-managed/runs/390a0761acef4a8eb5e1bcce389c7ef0.json`, 증거 SHA `640ca9779cf186ed9aa5d39fd875672fc4c5e1b773bbc58a0224f761574734e8`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/d287c9d5491b4921a2b02dd88eff8409.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/d287c9d5491b4921a2b02dd88eff8409.zip`

SHA `ee98881adaa29321fcf36c09a64e9809dddebf9ceae4949ca7b2b6fe7d7b6dd3` (2.13MiB).

## 보관·공간·고정 잔여

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `1ee505504ff79c29daa099b19db00fcdd9273c72`, `749a721162ae62744e23bf1f30d2ff77e6f1656e70e425120d52e50e831a0474.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `e4bbe7550860f5010a344489354d3cf0651ef62a8c7032c19346c4b08ca6bc74`.

- rollback: `bd4d65d0af61b2988948b6a2dbd948b4f66f2963`, `2dc5f5a6de8f9c335e6cfe57f944c4e994436ca1a72e429f12a55f27e393f6e8.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `39e59a59cc355b280e4b44adca74fa7befe449eb17d1848da94c37701ff8d49b`.


최신/롤백·재현/실패/최종 증거의 전체 SHA/manifest를 재확인했다. 기존 승인된 원자
두 세대 승격과 실행별 소유 임시물 수명만 사용했다. final RAM root는 제거됐다.
표본 최소 디스크 여유 1526.14MiB, 최대 cgroup 메모리 4501.68MiB.
최종 관리 실행 순증가 3.02MiB, 단위 시작부터 보관 확인까지
4.00MiB, 현재 여유 1523.18MiB. 이후 사용량의
보장값이 아니며 기존 144MiB 추가 예산/64MiB 안전 여유를 유지했다.

이번 마감은 일반 설명 Apply의 늦은 callback 보존이다. 공통 helper가 쓰이는 모든
인수/연결·copy/독립 창 조합을 새 필수 목록으로 늘리지 않는다. M11/M12/M4는 기존
실행 마감 경계를 유지한다. V2 다른 노출 안내, V3–V7 실제 팩/상태/권한/자산 backend,
V8 실제 영상/오디오 provider, V9 실제 신원/가시성과 종류 C# 표현/사용 중 삭제 대응은
기존 잔여다. Run은 여전히 `surfaceSupported=false`, `fpsSupported=false`다.
DPI/실제 IME·Windows/WebView2·모바일·전체 UI·Library/Space 전달은 미검증이며
현재 통제 callback·교차 패키지 검사로 대체하지 않는다. main은 사용자가 병합한다.
