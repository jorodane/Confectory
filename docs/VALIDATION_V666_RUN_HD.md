# v666 명시적 HD 소프트웨어 출력 검증

최종 제품/검사 동결 `d23d6324a731a6558ccb2e6db694ca569984ce35`. 제품은 원동결b7816f6a와 같고 후속 세 커밋은
검사의 닫기 선택자·disabled 판정·Stop 전 읽기 재확인만 수정했다. 문서 마감은 제품/검사 코드를 바꾸지 않는다.
최종 **65단계(신규 35·동일성 확인 후 재사용 30)**:
독립 LF 28·CRLF 26·owned IPC/새 패키지/전체 복원/실패 수명관리 11.
개발·선행 실패·도구 진단은 최종 통과 수에 중복 합산하지 않는다.

[지원 경계와 API](V8_RUN_HD.md). 원본 v666 ZIP SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`의 해상도 배열에서
HD가로1280×720/HD세로720×1280/4:3 1024×768을 원래 메뉴에 연결했다.
CSS/팝오버/form·기존640 선택·직접 입력/등록 구조는 유지한다. 실제 opt-in provider가
RGBA를 생성하고 size ACK/전체 SHA를 확인한 경우에만 canvas 크기를 바꾼다.

| 검사 | 확인한 실제 경계 |
|---|---|
| LF/CRLF | 독립 Git objects·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한 제품25파일/자산 hash·원본 메뉴·기존public ABI·권한/레이아웃/패킷 ceiling guard |
| 조각/표시 | deterministic xorshift 잡음1280×720 RGBA의 전체5조각/전체SHA, exact metadata/순서/길이·canonical base64, 혼합 publisher/revision·누락/변조·범위/잘못된cap 거절 |
| 실제 native pipe | 원래 인증 handle/secret/request/frameRuntime에서 전체 프레임을 검증한 뒤 bounded observer slice로 전달; 동작 중 producer와 분리한 coherent snapshot, foreign view/lease/handle·완료/retired/Stop 전송 거절 |
| 실제 native 회귀 | OpenHD의 명시 Configure·단일 실제owner·초기/byte/area/축/revision/copy 거절, 기존Open 예산 불변, 오디오·미보관 관측/취소/pack 경계; 실행 제어·history CAS/오류/cold·잘못된ACK·경계순서·pause/step/reconnect/stop·provider locality |
| 실제 browser UI | HD가로/세로/4:3 각 한 번의 크기 명령, pause 중 프레임 유지·명시Step 뒤 실제 픽셀, private HD등록/cold/no replay, 초과 입력 보존, 기존640/legacy512·자동 맞춤/오디오/선택 경계/발행FPS |
| 실패/중단 | source fake producer가 보낸 mixed/변조/초과/누락/cap 오류는 trusted native revision을 대체하지 않음; browser-only 조각 변조는 전체SHA에서 거절·같은 paused 프레임을 읽기만으로 복구 |
| UI 수명 | 늦은 accepted 크기 응답/입력·명시재확인/no command replay, 보이는 탭 닫기로 중단한 late slice는 새 창을 그리지 못함; cold는 실행/픽셀/조각을 재개하지 않음 |
| 새 패키지/전체 복원 | Windows 교차 생성/probe, 생성본과 전체 전개본에서 HD정상·유실/중단·640회귀 새 실행, CRC/SHA/전체파일/디렉터리 mode 확인 및 FIFO/예외·자식 종료 뒤 owned 임시 정리 |

최초 raw producer snapshot은 기존1,400,000B packet 안의 최대5조각이며 전체300ms deadline을
공유한다. 이는 I/O deadline이며 GC/CPU의 절대 실시간 보장을 뜻하지 않는다. native는 SHA 확인 전 trusted metadata를 바꾸지 않는다. browser 전송도 기존
8KiB 입력/2MiB 결과 안의786432B 단위이며 별도 SHA 확인 후에만 그린다. 전역RPC/FrameControl
한도, heartbeat/ACK·실행 조건은 바꾸지 않는다. HD는 ConfigureSize/RequestedSize를 직접
선택한 profile이다. 기존 readonly/640 Open을 자동 HD 전환하지 않는다.

사용자 자료·부모/참조 원본·사용자 C#·기존 public/override 계약·Review→Confirm/source CAS는 변경하지 않는다.
바뀐 C#은 출력/관측/해제 runtime pack 구현과 새 예제이며 기존 사용자 프로젝트 본문은
자동 재작성하지 않는다. 원래 resizable/software/audio/bounds 예제의 bytes도 그대로다.
새 HD 예제의 API와 같은 loop를 가진 생성 소유 프로젝트에서 실제 engine/브라우저를 실행했다.
기존 등록 파일 구조/ID/receipt/CAS는 유지하지만 큰 preset은 이전640 전용 reader가 읽지
못할 수 있다. 새 API/조각/cap는 짝맞춘 provider/reader/UI가 필요하며 이를 migration으로
숨기거나 목록을 삭제·축소하지 않는다.

기존 V7 그림/자료 source·Core/targets·FrameControl·오디오 source는 변경하지 않았다.
별도 자료의 참고 기록 `/workspace/artifacts/v536-verification-managed/runs/9fdf62c1e51f46a1871999226e08077c.json`의 ZIP/manifest와 관련
source 불변·SDK/NuGet 입력 동일성을 확인했다. 이 참고는 신규나 재사용 합산에 넣지 않는다.
HD·관측·시작/중단 backend는 바뀐 범위에 맞춰 위의 실제 native/API/UI 회귀를 수행했다.

재사용30개는 b7816f6a의 LF 보조/native/프로젝션/API faults11개,73f60e05의 HD정상/중단UI2개,
a49cd0a5의 LF legacy회귀8개·CRLF 보조/native/프로젝션9개다.
제품·해당 검사·fixture·SDK/NuGet·정규화 명령의 동일성, 봉인된 결과/로그/전체 manifest와
세 선행 실행의 실패 지점을 확인했다. 두 UI oracle만 바뀐 검사와 별도로, API normal의
Stop 전 읽기 재확인 변경은 LF/CRLF 양쪽에서 새로 실행하며 앞선 API normal 성공도 재사용하지 않는다. 변경SDK/변경제품을 거절하는
negative guard를 각각 실행했다. selector-recovery-driver.py·selector-reuse.json·각 reused
결과를 최종 증거에 보존한다. 실패 검사·빌드·패키지는 재사용하지 않았다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/69d34a616875406099cec7997534c916.json`
- 증거 ZIP SHA256: `ed37753e719e3c125bbf24bf8e8ba20143cf896315f4bf25e7666510a5dc5160` (1,693,552B)
- 개발의 실제HD API/UI 기록: `/workspace/artifacts/v536-verification-managed/runs/042c5eab9c40476789689e1ee812420e.json` (최종 수 제외)
- 선행 실패 5개: C# 지역변수 shadowing, 문서모드의 숨겨진 제목줄 닫기 선택, label에 감싼 select의 Playwright option-disabled 판정, CRLF API의 Stop 직전 한 번의 unavailable 관측, 재사용 guard에서 같은Python 바이너리의
실행 경로 차이(python/python3) 거절. C#·두 UI oracle은 수정했고 실행 경로는 원래python3로
맞췄으며 guard를 완화하지 않았다. unavailable 관측의 원인은 확정하지 않았다. 모두 증거를 보존했다.
- 선행 record: `/workspace/artifacts/v536-verification-managed/runs/17e01e0ba6ee4445a7780d0df6dd8cd7.json` / SHA256 `f7fe5231515e7346e7e752e63d916affb8bb1c5e4a0a940d42e676b10a51364d`.
- 선행 record: `/workspace/artifacts/v536-verification-managed/runs/2f30dd2b6a804f1d873e1715fa35d1bb.json` / SHA256 `5825df3ffd103d1f9858bb681f5e2c51c662a809878258e947640953f2e548e6`.
- 선행 record: `/workspace/artifacts/v536-verification-managed/runs/6a64db54af744346848f5bd0db6dda3a.json` / SHA256 `727962677540f7089072f02563f595980ba6c5a53c8b7bdcae59903654ad27b7`.
- 선행 record: `/workspace/artifacts/v536-verification-managed/runs/be6c9cccb36a4c13890820900b85280b.json` / SHA256 `21f53ea2f9625586338484b0c5f001df23eab24d06099dd75ecaa1fdd25e79f4`.
- 선행 record: `/workspace/artifacts/v536-verification-managed/runs/cbb9089ebae046509c5dd63a2eb4b4fc.json` / SHA256 `45f51727ec451dbb6d96a6a7459af9ea98ca1d488ec1593241d82eb359ea481c`.

label 진단은 별도 최소 browser 두 개로 확인했다. 기본 select는 DOM.disabled/:disabled와
matcher 모두 disabled였지만 label로 감싼 동일 option은 DOM.disabled/:disabled=true,
Playwright isDisabled=false·matcher enabled였다. 실제 HTML 속성으로 검증을 고쳤고
기존Native 크기 거절/실제legacy 메뉴 회귀를 유지했다. 제품에 HD를 허용한 오류가 아니었다.

Stop 준비의 관측 재확인은 최대20회/50ms 간격의 읽기 전용 관측으로 한정했다. 명령을
다시 실행하지 않으며 SHA/원본/권한 거절 검사와 최종 Stop 뒤 slice 거절을 유지한다.
계속 unavailable이면 마지막 관측과 실행 상태를 기록해 실패하며, 회복 시 관측 이유를 로그에 남긴다.
최종 LF·CRLF normal은 이 추가 재관측 없이 통과했다.
일시 관측의 원인이 수정됐거나 실행 명령의 자동 재시도가 허용됐다고 표현하지 않는다.

- 진단 record: `/workspace/artifacts/v536-verification-managed/runs/a5d3e8b085f542d19aa7a586294dc5b8.json` / SHA256 `33b2d5233763c8cf2b128b2fb640046a97f13c58a84b9d1259545f02fa6bfa04`.
- 진단 record: `/workspace/artifacts/v536-verification-managed/runs/d58f2d6c57a947d1af2402d1b3628d2a.json` / SHA256 `708a8868aa747b9be2d98914d5a5cafd620cc04e09c3a6c43b3d857429404299`.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `d23d6324a731a6558ccb2e6db694ca569984ce35` | `8ca5254ee138e342cb533ab8811c250a059a73cd7bb17c22878a592678ad89bb` | 53,815,396 | 2710/158 |
| rollback | `431b574a540556b581d4aadaef8691e5a45a33b5` | `4c4a93c7b28a7e84792fc98232d1c733df2460565ded1068915dfe9183ce8210` | 53,808,866 | 2704/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `781a543da0e6fa363a618a4b11b98f1c6bdcef4dcac862ea8a25b85baa8cf479`, rollback manifest `7cf07e6de39d86bb53554f5169b4a99a1f3d31dfe06fe5fa11fcad8f9b7af9ca`.
직전 정상 SVG 패키지를 rollback으로 남기고 기존 승인된2세대 원자 승격만 사용했다.
증거의 전체 manifest/CRC/SHA와 모든 owned root 부재·자식 종료를 확인했다.
원본·과거 자료·SDK·Git·사용자 파일·로그/프로필은 추가 삭제하지 않았다.

보관 검증 시점의 단위 순증가 11,448,320B
(약 10.9MiB), 최종 실행 순증가 2,793,472B,
여유 1,064,267,776B (약 0.99GiB).
사전 disk256MiB+안전64MiB, 임시 filesystem3GiB, 추가 memory7GiB+안전1GiB를 확인했다.
이번 최종 실행의 신규 단계 표본 최소 disk 여유 1,066,876,928B, cgroup peak 5,968,535,552B는 모든
압축/승격 순간의 hard 최저/최대 측정이 아니며 향후 증가량 보장도 아니다.

잔여는 HD profile을 넘는 FHD/4K·GPU/물리 출력/장치, 큰 자료, 실제 멤버·권한 backend와
그에 의존한 다른 참여자/공유, 기존 명시 ABI 미지원 흐름 등이다. M11/M12/M4를 확인된
회귀 없이 다시 열거나 가능한 조합을 무한한 필수 항목으로 늘리지 않는다.
초기 빈 #app 원인은 미확정이다. 실제Linux엔진/Chromium·교차패키지/복원과 실제Windows/
WebView2·모바일·DPI/IME·전체UI·Space/Library 전달을 구분하며 후자는 미실행이다.
