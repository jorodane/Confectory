# v666 새 일반 동작 직접 배치 첫 저장 복구 검증

제품·검사·도구·delta 최종 동결은 `d2204f103d22170fedb48d3efafd2a9258425f8c`다. 이후 마감 commit은 문서만 바꾼다.
[지원 경계](V2_DIRECT_CREATION_RECOVERY.md)와 [정확한 delta](v666-direct-creation-recovery-delta.json)를 따른다.

## 재현과 보완

게시본 `f9d06b8bf99d6cee5823a6f8835978ff5bc4306c`의 원래 canvas **동작 만들기**에서
일반 void 동작을 만들고 이름·설명·C# 본문·기존 next 줄을 나눈 두 연결을 첫 Save로 저장했다.
checkpoint 쓰기를 실패시키면 개인 입력 여섯 개가 모두 사라지고, 새 동작은 live에만 남았다.
원래 checkpoint/물리 원본은 같으며 cold 재시작하면 새 ID·본문·연결이 사라졌다.
입력·실패 화면·traffic·checkpoint와 원본 일치 관측을 개발 증거로 보존했다.

기존 native `authorBatch`가 같은 생성/본문/두 연결을 원자 checkpoint와 멱등 receipt에
저장하는 경로를 먼저 확인했다. UI의 단일 직접 소유 root/새 next code/인자 없음/void/
여섯 입력/원래 next 목적지 보존을 이 후보로 연결했다. 기존 callback이 검증한 정확한
receipt로만 입력을 해소한다. 불명확·응답 유실은 입력과 시도를 보존하고 새 ID를 만들지 않는다.

일반 생성은 미적용 기준 관측을 제공하지 않아, 쓰기 실패 뒤 본문 수정의 재시도가 안전하게
거절되던 경계도 확인했다. 같은 닫힌 여섯 native edit에 한해 새 ID 부재·직접 소유 root·
원래 next 목적지를 대조하고, 원래 checkpoint/live 버전·전체 소스 ID/해시·물리 원본이
같아야 `baselineUnchanged`를 준다. 편집 허용·새 source 할당·실행/컴파일·최종 CAS를
바꾸지 않으며 새 경로 충돌은 기존 expected-missing 후보/최종 CAS가 거절한다.
새 receipt 종류/권한/공개 또는 override 계약·C# 원문 재작성·부모/외부 편집은 없다.
Restore·Export·이력 recorder와 원래 UI/문구/레이아웃도 그대로다.

새 본문 소유 ID 생성은 기존 `OWNERSHIP_CHANGED` 소스 전용 이력 경계를 유지한다
(`packs/edit-workspace/README.md` 31행, `FEATURE_BLUEPRINT_ARCHITECTURE.md` 121행).
생성 전 개인 canvas Undo/Redo와, 생성 뒤 같은 소유 집합의 별도 본문 공유 Undo/Redo를
구분한다. 생성 전체를 공유 Undo로 삭제/재생성한다는 새 정책을 만들지 않는다.

## 최종 검사

독립 LF 17·CRLF 16·새 교차 패키지/전체 복원/실패 수명관리 8,
**총 41단계: 신규 34·재사용 7** 통과했다.
Git 객체·NuGet/home·엔진 캐시·실제 checkout 줄바꿈을 분리했다. 개발 단계는 이 수에 합산하지 않는다.

- 정확한 native 읽기 관측/UI 후보·재시도 delta만 대조했다. 기존 후보 admission·소유·
  권한·이력/CAS·완료된 copy/명시 async 경로와 authored markup/문구/레이아웃은 같다.
  canonical UI 자산 크기·SHA를 갱신했다. 실제 JS guard와 기존 source proof helper의
  양성·비소유/계약/분기/혼합/다른 ID/해시 거절, JS 문법과 native 공유 이력 회귀를 확인했다.
- API에서 stale checkpoint·변조 closure·기존 ID·다른 namespace 그래프를 거절했다.
  checkpoint 쓰기 실패 시 live/원본을 보존했다. 미적용 관측은 정확한 기준에서만 true이며
  다른 checkpoint·proof·물리 원본 변경에는 false다. 생성/본문/두 연결의 원자 저장·동일
  attempt 멱등 재요청·cold receipt, 새 파일 무쓰기와 소유 이력 경계/cold도 확인했다.
- 원래 UI의 생성 취소·개인 Undo/Redo·명시 설명/C#·두 실행선·여섯 입력/같은 ID cold
  복원과 Save를 확인했다. 쓰기 실패 뒤 본문 수정은 같은 원래 후보 기준에서만 재시도했다.
  다른 root 값이 추가되면 일곱 입력/시도를 cold 뒤에도 보존하며 live 변경으로 fallback하지 않는다.
  동료 source checkpoint는 오래된 생성 입력이 덮어쓰거나 묵시 재배정하지 않는다.
- 응답 유실은 receipt만 회수하고 생성 ID/본문/실행선을 다시 만들지 않았다. 적용 중의
  늦은 본문은 별도 source 후보로 저장했고, 그 본문의 공유 Undo/Redo/cold는 생성 ID와
  두 연결을 유지했다. 생성 소유 경계를 넘는 source-only 공유 역연산은 계속 제공하지 않는다.
- Review 취소·예상 새 파일 경로의 peer 충돌 거절·새 Review/Confirm·실제 .NET 실행·
  최종 cold와 변경 없는 반복 Save를 확인했다. 물리 반영은 명시 graph 삽입과 새 본문 파일뿐이며
  기존 C#·함수/구현/caller·핀/계약/ID/값/기존 연결은 보존했다. 실행은 `body`, `placed`
  (늦은/수정 본문은 `placed-late`), `10`이며 반환값 10이다.
- 기존 root 후속 본문 저장의 API는 LF의 동일 코드 봉인 근거를 재사용하고 CRLF에서 새로,
  늦은 본문 UI는 LF에서 새로 회귀했다.
  이전 입력 이름/반환 순서·다른 전체 기능/컴파일 거절 근거는 이전 검증 기록에 유지하며
  이번 신규 단계로 재합산하지 않았다.
- 새 Windows 교차 패키지의 구조·무결성과 패키지 엔진의 정상/응답 유실 UI를 실행했다.
  압축 CRC·전체 파일 SHA/모드로 완전히 복원한 엔진에서 쓰기 실패/본문 수정·늦은 본문을
  Confirm/실행/cold까지 확인했다. 실패/예외/반복 수명관리와 증거 보존·자식 종료·소유
  임시물 정리도 통과했다. 실제 Windows apphost/WebView2나 모바일 실행 검증은 아니다.

## 개발 검사 경계

fixture의 존재하지 않는 `units()` 호출과 생성 전체 공유 Undo 가정은 검사 오류였다.
새 경로는 실제 checkpoint의 소유 unit에서 읽고, 원래 소유 이력 보호를 검사하도록 고쳤다.
잘못된 작업 위치로 이전 fixture가 한 번 시작된 경우에는 해당 소유 worker만 중단하고
기록을 보존했다. native 보완의 nullable 빌드 진단은 명시 null guard로 수정했다.

늦은 입력 fixture의 첫 대기는 30초였지만 정상 여섯 편집 후보 응답은 관측상 33.24초였다.
이후 오류 수집이 뒤늦게 도착한 응답을 보류하며 기다려 정지했다. 소유 UI Python에만
SIGINT를 보내 보존 가능한 trace/traffic·checkpoint·프로필을 회수했다. 원래 예외를 먼저
기록하고 보류 응답을 해제한 뒤 유한 시간으로 증거를 수집하도록 고쳤다. 후보 응답 대기는
기존 Save 검사 수준의 90초로 한정했고, 저장·거절·원본 보존/단일 요청 조건은 그대로다.

별도 첫 일반 UI에서 전역 홈 버튼의 60초 대기 실패도 있었다. native 저장/receipt는
실패 수집 시점에는 성공했고, 읽기 전용 getter 진단은 모든 대기 플래그가 해제된 상태로
같은 저장을 통과했다. getter는 제거했으며 그 진단을 최종 검사로 합산하지 않았다.
그 최초 60초 대기의 원인은 미확정이고, 위에서 확인된 30초 fixture 문제와 혼동하지 않는다.
최종 제품·원래 자산의 UI 재검증/전체 복원본 검사는 통과했다.

최종 첫 실행의 cold 수정 재시도도 60초 홈 버튼 한도로 실패했다. 이 실행의 traffic에서
원자 후보 호출 자체가 59.87초였고, Save 시작 후 성공 응답은 66.81초, 최종 receipt/
읽기·입력 저장은 73.58초였다. 입력은 정상 해소됐고 예외 수집이 그 완료를 관측했다.
따라서 이 구체 실패는 검사 대기 한도 문제로 분류하고 해당 Save만 120초로 한정했다.
제품/거절/원자성/입력 보존 조건은 바꾸지 않았다. 첫 일반 UI의 별도 60초 실패 원인은
계속 미확정이며 이 측정만으로 소급 확정하지 않는다.

제품 및 선택 검사 파일·SDK/의존성/설정·LF 독립 checkout이 같음을 대조한 뒤 첫 최종
실행의 통과한 static 두 개·delta/문법/이력·새 API·기존 root 후속 API **7개**만 재사용했다.
독립 빌드와 모든 UI·CRLF·새 교차 패키지·전체 복원 검사는 새로 실행했다. 실패한 검사는
재사용하지 않았으며 정확한 한 줄 대기 변경과 호출 일치 증명을 최종 증거에 보관했다.
첫 실패 최종 record `/workspace/artifacts/v536-verification-managed/runs/182d5d7ce32f4a599602afa5a1c9b1b3.json`,
증거 SHA `989af3bebfb7f7f189ec8aa98fa4f06b31652de13206f17e837381998b2b9ba3`도 보존한다.

## 증거·보관·공간

개발 record `/workspace/artifacts/v536-verification-managed/runs/617b1f9b26404c0d9bd535ed67a8f6c8.json`

개발 증거 SHA `eb4277b1b71f1fbfe18baa603911123cd886245842ae5e5f851a8c8f20d53c3f`.

최종 record `/workspace/artifacts/v536-verification-managed/runs/da08e97597dc4d538f25a9f1f75899ad.json`

최종 증거 `/workspace/artifacts/v536-verification-managed/runs/da08e97597dc4d538f25a9f1f75899ad.zip`

SHA256 `b49ab9a6c5a23efafe56834ddefb1e015280e36be9c08382dd6ee3ab7ad251b9` (2.57MiB).

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.

- latest: 출처 `d2204f103d22170fedb48d3efafd2a9258425f8c`, `9736227508ad82f34d2a9ff9c074a5f01218713386a909c710fc8c01f69343a9.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `712377aaba66a04e6f87adfccfbdab0c3e4d18861f2d5687651d8d094df5345a`.

- rollback: 출처 `b1f6be970c8fb56bd0293335e8b485f7d9a6e694`, `d48a9b93d0806898cda36cdf8bfa856986696148cbd26c3ae80f11b9ef3d8d72.zip`, 49.13MiB, 파일 2381·디렉터리 147, 전체 manifest `7ef94e5dbfb72adca128c9e964fb459f39ba2016bb7ceb15297632f6e86722aa`.

최신은 최종 동결 코드와 일치한다. 이전 정상 최신본을 롤백으로 보관하고 모든 증거를
검증한 뒤 이번 실행의 소유 임시물만 승인 수명대로 정리했다. 다른 기존 자료는 삭제하지 않았다.
단계 표본 최소 여유 1565.30MiB, 최대 cgroup 메모리 4703.39MiB다.
최종 실행 순증가 3.59MiB, 개발 시작부터 보관 확인까지
7.32MiB, 문서 마감 전 여유 1561.75MiB다.
다음 실행의 고정 증가량을 보장하는 값은 아니다.

## 유한한 잔여·미실행

이 단일 새 일반 동작의 첫 저장/복구 흐름을 마감했다. 다른 root 정의·혼합 계약·직접
배치 형태는 원래 요구와 현재 지원을 대조할 별도 점검 후보다. 조합마다 새 필수 항목을
추가하지 않으며 완료 M11/M12/M4를 다시 열지 않는다. 기존 V2 후속·V3–V9·팩/backend·
종류 호환성 결정과 실제 Windows/WebView2·모바일·DPI/IME·전체 독립 창/프로젝트 왕복·
전체 UI·Space 전달 미완료를 유지한다. live AI·자격증명·유료 호출·새 외부 접근/권한은 사용하지 않았다.
