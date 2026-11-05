# v666 root 저장 뒤 일반 본문 저장 복원 검증

제품·검사·도구·delta 최종 동결은 `b1f6be970c8fb56bd0293335e8b485f7d9a6e694`다. 이후 마감 commit은 문서와
수용 표만 바꾼다. [지원 경계](V2_ROOT_FOLLOWUP_RECOVERY.md)와
[정확한 delta](v666-root-followup-recovery-delta.json)를 따른다.

## 재현·수정

게시본 `03af2ab3f3135792944c4d83ff19847125b34c3e`의 기존 UI에서 root 입력 이름을
바꿨다가 원래 이름으로 돌아와 Save했다. zero-dirty 함수·구현·그래프 묶음은 완전했다.
그 뒤 일반 C# 본문을 편집하고 Save하면 receipt 종류가 바뀌면서 변경 없는 함수·구현
두 멤버가 checkpoint에서 빠졌다. 개인 입력은 지워졌고 cold 프로세스는
`Project workspace unavailable`로 종료됐다. 물리 원본/C#은 그대로였다.
불완전한 checkpoint·typed 입력·traffic·시작 로그와 실패 화면을 개발 record에 보관한다.

기존에 이미 보관하던 receipt 판정을 한 곳에서 재사용하여, 해당 그래프의 기존 root
그룹도 같이 보관한다. 동일한 11개 flag·blueprint 종류·자기 graph ID 결합을 유지한다.
변경 있는 그룹 보관과 Restore·소유/경로·그룹 검증은 바꾸지 않는다. 새로운 ID/receipt/
편집 허용이나 묵시적 묶음 재구성은 없다. 원자 checkpoint CAS·Review→Confirm·최종 CAS·
Undo·입력 보존·원래 계약/ID/값/연결·부모/외부/권한·화면/문구/레이아웃은 그대로다.
명시적으로 편집한 C#만 Confirm 뒤 반영하며 다른 C#은 바꾸지 않는다.

생성 fixture의 graph JSON 공백 차이는 실제 draft 변경이어서 기존 native writer와 동일한
compact 형식으로 맞춘 뒤 재현했다. 원래 C# 값으로 되돌려도 node JSON 컨테이너는
정규화될 수 있으므로 API는 본문 값·zero-dirty root 멤버를 분리해 검사한다.
최종 정상 UI의 Confirm 뒤 반복 Save에서는 전체 dirty 0개와 receipt 복원을 확인했다.
개발 원본의 cold 시작 실패는 첫 probe의 catch 밖에서 발생했으나 입력 유실·누락 멤버·
원본 보존·시작 로그가 이미 기록돼 재빌드하지 않고 보존한 증거로 확정했다.

늦은 본문 검사에서 별도 실제 결함도 발견했다. root no-op 저장 뒤 cold 복원은 내용이 같은
소스의 process-local revision을 바꾼다. 성공한 source 저장을 기다리는 동안 입력한 새 본문이
이전 proof를 유지하여, 성공 receipt 후에도 재시도되지 않았다. 수정은 직접 소유 root의 단일
일반 code source에서만 기존 동일 소스 ID/해시·캡처한 같은 입력·정확한 두 receipt 확인을
사용해 새 proof로 연결한다. 변조/누락/다른 원본·입력과 비소유/copy/slot/whole-body 전달·
혼합 문맥은 새로 허용하지 않는다. 실제 helper의 양성/거절 경계를 추가 검사했고 native
권한·수락/CAS 계약은 같다. 늦은 입력 fixture가 revision만 다른 동일 원문이라는 선행 조건도
명시 검사한다. 실패 record `018754c15c6f4a14bc72f61d664285bc`와 원래 pending/receipt/
checkpoint/traffic/화면은 보존했다.

## 최종 검사

독립 LF 18·CRLF 19·새 패키지/전체 복원/실패 수명관리
8, **총 45단계: 신규 40·재사용 5** 통과.
Git 객체·실제 줄바꿈·엔진 캐시·NuGet/home을 분리했다. 개발 결과는 최종 수에 합산하지 않는다.
저장기와 단일 소유 source proof 복구 변경에 맞춰 root 그룹·일반 source·공유 이력·복원 영향 회귀를 실행했다.
이전 전체 기능 검사를 이번 수에 재합산하지 않는다.

- 정확한 Export delta·같은 11개 receipt flag와 graph 결합·기존 source/계약/Restore/권한/
  화면/문구/레이아웃 불변과 canonical asset 크기·SHA 갱신을 대조했다. JS 문법 및 실제 공유 history inverse/CAS/restart/
  owner·표시명 런타임 회귀도 확인했다.
- API에서 root Save 뒤 source Save·멱등 재요청·cold receipt를 확인했다. 원래 본문 값으로
  되돌리기와 같은 값 반복 저장도 완전한 root 멤버를 보관했다. 물리 원본은 같았다.
- 누락 멤버·다른 explicit 그룹·외부 경로·다른 namespace는 cold 시작에서 기존 검증대로
  거절하고 checkpoint/원본을 보존했다. receipt hash 변조도 저장 확인을 주지 않았으며,
  보존한 정상 checkpoint를 복원하면 마이그레이션 없이 다시 시작했다.
- 원본 root rename/back/Save 뒤 C# 편집기의 고정 선언·본문 Undo/Redo·취소·정확한 개인
  source cold 복원을 확인했다. checkpoint 쓰기 실패와 동료 저장 충돌은 개인 입력·다른
  checkpoint·live/원본을 보존했다. 새 source의 cold 명시 재시도도 통과했다.
- 응답 유실은 receipt만 회수하고 이전 본문을 재전송하지 않았다. 적용 후 늦은 본문은
  별도 source 후보로 저장했다. 공유 Undo/Redo·원본 root 그룹·cold도 확인했다.
- Review 취소·검토 뒤 물리 source 충돌 거절·새 Review/Confirm·실제 .NET 실행·cold를
  확인했다. 명시한 source JSON 본문 외 다른 파일과 function/implementation/graph·C#
  호출자·계약/ID/프로필/값/연결은 같다. 실행은 `body` 다음 `10`, 반환 10이다.
  변경 없는 source Save는 dirty 0개여도 complete root 묶음과 receipt를 복원한다.
- 기존 root 입력 이름·반환 핀 순서·ordinary source API를 양쪽에서 회귀했다.
  LF native API·공유 history는 UI 전용 수정 전의 동일 native 코드·검사·의존성·호출로
  봉인된 성공 결과 5개만 재사용했다. 모든 UI·정적 경계·빌드·패키지 및 CRLF는 새로 실행했다.
  CRLF에서는 CS0103 컴파일 거절·원본/checkpoint/입력 보존·명시 수정과 property 관찰·
  부분 Review·경로/원본 위조·expected-missing·readonly CAS도 확인했다.
- 새 Windows 교차 패키지의 구성/무결성과 패키지 엔진 정상/응답 유실 UI를 확인했다.
  CRC·전체 SHA/모드로 완전히 복원한 엔진에서 쓰기 실패/새 source 재시도와 늦은 source를
  Confirm/실행/cold까지 확인했다. 성공·반복·실패·예외의 증거 보존/복원·자식 종료·
  소유 임시물 cleanup도 통과했다.

최초 최종 실행의 storage-new 모드는 native Save와 receipt 재확인 뒤 전역 홈 버튼이
60초 안에 활성화되지 않아 실패했다. 입력과 성공 요청·화면·checkpoint 증거를 보존했다.
읽기 전용 상태 getter를 테스트에서만 추가한 진단 실행은 같은 경로 전체를 통과했다.
이 진단은 최종 검사 수에 합산하지 않으며 제품을 수정하거나 시간 제한을 낮추지 않았다.
최종 원래 fixture의 storage-new와 전체 복원본 재검사를 통과했지만 최초 UI 대기의
원인은 미확정이다. 저장 복구 수정과 별개로 일시 대기 원인을 해결했다고 표현하지 않는다.
최초 실패 record `5c7d5647fc1845428c34981cb7be8009`, 진단 record
`ac7286f780b14ba19d37ec6fca330f9c`도 보존한다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/b51fa3a85e35416998145d41f300995d.json`

개발 증거 SHA `a72e0c5d3d888de395e753fc29edcbf862df657e2a42e0b0dd36741b484f49d8`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/1abac68f571a4ed68456da35d22459b6.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/1abac68f571a4ed68456da35d22459b6.zip`

SHA256 `7524e00210b72e4e0f1db56fce9dc92a328006d0d679933c460015c19df05241` (2.48MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `b1f6be970c8fb56bd0293335e8b485f7d9a6e694`, `d48a9b93d0806898cda36cdf8bfa856986696148cbd26c3ae80f11b9ef3d8d72.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `7ef94e5dbfb72adca128c9e964fb459f39ba2016bb7ceb15297632f6e86722aa`.

- rollback: 출처 `68e76080d342ca634b95265cc74c875c9de68d89`, `b2eb727d092627398527cd89c61bb70c31ca0d15c6d3f318a85c79c9516d70e3.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `d1fc2cc9d4e3079cbcd062e916cec6672f8131d78e0b0a98202b6d8cba2b41a7`.

최신은 최종 동결 코드와 일치한다. 롤백·증거·원본을 보존하고 archive 검증과 자식 종료 뒤
이번 실행이 만든 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 추가 삭제하지 않았다.
단계 표본 최소 여유 1572.60MiB, 최대 cgroup 메모리 4685.23MiB다.
최종 실행 순증가 3.49MiB, 개발 시작부터 보관 확인까지
7.32MiB, 문서 마감 전 여유 1569.15MiB다.
이를 다음 실행의 고정 증가량 보장으로 쓰지 않는다.

## 유한한 잔여·미실행

다른 root 정의·혼합 계약 Save·직접 배치는 원본 요구/현재 지원과 대조할 별도 점검 후보다.
조합마다 새 필수 요구를 추가하지 않으며 완료 M11/M12/M4를 다시 열지 않는다.
이미 불완전한 checkpoint의 묵시적 재구성이나 자동 migration은 추가하지 않았다.
나머지 V2·V3–V9·기존 팩/backend·종류 호환성 결정은 고정 수용 표에 남긴다.
검증은 컨테이너 Chromium·실제 .NET·교차 패키지/복원이며 실제 Windows apphost/WebView2·
모바일 기기·DPI/IME·전체 독립 창/프로젝트 왕복·전체 UI·Space 전달은 미검증이다.
live AI·자격증명·유료 호출·새 권한/외부 접근은 사용하지 않았다.
