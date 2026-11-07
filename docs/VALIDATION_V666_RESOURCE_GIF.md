# v666 GIF 미리보기 검증

제품·검사 동결 `f7743cd01a9dd729b902b27297b00c7f72dd29b8`. 후속 문서는 제품/검사 코드를 변경하지 않는다.
최종 **57단계(신규 57·재사용 합산 0)**:
독립 LF 23·CRLF 23·새 패키지/전체 복원/실패 수명관리 11.
별도 개발5단계와 실패/보정 기록은 최종 수에 더하지 않는다.

원본 v666 GIF 그림 분류와 원래 contain `<img>` 화면을 [GIF 지원 경계](V7_RESOURCE_GIF.md)에
연결했다. 참조 ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`
및 CSS·메뉴·배치는 그대로다. 파일1MiB 이하·축16384·64프레임 이하이며
logical canvas 전체×프레임 수를 개별16MP/공유32MP 논리 lease로 계산한다.

| 검사 | 실제 확인 |
|---|---|
| LF/CRLF | 독립 Git objects/checkout·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한 제품3파일/asset size·SHA·원본 레이아웃·계약 guard |
| metadata/lifetime | GIF87a/89a 전역/지역 palette·logical screen/프레임 범위·control/disposal·sub-block/trailer, palette 상속 거절·truncated/reserved/interactive/초과 프레임·가중 픽셀 예산, mixed lease·취소 불가 bitmap·중복/late/failure·API 부재 |
| 실제 browser | interlace·전역/지역 palette RGB, 기본 프레임 alpha, 실제 GIF89a 두/세 프레임·투명도·disposal animation의 compositor RGB, 실제 손상 LZW decoder 거절·bitmap close/URL 정리 |
| 실제 engine UI | SHA 검증 사본·일반 MIME, contain 화면·기본 픽셀/실제 애니메이션, SVG/HTML 위장·예약/interactive/truncated/oversized 거절, 손상 codec/제어 실패·명시 retry·API 부재/복구 |
| 편집/수명 | 읽기/bitmap late·닫기/재열기, 인라인 이름·설명·확인 삭제, cold에서 ID/hash만 복원하고 bytes 재조회, 실제 읽기 권한 거절/복구, Home/동일 namespace 다른 프로젝트 격리·별개 chat 입력 유지 |
| 회귀 | 기존 PNG/JPEG/WebP/BMP metadata와 실제 codec/pixel·수명, 원본 자료 진입·GIF와 기존 형식의 공통 lease, 선택합계4MiB 원자 보관·실패/CAS/응답 유실·취소/cold와 닫힌 목록/Home 로딩 보호 |
| 새 패키지/전체 복원 | Windows 교차 생성/probe, 새 생성본과 전체 전개본에서 GIF/BMP/전송 UI 새 실행, 전체 SHA/CRC/파일·디렉터리 mode, 반복/FIFO/실패·자식 종료 뒤 증거 보존과 owned 임시 정리 |

실제 원본 GIF bytes를 native browser codec에 전달한다. 새 변환기·가짜 프레임·타이머로
애니메이션을 만들지 않는다. Canvas drawImage는 HTML 규칙상 기본/첫 프레임을 사용하므로
초기 개발의 canvas motion 기대 실패는 fixture 오류였다. 같은 실제 GIF의 compositor screenshot
pixel로 움직이는 두/세 색상을 확인했다. 정지/alpha canvas pixel과 화면 animation을 구분한다.
[GIF 사양](https://www.w3.org/Graphics/GIF/spec-gif89a.txt)과
[HTML image source 규칙](https://html.spec.whatwg.org/dev/canvas.html#image-sources-for-2d-rendering-contexts)을 따른다.
개인 파일/외부 자료 대신 코드로 생성한 fixture만 사용했다. 첫 프레임의 실제 손상 codec 거절과
제어한 Promise 실패를 구분하며 모든 후속 프레임의 LZW를 별도 decoder로 검증했다고 주장하지 않는다.

제품 변경은 `resource-images.js`, 안내 문자열의 `resource-previews.js`, 두 자산의
`WebBundle.csbody` hash/size뿐이다. GIF 분기·타입 gate·GIF 전용 정확 치수 조건을 제거하면
기존 PNG/JPEG/WebP/BMP 코드가 그대로인 byte 대조를 수행했다. native 저장·권한·v1 문법·
공개/override 계약·C#·ReviewConfirm/최종CAS·자료 전송/편집기·CSS/vendor/asset 수는 바꾸지 않았다.

native provider/controlled-CAS·입력 복구의 상세 불변 참고는 직전 신규61단계
`/workspace/artifacts/v536-verification-managed/runs/95b2e233c0764e00a6337a73c899cbab.json`다. 전체 증거/manifest 무결성과 source간
native/관련 probe·fixture diff 없음, SDK/NuGet fingerprint 동일을 확인했다. 이 component 참고는
위 신규 수나 재사용 합산에 포함하지 않는다. 변경된 이미지·UI·빌드·패키지/복원은 모두 신규다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/578bcf7ac8d845909a9668d7598b4c59.json`
- 증거 ZIP SHA256: `b5b69991fd9011f15e32f4ed492c6e6e01fa08317768bd5dfa3e78c6ff667b67` (3,648,342B)
- 개발 기록: `/workspace/artifacts/v536-verification-managed/runs/43cf5aa51fc14ebe908887642c7046de.json`
- 선행 실패/보정 기록: 1개, 별도 보존·중복 합산 없음.
- 모든 기록은 archive/manifest 전체 확인 후 cleaned, 각 owned root 부재 확인.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `f7743cd01a9dd729b902b27297b00c7f72dd29b8` | `5bad26bb626ebb8ce54b6b5c0b6a8e781d5261e09fa007941d4e4cf030460837` | 53,803,176 | 2703/158 |
| rollback | `416396dbcdaf5deedae705d94b0116c16d23b52e` | `5032d15756c574f679d50b0601f01a50a2ef19a82582237647fe729a0d5eb36a` | 53,802,814 | 2703/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `a64633de07e17509016730c427b56e0ee844fa2b9cdf9c440dadc45585280290`, rollback manifest `4ae0b054e4df5dbf4a007bede66ecef601443be19b3bfd64fcff0abf9962c4c6`.
직전 정상 전송/로딩 복구 패키지를 rollback으로 남겼다. native 데이터/개인 문법은 같으며
rollback에서도 기존 사본을 읽고 GIF는 이전 미지원 표시로 남는다. 관리형 원자 승격과 이번
실행이 만든 임시물 정리만 수행했고 과거 자료·원본·SDK·로그·프로필·사용자 데이터는 삭제하지 않았다.

사전 확인 이후 순증가 6,750,208B (약 6.4MiB),
최종 실행 자체 순증가 5,009,408B, 여유 1,089,196,032B
(약 1.01GiB). 향후 단위당 증가량 보장이 아니다.
사전 candidate56+증거20+코드/Git8+안전64=148MiB, RAM3GiB+여유512MiB,
추가 memory7GiB+안전1GiB를 유지했다. 단계 표본 최소 여유 1,094,131,712B,
cgroup peak 7,268,806,656B는 압축/승격 순간 전체 최저 측정은 아니다.

논리 pixel lease는 브라우저 실제 memory/CPU 해제의 hard 상한이 아니다. GIF user-input·Plain
Text/알 수 없는 extension·예약 disposal·64초과 프레임·예산 초과, 큰 파일·다른 원본 형식은
지원 완료가 아니다. 초기 빈 화면은 원인 미확정이다. 실제 Windows/WebView2/mobile·전체 UI·
Space/Library 전달은 미실행이며 실제 Linux 엔진/Chromium과 교차 패키징/복원 검증을 구분한다.
