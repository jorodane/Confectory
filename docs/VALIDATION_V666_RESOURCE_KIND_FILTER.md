# 자료 종류 필터·Data 설명 cold 복원 최종 검증

동결 `5e3ec51913ad6536ead40359c02714c3c778ed8c`의 신규57단계를 모두 통과했다. 재사용0이며 개발 시도는 최종 단계로
계수하지 않는다. 분포 `{"resource": 1, "lf": 20, "crlf": 20, "windows": 2, "packaged": 6, "restored": 7, "package": 1}`다. [원본 근거·지원 경계](V6_RESOURCE_KIND_FILTER.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash와 정확6개 UI 제품 파일 대조. native/compiler/팩·공개/override ABI·권한/CAS·CSS·workspace schema 불변 |
| 종류 UI | 원본 정렬 앞 버튼·다섯 메뉴/pressed 상태, 실제 native document/image/mesh/file와 카테고리 유지. Compact/Preview/Data·숫자 이름 정렬·검색/미확정 입력·폴더 왕복, 숨겨진 선택 해제와 단일 삭제 메뉴. 삭제는 하지 않음 |
| 개인 수명 | 실제 지원 child browser 복제와 독립 종류 변경, 상위 카테고리 명시 선택의 새 창만 all 초기화. cold 종류/query/chat·미확정 이름/설명 보존, 오래된 메뉴/새 입력/새 종류/창 닫기/프로젝트 이탈 폐기, 차단 버튼의 실제 pointer로 이름/설명 blur 저장 방지, 실제 같은 namespace 다른 project 격리. 종류 선택 뒤 대기 parent 탐색 폐기 |
| Data 설명 복원 | 게시본52a5785의 정확 자산 bytes로 같은 ID/세대의 초안이 orphan에 남는 결함 재현. ready metadata와 현재 표시 목록의 같은 소유 ID/세대·연결 필드가 모두 orphan일 때만 재결합. 기존 revision/value/pending command 불변, 자동 Save/rebase 없음 |
| 실제 충돌/새 세대 | 동료가 저장한 뒤 cold에서 원래 revision/미확정 값을 유지. 명시 Save·동일 receipt 재시도는 stale 거절하고 동료 bytes 보존. cold pending receipt 정확 복원, 명시 취소만 최신 peer 값을 표시. 삭제/재import한 같은 ID의 새 생성 세대에는 readonly orphan 유지·취소만 허용 |
| 기존 경계 | 독립 실제 자산 pack 소비자와 metadata 마지막 관측 race, WebUI scope/revision/cancel/dispose. 기존 parent·자료 생성/이동/이름/삭제/복구·Review/Confirm·원본 파일 byte/pixel/download·최종 읽기 회귀 |
| package | 새 Windows 교차 패키지·구조/의존성/무결성. 포함 Linux engine 생성본과 전체 CRC/SHA·파일/디렉터리 mode 복원본에서 filter normal/lifecycle/draft-conflict·기존 parent/layout/original 회귀. 실패/예외 수명·증거 지속 보존 뒤 소유 임시물 정리 |

메시는 실제로 등록된 kind를 거르는 기능이며 새 mesh renderer나 형식 지원을 주장하지 않는다.
카테고리 root는 표시 범위이고 권한이 아니다. 새 native API·공개 실행/override 계약·저장
형식·권한 정책·자료 예산(파일4MiB/누적8MiB/RPC2MiB)을 추가하거나 바꾸지 않았다.
기존 private metadata에 bounded 종류 preference만 저장하며 미지 값은 all로 표시한다.
구 UI는 preference를 사용하지 않아 모든 종류를 표시하며 자기 저장 시 preference가 없어질
수 있다. 자산/초안의 자동 이행이나 재작성은 하지 않는다. 최신 UI/engine을 함께 사용한다.
완료된 M11/M12/M4의 전체 기능 검사는 다시 실행하지 않았다. 관련 core/계약 bytes 불변
대조와 영향받는 자료/UI 회귀를 실행하고 과거 검증을 신규 단계로 다시 세지 않는다.

개발28 managed 시도 중22개 exit0/6개 실패를 보존했다. 앞선 실패2개는 기존 계약상 복제
메뉴가 없는 project browser를 검사한 fixture였으며 제목 클릭 위치라는 초기 추정은
지지되지 않았다. 실제 지원 child browser로 바꾸고, 새 창 생성 후 live last() locator가
새 대상까지 따라가는 fixture 실패1개도 고정 key 캡처로 수정했다. 또한 새 프로젝트 브라우저에 닫힌 창의 설정을 기대한 fixture 실패1개는 창 키별 격리로 바로잡았다. Data 화면에 함께 있는 숨겨진 폴더 동작 버튼을 포함한 strict selector 실패1개는 현재 보이는 동작을 선택하도록 수정했다. 제품 실패1개는
위 실제 cold Data 설명 재결합 결함이었다. 같은 게시본 자산과 원래 revision/generation으로
재현한 뒤 보수적 재결합을 구현하고 세 UI 모드를 통과했다. 별도 실제 포인터 진단에서도 새 필터의 차단 click 전에 blur 저장이 발생함을 재현하고 pointerdown의 기본 포커스 이동을 차단했다. 수정 후 실제 포인터·입력/포커스/원본 불변 수명을 다시 통과했다. 실패별 로그·입력·소스
세대·baseline 자산 hash·프로필/스크린샷을 지속 보존했다.

실제 Windows/WebView2·모바일·OS 외부 앱·물리 GPU/오디오·전체 UI·Space/Library 전달은
미실행/미완료다. 더 큰 파일/일반 보관, 실제 신원/그룹 권한 backend, 기존 종류 C#표현/
사용중 항목 삭제 정책과 원인 미확정 초기 빈 화면은 별도 잔여다. M11/M12/M4는 닫힌
상태이며 선택적 타입/문맥 조합을 새 필수 잔여로 늘리지 않는다.

## 지속 보관과 자원

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/6550614f61d54077ae91e3572731bce3.json`
- 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/6550614f61d54077ae91e3572731bce3.zip` (13,019,352B), SHA256 `06ef53c5812e8caaa9a48e0bf7f535039b11e6e048c5b99f109634505a964e15`
- 개발 record `/workspace/artifacts/v536-verification-managed/runs/7929740473294693bce59da9d7529f3a.json`, 증거 1,885,268B, SHA256 `050a0b82b4655845ff31b17c90e0b3d2cfeeed63defa8426fdc1b0cf2f5d50eb`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index `/workspace/artifacts/v536-verification-managed/runs/6550614f61d54077ae91e3572731bce3.closing-index.json`, SHA256 `4173ecfaf630c57d572713354149ec0a577dbbcea630821fce59ed6931645505`

| 보관 | source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 5e3ec51913ad6536ead40359c02714c3c778ed8c | 04d4225fa39b813e1e2619f18f433a6eb3df3c5e529fe6f6c2026ab5138f1d01 | 53,852,217 |
| rollback | d872b05e31f5eb15672ae8425fa50308d3e53a8f | 841eb11e86bbd8e4370e718cbad9cc3297e940a06855ebbb4651f5653f1d351b | 53,851,041 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전 d872b05e를 rollback으로 남기고 승인된 관리
두 세대 수명으로 이전 rollback ec88e8d6 `10099f97c154f626e3839c6a75346d6a2c3d90a197afdcaa3e71de70c8b7beb6`만 퇴역했다. rollback에는
위 Data cold 설명의 orphan 표시 제한이 있으나 입력/저장 기준과 원본은 유지된다. 다른
기존 자료/원본/로그/프로필/SDK/Git는 삭제하지 않았다. 개발/최종 소유 임시 root는 자식
종료·소유와 지속 증거 무결성을 확인한 뒤 정리했다. 게시 SHA와 문서만의 차이·main/원본
보존은 별도 기록한다.

계획은 개발256MiB+최종512MiB+추가 archive56MiB+코드4MiB+별도 disk 안전64MiB=
935,329,792B다. 최종 시작 필요한 추가 disk 666,894,336B도 재확인했다.
RAM 작업공간4GiB+별도512MiB·추가 메모리9GiB+안전1GiB를 유지했다. 실제 개발/최종 증거
1.80/12.42MiB, 단위 시작/현재 disk
26,000,666,624/25,980,846,080B, 관측 순증가 19,820,544B다. 개발/최종 cgroup 표본 peak
9,938,104,320B로 limit 17,179,869,184B 대비 여유 7,241,764,864B다. 이는 tmpfs/
컴파일러/cache 포함 표본이며 제품 단독 peak·절대 극값·향후 증가량 보장이 아니다.
