# v666 정지 AVIF 검증

제품·검사 동결 `8c861c7223414f77596666c8f0f465fb76cfc2bf`. 후속 문서는 제품/검사 코드를 변경하지 않는다.
최종 **57단계(신규 57·재사용 합산 0)**:
독립 LF 23·CRLF 23·새 패키지/전체 복원/실패 수명관리 11.
개발6단계와 기존 GIF DOM 예비 기록은 최종 수에 더하지 않는다.

원본 v666 AVIF 분류와 원래 contain `<img>` 화면을 [정지 AVIF 지원 경계](V7_RESOURCE_AVIF.md)에
연결했다. 참조 ZIP SHA256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`
및 CSS·메뉴·배치를 보존한다. 1MiB 이하의 자체 mdat·기본 SDR8 색상과 선택 alpha를 다루며,
양쪽의 실제 reduced-still AV1 최대 치수와 연결된 ispe·codec/pixel 속성을 함께 검증한다.

| 검사 | 실제 확인 |
|---|---|
| LF/CRLF | 독립 Git objects/checkout·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한 제품3파일/자산 size·SHA·원본/계약/레이아웃 guard |
| metadata/lifetime | primary/alpha·항목/속성/extent 연결·OBU/실제 sequence 치수·8bit 설정, 잘린/변조/시퀀스/transform/외부 data reference·겹침/남는 데이터 거절, 색상/alpha 합산16MP 경계와 기존 PNG 공유32MP·취소 불가 bitmap·late/repeat/failure/API 부재 |
| 실제 browser | AVIF444/420 SDR RGB와 alpha0/128/255, 실제 손상 AV1 decoder 거절, metadata만 바꾼 치수/다른 깊이/sequence 거절, bitmap close/URL 정리 |
| 실제 engine UI | SHA 검증 사본·일반 MIME, contain pixel·alpha, SVG/HTML 위장·손상/미지원·치수 불일치 거절, 제어 실패/실제 codec 실패·명시 retry·API 부재/복구 |
| 편집/수명 | read/bitmap late·닫기/재열기, 이름/설명·확인 삭제, cold에서 ID/hash만 복원하고 bytes 재조회, 실제 읽기 권한 거절/복구, Home/동일 namespace 다른 프로젝트 격리·별개 chat 입력 |
| 회귀 | PNG/JPEG/WebP/BMP/GIF metadata, 실제 GIF/WebP/BMP codec/pixel·애니메이션·공유 lease, GIF/BMP engine 수명과 선택합계4MiB 원자 전송·실패/CAS/응답 유실/취소/cold·숨김 목록/Home 보호 |
| 새 패키지/전체 복원 | Windows 교차 생성/probe, 새 생성본과 전체 전개본에서 AVIF/GIF/전송 UI 새 실행, 전체 SHA/CRC/파일·디렉터리 mode와 반복/FIFO/실패·자식 종료 후 증거/owned 임시 정리 |

AVIF 컨테이너의 임의 ispe만 추정하지 않고 각 항목 association·데이터 위치·실제 AV1 reduced
header를 대조한다. 프레임 entropy는 새로 구현하지 않으며 실제 native browser codec이 디코드한다.
알파 표면도 예산에 포함한다. 픽셀 평가는 손실/색공간 roundtrip의 작은 오차를 허용하며 색상과
0/128/255 alpha를 각각 확인한다. 거대한 표면의 실제 decode를 실행하는 대신 실제 생성된
AVIF 헤더/sequence를 단위 검사에서 정확히 경계 비교하며, 실제 browser pixel은 작은 fixture로 검증한다.
[AOM AVIF v1.2.0](https://aomediacodec.github.io/av1-avif/v1.2.0.html)과
[AV1 bitstream specification](https://aomediacodec.github.io/av1-spec/av1-spec.pdf)을 근거로 한다.
개인 파일/외부 자료 대신 코드로 생성한 fixture만 사용했고 runtime encoder/vendor를 추가하지 않았다.

제품 변경은 `resource-images.js`, 안내 문자열의 `resource-previews.js`, 두 자산의
`WebBundle.csbody` hash/size뿐이다. AVIF 분기·타입 gate·정확 치수 조건을 제거하면 기존
PNG/JPEG/WebP/BMP/GIF 코드가 그대로인 byte 대조를 수행했다. native 저장·권한·v1·공개/override·
C#·ReviewConfirm/최종CAS·완료 편집기/자료 전송·CSS·vendor/asset 수는 바꾸지 않았다.

변경 없는 native provider/CAS/입력 복구의 상세 참고는 신규61단계
`/workspace/artifacts/v536-verification-managed/runs/95b2e233c0764e00a6337a73c899cbab.json`다. PNG/JPEG/WebP와 기존 원본 자료 메뉴의
native UI 참고는 `/workspace/artifacts/v536-verification-managed/runs/578bcf7ac8d845909a9668d7598b4c59.json`다. 두 증거/manifest 무결성,
관련 source/probe/fixture 불변·SDK/NuGet fingerprint 동일·기존 renderer byte 불변을 구분해
확인했다. 이 component 참고는 위 신규 수나 재사용 합산에 포함하지 않는다. 변경된 AVIF/UI·
빌드·패키지/전체 복원과 표의 공유 component 검사는 모두 최종 동결에서 신규 실행했다.

- 최종 기록: `/workspace/artifacts/v536-verification-managed/runs/8bc6cfbe28fd42bab14ed2fbd27d340d.json`
- 증거 ZIP SHA256: `a1b06da5f35ef19500938a63c4a0c3fe79a7688f8f504d882c4aea9c09063831` (3,132,398B)
- AVIF 실제 DOM을 포함한 개발6단계: `/workspace/artifacts/v536-verification-managed/runs/a48f945317b44a4ea66f5576ead7e6de.json`
- 기존 GIF DOM/metadata 예비 기록: `/workspace/artifacts/v536-verification-managed/runs/4364cd0ba4344aa4a644fa5c1b30e92c.json` (AVIF DOM으로 합산하지 않음).
- 선행 실패 기록: 0개. 모든 기록은 archive/manifest 전체 확인 후 cleaned·owned root 부재 확인.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `8c861c7223414f77596666c8f0f465fb76cfc2bf` | `02b32d22ad64fe4f6447c70d284639f873e2335509b25d66c782b230f6f903d6` | 53,805,250 | 2703/158 |
| rollback | `f7743cd01a9dd729b902b27297b00c7f72dd29b8` | `5bad26bb626ebb8ce54b6b5c0b6a8e781d5261e09fa007941d4e4cf030460837` | 53,803,176 | 2703/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `aeac8f6c60e6bd3496a8da887ca94391348e0aa68c31c5f9d84119cd633d20af`, rollback manifest `a64633de07e17509016730c427b56e0ee844fa2b9cdf9c440dadc45585280290`.
직전 정상 GIF 패키지를 rollback으로 남겼다. native/개인 문법은 같고 rollback도 사본을 읽으며
AVIF 표시는 이전 미지원 상태다. 관리형 원자 승격과 이번 실행이 만든 임시물만 정리했다.
과거 자료·원본·SDK·로그·프로필·사용자 데이터는 추가 삭제하지 않았다.

사전 확인 이후 순증가 6,160,384B (약 5.9MiB),
최종 실행 자체 순증가 4,378,624B, 여유 1,082,937,344B
(약 1.01GiB). 향후 단위당 증가량 보장이 아니다.
사전 candidate56+증거20+코드/Git8+안전64=148MiB, RAM3GiB+여유512MiB,
추가 memory7GiB+안전1GiB를 유지했다. 단계 표본 최소 여유 1,087,242,240B,
cgroup peak 6,514,765,824B는 압축/승격 순간 전체 최저 측정은 아니다.

모든 AVIF/grid/layer/sequence/transform/HDR·metadata·큰 파일/SVG 지원은 아니다. 논리 pixel
lease는 실제 브라우저 memory/CPU 해제의 hard 상한이 아니다. 초기 빈 화면은 원인 미확정이다.
실제 Windows/WebView2/mobile·전체 UI·Space/Library 전달은 미실행이며 실제 Linux 엔진/
Chromium과 교차 패키징/복원 검증을 구분한다.
