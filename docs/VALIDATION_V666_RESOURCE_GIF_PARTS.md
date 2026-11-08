# 큰 GIF 그림·애니메이션의 최종 검증

동결 e96f6e06124c14d82f83c94cdd3cc9649fe65639의 신규61단계·재사용0을 통과했다.
LF 27·CRLF 27와 새 패키지/전체 복원/수명 검사다.
[원본 사용자 흐름과 유한 지원 경계](V7_RESOURCE_GIF_PARTS.md)를 따른다. 이미 보관한
1MiB 초과–4MiB GIF를 전체 bytes/SHA 확인 뒤 원래 contain 패널에 표시한다.
원본 UI/레이아웃·입력·원문/공개/override 계약·권한·Review→Confirm·최종 쓰기CAS는 유지한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache, Release/MCP/Linux engine.3개 runtime 파일+README의 정확 차이·canonical assets·동일 HTML/CSS/자산 수. 기존 native 읽기/쓰기·저장v1·공개/permission/override와 Office/PDF·Run source 보호 |
| encoded/형식 | GIF87a/89a의1MiB 초과·정확4MiB/초과, comment sub-block·잘린/후행 길이·palette/control/축과 frame 가중 budget 거절. 원래64frame·logical canvas×frames≤16MP/공유32MP를 유지한다. 큰 AVIF/SVG의1MiB 예산도 미변경. GIF/WebP/BMP/조각/raster/AVIF의9개 단위 검사 |
| 조각/최종 읽기 | strict header/각 item·revision·정수 part/offset/길이/canonical base64·각/전체SHA.4MiB 네 조각과 짧은 마지막 조각, 전체 사본/영수증·rename/같은 ID/hash 재import 세대·tail 변조·9개 최종 의존성 race. 이전4ec reader는 GIF metadata-only/part 거절. BMP와 PNG/JPEG 실제 final-read도 신규 실행 |
| 기본 이미지/실제 운동 | 실제 큰 GIF87a900×900(1,113,303B)와 GIF89a2×700×600(1,154,299B)의 canvas 기본 프레임 전체 RGBA SHA. 실제 compositor screenshot의 빨강/초록 전환을 별도 확인한다. 실제 압축 frame+무작위 comment의 정확4MiB도 같은 기본 픽셀/네 조각. 작은 interlace/global/local palette·투명도/2·3frame/disposal 실제 compositor와 첫 LZW decoder 실패도 신규 DOM 검사 |
| 실패/입력 | foreign/stale/path/누락/실수·문자 part/범위 밖·mutation lane 거절. malformed/legacy cap·혼합/변조 part·원본 tail 변조는 decoder/URL 전에 거절. 큰 손상 첫 LZW의 실제 bitmap 실패는 URL/img fallback 없이 처리. 늦은 설명/명시 저장·기타 입력/원본을 보존하고 old revision 거절 |
| 중단/권한 | pending part의 close/reopen·삭제·Home·동일 namespace 다른 project·cold의 늦은 응답 격리. 생성 사본의 실제 native 읽기 권한 거절·정확 mode 복원/명시 retry. 원래 비취소 bitmap/lease는 단위/실제 codec 실행으로 구분하며 뒤 프레임 전체 LZW의 별도 인증을 주장하지 않음 |
| 관련 회귀 | 큰 WebP/BMP의 실제 픽셀·API/수명과 일반 내용 편집/복구를 LF/CRLF에 재실행. PNG/JPEG native/메타데이터와 공유 lease도 신규. Office/PDF/FHD·앞선 다른 전체 UI 기록은 미변경 source로 유지하지만 이번 신규 수에 합산하지 않음 |
| 패키지/복원 | 새 Windows 교차 생성·구조/변조/의존성 거절·실제 Linux 엔진 startup. 생성 패키지 GIF normal, ZIP CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤 GIF lifecycle. 소유 IPC/실패 수명관리·증거 봉인/소유 임시물 정리 |

개발 기록 /workspace/artifacts/v536-verification-managed/runs/256fa996cd704f328c63e334add4a37e.json에서 게시본4ec의 metadata-only 누락을 실제 엔진으로 재현했다.
총 21시도 중 초기 normal1회는 실제 그림 대신 contain 여백을 읽은 검사 오류로
실패했고 나머지는 통과했다. 저장한514×375 화면에서 기존(8,8)은 배경RGB20/24/25,
logical700×600의 실제 그림(48,10)은 예상RGB240/10/20임을 직접 확인했다. 원래 CSS의
width/height100%·object-fit contain을 유지하고 중앙 정렬의 실제 그림 좌표만 계산하도록
수정했다. 제품 코드는 변경하지 않았으며 단순 종료 label도 GIF로 바로잡았다. 실패 로그/
화면·검사 전후 source/SHA와 수정 뒤 normal/lifecycle를 보존하고 최종 신규 수에 재사용하지 않았다.
개발 화면에서4,194,304B 생성 GIF의 원래 contain 배치/readonly도 직접 확인했다.

canvas drawImage의 기본/첫 frame 픽셀과 실제 compositor 운동을 구분한다. 자연 압축 GIF와
큰 comment padding은 별개이며 모든 대형 frame/최악의 LZW·브라우저 스케줄 성능 증거가 아니다.
native4MiB fixture는 알려진 작은 frame+무작위 comment로 읽기 경계를 검증한다. native race/
지연·변조는 통제된 fixture, bitmap/codec/DOM/canvas/compositor와 읽기 권한 거절은 실제 실행이다.
개인 파일/외부 자료를 임의 업로드하지 않았으며 hard CPU/브라우저 전체 메모리 상한을 주장하지 않는다.

기본 metadata-only read와 imagePreview/preview-image-part 문법은 유지한다. GIF signature는
codec 인증이 아니며 원래 구조/프레임 검증과 실제 기본 bitmap decode를 거친다. metadata-only
구 client는 기존 fallback, 종전 image-parts client는 이전 decoder bound로 큰 GIF를 거절할 수 있다.
보관 bytes/receipt/저장v1·작은 read/내용편집/백업1MiB·파일/합계4MiB/64개·2MiB RPC와
외부 원본/권한·CAS는 그대로다. 애니메이션을 작업 실행의 선행 조건으로 만들지 않는다.

## 지속 보관과 공간

- 최종 record: /workspace/artifacts/v536-verification-managed/runs/a73917e272874d12a3590bee8f37fb90.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/a73917e272874d12a3590bee8f37fb90.zip, 115,998,707B, SHA256 3f877a0f96452deaa3136530e553b47d17b78e25dc89eefceeab998f02002ae6
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/a73917e272874d12a3590bee8f37fb90.closing-index.json, SHA256 4a9b81df33988b9206d466a379764dba9b9c1663a92518b6d783aff1ad48d71c

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | e96f6e06124c14d82f83c94cdd3cc9649fe65639 | 4f0182d712e688ad9f2d198741ed1fcd1e54a2689c0d4bb1637562f7566d96cd | 53,830,214 | 2720/158 |
| rollback | ec7cb80a6e40c2bd2f0543f00c4af6cafcf07745 | 3f70c5f351e1b717a75dc835330de49a5ccec16bd96367933c183e939b9bb71e | 53,830,848 | 2720/158 |

새 복원과 지속 증거 검증 뒤 원자 승격했다. 직전 정상ec7cb80a를 rollback으로 보존하고
이전 관리 rollbackf4208fa3 2c9422fab533477120996142cc4dd97a0285770608849f53048f2eff0561cc9a만 승인된2세대 수명으로 퇴역했다.
rollback은 동일 ZIP SHA/전체 manifest·이전 전체 복원 근거를 유지하며 이번에 구버전 엔진을
다시 실행하지 않았다. 다른 기존 원본/과거 로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다.
각 실행이 직접 만든 임시물만 자식 종료/소유권·지속 증거 검증 뒤 정리했다.

추가 디스크 331,350,016B(archive56MiB·증거192MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
29,758,414,848/29,639,970,816B, 표본 차이 118,444,032B다. 개발 포함 단위
시작/종료 29,803,073,536/29,639,970,816B다. 최종 단계 표본 최저 디스크 29,758,324,736B,
관측 cgroup peak 6,495,215,616B다. 모든 순간의 절대 극값/고정 순증가
보장이 아니며 안전 기준을 낮추거나 증거를 버려 예산에 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 보존한다. 후속 문서 마감 뒤
runtime/검사/tools가 위 동결과 같음을 확인하고 work/current만 정상 게시한다.
큰 AVIF/SVG·내용/Office 편집/백업·4MiB 초과/총 보관 확대, 실제 신원/권한 backend·
QHD/4K/FHD+·GPU/물리 장치가 기존 잔여다. 초기 빈 #app와 과거 cold 읽기1회 원인은 미확정이다.
M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·
물리 오디오·Office 앱 호환·Space/Library는 미실행/미완료이며 교차 패키지와 구분한다.
