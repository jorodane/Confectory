# 큰 정지 AVIF 그림의 최종 검증

동결 82444451f705e81f4ac00b74101257868778239f의 신규63단계·재사용0을 통과했다.
LF 28·CRLF 28와 새 패키지/전체 복원/수명 검사다.
[원본 사용자 흐름과 유한 지원 경계](V7_RESOURCE_AVIF_PARTS.md)를 따른다. 이미 보관한
1MiB 초과–4MiB 정지 AVIF를 전체 bytes/SHA 확인 뒤 원래 contain 패널에 표시한다.
원본 UI/레이아웃·입력·원문/공개/override 계약·권한·Review→Confirm·최종 쓰기CAS는 유지한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache, Release/MCP/Linux engine.3개 runtime 파일+README의 정확 차이·canonical assets·동일 HTML/CSS/자산 수. 기존 native 읽기/쓰기·저장v1·공개/permission/override와 Office/PDF·Run source 보호 |
| encoded/형식 | major/compatible avif의 제한 ftyp·길이/알 수 없는 brand 거절, 1MiB 초과·정확4MiB/free box·초과. FRAME OBU만4MiB이며 sequence 등1MiB와 기존 profile/association/extent/alpha/color·축/16MP/공유32MP를 유지한다. AVIF/GIF/WebP/BMP/조각/raster의10개 단위 검사. 큰 SVG는1MiB 유지 |
| 조각/최종 읽기 | strict header/item·revision·정수 part/offset/길이/canonical base64·각/전체SHA.4MiB 네 조각/짧은 마지막 조각, 전체 사본/영수증·rename/같은 ID/hash 재import 세대·tail 변조·9개 최종 의존성 race. 이전4e598 reader는 AVIF metadata-only/part 거절. GIF와 PNG/JPEG 실제 final-read도 신규 실행 |
| 실제 기본 이미지 | 자연 압축 RGB700×600(1,574,540B)와 alpha600×500(1,553,057B), color FRAME 각각1,574,247/1,125,018B. Pillow 독립 decode와 브라우저 전체 canvas의 RGB/alpha 비교·전체 canvas SHA. RGB 차이0, alpha의 premultiplied color 최대1/alpha0, 허용color6/alpha1. 실제 RGB stream+inert free box 정확4MiB 네 조각도 같은 픽셀. 작은 AVIF 실제 alpha/색/profile/실패 DOM 회귀 |
| 실패/입력 | foreign/stale/path/누락/실수·문자 part/범위 밖·mutation lane 거절. malformed/legacy cap·혼합/변조 part·원본 tail 변조는 decoder/URL 전에 거절. 큰 손상 AV1의 실제 bitmap 실패는 URL/img fallback 없이 처리. 늦은 설명/명시 저장·기타 입력/원본을 보존하고 old revision 거절 |
| 중단/권한 | pending part의 close/reopen·삭제·Home·동일 namespace 다른 project·cold의 늦은 응답 격리. 생성 사본의 실제 native 읽기 권한 거절·정확 mode 복원/명시 retry. 기존 비취소 bitmap/lease 수명은 미변경 source·기존 단위/실제 codec 검사로 구분 |
| 관련 회귀 | 큰 GIF/WebP의 실제 픽셀/운동·API/수명과 일반 내용 편집/복구를 LF/CRLF에 재실행. PNG/JPEG native/메타데이터와 공유 lease도 신규. Office/PDF/FHD·앞선 다른 전체 UI 기록은 미변경 source로 유지하지만 이번 신규 수에 합산하지 않음 |
| 패키지/복원 | 새 Windows 교차 생성·구조/변조/의존성 거절·실제 Linux 엔진 startup. 생성 패키지 AVIF normal, ZIP CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤 AVIF lifecycle. 소유 IPC/실패 수명관리·증거 봉인/소유 임시물 정리 |

개발 기록 /workspace/artifacts/v536-verification-managed/runs/9413aaee34da45f5b368ee0cf3dab67c.json의21단계를 모두 통과했다. 게시본4e598에서 실제 엔진의 metadata-only
누락을 먼저 재현했고, 자연 압축 FRAME을 기존 parser가1MiB bytes/OBU bound로 거절함을
확인했다. 변경 뒤 parser/native/실제 codec/normal/lifecycle가 통과했다. 개발 화면에서
4,194,304B 생성 AVIF의 원래 contain 배치/readonly와 다른 채팅 입력 보존을 직접 확인했다.
개발 결과는 최종 신규 수에 재사용하지 않았다. 생성 입력/encoder 옵션/별도 픽셀 비교 결과와
source·로그·화면은 지속 증거에 보존했다. 새 vendor/runtime encoder 설치는 없다.

정확4MiB는 자연 압축 RGB stream+inert free box이며 FRAME 자체4MiB 또는 최악 성능의 증거는
아니다. native4MiB fixture는 알려진 작은 AVIF+free box로 읽기 경계를 검증한다. native race/
지연·변조는 통제된 fixture, bitmap/codec/DOM/canvas와 읽기 권한 거절은 실제 실행이다.
모든 AVIF 문법/HDR/sequence/grid나 hard CPU/브라우저 전체 메모리 상한을 주장하지 않는다.
개인 파일/외부 자료를 임의 업로드하지 않았다.

기본 metadata-only read와 imagePreview/preview-image-part 문법은 유지한다. avif brand는
codec 인증이 아니며 원래 구조/sequence/frame 검증과 실제 bitmap decode를 거친다. metadata-only
구 client는 기존 fallback, 종전 image-parts client는 이전 decoder bound로 큰 AVIF를 거절할 수 있다.
새 UI+구 backend도 metadata-only다. 보관 bytes/receipt/저장v1·작은 read/내용편집/백업1MiB·
파일/합계4MiB/64개·2MiB RPC와 외부 원본/권한·CAS는 그대로다.

## 지속 보관과 공간

- 최종 record: /workspace/artifacts/v536-verification-managed/runs/e4c3259278a0478f86c803e24b5f098c.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/e4c3259278a0478f86c803e24b5f098c.zip, 119,888,159B, SHA256 655fb30875e7100a3752c39c2e7942dd268085918fa646a713206cb72333638f
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/e4c3259278a0478f86c803e24b5f098c.closing-index.json, SHA256 666a73a621ef18031e06c716abf469f41bb10f3166b5c247bfd802aa645cfabb

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | 82444451f705e81f4ac00b74101257868778239f | 75f84e08dc61b35b846eb1d9e2a7dc3f45cf73ae1b9b8ee73df8c06b50e4d689 | 53,830,504 | 2720/158 |
| rollback | e96f6e06124c14d82f83c94cdd3cc9649fe65639 | 4f0182d712e688ad9f2d198741ed1fcd1e54a2689c0d4bb1637562f7566d96cd | 53,830,214 | 2720/158 |

새 복원과 지속 증거 검증 뒤 원자 승격했다. 직전 정상e96f6e06을 rollback으로 보존하고
이전 관리 rollbackec7cb80a 3f70c5f351e1b717a75dc835330de49a5ccec16bd96367933c183e939b9bb71e만 승인된2세대 수명으로 퇴역했다.
rollback은 동일 ZIP SHA/전체 manifest·이전 전체 복원 근거를 유지하며 이번에 구버전 엔진을
다시 실행하지 않았다. 다른 기존 원본/과거 로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다.
각 실행이 직접 만든 임시물만 자식 종료/소유권·지속 증거 검증 뒤 정리했다.

추가 디스크 331,350,016B(archive56MiB·증거192MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
29,594,554,368/29,472,202,752B, 표본 차이 122,351,616B다. 개발 포함 단위
시작/종료 29,639,835,648/29,472,202,752B다. 최종 단계 표본 최저 디스크 29,594,472,448B,
관측 cgroup peak 6,995,390,464B다. 모든 순간의 절대 극값/고정 순증가
보장이 아니며 안전 기준을 낮추거나 증거를 버려 예산에 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 보존한다. 후속 문서 마감 뒤
runtime/검사/tools가 위 동결과 같음을 확인하고 work/current만 정상 게시한다.
큰 SVG·내용/Office 편집/백업·4MiB 초과/총 보관 확대, 실제 신원/권한 backend·
QHD/4K/FHD+·GPU/물리 장치가 기존 잔여다. 초기 빈 #app와 과거 cold 읽기 원인은 미확정이다.
M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·
물리 오디오·Office 앱 호환·Space/Library는 미실행/미완료이며 교차 패키지와 구분한다.
