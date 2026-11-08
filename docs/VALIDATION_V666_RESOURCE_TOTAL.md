# 누적 자료8MiB 최종 검증

동결 `a505ab74ee574f3022296d3c1b37bc4e64b54a8a`의 신규82단계를 모두 통과했다. 재사용0이며 개발 결과를 최종 검사로
세지 않았다. 분포 `{"resource": 1, "lf": 35, "crlf": 32, "windows": 2, "packaged": 5, "restored": 6, "package": 1}`다. [원본 근거·지원/호환 경계](V6_RESOURCE_TOTAL.md)를 따른다.

| 검사 | 실제 범위 |
|---|---|
| 독립 source | no-hardlinks LF/CRLF Git·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine. 고정 ZIP/hash·정확 두 runtime 본문/README 변경·나머지 UI/ABI/core/FileStream·권한·최종CAS 불변 대조 |
| native | 고엔트로피 두4MiB/정확8MiB 원본·64개/파일·선택4MiB 한도·전체SHA/ID/immutable 영수증·명시 v1→v2·정확 재전송/충돌·초과/위조 v1 거절·metadata-only 큰 읽기/소유 보호 |
| 최종 거래 | 실제 production bodies의 승격 후보 직전 manifest/identity/store/deletion 경합과 write failure. 기본/선택 일괄·배치/폴더 결합·내용 거래·파일/폴더 삭제4/5개 write 및 설명 peer race·다중 삭제 |
| 실제 UI | 기준4MiB 거절. root/folder 두 File로8MiB 보관, 초과 실패·명시 취소/재시도·삭제 후 공간 재사용/버전 유지·원본/다른 사본 보존·응답 유실/영수증/늦은 입력·부분 upload 중 닫기·다른 프로젝트·cold |
| Office/기존 | v2 catalog의 별도4MiB 사본과 큰 DOCX/XLSX 편집·직전 복원·cancel/보호·실패/충돌/Worker/개인 입력/응답 유실/cold. 기존 v1 작은 자료·큰 단일/배치/transfer/content/설명·SVG 회귀 |
| package | 새 Windows 교차 패키지·구조/의존성/변조 검사. 포함 Linux engine에서 생성본·전체 CRC/SHA/파일·디렉터리 mode 복원본의 누적 보관/수명·XLSX private recovery·실패 수명 |

원본 v666은 File 사본의 프로젝트별 축적을 지정하며8MiB 자체는 이번 구현의 bounded
실행 예산이다. 기존 파일/선택4MiB·64개·upload6,000,000B/RPC2MiB·공통 snapshot/CommitPlan16MiB는
유지한다. catalog만 최대12MiB로 읽고 버전별 raw aggregate를 검증한다. load/작은 기존 v1은
재작성하지 않는다.4MiB를 넘는 명시 import 후보만 v2가 되며 삭제 뒤에도 자동 downgrade하지
않는다. 원래 IDs/receipts/path/필드와 공개/override·권한·Review/Confirm을 보존한다.

실제 이전65d8f298 production reader의 v2 load/read/write 거절과 원본 불변, v1 사본의 양쪽
호환을 확인했다. enlarged-v1 위조나 손상은 unavailable/거절이며 비우거나 이행하지 않는다.
rollback archive 복원 가능성과 새 v2의 구 parser 호환은 구분한다. 새 버전으로 만든 큰
catalog를 구 reader로 편집할 수 있다고 표시하지 않는다.

개발 managed21시도 중18개 exit0,1개 예상 밖의 기존 삭제 fixture 실패,2개 같은 오류의
통제된 현재/기준 재현(exit134)을 보존했다. 이미 있던 설명 sidecar가 최종 dependency 집합에
들어갔지만 옛 fixture 기대 목록에는 없던 문제다. baseline65d8f298에서도 같은 실패를 확인하고
제품은 그대로 두었다. File/Folder fixture에 실제 설명 의존성과 해당 race를 추가해 원래
4/5개 write·각 단계 rollback/peer 보존과 정확 receipt 재실행을 통과했다. 수정 전/후 프로그램·
로그·입력·프로필/스크린샷을 남겼다. 준비 script의 예상 snapshot 개수 assertion과 실행 중
workspace 재개 거절도 소유 보호가 동작한 준비 오류로 구분하며 제품 검사로 세지 않았다.

실제 Windows/WebView2·모바일/OS 파일 드롭·Office 앱·GPU/물리 오디오·전체UI·Space/Library는
미실행/미완료다. 초기 빈 화면과 역사적4K 재조회 실패의 정확 원인은 미확정이다.4MiB 초과 파일/
더 큰 일반 총보관·실제 신원/권한 backend·종류 C#표현/사용중삭제 정책·전체8192² 출력은
기존 별도 잔여이며 선택적 조합을 새로운 필수 목록으로 늘리지 않는다. M11/M12/M4는 닫힌다.

## 지속 보관과 자원

- 최종 record `/workspace/artifacts/v536-verification-managed/runs/5b03f81795744679a2b0ed0051337b29.json`
- 최종 증거 `/workspace/artifacts/v536-verification-managed/runs/5b03f81795744679a2b0ed0051337b29.zip` (373,896,633B), SHA256 `8e2367381bb5ed38063f4c2eedf7d715d5e7c6b9d9bfab8cbf7f6fd5a7f74bf0`
- 개발 record `/workspace/artifacts/v536-verification-managed/runs/3d14b7e5bbab4fb39bac545a26cf3984.json`, 증거 142,994,548B, SHA256 `0ef793f35d8753e3d8cd26386cfe83107ee27b58b3c9a6b7fc78a6df35cfcade`
- 승격 전 index는 최종 증거 package-index-before.json, 후 index `/workspace/artifacts/v536-verification-managed/runs/5b03f81795744679a2b0ed0051337b29.closing-index.json`, SHA256 `28a6f6b69546b900c3b4eddef14e12c1de639cf3268c1fbd245a447672ebc87a`

| 보관 | source | ZIP SHA256 | bytes |
|---|---|---|---:|
| latest | a505ab74ee574f3022296d3c1b37bc4e64b54a8a | 56aa00a6e41e119c9b083ae22264488a711da6a73fe33b6cf2c16f67e1c9bee8 | 53,843,722 |
| rollback | b810acbc4eb4ed4b93b6cdc1576975027de50b37 | 9af4e9209cf60ac41b5a1c9fca775cf0aae9cecae7230f58369cf216d6b0eb0b | 53,843,851 |

전체 복원·증거 봉인 후 원자 승격했다. 직전 b810acbc를 rollback으로 남기고 승인된 관리
2세대 수명으로 이전 rollback141f0b17 `922d2ba97a3f919742a99a4041441f332b1682b0b09a17ed40639584ea7a7aba`만 퇴역했다. 다른 기존 자료/
원본/로그/프로필/SDK/Git를 삭제하지 않았다. 개발/최종 소유 임시 root만 자식 종료·소유와
지속 증거 무결성을 확인한 뒤 정리했다. 게시 시점 main·원본 checkout/clean도 별도 확인한다.

단위 계획은 개발512MiB+최종768MiB+추가 archive56MiB+코드4MiB+별도 disk 안전64MiB=
1,472,200,704B다. 최종 시작 필요한 추가 disk 935,329,792B를 재확인했다.
RAM 작업공간4GiB+별도512MiB·추가 메모리9GiB+안전1GiB를 유지한다. 실제 개발/최종 증거는
136.37/356.58MiB다.
단위 시작/현재 disk 26,715,533,312/26,192,916,480B, 관측 순증가 522,616,832B다. 개발/최종 cgroup
표본 peak 14,591,078,400B로 limit 17,179,869,184B 대비 여유 2,588,790,784B다.
이는 tmpfs/컴파일러/cache를 포함한 표본이며 제품 단독 peak·절대 극값·향후 증가량 보장이 아니다.

연결 단절 직전에는80단계만 확인되어 복원본 XLSX/실패 수명·보관을 미확정으로 보고했다.
이후 같은 환경의 실제 읽기 명령이2026-11-08T20:37:21Z에 exit0으로 응답했고, 기존 실행이
82단계/오류0·증거 봉인/원자 승격/소유 임시 정리까지 완료한 기록과 로그를 회수했다.
구성 API의 connected 표시만으로 회복을 판단하지 않았으며 새 빌드/검사나 마지막 수정은
재실행하지 않았다. 45초 exec-server recovery timeout의 인프라 원인과 초기 빈 화면 원인은
확정하지 않는다. 원격 확인 뒤 문서만 추가하며 실제 패키지/제품 source는 위 동결 SHA다.
