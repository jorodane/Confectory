# 큰 BMP 미리보기의 최종 검증

동결 f4208fa3f255560faf1d67f0da85c7b90d50f3c3의 신규57단계·재사용0을 통과했다.
LF 25·CRLF 25와 새 패키지/복원/수명 검사다.
[원본 사용자 흐름과 유한 지원 경계](V7_RESOURCE_BMP_PARTS.md)를 따른다. 이미 보관한
1MiB 초과–4MiB BMP를 현재 전체 bytes/SHA 확인 뒤 기존 그림 패널에 표시한다.
원본 UI/레이아웃·입력·원문/공개/override 계약·권한·Review→Confirm·최종 쓰기CAS는 유지한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache, Release/MCP/Linux engine.3개 runtime 파일과 README만 허용한 차이·canonical assets·동일한 HTML/CSS/자산 수. 원래 native 읽기/쓰기·저장v1/원문/public/permission과 PDF/Office·텍스트/Run 보호 |
| encoded/형식 | 큰24/32bpp·signed height·행 padding·imageSize0/정확 길이와4,193,334B 유효 BMP.4MiB 초과 거절, 정확4MiB의 잘못된 픽셀 길이도 거절. 이전 팔레트/RLE/bitfields/CORE/V4/V5/ICC/다른offset·후행/잘린 길이·축/pixel 거절 유지. 큰 WebP/GIF/AVIF/SVG 한도는 미변경 |
| 조각/최종 읽기 | 기존 strict image parts header/각 item·revision·정수 part/offset/길이/canonical base64·각/전체SHA. BMP 네 조각과 짧은 마지막 조각, native 전체 사본/영수증·rename/같은 ID/hash 재import 세대·tail 변조·9개 최종 의존성 race. 이전e495 reader는 BMP metadata-only/새 BMP 관찰 거절. 기존 PNG/JPEG·Office의 실제 최종 읽기도 별도 실행 |
| 실제 표시 | 실제 큰24bpp bottom-up/행 padding과32bpp top-down BGRX의 전체 RGBA SHA를 비교했다.4,193,334B 원본은 네 조각 뒤 동일 contain 패널/readonly 표시. 작은 BMP24/32·상하 방향/행 padding/불투명 실제 픽셀·URL 정리도 새 Chromium DOM 검사 |
| 실패/입력 | foreign/stale/path/누락/실수·문자 part/범위 밖·mutation lane 거절. malformed/legacy cap·혼합/변조 part·overdimension·원본 tail 변조는 decoder/URL 전에 거절. 새 설명 입력을 덮지 않고 명시 저장 뒤 old revision 거절. 원본/기타 입력 불변 |
| 중단/권한 | pending part의 close/reopen·삭제·Home·같은 namespace 다른 project·cold에서 늦은 응답 격리. 실제 생성 사본의 native 읽기 권한 거절은 bitmap/URL 없이 실패하고 정확 mode 복원/명시 retry로 복구. 원래 비취소 bitmap Promise/close·pixel lease의 단위 검사도 새로 실행 |
| 회귀 | 기존 작은 BMP 및 image-parts/raster budget/WebP/GIF/AVIF metadata/수명 단위를 신규 실행. 큰 PNG/JPEG의 실제 pixels·큰 Office 실제 Worker/DOM·일반 내용 편집/복구를 LF/CRLF에 재실행. 기존 작은 Office/DOCX/XLSX와 PDF·FHD의 미변경 소스/직전 기록은 유지하지만 해당 전체 과거 검사를 이번 신규 수에 더하지 않음 |
| 패키지/복원 | 새 Windows 교차 생성·구조/변조/의존성 거절·실제 Linux 엔진 startup. 생성 패키지의 큰 BMP normal과 ZIP CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤 큰 BMP lifecycle. 소유 IPC/실패 수명관리·증거 봉인/소유 임시물 정리 |

개발 기록 /workspace/artifacts/v536-verification-managed/runs/b5af53745e84495187b3f1d5b473adae.json는 게시본e495의 metadata-only 누락을 실제 엔진으로 재현한 뒤
runtime overlay·unit/native와 실제 normal/lifecycle를 17단계 모두 통과했다.
생성한 입력/검사 source·실행 로그·화면을 보존했고 최종 신규 수에 합산/재사용하지 않았다.
개발 화면에서4,193,334B 생성 BMP의 원래 contain 배치와 readonly 표시를 직접 확인했다.
정확 픽셀은 실제 Chromium canvas RGBA SHA, 최종 읽기 race/지연 응답은 통제된 fixture다.
생성한 무작위 사본만 사용했으며 사용자 개인 파일/외부 자료를 임의 업로드하지 않았다.
모든 BMP 표준/codec·GPU·hard CPU/메모리 상한의 증거가 아니다.

기본 metadata-only read와 imagePreview/preview-image-part 문법은 유지한다. BM signature는
인증이 아니며 기존 엄격한 BMP parser와 실제 bitmap decode/크기 확인을 거친다. metadata-only
구 client는 기존 fallback, 종전 image-parts client는 이전 decoder 한도로 큰 BMP를 거절할 수 있다.
보관 bytes/receipt/저장v1·1MiB 작은 read/내용편집/백업·파일/합계4MiB/64개·2MiB RPC와
권한·외부 원본·CAS는 그대로다. 임의 후행 padding이나 자동 재인코딩으로 새 형식을 허용하지 않는다.

## 지속 보관과 공간

- 최종 record: /workspace/artifacts/v536-verification-managed/runs/154bf9b4aff145429a55f0b2b7243fd8.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/154bf9b4aff145429a55f0b2b7243fd8.zip, 107,317,920B, SHA256 1f7c09ed4885c84234b4e70a0b46f41022d4a0a6691a99bb465e2b3bf57260a8
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/154bf9b4aff145429a55f0b2b7243fd8.closing-index.json, SHA256 3913480e3276f0e23d7c3e4b0fe8f6473c656cf7884806e469fc4f7381abfa37

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | f4208fa3f255560faf1d67f0da85c7b90d50f3c3 | 2c9422fab533477120996142cc4dd97a0285770608849f53048f2eff0561cc9a | 53,831,038 | 2720/158 |
| rollback | 61a72f553cbb7462f2474990e9cf0e78f86d62bf | d6bf5702fd96c7013467645673643cb1b3bd863613a7b62fb529d9ac502fb7ce | 53,830,263 | 2720/158 |

새 복원과 지속 증거 검증 뒤 원자 승격했다. 직전 정상61a72f55를 rollback으로 보존하고
이전 관리 rollbackd8279712 deed66a9cb3bc0a0a3d4d9bb13955f690b42d8780ba1316393e50450eedc4923만 승인된2세대 수명으로 퇴역했다.
rollback은 동일 ZIP SHA/전체 manifest·이전 전체 복원 근거를 유지하며 이번에 구버전 엔진을
다시 실행하지 않았다. 다른 기존 원본/과거 로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다.
각 실행이 직접 만든 임시물만 자식 종료/소유권·지속 증거 검증 뒤 정리했다.

추가 디스크 264,241,152B(archive56MiB·증거128MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
30,080,815,104/29,971,062,784B, 표본 차이 109,752,320B다. 개발 포함 단위
시작/종료 30,116,712,448/29,971,062,784B다. 최종 단계 표본 최저 디스크 30,080,741,376B,
관측 cgroup peak 5,896,450,048B다. 모든 순간의 절대 극값/고정 순증가
보장이 아니며 안전 기준을 낮추거나 증거를 버려 예산에 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 보존한다. 후속 문서 마감 뒤
runtime/검사/tools가 위 동결과 같음을 확인하고 work/current만 정상 게시한다.
큰 WebP/GIF/AVIF/SVG·내용/Office 편집/백업·4MiB 초과/총 보관 확대, 실제 신원/권한 backend·
QHD/4K/FHD+·GPU/물리 장치가 기존 잔여다. 초기 빈 #app와 과거 cold 읽기1회 원인은 미확정이다.
M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·
물리 오디오·Office 앱 호환·Space/Library는 미실행/미완료이며 교차 패키지와 구분한다.
