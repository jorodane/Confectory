# v666 정지 BMP 미리보기 검증

최종 동결: `273c1c48cac321e2c39d692dc56ba65cc5be7e46`. 후속 게시는 문서만 변경하며 제품·검사 코드는 같다.
최종 **49단계(신규49·재사용 합산0)**:
LF19·CRLF19·새 교차 패키지/전체 복원/실패 수명관리11.
개발3단계는 최종 수에 더하지 않는다.

원본 v666의 BMP 그림 분류·기존 contain 패널을 [한정된 BMP 지원](V7_RESOURCE_BMP.md)에
연결했다. ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`
및 CSS는 그대로다. 40-byte 정보 헤더·24/32bpp BI_RGB, 실제 stride/픽셀 길이와 signed
높이를 검사하며 1MiB 이하 프로젝트 사본만 실제 브라우저 디코드 후 표시한다.

| 최종 검사 | 실제 확인 |
|---|---|
| 독립 LF/CRLF | 별도 Git objects/checkout·HOME·NuGet·빈 engine cache, Release/MCP·실제 Linux engine, 정확한 제품3개 파일/자산 hash·원본 레이아웃·계약 경계 |
| metadata/수명 | 파일/정보 헤더·reserved/offset/format·signed 치수·padding/길이/예산, PNG/BMP 공통 pixel lease·취소 불가 decode 완료까지 보존·late/repeat/error/mismatch·capability 거절 |
| 실제 Chromium | 24/32비트 상단/하단 방향, 홀수 폭 행 padding, 0 image-size, BGRX의 여러 unused-byte 값에서 실제 불투명 pixel, 실제 unsupported/truncated/oversized 파일 거절·URL 정리 |
| BMP engine UI | LF 정상11·CRLF 수명5: 실제 SHA 확인 bytes/pixel/일반 MIME, 잘못된 형식·제어한 predecoder 거절/명시 retry·API 부재/복구, 늦은 bitmap/read·닫기/재열기, 이름/설명/확인 삭제 |
| cold/권한/격리 | 실제 읽기 거절 후 명시 retry, owner/ID/hash만 복원하고 bytes를 다시 읽기, Home/같은 namespace의 실제 다른 프로젝트와 늦은 응답 격리 |
| 회귀 | 기존 PNG/JPEG/EXIF와 WebP 헤더·실제 codec/pixel·late/실패 수명, 원본 자료 추가 메뉴·선택/목적지·원자 실패/응답 유실/최종 CAS·cold/프로젝트 격리 |
| 패키지/복원 | 새 Windows 교차 패키지/probe와 전체 전개본에서 BMP/WebP/메뉴 UI를 새로 실행, 전체 SHA/ZIP CRC/파일·디렉터리 mode, 반복/FIFO/실패·자식 종료 후 증거 보관과 owned 임시 정리 |

BMP 검사 파일은 생성한 RGB sample뿐이며 사용자 개인 파일/외부 자료를 탐색·업로드하지 않았다.
BMP는 비압축 RGB여서 구조상 유효한 모든 pixel byte가 색을 나타낼 수 있다. 손상/미지원
구조의 실제 거절과 제어한 decoder Promise 거절을 구분한다. 후자는 실제 viewer의 retry/URL
수명 검증이며 실제 codec 취약점이나 손상 entropy 오류로 표현하지 않는다. 이전 WebP의
실제 손상 bitstream decoder 거절도 이번 회귀에서 새로 검사했다.
원본 contain 화면에서 red-top/green-bottom BMP와 제목/설정 패널을 직접 확인했고
source-bound screenshot·`visual-review.json`을 보존했다.

제품 변경은 `resource-images.js`, 안내 문자열의 `resource-previews.js`, 두 자산의
`WebBundle.csbody` hash/size뿐이다. PNG/JPEG/WebP의 parser·decode 동작은 추가한 BMP 분기를
제거하고 조건만 되돌리는 byte 대조로 확인했다. native 저장·권한·개인 schema·공개/override
계약·사용자 C# 원문·완료한 편집기/메뉴·CSS·vendor/자산 수는 바뀌지 않는다. 기존 자료
File/선택1MiB·전체4MiB/64개·전송 한도를 유지한다. 새 기능을 위해 권한을 부여하지 않는다.

native controlled-race/private/provider 세부 검사는 바이트 불변이라 반복하지 않았다.
이전 77단계 `acf81ac09c2a4d999812a3b536e9019b`의 전체 증거/manifest와 source간 native·
프로브 diff 없음/SDK·NuGet fingerprint 동일을 별도 확인했다. 이 component 참고는 위 신규
수와 재사용 합산에 포함하지 않는다. 다른 완료 편집기를 새로 미구현으로 되돌리지 않는다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/f854285a23f8448ea76a09a7a0120043.json`
- 증거 ZIP SHA256: `74959ce19f22e09f07188abffbe42c70804cb8104ccd47d3dfa380c66a06fc02` (2,799,397B)
- 개발3단계: `/workspace/artifacts/v536-verification-managed/runs/1cd566d583d944b5815dd71ccc28f5c5.json`
- 최종/개발은 전체 archive/manifest 확인 후 `cleaned`; 각 owned root 부재 확인.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `273c1c48cac321e2c39d692dc56ba65cc5be7e46` | `0cc0c023568cdd7c9f2926634e6c0444fcbbed8ccaf741767c203a5da3466b22` | 53,799,584 | 2703/158 |
| rollback | `522455d59ae176f25a231edbd7e310d4ed0d8546` | `7a0520f5260fb7cc361787ab0c57e5f6c30df7e3a7b5d1b266b528f52710bf84` | 53,799,375 | 2703/158 |

index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `5dae0cd1965905806ec6b0de76e8d253d7f109e5017497fbbb582dbfcecb49ae`, rollback manifest `acef8bf28874361bb990dde5f1ddff728e4e8e163a0542f7ce803390d4ec1b95`.
rollback은 이전 검증 자료 메뉴 패키지이며 BMP 표시는 없다. native 데이터/개인 문법은 같아
migration 없이 기존 사본을 읽는다. 관리형 원자 승격과 해당 실행의 owned 임시물 정리만
사용했고 과거 자료·원본·SDK·기존 로그/프로필·사용자 데이터는 추가 삭제하지 않았다.

사전 검사 이후 순증가 5,632,000B (약 5.4MiB),
결과 여유 1,107,431,424B (약 1.03GiB).
최종 실행 자체 순증가 4,030,464B. 향후 단위당 보장값은 아니다.
사전 예산 candidate56+증거20+코드/Git8+안전64=148MiB, RAM3GiB+여유512MiB,
추가 memory7GiB+안전1GiB를 유지했다. 단계 표본 최소 여유 1,111,384,064B,
cgroup peak 5,443,026,944B는 압축/승격 순간 전체 최저 측정이 아니다.

BMP의 팔레트·압축·bitfields/alpha·CORE/V4/V5/ICC·다른 offset과 큰 파일/선택 예산 초과,
다른 원본 그림 형식은 지원 완료가 아니다. 16/32MP는 논리적 lease이며 브라우저 실제
CPU/메모리 해제의 hard 상한이 아니다. API/codec이 없는 환경은 거절한다.
mesh는 원본에 실제 renderer 근거가 없다. 간헐 초기화 빈 화면은 원인 미확정이다.
실제 Windows/WebView2·모바일·전체 UI 및 Space/Library 전달은 미실행이며 Linux 자동화와
교차 패키징/복원 검증을 구분한다.
