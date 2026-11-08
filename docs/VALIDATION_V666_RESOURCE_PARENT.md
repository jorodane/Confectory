# 자료 상위 카테고리 열기 최종 검증

동결 `d872b05e31f5eb15672ae8425fa50308d3e53a8f`의 신규49단계를 모두 통과했다. 재사용0이며 개발 검사는 최종 단계로
계수하지 않았다. 분포 `{"resource": 1, "lf": 18, "crlf": 18, "windows": 2, "packaged": 4, "restored": 5, "package": 1}`다. [원본 근거·지원 경계](V7_RESOURCE_PARENT.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash·정확8개 제품 파일·기존 read/save/storage/공개ABI·FileStream·권한/CAS·CSS 불변 대조 |
| native | 독립 실제 pack 소비자에서 file/folder/root의 현재 metadata와 정확한 parent. 오래된 revision/ID/hash·다른 project·추가 OS 경로 거절, 변경/쓰기0. production body의 manifest/identity/catalog/layout/이름/설명/deletion/content 최종 관측27개 race와 기존 load 동일·구 reader 새 operation 거절 |
| 실제 UI | 파일·폴더의 원본 메뉴 순서, ProjectPack root, 별도 독립 창, 선택/포커스·현재 카테고리 트리/경로·Enter·기존 복제. 원래 창의 위치/검색/채팅 입력과 모든 원본/이름/ID 유지. cold 복원에서 기존 key/meta로 root·선택·검색 복구, 대기 탐색 재생0 |
| 실제 수명 | 반복 클릭 합치기·최종 순수 관측, 변조·읽기 권한 철회 거절, 늦은 검색/별도 채팅 입력 및 포커스 보존, 닫힘·Home/프로젝트 왕복 폐기. 첫 증명 뒤 실제 peer 이동을 마지막 관측에서 거절하고 명시 재조회 후 현재 parent 열기. 삭제된 표시 root의 원본 ProjectPack fallback. 문서 탭에서도 독립 창 |
| 기존 기능 | 기존 자료 생성/이동/이름/삭제/복구·Review/Confirm·충돌/실패/늦은 입력과 원본 파일의 실제 byte/pixel/download·읽기 수명 회귀. WebUI scope/revision/cancel/dispose 및 기존 원본 파일 최종 읽기 race. M11/M12/M4·원본 레이아웃 보존 |
| package | 새 Windows 교차 패키지·구조/의존성/무결성. 포함 Linux engine의 생성본과 전체 CRC/SHA·파일/디렉터리 mode 복원본에서 새 메뉴 normal/lifecycle 및 기존 자료/원본 파일 회귀. 실패/예외 수명·증거 지속 보존 뒤 소유 임시물 정리 |

새 `readProjectResourceLocation`/native `locate`는 현재 ProjectContext의 순수 관측이다.
파일 바이트·OS 경로·쓰기/자동 저장을 노출하지 않는다. 동일 id/hash/전체 revision의 두 관측이
일치하고 요청의 창/입력/프로젝트 수명이 현재일 때만 독립 창을 연다. root는 표시 범위이며
권한 부여가 아니다. 기존 저장·공개/override 실행·permission 계약·팩 ID·workspace 저장 형식과
파일4MiB/누적8MiB/RPC2MiB 예산을 바꾸지 않았다. 새 관측은 같은 UI/engine 패키지를 사용하며
구 engine은 새 관측을 거절한다. 이미 지원한 원본 파일 열기는 유지한다.
완료된 M11/M12/M4의 전체 기능 검사는 이번 단위에서 다시 실행하지 않았다. 해당 core/계약
제품 bytes 불변 대조와 영향받는 자료/UI 회귀를 실행했으며, 과거 기능 검증을 신규 검증 단계로
재계수하지 않는다.

개발24 managed 시도 중20개 exit0/4개 실패를 모두 보존했다. 기존 게시본064e922d의 실제
canonical UI bytes로 private query/queryInput은 남지만 cold 입력란이 비는 결함을 재현하고
포커스되지 않은 입력란만 복원 값과 동기화했다. 새 지연 탐색이 나중에 입력한 별도 chat의
포커스를 가져가는 현상도 통제 재현하고 편집 중 요청을 폐기했다. 나머지 실패3개는 selector
인용 문법, baseline engine과 새 UI bytes의 canonical 불일치(정상 보호), Python 응답 event
callback 집계 문제였다. 마지막은 실제 in-page fetch 횟수와 이력으로 검증했다. 최종 normal/
lifecycle·경계/unit 통과와 실패별 로그·소스 epoch·입력·프로필/스크린샷을 지속 보존했다.

환경 알림 뒤 같은 환경의 ready와 실제 exec/files를 확인했다. 이전 exec session은 소실됐으나
정상 UI 통과 기록은 남아 있었다. 미시작 lifecycle만 이어서 실행했으며 정상 검사를 중복하지
않았다. 최종 검사의 두 번째 환경 알림에서도 같은 환경은 ready/실제 exec를 반환했고, 도구
세션은 소실됐지만 최종 검증 owner 프로세스와29개 통과 결과가 남아 있어 재실행 없이
계속했다. 이 관측도 최종 증거에 보존했다. 환경 알림과 과거 초기 빈 화면의 정확 원인은 미확정이다.

실제 Windows/WebView2·모바일·OS 외부 앱·물리 GPU/오디오·전체 UI·Space/Library 전달은
미실행/미완료다. 더 큰 파일/일반 보관, 실제 신원/그룹 권한 backend, 기존 종류 C#표현/
사용중 항목 삭제 정책과 원인 미확정 초기 빈 화면은 기존 별도 잔여다. M11/M12/M4는 닫힌
상태이며 선택적 타입/문맥 조합을 새 필수 잔여로 추가하지 않는다.

## 지속 보관과 자원

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/59937ad981f64122a2c4415884fa1af3.json`
- 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/59937ad981f64122a2c4415884fa1af3.zip` (11,903,258B), SHA256 `474064d89026a8d3cce2c2daf6cd1e80474f90342564dcfdc7dbb3b46fae5564`
- 개발 record `/workspace/artifacts/v536-verification-managed/runs/2429af76716e4419949f27c13d6417db.json`, 증거 2,121,012B, SHA256 `54c97bf4b6d601337e20959c6cec2a9af2b1a57acbfd8ba3fe7f73312594de68`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index `/workspace/artifacts/v536-verification-managed/runs/59937ad981f64122a2c4415884fa1af3.closing-index.json`, SHA256 `24ddc92cbf679576c18e55f244a4a3646c4504b50540d304b1e74a1e7342244f`

| 보관 | source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | d872b05e31f5eb15672ae8425fa50308d3e53a8f | 841eb11e86bbd8e4370e718cbad9cc3297e940a06855ebbb4651f5653f1d351b | 53,851,041 |
| rollback | ec88e8d66ade3ccb414b6a08e73bde0b4cb38512 | 10099f97c154f626e3839c6a75346d6a2c3d90a197afdcaa3e71de70c8b7beb6 | 53,848,271 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전 ec88e8d6를 rollback으로 남기고 승인된 관리
두 세대 수명으로 이전 rollback a505ab74 `56aa00a6e41e119c9b083ae22264488a711da6a73fe33b6cf2c16f67e1c9bee8`만 퇴역했다. rollback에는
위 cold query 표시 제한이 있으며 저장된 private 입력/데이터는 유지된다. 다른 기존 자료/
원본/로그/프로필/SDK/Git는 삭제하지 않았다. 개발/최종 소유 임시 root는 자식 종료·소유와
지속 증거 무결성을 확인한 뒤 정리했다. 게시 SHA와 문서만의 차이·main/원본 보존은 별도 기록한다.

단위 계획은 개발256MiB+최종512MiB+추가 archive56MiB+코드4MiB+별도 disk 안전64MiB=
935,329,792B였다. 최종 시작 필요한 추가 disk 666,894,336B도 재확인했다.
RAM 작업공간4GiB+별도512MiB·추가 메모리9GiB+안전1GiB를 유지했다. 실제 개발/최종 증거
2.02/11.35MiB, 단위 시작/현재 disk
26,019,590,144/26,000,781,312B, 관측 순증가 18,808,832B다. 개발/최종 cgroup 표본 peak
10,822,410,240B로 limit 17,179,869,184B 대비 여유 6,357,458,944B다. 이는 tmpfs/
컴파일러/cache 포함 표본이며 제품 단독 peak·절대 극값·향후 증가량 보장이 아니다.
