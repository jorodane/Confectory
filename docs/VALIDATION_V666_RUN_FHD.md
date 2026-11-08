# 명시적 FHD 출력 검증

동결 `47262dc1664552014589b4f92a51a1692c4c0391`의 **총69단계(신규69·동일성 확인 재사용0)**을 통과했다.
[원본 FHD 요구와 지원·호환 경계](V8_RUN_FHD.md)를 따른다.1920×1080·1080×1920의
실제 RGBA8 software pixels와 기존 크기/등록 메뉴를 연결했다. 최종 LF UI 스크린샷에서도
실제1920×1080 ACK와 범위 밖1920×1081 입력 보존/비활성 적용·기존 배치를 직접 확인했다. 기존 Open/OpenHD·공개
입출력/override 계약·권한·원본 C#·Review→Confirm·최종 CAS를 보존한다.

| 검증 | 실제 확인 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks checkout·독립 Git/HOME/NuGet/빈 engine cache, Release/MCP/Linux engine. 원본 ZIP SHA·정확24개 제품 파일·canonical asset·동일 HTML/CSS, 원래 Open/HD/Configured 계약과 기존 producer 본문의 owner/rate/bounds/publish/close 의미 보존 guard |
| 명시 profile/native | FHD configured-before-Present·1920축/2073600픽셀/8294400B, 정확 길이·canonical input·실패 전 revision 유지. 기존 default/HD·thread·소유자·중복 publisher·close/복사/요청 수명 검사를 같은 최종 RunSurfaceTests로 실행. 응답 전/본문 중 연결 중단 뒤 같은 owner/frame/ACK의 재접속·자동 Step 없음. FrameControl/오디오·WebUI observe/scope와 실행/이력·foreign/stale ACK 회귀 |
| 전체 조각·부정 경계 | 고엔트로피1920×1080 전체 Buffer/SHA와 정확11개 조각/index10, 실제 인증 채널의 전체 pixels·표본색/alpha. mixed runtime/revision·SHA 변조·noncanonical +/slash/공백/Unicode·missing/extra parts·잘못된 cap/크기를 신뢰 revision 갱신 전 거절하고 기존 unchanged receipt 보존. 완료/범위 밖/Stop·다른 lease/view/handle은 오래된 cache를 읽지 못함 |
| 실제 원본 메뉴 | 가로 FHD·세로 FHD·기존4:3와 명시 Step 뒤 실제 canvas 크기·표본 pixels, 접수와 실제 출력 ACK 분리. 일시정지 중 자동 Step/Resume 없음. private FHD 등록/cold·범위 밖 입력 보존·기존 HD/640/512 UI/API 및 preset/auto/오디오/bounds/rate 회귀 |
| 중단·입력·원자성 | 조각 변조의 전체 SHA 거절과 같은 paused frame의 읽기 복구, 조각 대기 중 close·새 view·cold 격리. size 응답 유실 뒤 명시 확인이 명령을 재실행하지 않으며 더 새 크기/이름/chat을 보존. foreign/stale/초과 size와 닫힌 form 거절. 실제 private preset 파일의 CAS·동일 request replay·읽기/쓰기 실패·손상/foreign/symlink·32개 한도·프로젝트 왕복/cold |
| 납품 구조/복원 | 새 Windows 교차 패키지/probe와 그 안의 실제 Linux 엔진/UI(FHD normal/parts·기존 wide), 전체 ZIP CRC·파일 SHA·파일/디렉터리mode 복원 및 FHD lifecycle/parts·wide lifecycle. 실패 수명관리와 증거 보관 후 소유 임시 checkout/cache/build 종료·정리 |

전역 RPC/관측 결과2MiB·child packet1400000B·native pipe I/O300ms는 유지했다. FHD profile의
max/maxPixels와 모든 조각 정체성/길이·전체 SHA를 검사한 뒤 프레임을 교체한다. 읽기와
실제 작업/ACK·3D 이동은 별도이며 화면 완성을 실행 조건으로 만들지 않는다.
FHD preset은 같은 JSON v1/ID/receipt/CAS다. 이전1280 한도 reader의 큰 항목 거절 가능성을
문서화했고 자동 이행/삭제/축소하지 않는다. 현재 기본/HD provider는 각 실제 cap으로 적용을
제한한다. 이전 binary 자체를 이번 환경에서 실행했다고 표현하지 않는다.

개발 record `/workspace/artifacts/v536-verification-managed/runs/9bacff0aef96436db37a2e0058cdf64c.json`
의11단계 native/API/UI와 실제 FHD 스크린샷을 확인했다. uncommitted overlay에 대한 개발
검증이며 최종 수에 더하거나 재사용하지 않았다. 동결 전 기존 오류 문구 보존·검사 label/
스크린샷 이름·FHD private preset의 긍정 입력을 정리했고 최종 source 전체를 새로 검증했다.
첫 최종 실행06d1d5a1은 선행18단계 뒤 첫 정상 관측의 surface-unavailable로 중단했고
봉인된 실패 증거를 보존했다. generic 실패 신호만으로 원인을 확정하지 않았다. 정상 초기 관측만20회/50ms의 읽기로
재확인하고 실제 invoke 수 불변을 검사했다. 제품/native300ms/패킷 한도는 바꾸지 않았다.
손상 주입 모드는 재시도로 거절을 숨기지 않는다.
두 번째 bdae2cc8도20회 모두 unavailable로 실패했다. 그 실행의11건 재사용은 봉인된 선행
LF 동일 코드에만 적용했으며, 이후 실제 producer/reader 코드를 수정했으므로 이번 최종에는
적용하지 않았다. 진단용 aee943f0에서7/8번째 조각 연결 시302–307ms 취소를 기록했다.
producer의 전체 pixel 노드 반복 복제와 native 조립/캐시 metadata의 큰 복제를 제거하고,
중복 전체 wire 정규식 스캔 대신 같은 canonical URL roundtrip·정확한 길이/전체 SHA를
검사한다. 원래 SHA를 유지하는 +/slash 치환·공백/Unicode wire 입력도 거절했다.
이후 결정적으로 재현한 pipe 수명 결함은 응답 전/큰 본문 중간에 클라이언트가 종료되면
IsConnected=false인 broken stream의 Disconnect를 건너뛰어 다음 정상 관측도 실패하는 것이다.
기존 코드의 phase5 실패와 수정 후3회 성공을 보존했다. finally 정리는 연결 상태에 관계없이
reset을 시도한다. 같은 runtime/frame0/ACK0·기존 reader가 유지되며 Step/명령 재실행은 없다.
한 중간 실패는 제품 복구가 아니라 추가 stdout으로 인한 exact Output fixture 불일치였고,
최종 회귀에서 문구를 바로잡아 재검증했다. 계측 없는 제품의 native·독립 API5회·faults·UI3모드
11개 개발 단계도 통과했다. 이 개발 증거는 최종 수에 더하지 않았다.
세 번째 최종 c62ef89a는 회귀용 pipe 이름과 독립 LF TMPDIR의 합이 Linux socket108자
한도를 넘어 본문 진입 전 실패했다. 검사용 고정 prefix만 줄이고 무작위 ID와 실제 중단/
재접속 검증·제품 코드를 유지했다. 실패 ZIP도 보존했다. 현재 최종 검사 source 전체를
새로 검증했으며 이전 검사를 재사용하지 않았다.
300ms는 I/O cancellation 예산이며 CPU 검증/직렬화를 포함한 전체 호출 시간 보장은 아니다.
일시 실패의 generic 신호만으로 선행 모든 실패의 원인을 같다고 단정하지 않는다. 앞선 큰 그림 단위의 실패/복구 증거는 그대로 보존한다.

## 지속 보관과 공간

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/094c022494424c118e73e5f2d5d23ef4.json`
- 증거 ZIP SHA256: `7bc3ca94dfb6572bb329993277228bbfa1a34b3c12a554e54b30d5bed0008e45` (2,968,409B)
- 승격 전 index: 최종 증거 ZIP의 `package-index-before.json`
- 승격 후 동반 index: `/workspace/artifacts/v536-verification-managed/runs/094c022494424c118e73e5f2d5d23ef4.closing-index.json`, SHA256 `404486154134f0b54740ba8743685a9a38fe7958f3ed2fd00cd7036f41825ba9`

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `47262dc1664552014589b4f92a51a1692c4c0391` | `3c84f7d4b3671fb074930680f12422da67856d6cfc5e459b7c194fa527363b6d` | 53,825,178 | 2718/158 |
| rollback | `a91bd900a22256647351810e8e6868a83e9540d2` | `9f62d0b9a127729f1817a63a80ad732a9b22360be6eee6dd431a5317814f28e5` | 53,822,037 | 2712/158 |

새 전체 복원과 지속 증거를 검증한 뒤 두 세대 방식으로 원자 승격했다. 직전 정상a91bd900을
rollback으로 보존하고, 이전 관리 rollback9588568e `8f310ebfcddc4ad78f1d505bcd11521ba452d63059eff600dea2c42adeb1efbf`만 승인된 세대 수명으로
퇴역했다. rollback의 기존 전체 복원 증거와 동일 ZIP/전체 manifest를 보존하고 이번에
ZIP SHA를 재확인했다. rollback 구버전 엔진 자체는 이번에 다시 실행하지 않았으며,
새 FHD preset/함수의 구버전 읽기 한계는 그대로다. 다른 기존 원본·로그/프로필·SDK/Git·개인/사용자 자료는 보존한다. 실행이 직접 만든
임시물만 자식 종료/소유권을 확인해 정리했다. 코드·문서·검사만 Git에 게시하며 마지막 문서
마감 뒤 runtime/검사/패키지 source가 동결 코드와 같은지 확인한다.

추가 디스크 264,241,152B(archive56MiB·증거128MiB·코드4MiB와
**별도 안전64MiB**), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다.
최종 실행 전/후 여유 30,346,203,136/30,340,837,376B, 차이 5,365,760B다.
개발 증거까지 포함한 이번 단위 시작/종료 여유는 30,362,587,136/30,340,837,376B다.
최종 신규 단계 표본 최저 디스크 30,346,125,312B·관측 cgroup peak
5,864,882,176B이며 모든 순간의 절대 최저/최대나 이후 고정
증가량 보장은 아니다. 원래 안전 기준을 낮추거나 증거를 버려 예산을 맞추지 않았다.

기존 환경 연결/SDK10.0.401·seed/범위와 최신·롤백 무결성을 확인했다. 기존 원본 checkout과
main은 변경하지 않는다. 초기 빈 #app의 원인은 미확정이다. 실제 Windows/WebView2·모바일·
DPI/IME·GPU/모니터 FPS·물리 오디오·전체 UI·Space/Library 전달은 미실행/미완료다.
QHD/4K/FHD+·실제 신원/권한 backend·큰 다른 자료 형식/4MiB 초과는 기존 잔여다.
M11/M12/M4를 구체적 회귀 없이 다시 열거나 해상도/타입 조합을 새 필수 항목으로 늘리지 않는다.
