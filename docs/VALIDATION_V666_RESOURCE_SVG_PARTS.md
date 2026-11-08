# 큰 정지 SVG 그림의 최종 검증

동결 d94ee5e991b547849e1adf9a99cf915f668ce232의 신규65단계·재사용0을 통과했다.
LF 29·CRLF 29와 새 패키지/전체 복원/수명 검사다.
[원본 흐름과 지원 경계](V7_RESOURCE_SVG_PARTS.md)의256KiB 초과–4MiB 정지 SVG를 다룬다.
원본 화면·소유 데이터/권한·공개/override·Review→Confirm·최종 쓰기CAS를 유지한다.

| 검증 | 실제 범위 |
|---|---|
| 독립 source | LF/CRLF no-hardlinks Git/HOME/NuGet·빈 engine cache·Release/MCP/Linux engine.4개 runtime+README의 정확 delta/canonical assets·동일 HTML/CSS/자산 수. 기존 native 저장v1/쓰기/permission/공개/override·Office/PDF/Run source 보호 |
| XML/profile | 첫 BOM/ASCII공백 뒤 `<`는 후보일 뿐이다. 전체 UTF-8·SHA 뒤 기존 static profile. 새 큰 입력의 전진 주석/markup 검사와 주석1024/markup4096 한도·미완성 반복 주석 거절, DTD/entity/PI/encoding/HTML/invalidUTF8는 XML 전에 거절. 기존 요소1024/깊이24·속성65536자/숫자32768/문자65536/경로4096·내부 참조/외부/active 거절·축/16MP/공유32MP 유지. 작은1025주석 profile도 보존 |
| 조각/최종 읽기 | strict header/item·revision·정수 part/offset/길이/canonical base64·각/전체SHA.4MiB 네 조각/짧은 마지막 조각·UTF-8 경계 분리, rename/같은 ID/hash 재import 세대·tail 변조·9개 최종 의존성 race. native의 DTD 후보 전달은 SVG 허용이 아니며 별도 pre-XML 거절 검사. 이전bcea reader는 metadata-only/part 거절. AVIF/PNG/JPEG native final-read도 신규 |
| 실제 픽셀 | 800 rect/400×200의1,267,431B 긴 수치 정밀도 파일·alpha65×33의1,048,600B·256KiB+1·정확4MiB. 별도 정수 plane과 전체 canvas의 premultiplied color/alpha 허용1·전체 RGBA SHA 기록, 실제 최대차0/0. 정확4MiB는 도형+inert 주석이며4MiB의 복잡한 geometry/최악 성능 증거가 아님 |
| 실패/입력 | foreign/stale/path/누락/실수·문자 part/범위 밖·mutation lane·malformed/legacy cap·혼합/변조 part와 tail 변조 거절. 큰 손상 path는 URL 전에 거절. 제어한 isolated decode 실패는 URL 생성 뒤 정확 해제/명시 retry. 늦은 설명 저장과 새 입력·원본 보존, old display revision 거절 |
| 수명/권한 | pending part close/reopen·삭제·Home·동일 namespace 다른 project·cold 격리. 실제 생성 사본의 native 읽기 권한 거절·정확 mode 복원/retry. 실제 SVG decode 완료를 지연해 닫힌 owner의 URL과 늦은 완료를 격리. 기존 비취소 decode/공유 lease·viewBox derivative·DOM 격리 코드는 그대로 |
| 회귀 | AVIF/GIF/WebP/BMP/image-parts/raster10개 단위, 작은 SVG 실제 geometry/viewBox/gradient/clip/alpha와 공유 lease·URL, 큰 AVIF와 작은 SVG UI, 일반 내용 저장/복구. 앞선 Office/PDF/Run의 미변경 source/기존 기록은 신규 수에 합산하지 않음 |
| 패키지/복원 | 새 Windows 교차 생성·구조/변조/의존성 거절·실제 Linux engine startup. 생성 패키지 SVG normal, ZIP CRC/전체파일SHA/파일·디렉터리 mode 복원 뒤 lifecycle. 소유 IPC·실패 수명관리·증거 봉인/소유 임시 정리 |

개발 record /workspace/artifacts/v536-verification-managed/runs/4efe3bda698047118cb0c3c7d82e8e0c.json의30시도 중29개 통과와1개 검사 오류를 보존했다. 게시본bcea에서 실제
metadata-only 누락을 먼저 재현했다. 초기 normal 검사는 tail-retry 뒤 열린 같은 창에 decode
실패를 주입하고 Enter로 다시 열어 새 decode가 발생하지 않아 시간 초과됐다. 제품 수정 없이
현재 창을 닫은 뒤 실패를 설치하도록 고쳤고 normal/lifecycle가 통과했다. 실패 화면/로그·검사
전후 source/SHA를 보존했다. 검증 라우팅 초안의 들여쓰기/분기 수 오류도 동결 전에 바로잡았고
최종 세 경로 guard를 통과했다. 이를 최종 통과 검사로 집계하거나 완료된 검사를 재사용하지 않았다.

이후 큰 XML의 반복 미완성 주석에 정규식 검색이 반복되지 않도록 전진 scanner를 적용했다.
변경 전 runtime source/SHA와 확대된 공격 입력, 최종 scanner의 boundary/DOM·engine·일반/
lifecycle 검사를 개발 증거에 보존했다. 최종65단계는 모두 최종 source로 신규 실행했다.
개발 화면의4,194,304B 생성 SVG·원래 contain/readonly와 다른 입력 보존도 직접 확인했다.

native4MiB fixture는 작은 SVG+생성 주석으로 읽기 경계를 검사한다. 큰 파일의 실제 geometry/
alpha 픽셀은 별도 브라우저 흐름이다. 지연/변조/실패 주입·읽기 race는 통제된 fixture,
codec/DOM/canvas와 생성 사본 읽기 권한 거절은 실제 실행이다. XML은 페이지 DOM에 삽입하지
않으며 검증한 전체 문서만 격리 image decode한다. hard CPU/브라우저 전체 메모리 해제 상한이나
SVG 표준 전체·편집·외부 서비스 지원을 주장하지 않는다. 개인/외부 자료는 사용하지 않았다.

기본 read/descriptor/part·저장v1/원본 bytes/영수증·파일/합계4MiB/64개·2MiB RPC와
내용 편집/백업1MiB·권한·CAS는 그대로다. 구 image-parts client는 이전1MiB/256KiB SVG bound로
거절할 수 있으며 새 UI+구 backend의1MiB 초과는 metadata-only다. 현재 작은 사본을 이행하거나
C# 원문·override IO를 재작성하지 않는다.

## 지속 보관과 공간

- record: /workspace/artifacts/v536-verification-managed/runs/71053d69a60c40d9885929b73ec65e48.json
- 증거 ZIP: /workspace/artifacts/v536-verification-managed/runs/71053d69a60c40d9885929b73ec65e48.zip, 132,561,869B, SHA256 579c576aec151e1123b07c0766735369190a2eb9422bff467abdf839ce5e6fb3
- 승격 전 index: 증거 ZIP의 package-index-before.json
- 승격 후 동반 index: /workspace/artifacts/v536-verification-managed/runs/71053d69a60c40d9885929b73ec65e48.closing-index.json, SHA256 aeb88a60aa62b4111bbad14336aae71a4e0dad3fe96cd96ae4d1c149a9ae9ca4

| 보관 | source | ZIP SHA256 | bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | d94ee5e991b547849e1adf9a99cf915f668ce232 | b43ffceedead98ec617bc7b0df49875fe948e6792724b65e9e051b01c6645740 | 53,831,571 | 2720/158 |
| rollback | 82444451f705e81f4ac00b74101257868778239f | 75f84e08dc61b35b846eb1d9e2a7dc3f45cf73ae1b9b8ee73df8c06b50e4d689 | 53,830,504 | 2720/158 |

전체 복원·지속 증거 검증 뒤 원자 승격했다. 직전 정상82444451을 rollback으로 보존하고
이전 관리 rollbacke96f6e06 4f0182d712e688ad9f2d198741ed1fcd1e54a2689c0d4bb1637562f7566d96cd만 승인된2세대 수명으로 퇴역했다.
rollback은 동일 ZIP SHA/전체 manifest·이전 전체 복원 근거를 유지하며 이번에 구버전 엔진을
다시 실행하지 않았다. 다른 기존 원본/로그·프로필·SDK/Git·사용자 자료는 추가 정리하지 않았다.
각 실행이 만든 임시물만 자식 종료/소유권·지속 증거 검증 뒤 정리했다.

추가 디스크 331,350,016B(archive56MiB·증거192MiB·코드4MiB와 별도
안전64MiB), RAM 작업공간3GiB·추가 메모리7GiB+안전1GiB를 유지했다. 최종 시작/종료 여유
29,351,092,224/29,216,006,144B, 표본 차이 135,086,080B다. 개발 포함 단위
시작/종료 29,472,071,680/29,216,006,144B다. 최종 단계 표본 최저 디스크 29,351,002,112B,
관측 cgroup peak 6,942,609,408B다. 모든 순간의 절대 극값/고정
순증가 보장이 아니며 안전 기준을 낮추거나 증거를 버려 예산에 맞추지 않았다.

기존 환경·SDK10.0.401/seed·원본 checkout과 main을 보존한다. 마감 문서 뒤 runtime/검사/tools가
동결과 같음을 확인해 work/current만 정상 게시한다. 큰 내용/Office 편집/백업·4MiB 초과/총
보관 확대·실제 신원/권한 backend·상위 Run/물리 출력은 기존 잔여다. 초기 빈 #app와 과거
cold 읽기 원인은 미확정이고 M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/
WebView2·모바일·DPI/IME·물리 오디오·Office 앱·전체 UI·Space/Library는 미실행/미완료다.
