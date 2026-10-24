# v536 I5-3: 구현 삭제 후 새 구현 작성

직접 소유 정보 함수의 선언·핀을 남기고 구현만 보관한 뒤, 기존 `직접 작성`에서 새 구현을 만들 수 있게 했다. I5-2의 공유·상속·복사 구현 삭제 수명을 완료했다는 뜻은 아니다. 고정 여섯 항목 중 I5-1/I5-4의 지원 경로는 유지하고 I5-2/I5-5/I5-6는 후속으로 남긴다.

## 재현과 수정

실제 격리 엔진에서 구현만 삭제한 뒤 `createFeature`가 거절되는 것을 재현했다. 삭제는 복구를 위해 기존 파일을 남기는데 생성 경로가 같은 `<function>BlueprintBody` ID/파일명을 다시 사용했다. 기존 destination 보호가 덮어쓰기를 막은 결과였다.

첫 생성의 기존 ID와 전역 unpublished 함수 경로는 유지한다. 정보 구현을 생성할 때 기존 unit·파일·디렉터리 또는 archive가 이전 ID를 예약했다면 새 `Impl_<GUID>` 소유 구현과 독립 graph/node를 만든다. 미확정 본문은 물리 파일이 없어도 archive 기록이 그 ID를 예약한다. 원래 함수 identity와 과거 archive는 바꾸지 않는다. 기존 destination 소유권·중복/링크 검사, 원본 baseline, checkpoint CAS, 단일 후보 쓰기 및 별도 compiler Review/Confirm을 그대로 사용한다.

화면은 고정 이름을 추측하지 않고 서버가 반환한 함수/owner/구현/graph 일치를 확인한다. 생성 성공 응답이 유실되면 같은 현재 함수·정보의 유효한 provider를 조회해 연다. 생성 요청을 재전송해 두 번째 본문을 만들지 않는다. 프로젝트·창 수명 가드는 유지한다.

새 provider가 존재하는 동안 이전 archive 복구는 거절한다. 새 본문을 지우거나 원래 보관본을 덮는 자동 복구는 없다. C# 팝오버 취소와 Review 취소는 기존 의미이며, 이미 보관된 새 구현을 전혀 생성하지 않은 상태로 소급하는 새 취소 계약은 추가하지 않았다.

## 검증

사용자 계정·프로젝트·유료 추론을 사용하지 않았다. 로그와 격리 자료는 `/workspace/scratch/v536-information-reimplementation`에 남긴다. 같은 소스가 실제 달라지면 projection 조회도 거절될 수 있어, 충돌 검사에서는 정확한 live 정보 원문·디스크 checkpoint·동료 source bytes로 전체 미적용을 확인한다.

| 검사 | 결과 |
|---|---|
| Linux engine-1 | warnings 0 / stderr 0 |
| 실제 API, 이전 archive pending / confirmed | 각각 4 PASS: 독립 identity·이전 복구 차단·cold/중복 생성 거절·본문/Review/Confirm |
| 실제 API, checkpoint 쓰기 실패 / 함수 source 경합 | 각각 5 / 1 PASS: live와 디스크 전체 미적용·기존 원문 보존·명시적 재시도 |
| 실제 API, 이전 본문이 미확정인 archive | 4 PASS: 실제 파일 없이도 기존 archive의 ID와 본문 snapshot을 예약하며 새 identity·저장·cold·Confirm을 분리 |
| 실제 기본 창 UI | 4 PASS: 원본 삭제 취소/Undo/Redo·새 편집기·C# 취소/미저장 cold/저장·Review 취소/Confirm/cold |
| 실제 독립 창 UI, 생성 응답 유실 | 4 PASS: 성공 응답 한 번 유실 후 조회 복구, create 요청 1회, 이후 같은 저장/취소/cold/Confirm |
| 실제 기본 창 UI, 생성 쓰기 실패 | 5 PASS: 실패 미적용과 명시 재시도, 이후 같은 저장/취소/cold/Confirm |
| 기존 첫 본문 작성 UI | 5 PASS: 기존 고정 첫 identity·빈 본문 cold·C# 취소·private 입력/창 복원·Review/Confirm 호환 |
| 깨끗한 checkout의 확정 archive 독립 창 UI / 실제 source 경합 API | 각각 4 / 1 PASS: 확정된 삭제 뒤 새 생성·본문 취소/미저장 cold/저장·새 Review/Confirm·원본 보존 및 실제 변경 전체 거절 |

처음 작성한 fixture의 archive 요약 키와 source 경합 후 projection 가정을 고쳤다. 생성 응답 유실 주입은 동일 request의 첫 성공 응답만 제거하도록 했다. 모달 종료 직후에는 임의 대기 대신 실제 idle 상태를 기다린다. 여러 Chromium을 동시 실행하다 렌더러가 종료된 실행은 통과로 세지 않으며 동시 실행 수를 줄였다. 실패 로그도 보존한다.

HTML/CSS/원본 버튼·팝오버 배치는 변경하지 않았다. 실제 정보 카드 폭 460px와 원본 C# 편집기·기존 Review를 사용했다. 보존한 [기본 창](evidence/v536-information-reimplementation/primary.png)과 [독립 창](evidence/v536-information-reimplementation/detached.png)은 격리 fixture의 실제 화면이며 전체 화면 pixel equality나 실제 Windows 검증을 의미하지 않는다.

구현 snapshot은 `1120407d92b888251c3c304c639d8fb117faf75d`다. 별도 깨끗한 checkout의 Linux 빌드는 warnings/stderr 0이며, 실제 Git의 CRLF 유지/새 LF checkout과 74 canonical 리소스·변조/encoding/BOM/binary/budget 거절 검사를 통과했다.

Windows x64 교차 패키지의 2,327 runtime files, 무관 cwd/runtime-only 관리 엔진 web 기동, 기존 fixture profile 보존, 74 assets, 최소 연결 화면, 변조/누락 dependency 거절을 확인했다. 패키지의 변경된 JS·resource manifest·BlueprintFeature 소스가 구현 snapshot과 동일하다. 폴더는 `/workspace/artifacts/v536-information-reimplementation/Windows-x64`이며 전체 폴더를 함께 두고 `Confectory.exe`를 실행한다. `confectory-desktop-package.json` SHA256은 `896b1951dc91d13524df176b27312e6d19f53dec984c3ffe023e8e52919a20f7`이다. 실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미검증이다. 생성 패키지·사용자 자료·로그는 Git에 포함하지 않는다.

중간 검사에서 `/tmp` tmpfs가 100%가 되어 sandbox 명령 시작과 새 임시 복사에 실패했다. 이번 두 실패 probe의 재생성 가능한 runtime/package 복사만 정리하고 로그·소스·profile을 남겼다. 같은 환경의 workspace TMPDIR에서 패키지·리소스 검사를 다시 실행하여 통과했다. 코드/계정/권한 검사 우회는 하지 않았다.

## 다음 고정 단위

I5-2는 단독 소유 구현 archive와 구분한다. 기존 모듈 `provide` 해제는 원본/부모/복사 원문을 보존하지만, 확장된 복구 수명의 완료 증거를 대신하지 않는다. 공유·상속 원본을 삭제하거나 소유권 검사를 완화하지 않고, 소유 연결 또는 독점 소유 copy에 한정한 삭제/복구 근거를 다음 단위에서 연결한다. 함수 순서(I5-5)와 연결된 전체 계약(I5-6)은 별도 후속이다.
