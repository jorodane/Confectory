# V666 일반 Blueprint 읽기 중 창 닫기 검증

제품·검사·도구 동결 `bd4d65d0af61b2988948b6a2dbd948b4f66f2963` 이후 마감 commit은 문서만 바꾼다.
[지원 범위](V1_NATIVE_READ_CLOSE.md)·[정확한 delta](v666-native-read-close-delta.json)를 따른다.

## 원래 흐름·실제 재현·변경

고정 v666의 일반 창 닫기·Blueprint 진입과 native의 숨긴 창 수명을 보존한다.
게시 `54347f19`와 제품 코드가 같은 보관 패키지 `5deb5f28`를 전체 SHA/manifest로
복원했다. 생성 프로젝트의 실제 Linux managed engine/Chromium에서 ‘현재 원본 읽기’의
성공 update 응답을 보류하고 창을 닫았다. 응답을 전달하니 창이 다시 열렸다. 지연은
로컬 route 주입이며 실제 네트워크 장애나 기기 검증으로 표시하지 않는다.

읽기 시작 때 창이 표시돼 있었는지 기억하고, 결과 표시 직전 같은 창이 숨겨져 있으면
reveal/show/focus하지 않는다. 이미 실행된 readonly 관측을 취소하거나 Shared source를
롤백하지 않는다. 시작부터 숨긴 창을 사용자가 명시적으로 다시 여는 흐름은 허용한다.
기존 프로젝트/객체 교체·연결 해제 경계, API 요청/읽기 retry·basis/hash·source 저장·
C# bytes·ID/IO/핀/연결·부모/외부 원본·권한·Review→Confirm·최종 CAS·Undo·private 입력·
배율/카메라·레이아웃은 바꾸지 않는다. 제품 delta는 일반 Blueprint 두 구간과 해당
canonical 리소스 크기/SHA뿐이며 최종 LF/CRLF의 정확한 source delta로 감사했다.

## 최종 결과

**총 29단계(신규 29·재사용 0)**, 모두 exit 0이다.
독립 LF 11·CRLF 11·새 패키지/전체 복원/실패 수명관리
7로 구성한다. Git 객체·NuGet/home·빈 엔진 캐시를
독립시켰다. 초기 재현과 기존 검증은 최종 합계에 넣지 않는다.

- 실제 성공 읽기 결과를 보류한 상태에서 창을 닫으면 결과 전달 뒤에도 닫혀 있었다.
  이를 세 번 반복하고 매번 사용자가 숨긴 창을 명시적으로 다시 열어 현재 원본과 같은
  300% 개인 화면을 확인했다. 개인 입력의 정확한 문자열과 fixture 물리 source의 byte를 각각 보존했다.
- 실제 read가 실행된 뒤 update의 해당 결과를 `transport-interrupted`로 바꾼 응답도
  닫힌 창을 열거나 오류 placeholder로 덮지 않았다. 다음 명시 열기는 현재 source를
  정상 관측했다. 성공/실패를 섞은 반복에서도 변경/Save/Confirm/실행을 호출하지 않았다.
- cold는 private 입력/배치/300%만 복원하고 이전 관측을 편집 권한으로 복원하지 않았다.
  편집 화면은 명시적인 ‘현재 원본 읽기’ 뒤에만 다시 연결됐다. 이 cold는 보류 응답을
  처리한 후 수행했으며, read 진행 중 강제 프로세스 중단 검사로 표시하지 않는다.
- 기존 일반 Blueprint의 두 번 stale 읽기 재관측·세 번 한도/명시 재시도, 팝오버 반복/
  취소·retired slider/preset/fit/blur/Enter/Escape·cold·창 종료도 관련 실제 엔진 회귀로
  실행했다. 소유권·연결·layout 기록을 허용/추가 데이터 권한으로 사용하지 않는다.
- 새 Windows 교차 패키지의 구조·무결성을 확인하고 packaged managed engine에서
  정상 늦은 닫기를 실행했다. 전체 SHA/CRC/권한 복원본에서 실패 응답·명시 재열기/
  cold와 기존 일반 Blueprint 읽기/배율 회귀가 다시 통과했다. 실제 Windows 실행은 아니다.
- 기존 소유 임시물의 성공/반복 성공·실패/예외·자식 종료·증거 보존/정리가 통과했다.
  source 거래를 새로 만들지 않아 source CAS 충돌을 새로 시험한 것으로 계상하지 않는다.

재현 record `/workspace/artifacts/v536-verification-managed/runs/66e864402c514491bef980eaaddf34e7.json`, 증거 SHA `9861382b01b74919ef98b2a537f33dabd8d32366e7530b8da5d4181525801033`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/5e6014c6fcad49a4ab4097904074e643.json`

증거 `/workspace/artifacts/v536-verification-managed/runs/5e6014c6fcad49a4ab4097904074e643.zip`

SHA `0489a010e11ff1d1891549aee28c866bf4f7dda221cc046a23520badaa891d5c` (1.71MiB).

## 보관·공간·남은 경계

Index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: `bd4d65d0af61b2988948b6a2dbd948b4f66f2963`, `2dc5f5a6de8f9c335e6cfe57f944c4e994436ca1a72e429f12a55f27e393f6e8.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `39e59a59cc355b280e4b44adca74fa7befe449eb17d1848da94c37701ff8d49b`.

- rollback: `5deb5f28311aa275570dffd2f3c301b270c82b32`, `a2a9a5c37e230c5a587e73c9b2fbe96038bd42f23e0890b1b75c9b98b2a642a3.zip`, 49.15MiB, 파일 2386·디렉터리 147, manifest `fa3bf332426ad753cee09db87ef8c81d7d20ebbaa8a307561609f995ac6c5b36`.


최신/롤백·재현/최종 증거의 전체 SHA/manifest를 재확인했다. 기존 승인된 원자 승격/
두 세대 보관과 실행별 소유 임시물 수명만 사용했다. final RAM root는 제거됐다.
표본 최소 디스크 여유 1529.80MiB, 최대 cgroup 메모리 4474.38MiB.
최종 관리 실행의 순증가 2.57MiB, 단위 시작부터 보관 확인까지
3.11MiB, 현재 여유 1527.29MiB. 다음 실행의
보장값이 아니며 기존 144MiB 추가 예산/64MiB 안전 여유를 낮추지 않았다.

마감한 것은 일반 Blueprint readonly 완료의 닫기 보호다. 실행 중인 프로젝트 작업이나
네이티브 read 자체를 취소하는 기능, source 재배정/새 정책을 추가하지 않았다.
독립 정보 창의 모든 배율 문맥·DPI/IME와 실제 Windows/WebView2·모바일·전체 UI·
Library/Space 전달은 별도 미검증이다. M11/M12/M4를 새 조합으로 늘리지 않는다.
V2 다른 노출 안내, V3–V7 실제 팩/상태/권한/자산 backend, V8 실제 영상/오디오 provider,
V9 실제 신원/가시성 및 기존 종류 C# 표현/사용 중 삭제 대응 경계를 유지한다.
Run의 실제 capability는 `surfaceSupported=false`, `fpsSupported=false`이며 frame-control
IPC를 영상·오디오 성공으로 쓰지 않는다. 새 권한/접근·과금·자료 정리/보관정책 변경은 없다.
