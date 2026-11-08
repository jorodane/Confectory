# v666 자체 포함 정지 SVG 검증

제품·검사 동결 `431b574a540556b581d4aadaef8691e5a45a33b5`. 후속 문서 마감은 제품·검사 코드를 바꾸지 않는다.
최종 **60단계(신규 24·재사용 합산 36)**:
독립 LF 24·CRLF 24·새 패키지/전체 복원/실패 수명관리 12.
개발/선행 실패 기록은 최종 통과 수에 더하지 않는다. 제품/검사 원동결7b3cd6e1에서 패키지 suite 연결만 수정한431b574a 기준이며 제품과36개 재사용 검사·SDK/NuGet·명령은 동일하다.

원본 v666 `app.js`의 SVG 이미지 분류와 `resource-preview.js`의 Blob/`img`·contain·URL
종료 흐름을 [소유 정지 SVG 표시](V7_RESOURCE_SVG.md)에 연결했다. 원본 ZIP SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`, 창·CSS·설정 배치를
그대로 대조했다. 새 제품 파일은 SVG profile helper 하나이며 기존 image renderer/안내 문자열과
명시적 bundle 자산 hash/size를 함께 갱신했다. native/public/override/C#/권한/저장/CAS는 불변이다.

| 검사 | 확인한 실제 경계 |
|---|---|
| LF/CRLF | 독립 Git objects/checkout·HOME·NuGet·빈 engine cache, Release/MCP/Linux engine, 정확한4파일 제품 목록·자산 size/SHA·원본/CSS/계약 불변 guard |
| 실제 Chromium | 명시 크기/viewBox 전용, 도형·경로·text·gradient/clip, RGB/alpha0·128·255 픽셀과 원본 bytes 불변, 실제 격리 image decode/URL 해제 |
| 표시 거절 | XML 파싱 전 DTD/entity/처리명령, script/이벤트/외부 URI/style/animation/foreignObject/filter/잘린 XML·경로/유효하지 않은 참조·중복 ID·재귀 clip·복잡도/크기/입력 예산 |
| 공유 수명 | controlled decode hold에서 닫힌 image의 lease를 promise 완료 전 반환하지 않음, 전체32MP/한개16MP, 반복 정리·닫기/재열기/늦은 read/decode 격리 |
| 실제 engine UI | SHA 확인 SVG·일반 MIME의 실제 contain 픽셀, viewBox/gradient/geometry/alpha, 명시 retry, decoder API 부재/거절·복구, 이름·설명·확인 삭제와 별개 chat 입력 보존 |
| 재시작/소유 | cold에서 owner/ID/hash만 복원하고 bytes 재조회, 실제 native 읽기 권한 거절과 복구, Home 왕복·같은 namespace 다른 실제 프로젝트 격리 |
| 회귀 | PNG/JPEG/WebP/BMP/GIF/AVIF metadata, 실제 SVG/AVIF/GIF/WebP/BMP codec·공유 수명 DOM, AVIF/GIF engine UI, 선택 합계4MiB 전송의 원자 저장/충돌·실패/응답유실/취소/cold |
| 새 패키지/전체 복원 | Windows 교차 생성·probe, 생성본과 전체 전개본에서 SVG/AVIF/전송 UI 새 실행, ZIP SHA/CRC/전체파일 hash·디렉터리 mode와 FIFO/실패·증거 보관 뒤 owned 임시 정리 |

SVG는 최대256KiB, UTF-8, 축16384/16MP와 제한된 자체 포함 정지 profile이다.
전체 SVG 표준·필터/외부 자산/애니메이션·SVG 편집을 지원한다고 주장하지 않는다.
DOMParser 전의 DTD/처리명령/입력 경계를 두며, 속성/요소/참조를 승인 목록으로 확인한다.
검증 XML을 페이지 DOM에 삽입하지 않는다. 명시적 bounded viewport를 가진 표시용 derivative를
Blob/image로 디코드하며 원래 도형·저장 bytes/hash/ID는 유지한다. viewBox 전용 파일도 같은
한도를 따른다. 실제 Chromium이 SVG Blob을 bitmap decoder에서 거절한 선행 결과를 보존했고,
격리 HTMLImageElement.decode로 연결한 최종 코드에서 픽셀을 다시 확인했다.

큰 surface의 실제 비용 hard 상한을 가정하지 않는다. shared lease hold는 controlled promise
시험이며 실제 브라우저 pixel 검증과 구분한다. decoder 거절/API 부재·late 응답 hold도 fixture
제어 시험이고 native 저장 읽기 권한 거절·재시작은 실제 임시 소유 프로젝트에서 확인했다.
개인 파일/외부 자료 대신 생성한 SVG만 사용했으며 runtime/vendor를 추가하지 않았다.

변경 없는 native provider/CAS/입력 복구의 상세 component 참고는
`/workspace/artifacts/v536-verification-managed/runs/95b2e233c0764e00a6337a73c899cbab.json`다. PNG/JPEG/WebP와 원본 자료 메뉴의 기존 UI 참고는
`/workspace/artifacts/v536-verification-managed/runs/578bcf7ac8d845909a9668d7598b4c59.json`다. 두 ZIP/manifest 전체 무결성·관련 source/probe/fixture
불변, SDK/NuGet 입력 동일성을 확인했다. 새 verification_svg_suite.py는 검증 도구의 분기 검사로만 추가됐고 이전 native/probe 입력은 바꾸지 않았다. 이 참고는 최종 신규 수나 재사용 합산에 넣지 않는다.
SVG와 공통 image 영향 검사36개는 봉인된7b3cd6e1 결과를 재사용했다. 제품/실행 검사 파일의 변경 없음, 정확한 검증 도구 수정 hash, SDK/NuGet·명령 동일성과 이전 ZIP/manifest를 확인하고 SDK/제품 변경 시 재사용을 거절하는 negative guard를 수행했다. 실패한 packaged-feature 검사와 빌드/패키지는 재사용하지 않았다. LF/CRLF 빌드를 재생성하고 수정된 SVG package/full restore 및 suite routing/FIFO·실패 수명 검사는 신규 실행했다.

- 최종 record: `/workspace/artifacts/v536-verification-managed/runs/9fdf62c1e51f46a1871999226e08077c.json`
- 증거 ZIP SHA256: `51491555c860c35341c6227d047f62ed0aafc1b64fcfc4a05415be2e5e98c9b6` (1,880,146B)
- 개발6단계: `/workspace/artifacts/v536-verification-managed/runs/ff4702292fff4b5facbfa27c1dda9cbf.json` (최종 수 제외)
- 선행 실패: 3개. Node data-URI fixture의 dependency loader, 실제 Chromium SVG bitmap decoder 한계, SVG suite가 generic header package 검사로 잘못 떨어진 도구 연결 오류의 기록을 남겼다. 마지막 generic feature 헤더 검사는 기존 화면 컨트롤의 pointer intercept로 실패했으며 SVG 제품 실패나 초기 빈 화면 원인으로 간주하지 않는다. 최종 결과와 섞지 않는다.
- 선행 증거: `/workspace/artifacts/v536-verification-managed/runs/831a8f558e04422da06ba47f1310688b.json` / SHA256 `ff616dfe017b0c9c64ba6a24a7388b436291c8f2d837fdd2b060fd69f185b74d`.
- 선행 증거: `/workspace/artifacts/v536-verification-managed/runs/d8f485996a4c459db552f9649be33a14.json` / SHA256 `84e7b6eb0a1d78bd0725ffdaa0fc55b82b24458c4c21adb7b396146ac766584f`.
- 선행 증거: `/workspace/artifacts/v536-verification-managed/runs/9ceaf96665f94106b34a2d52c58f9ea7.json` / SHA256 `e696360cef1f658f58bbe27de3e00beda2204376a1c4f45df55d102ec82db123`.
- 모든 기록 archive/manifest 무결성·cleaned·owned root 부재를 확인했다. 최종 svg-reuse.json과 각 reused 결과가36개 기존 통과의 출처·동일성·negative guard를 별도로 기록한다.

| 지속 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `431b574a540556b581d4aadaef8691e5a45a33b5` | `4c4a93c7b28a7e84792fc98232d1c733df2460565ded1068915dfe9183ce8210` | 53,808,866 | 2704/158 |
| rollback | `8c861c7223414f77596666c8f0f465fb76cfc2bf` | `02b32d22ad64fe4f6447c70d284639f873e2335509b25d66c782b230f6f903d6` | 53,805,250 | 2703/158 |

index `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest `7cf07e6de39d86bb53554f5169b4a99a1f3d31dfe06fe5fa11fcad8f9b7af9ca`, rollback manifest `aeac8f6c60e6bd3496a8da887ca94391348e0aa68c31c5f9d84119cd633d20af`.
직전 정상 AVIF 패키지는 rollback이다. 이전 reader도 동일 저장 사본을 읽으며 SVG 표시는
이전 미지원 상태다. 기존 승인된 관리형2세대 원자 승격/실패 복구와 이번 owned 임시물 수명만
사용했다. 과거 자료·원본·SDK·로그·프로필·사용자 데이터 추가 삭제는 없다.

사전 여유부터 단위 순증가 7,024,640B
(약 6.7MiB), 최종 실행 순증가 2,875,392B,
남은 여유 1,075,818,496B (약 1.00GiB).
사전 최대 disk256MiB+안전64MiB와 임시 filesystem3GiB/추가 memory7GiB+안전1GiB를
확인했다. 단계 표본 최소 disk 여유 1,078,632,448B, cgroup peak 6,626,299,904B는
압축/승격 모든 순간의 hard 최저/최대 측정이 아니다. 이후 증가량 보장도 아니다.

고정 잔여는 큰 파일(현재 per-file1MiB/합계4MiB), 실제 멤버/신원/권한 source 및 그에 의존한
공유/다른 참여자, HD/물리 Run 출력·장치와 기존 ABI의 명시 미지원 경계 등이다.
원본에 실제 mesh renderer 근거가 없으므로 임의 구현을 필수 범위에 더하지 않았다.
M11/M12/M4는 증거 있는 회귀 없이 다시 열지 않는다. 초기 빈 #app 원인은 미확정이다.
실제 Linux 엔진·Chromium과 Windows 교차 생성/복원을 수행했으며 실제 Windows/WebView2/
모바일·전체 UI·Space/Library 전달은 미실행이다.
