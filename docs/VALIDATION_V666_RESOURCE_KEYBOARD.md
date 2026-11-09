# 자료 목록 키보드 최종 검증

동결 `2a81b5520759e066e004ee62c9bc6aa8a0d9cc66`의 신규57단계를 모두 통과했다. 재사용0이며 개발 시도는 최종 단계로
계수하지 않는다. 분포 `{"resource": 1, "lf": 20, "crlf": 20, "windows": 2, "packaged": 6, "restored": 7, "package": 1}`다. [원본 근거·지원 경계](V6_RESOURCE_KEYBOARD.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash와 정확4개 UI 제품 파일. native/compiler/팩·공개/override ABI·권한/CAS·CSS·자료/개인 저장 형식 불변 |
| 목록 명령 | 실제 Ctrl/Meta+A는 현재 폴더/검색/종류의 보이는 행만 선택, Escape는 개인 선택만 해제. Delete는 기존 폴더 하위 전체 집계·확인 후 명시 삭제, Cancel 쓰기0. 선택 문서2개의 Enter는 원래 각 ID/hash 미리보기에서 실제 원문 표시, focused folder Enter는 한 번 탐색 |
| 편집/실제 저장 | F2 단일 인라인 초안·Escape 취소·Enter alias 저장. 여러 선택은 대상 추측0, 검색 Ctrl+A/Delete/Enter는 native 편집, 실제 명시 삭제는 한 소유 사본만 제거·숨겨진 독립 image/나머지 ID 유지. 원본 C#과 삭제 대상 밖의 import bytes/ID 보존 |
| 실패/재시작/경합 | 실제 alias 파일 readonly로 저장 실패·정확 command/revision 입력 보존. 미확정 중 목록 키는 무시하고 창 삭제로 전파0. cold 자동 Save0·같은 receipt 명시 재시도는 alias1개, 미확정 F2 text 복원/취소. 실제 동료 alias 변경 뒤 기존 CAS·재조회/재시도 거절과 입력만 취소 |
| 수명/경계 | 취소된 확인은 새 선택에 적용0, 계층/IME/반복 Delete는 목록/Workspace 삭제0. 닫힌 창·프로젝트 이탈 후 옛 키 handler는 무효. 실제 layout handler의 통제된 idle 대기에서 중복 Delete 합치기·새 검색/Escape/다른 편집 포커스 폐기·idle 예외 시 선택 유지 |
| 기존 기능 | 실제 독립 자산 pack 소비자·최종 metadata/read race, WebUI scope/revision/cancel/dispose. 자료 종류/설명 cold 및 충돌·pending receipt/새 세대, 기존 parent·layout·original byte/pixel/download·입력/권한/CAS 회귀 |
| package | 새 Windows 교차 패키지·구조/의존성/무결성. 포함 Linux engine 생성본과 전체 CRC/SHA·파일/디렉터리 mode 복원본에서 keyboard normal/lifecycle 및 기존 filter/parent/layout/original 회귀. 실패/예외 수명·증거 지속 보존 뒤 소유 임시물 정리 |

새 동작은 원본 `renderResourceBrowser`의 다섯 목록 키 흐름이다. native API·실행/override
계약·권한·자료 예산(파일4MiB/누적8MiB/RPC2MiB)과 저장 형식을 바꾸지 않았다. 키/대기
확인은 휘발성이며 저장/재생하지 않고 기존 선택·인라인/미확정 입력만 private 상태로 보존한다.
실제 편집 필드·버튼·도구/계층과 IME는 목록 명령으로 해석하지 않는다. 자료 body의 Delete는
전역 Workspace 창 삭제로 넘기지 않지만 실제 입력란 기본 편집은 유지한다. 자료 body 밖의
Workspace 삭제는 변경하지 않는다. 반복 Enter/Delete/F2는 소비하되 재실행하지 않는다.
폴더 삭제는 기존 모든 하위 집계/확인 의미를 유지하며 종류 밖 독립 항목을 선택에 넣지 않는다.
완료 M11/M12/M4 전체 검사는 다시 실행하지 않았다. 관련 core/계약 bytes 불변 대조와
영향받는 자료/UI 회귀를 실행하며 과거 증거를 신규 단계로 다시 세지 않는다.

개발16 managed 시도 중15개 exit0/1개 실패를 보존했다. 실제 실패 복구에서 차단된 목록
Delete가 바깥의 기존 Workspace 삭제 handler로 전파돼 자료 창을 닫는 결함을 확인했다.
명령은 차단 중에도 소비하고 body의 IME/반복/계층 Delete도 바깥으로 넘기지 않도록 수정한
뒤 일반/수명 검사를 통과했다. 원본 사본이나 미확정 요청을 폐기한 것으로 표현하지 않는다.
관리 검사 전 로컬 단위 검사에서는 미지 키 `__proto__`가 일반 객체의 상속 property로
매핑됨을 확인해 고정 명령의 own-property만 허용했다. 실제 UI/native 호출 전의 단위
finding이며 local-precheck.json과 최초 구현 script를 보존했다. 실패 로그·생성된 입력·소스
세대·프로필과 생성된 스크린샷은 지속 보관한다.

최종 첫 wrapper+child 실행은 managed 작업공간/빌드 생성 전 메모리 preflight에서 거절됐다.
당시 cgroup6,448,234,496B로 추가9GiB+안전1GiB 기준보다5,783,552B 부족했다. 종료 후
실제 프로세스와 회수된 메모리를 확인하고, 같은 검증기를 부모 Python 없이 직접 실행해
동일 예산 검사를 통과했다. 첫 실패 로그와 memory-preflight-recovery.json을 최종 증거에
보존했다. 예산 축소·기존 파일 삭제·시스템 cache 설정/환경 교체나 중복 빌드는 없었다.

실제 Windows/WebView2·모바일/기기 IME·OS 외부 앱·물리 GPU/오디오·전체 UI·Space/Library
전달은 미실행/미완료다. 더 큰 파일/일반 보관, 실제 신원/그룹 권한 backend, 기존 정보 종류
C#표현/사용중 항목 삭제 정책과 원인 미확정 초기 빈 화면은 별도 잔여다. M11/M12/M4는
닫힌 상태이며 선택적 타입/문맥 조합을 새 필수 잔여로 늘리지 않는다.

## 지속 보관과 자원

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/d55a5b171efe4772b5c3103f2860cf23.json`
- 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/d55a5b171efe4772b5c3103f2860cf23.zip` (12,836,746B), SHA256 `468c0887267838896956ff1ea7448741e419bc8405c1f34d0235b23eb812277f`
- 개발 record `/workspace/artifacts/v536-verification-managed/runs/49a8b1a0ddbe4ca9abfd504c0bf33b93.json`, 증거 955,604B, SHA256 `d04bea6a679465fbc7a8b4752f4027a665dd7d22f36d4043ce3ee4456d698ffe`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index `/workspace/artifacts/v536-verification-managed/runs/d55a5b171efe4772b5c3103f2860cf23.closing-index.json`, SHA256 `e66b8e87d9d659f5f575c0f124f54f05bed6ab52ff1386d9875ec221829e35e9`

| 보관 | source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | 2a81b5520759e066e004ee62c9bc6aa8a0d9cc66 | 99a752dd817b1cb6a55e5cf2f528216fea3cd2306fe25ec48cf26790f7e93512 | 53,853,676 |
| rollback | 5e3ec51913ad6536ead40359c02714c3c778ed8c | 04d4225fa39b813e1e2619f18f433a6eb3df3c5e529fe6f6c2026ab5138f1d01 | 53,852,217 |

전체 복원·증거 봉인 뒤 원자 승격했다. 직전 5e3ec519를 rollback으로 남기고 승인된 관리
두 세대 수명으로 이전 rollback d872b05e `841eb11e86bbd8e4370e718cbad9cc3297e940a06855ebbb4651f5653f1d351b`만 퇴역했다. rollback에는
이번 목록 단축키와 차단 Delete 경계가 없다. 다른 기존 자료/원본/로그/프로필/SDK/Git는
삭제하지 않았다. 개발/최종 소유 임시 root는 자식 종료·소유와 지속 증거 무결성을 확인한
뒤 정리했다. 게시 SHA와 문서만의 차이·main/원본 보존은 별도 기록한다.

계획은 개발256MiB+최종512MiB+추가 archive56MiB+코드4MiB+별도 disk 안전64MiB=
935,329,792B다. 최종 시작 필요한 추가 disk 666,894,336B도 재확인했다.
RAM 작업공간4GiB+별도512MiB·추가 메모리9GiB+안전1GiB를 유지했다. 실제 개발/최종 증거
0.91/12.24MiB, 단위 시작/현재 disk
25,980,731,392/25,962,328,064B, 관측 순증가 18,403,328B다. 개발/최종 cgroup 표본 peak
10,113,912,832B로 limit 17,179,869,184B 대비 여유 7,065,956,352B다. 이는 tmpfs/
컴파일러/cache 포함 표본이며 제품 단독 peak·절대 극값·향후 증가량 보장이 아니다.
