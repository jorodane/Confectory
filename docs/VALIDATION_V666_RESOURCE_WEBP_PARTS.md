# 큰 정지 WebP 미리보기의 최종 검증

동결 ec7cb80a6e40c2bd2f0543f00c4af6cafcf07745의 신규61단계·재사용0을 통과했다.
LF 27·CRLF 27와 새 패키지/전체 복원/수명 검사다.
[원본 사용자 흐름과 유한 지원 경계](V7_RESOURCE_WEBP_PARTS.md)를 따른다. 이미 보관한
1MiB 초과–4MiB 정지 WebP를 전체 bytes/SHA 확인 뒤 기존 그림 패널에 표시한다.
원본 UI/레이아웃·입력·원문/공개/override 계약·권한·Review→Confirm·최종 쓰기CAS는 유지한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache, Release/MCP/Linux engine.3개 runtime 파일+README의 정확 차이·canonical assets·동일 HTML/CSS/자산 수. 기존 native 읽기/쓰기·저장v1·공개/permission/override 계약과 Office/PDF·Run source 보호 |
| encoded/형식 | VP8/VP8L의1MiB 초과·정확4MiB/초과, 전체 RIFF 길이/청크/패딩·truncation·unknown inert metadata. 큰 ANIM/ANMF/animation flag는 DOM 전에 거절. 기존 WebP의 frame/canvas/alpha·side/pixel·지원 feature 및 GIF/AVIF/SVG의1MiB 예산 유지 |
| 조각/최종 읽기 | 기존 strict image parts header/각 item·revision·정수 part/offset/길이/canonical base64·각/전체SHA.4MiB 네 조각과 짧은 마지막 조각, 전체 현재 사본/영수증·rename/같은 ID/hash 재import 세대·tail 변조·9개 최종 의존성 race. 이전e5ca reader는 WebP metadata-only/part 거절. BMP와 PNG/JPEG 실제 native final-read도 신규 실행 |
| 실제 픽셀/codec | 실제 lossless640×600(1,152,080B)의 전체 canvas RGBA SHA와 lossy1200×900(1,204,884B)의 디코드 샘플 픽셀. 실제 압축 frame+불활성 무작위 JUNK로 정확4MiB에서도 네 조각 뒤 같은 전체 픽셀. 작은 lossy/lossless·alpha·inert metadata 실제 Chromium 픽셀과 broken entropy의 bitmap 오류/URL 정리도 신규 실행 |
| 실패/입력 | foreign/stale/path/누락/실수·문자 part/범위 밖·mutation lane 거절. malformed/legacy cap·혼합/변조 part·원본 tail 변조는 decoder/URL 전에 거절. 큰 손상 entropy는 실제 bitmap 실패 뒤 URL을 만들지 않고 img 성공 fallback을 사용하지 않는다. 늦은 설명 입력/명시 저장을 보존하고 old revision 거절 |
| 중단/권한 | pending part의 close/reopen·삭제·Home·동일 namespace 다른 project·cold에서 늦은 응답 격리. 생성 사본의 실제 native 읽기 권한 거절은 bitmap/URL 없이 실패하고 정확 mode 복원/명시 retry로 회복. 원래 비취소 bitmap Promise/close·pixel lease는 신규 unit과 실제 codec 검사로 구분 |
| 회귀 | 기존 BMP/PNG/JPEG의 큰 실제 픽셀·API/수명과 큰 Office 실제 Worker/DOM·일반 내용 편집/복구를 LF/CRLF에 재실행. BMP/그림 조각·raster budget/GIF/AVIF metadata/수명 단위도 신규 실행. 이전 전체 작은 Office/DOCX/XLSX·PDF·FHD 기록은 미변경 source로 유지하지만 이번 신규 수에 합산하지 않음 |
| 패키지/복원 | 새 Windows 교차 생성·구조/변조/의존성 거절·실제 Linux 엔진 startup. 생성 패키지의 큰 WebP normal과 ZIP CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤 WebP lifecycle. 소유 IPC/실패 수명관리·증거 봉인/소유 임시물 정리 |

개발 기록 /workspace/artifacts/v536-verification-managed/runs/02208ebdfdf04ebb8c2087d725f8aaba.json에서 게시본e5ca의 metadata-only 누락을 실제 엔진으로 재현한 뒤
runtime overlay·unit/native·실제 DOM와 normal/lifecycle를 19단계 모두 통과했다.
생성 입력/실제 검사 source·실행 로그·화면을 보존했고 최종 신규 수에 합산/재사용하지 않았다.
개발 화면에서4,194,304B 생성 WebP의 원래 contain 배치와 readonly 표시를 직접 확인했다.
실제 큰 lossless/lossy 압축 파일과4MiB metadata padding을 구분하며 임의 복잡도·색상 profile·
최악의 codec 성능 증거로 보지 않는다. 큰 alpha 조합 전체의 별도 실제 픽셀 검사는 하지 않았고
작은 alpha의 기존 parser/codec 수명은 신규 DOM으로 검증했다. native4MiB fixture는 합성 RIFF/
chunk/header와 무작위 JUNK로 읽기 경계를 검증하며 실제 codec entropy의 증거가 아니다.
canvas/bitmap/엔진은 실제 실행, native 최종 읽기 race/지연·변조는 통제된 fixture다.
개인 파일/외부 자료를 임의 업로드하지 않았으며 hard CPU/브라우저 전체 메모리 상한을 주장하지 않는다.

기본 metadata-only read와 imagePreview/preview-image-part 문법은 유지한다. RIFF/WEBP
signature는 codec 인증이 아니며 기존 엄격한 구조/animation 거절과 실제 bitmap decode를 거친다.
metadata-only 구 client는 기존 fallback, 종전 image-parts client는 이전 decoder 한도로
큰 WebP를 거절할 수 있다. 보관 bytes/receipt/저장v1·작은 read/내용편집/백업1MiB·파일/합계4MiB/
64개·2MiB RPC와 외부 원본/권한·CAS는 그대로다. 큰 파일을 재인코딩하거나 저장 정책을 이행하지 않는다.

## 지속 보관과 공간

- 최종 record: /workspace/artifacts/v536-verification-managed/runs/18f42dc6618740c6a685fe936f2d4028.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/18f42dc6618740c6a685fe936f2d4028.zip, 129,177,295B, SHA256 a050119389b4889f00959455aafecae8c8b1200d2d7c439b0885905a94c5802a
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/18f42dc6618740c6a685fe936f2d4028.closing-index.json, SHA256 44d6f6ba2624a48e5e02375c227dc76b009357b6009d53378ccd3a56bccdfc96

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | ec7cb80a6e40c2bd2f0543f00c4af6cafcf07745 | 3f70c5f351e1b717a75dc835330de49a5ccec16bd96367933c183e939b9bb71e | 53,830,848 | 2720/158 |
| rollback | f4208fa3f255560faf1d67f0da85c7b90d50f3c3 | 2c9422fab533477120996142cc4dd97a0285770608849f53048f2eff0561cc9a | 53,831,038 | 2720/158 |

새 복원과 지속 증거 검증 뒤 원자 승격했다. 직전 정상f4208fa3를 rollback으로 보존하고
이전 관리 rollback61a72f55 d6bf5702fd96c7013467645673643cb1b3bd863613a7b62fb529d9ac502fb7ce만 승인된2세대 수명으로 퇴역했다.
rollback은 동일 ZIP SHA/전체 manifest·이전 전체 복원 근거를 유지하며 이번에 구버전 엔진을
다시 실행하지 않았다. 다른 기존 원본/과거 로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다.
각 실행이 직접 만든 임시물만 자식 종료/소유권·지속 증거 검증 뒤 정리했다.

추가 디스크 264,241,152B(archive56MiB·증거128MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
29,934,862,336/29,803,192,320B, 표본 차이 131,670,016B다. 개발 포함 단위
시작/종료 29,970,980,864/29,803,192,320B다. 최종 단계 표본 최저 디스크 29,934,772,224B,
관측 cgroup peak 6,527,840,256B다. 모든 순간의 절대 극값/고정 순증가
보장이 아니며 안전 기준을 낮추거나 증거를 버려 예산에 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 보존한다. 후속 문서 마감 뒤
runtime/검사/tools가 위 동결과 같음을 확인하고 work/current만 정상 게시한다.
큰 GIF/AVIF/SVG·내용/Office 편집/백업·4MiB 초과/총 보관 확대, 실제 신원/권한 backend·
QHD/4K/FHD+·GPU/물리 장치가 기존 잔여다. 초기 빈 #app와 과거 cold 읽기1회 원인은 미확정이다.
M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·
물리 오디오·Office 앱 호환·Space/Library는 미실행/미완료이며 교차 패키지와 구분한다.
