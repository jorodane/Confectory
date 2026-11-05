# v666 일반 동작 표시명 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `305271cbcfe8468cbfec0d2eef5d9526e1f1a484`다. 마감 commit은 검증 문서 두 개만
바꾼다. [지원 경계](V2_NAME_RECOVERY.md), [정확한 delta](v666-name-recovery-delta.json)를 따른다.

## 재현과 변경

게시본 98a3098의 생성 프로젝트에서 Main의 직접 소유 ordinary code 동작 `after`를
기존 작은 화면 카드 inspector에서 이름 편집했다. checkpoint 쓰기 실패 뒤 개인 입력은
사라지고 live 이름만 바뀌었으며, cold에서는 원래 이름만 복원됐다. 원본과 checkpoint는
그대로였다. 수정 전 입력·실패·traffic·스크린샷·cold 결과를 개발 증거에 보존했다.

이름 전용 입력 하나를 기존 private 후보/checkpoint CAS/receipt와 공유 Undo/Redo에
연결했다. 실패 시 같은 checkpoint·source closure·물리 원본이 유지되고 미반영임이
확실한 경우에만 새 이름으로 명시 재시도한다. 응답 유실은 기존 receipt로 판정하고
이전 이름을 재전송하지 않는다. Save 응답을 기다리는 같은 직접 소유 이름 입력만
보존한다. 다른 busy 동작의 차단이나 외부 권한은 바꾸지 않았다. `ownedRename` receipt를
명시적으로 보관해 수정 파일이 없는 반복 Save도 cold 후 판정한다. 기존 `ownedSource`
receipt와 C# 본문 복구를 보존하며 가짜 graph/C# 변경은 만들지 않는다.

표시명은 식별자/실행 계약이 아니다. ID·C# bytes·정의 hash·signature·핀·외부 연결과
profile을 보존한다. 물리 쓰기는 기존 Review→Confirm과 최종 원본 CAS를 따른다.
비소유 원본/slot/copy/private/whole-body 문맥이나 표시명+본문/계약 혼합을 새로
허용하지 않는다. 데스크톱 F2/클릭 이름 편집은 이번에 새로 구현하지 않았다.

제품 delta는 feature-authoring.js·그 JS canonical metadata·Blueprint.csbody·Export.csbody
뿐이다. 레이아웃/HTML/CSS·공개 .celem/override 계약·권한을 바꾸지 않았다. 관련 V2의
공통 저장/확정 후 안내 3문구·3곳만 문체를 정리하고 backend 원문 진단은 보존했다.

## 최종 검증

독립 LF 16·CRLF 18·새 패키지/전체 복원/실패 수명관리
8, **총 42단계: 신규 42·재사용 0** 통과.
Git 객체·엔진 캐시·NuGet/home·실제 줄바꿈을 분리했다. 개발의 통과/실패 수는 합산하지 않는다.

- 정확한 제품/안내 delta·canonical asset·JS 문법과 이전 완료 문구 보존을 확인했다.
  공유 history의 inverse/CAS/restart/owner 및 표시명/실제 의미 변경 native 경계를 검증했다.
- 실제 API에서 stale checkpoint·위조 source closure·없는 노드·참조 call·owner/slot/frame·
  route/매개변수/본문 혼합, 빈 이름·제어문자·길이 초과를 거절했다. 저장은 멱등이며 cold와
  공유 Undo를 유지하고, receipt hash 위조를 거절한다. C# source API도 LF/CRLF 새로 회귀했다.
- 390×844 Chromium의 기존 이름 input에서 Undo/Redo·정확한 Unicode 입력/cold, 쓰기 실패
  후 새 이름 수정/명시 재시도, 동료 checkpoint 충돌/cold를 검사했다. 응답 유실은 receipt만
  회수하며, 응답 대기 중 새 이름은 별도 저장한다. 이전 이름은 재전송하지 않는다.
- 빈 이름 거절은 입력·checkpoint·원본을 유지하며 명시 수정만 받아들인다. 공유 Undo/Redo/
  cold·Review 취소·검토 후 Main.graph.json 원본 충돌 거절·새 Review/Confirm을 확인했다.
  물리 graph에는 해당 displayName만 바뀌고 모든 다른 물리 파일과 C# bytes가 같다.
  실제 .NET 반환 10, stdout `callee:1 → after:10`을 그대로 확인했다.
- 수정 파일이 없는 반복 이름 Save도 receipt를 보관하고 cold에서 물리 파일 쓰기 없이 판정한다.
  CRLF의 기존 C# source 쓰기 실패/새 입력/cold/Undo/최종 Confirm·실행 UI와 property
  observation·부분 Review·경로/원본 위조·expected-missing/readonly CAS 거절도 새로 회귀했다.
- 새 Windows 교차 패키지의 구성/무결성·패키지 엔진 웹 시작과 이름 normal/loss UI·실행을
  확인했다. 압축 CRC·전체 파일 SHA/모드를 검증해 완전히 복원하고, 복원 엔진에서 이름
  쓰기 실패/새 입력과 늦은 입력을 최종 Confirm·실행/cold까지 새로 검사했다.
- 성공·실패·예외와 증거 보존·복원·자식 종료·소유 임시물 cleanup 수명관리도 통과했다.

각 안내의 모든 오류 조건이나 모든 문맥/프로젝트 왕복을 새로 UI 주입하지는 않았다.
일반 이름은 기존 compact inspector의 검사이며 데스크톱 이름 편집이나 실제 모바일
기기 검증으로 확대하지 않는다. 기존 C# source 전체 UI 회귀는 CRLF에서 수행했다.

## 개발 증거와 보관

초기 UI probe는 C# 전용 편집기에서 쓰던 Ctrl+Y를 일반 input의 Redo에도 적용했다.
이 Linux Chromium input은 Ctrl+Shift+Z로 확인하고 수정했다. Undo는 이미 통과했고
이 실패는 제품 저장 실패와 구분한다. 실패 자료도 보존했다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/3b2eba9c42c04a83ba226f4d7bae10c2.json`

개발 SHA `d078d6fc77176c587559a6f74244184e0e65f6bef81acc1cbdba7fc0a26d4bfc`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/21a2cd3b50e84fd78152039069f99f1a.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/21a2cd3b50e84fd78152039069f99f1a.zip`

SHA256 `013c51d00e684abc3cf56e638fd452817c744ffd9362a9bd29ac7580235da186` (2.21MiB).

보관 index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `305271cbcfe8468cbfec0d2eef5d9526e1f1a484`, `4bdb3349994d7e5eaea4708c2c49be1b125e6ff4b42605aafebb18300f7848da.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `6aba0698f3f32fa6283047c5a64c022054d690db902cae27355e1a50ffdfa2ac`.

- rollback: 출처 `b045f85a6b7b1a5a7333e98147944bdc9a13a73a`, `4d65204674f377bef362bcae791f8b6d247b75434d38aa07fb5eb095cb35ce00.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `73a459d0c2675b3975a8ef47b776a49952d9d86d1f362747c2955c8c1fc53658`.

최신은 최종 동결 코드와 일치하고 정상 롤백·증거·기존 원본을 유지한다. 자식 종료와
archive 검증 후 이 실행이 직접 만든 임시물만 승인 수명대로 정리했다. 다른 과거 자료는
추가 삭제하지 않았다. 단계 표본 최소 여유 1632.54MiB, 최대 cgroup 메모리
4623.73MiB. 최종 실행 순증가 3.26MiB, 개발 시작부터
보관 확인까지 4.85MiB, 문서 마감 전 여유 1629.33MiB다.
이를 다음 실행의 증가량 보장으로 삼지 않는다.

## 유한한 잔여와 한계

route/root 핀/export·혼합 signature/description·이름과 다른 입력의 혼합 등 다른 일반
Save는 별도 읽기 점검 후보다. 재현 없이 결함/정상 금지/새 필수 조합으로 확정하지 않는다.
나머지 V2와 V3–V9·기존 팩/backend·종류 호환성 결정, 실제 Windows/모바일·전체 UI·Space
전달은 남는다. 완료한 M11/M12/M4를 다시 조합별 잔여로 세지 않는다.

검증은 컨테이너 Chromium 반응형 UI·실제 .NET·교차 패키지/복원이다. 실제 Windows
apphost/WebView2·모바일 기기·IME/DPI·전체 독립 창/프로젝트 왕복·전체 UI·Space는 미검증이다.
live AI·계정/자격증명·유료 호출·새 외부 권한은 사용하지 않았다.
