# v666 정지 WebP 미리보기 검증

최종 동결: `78bc55751bcb35203b6b9b414777064f9778363d`. 게시 후속은 문서만 바꾸며 제품/검사 코드는 같다.
총 **65단계(신규65·재사용 합산0)**: LF22, CRLF22,
새 패키지·전체 복원·실패 수명관리21. 개발 검사는 최종 수에 더하지 않았다.

| 구분 | 실제 확인 |
|---|---|
| 독립 LF/CRLF | 별도 Git objects/checkout, HOME, NuGet, engine cache; Release/MCP/실제 Linux engine과 원본/계약·자산 경계 |
| 메타데이터·수명 단위 | VP8/VP8L/VP8X/ALPH·RIFF 길이/패딩·단일 bitstream/canvas·animation 거절, PNG/WebP 공통 pixel lease와 늦은 bitmap/URL 정리 |
| 실제 브라우저 | 손실/무손실/손실 alpha/무손실 alpha의 실제 pixel·크기, unknown metadata의 불활성 URL, 손상 데이터의 실제 bitmap decode 거절 |
| WebP engine UI | LF10·CRLF5 흐름; 새 패키지/전체 복원본에서도 정상/수명 흐름을 새로 실행 |
| 기존 기능 회귀 | PNG/JPEG·EXIF와 원래 pixel/URL 수명, DOCX/XLSX 편집·no-op 복원본 보호, 설명·내용·Office/PDF와 일반 C# Review→Confirm/CAS/Undo/Redo·재시작/늦은 입력 |
| 보관·실패 | 새 Windows 교차 패키지 구조/프로브, 전체 SHA/ZIP CRC/파일·디렉터리 모드 복원, FIFO/반복/실패/자식 종료 후 증거 내구 보존과 owned 임시물 정리 |

원본은 저장소 v666 ZIP의 WebP 그림 분류와 `resource-preview.js`의 `<img>`·Blob URL·
contain 패널이다. 기준 SHA256
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`과 CSS를 유지했다.
[지원 경계](V7_RESOURCE_WEBP.md)에 따라 1MiB 이하 정지 WebP를 추가했고 새 저장/권한
계약이나 vendor·이미지 편집 화면을 만들지 않았다. native 저장/권한 코드와 완료한 편집기는 바이트 그대로다.

실제 Linux engine/Chromium에서 SHA 확인된 프로젝트 사본을 손실/무손실/alpha로 표시하고,
Canvas pixel 값을 확인했다. 일반 binary MIME의 `.webp`와 unknown RIFF metadata도 같은
보관 bytes로 표시하며 URL을 조회하지 않았다. 실제 animated/truncated·과도한 canvas와
SVG/HTML 위장은 URL을 만들지 않는다. 깨진 entropy는 실제 bitmap decode에서 실패하며
재시도도 파일/입력·예산을 보존한다. 정상 WebP의 늦은 실제 bitmap 완료를 제어해 닫힌 viewer가
bitmap을 닫고 URL을 만들지 않는지, 기능 부재가 무검증 fallback 없이 거절/명시 재시도되는지
확인했다. native 읽기 지연 응답/닫기·다시 열기, 이름/설명 metadata와 확인한 삭제도 확인했다.
CRLF/전체 복원본에서는 owner/ID/hash만 private layout에 남고 새 bytes를 다시 읽는 cold engine,
실제 읽기 거절/재시도, Home 왕복·다른 실제 프로젝트의 같은 namespace 격리를 확인했다.
LF의 실제 contain 화면·제목·설정 패널도 직접 확인했고 source-bound screenshot을 보존했다.

최종 신규65단계 검사는 이 변경에 필요한 UI/API/자산/수명 범위다. native controlled-race/private/
독립 공급자 세부 검사는 native 코드·프로브가 바뀌지 않아 이번에 반복하지 않았다. 이전
77단계 기록 `/workspace/artifacts/v536-verification-managed/runs/acf81ac09c2a4d999812a3b536e9019b.json`을 별도 참고 근거로 보존하며
이번 신규 통과 수에는 재사용으로 합산하지 않는다. 전체 byte/계약 불변은 이번 경계 검사다. 이전/현재 source의 native·프로브 diff가 없고 SDK/NuGet 전체 fingerprint가 같은 참조 증명을 별도 보존했다.

개발 첫 실행은 깨진 WebP의 `<img>` load 성공을 전체 디코드 완료로 가정해 오류 판정을
기다리다 실패했다. 실제 진단에서 현재 Chromium의 크기/load와 `image.decode()`는 성공하지만
잘못된 픽셀 데이터가 남을 수 있음을 확인했다. `createImageBitmap`은 같은 샘플을 거절하고
정상 샘플은 실제 pixel을 복원했다. 이에 WebP 사전 디코드와 bitmap close/lease 수명을 추가하고
개발3단계를 통과한 뒤 최종 동결에서 모두 새로 검사했다. 이 개발 실패는 숨기지 않는다.

증거:

- 최종 실행: `/workspace/artifacts/v536-verification-managed/runs/03f75b815f4d4d59bd78d8356ebf113e.json`
- 증거 ZIP SHA256: `d916c3e13cabc27e77d36d9c222183a4cf932a6f06c04e2bc87691771fa4da86` (5,876,495B)
- 개발 실패: `/workspace/artifacts/v536-verification-managed/runs/a6e988ea2d064eaa9198242b446a5187.json`
- 개발3단계: `/workspace/artifacts/v536-verification-managed/runs/15a58186bb2e46ac83d3c740be0310d7.json`
- 최종·두 개발 실행은 전체 manifest/ZIP 검증 후 `cleaned`; 각 owned root 부재를 확인했다.
- 디코드 진단 입력/스크립트/결과는 `/workspace/scratch/v666-resource-webp/decoder-observation.json`과
  `decode-observation.json`에 남긴다. 앞선 중간 진단의 error event는 cleanup 영향이 있을 수 있어
  실패 판정의 근거로 쓰지 않고 bitmap/Pillow와 최종 실제 디코드 검사를 사용한다.

| 지속 보관 | 출처 동결 커밋 | ZIP SHA256 | ZIP bytes | 파일/디렉터리 |
|---|---|---|---:|---:|
| latest | `78bc55751bcb35203b6b9b414777064f9778363d` | `1b0f6a4ecabae9ffbc72b3e97d7566d7d5018a41b4afe5c316ef62459828f06b` | 53,800,180 | 2703/158 |
| rollback | `55b1d1ffdfc88c8cfb72be2e12be68efc901d050` | `e977fd848fcfeecb35c87b2cdcae46fce006dba38746d68d806ca3f5e9bfbead` | 53,798,299 | 2703/158 |

보관 index: `/workspace/artifacts/v536-verification-managed/packages/index.json`.
latest manifest SHA256: `a2c413167d0454f7b581287db0f935eee847a6e022091707516fb98939fdb0bd`.
rollback manifest SHA256: `58027fe5e10cf1cb2b88f20057dbb6bfa596f816dda81531b38838d87e21c66e`.
rollback은 이전 검증본이며 WebP 표시를 포함하지 않는다. native 데이터/초안/권한 schema는
그대로이므로 새 codec 이행은 없다. 기존 관리형 원자 승격과 이 실행의 owned 임시물 정리만
사용했다. 과거 보관자료·원본·SDK·기존 로그/프로필·사용자 데이터는 추가 정리하지 않았다.

공간: 시작 여유 1,131,261,952B, 결과 수집 시 1,121,792,000B
(약 1.04GiB), 이번 단위 순증가 9,469,952B
(약 9.0MiB). 개발/실패 증거와 Git 변경을 포함하며 향후
단위당 증가량 보장은 아니다. 최종 실행 자체 순증가는 7,733,248B다.
사전 예산 candidate56+증거20+코드/Git8+안전64=148MiB, RAM 작업공간3GiB+여유512MiB,
추가 메모리7GiB+안전1GiB를 유지했다. 명령 단계 표본 최소 여유 1,129,398,272B,
환경 cgroup peak 5,420,482,560B는 압축/승격 순간 전체 최저 직접 측정이 아니다.

16MP/전체32MP는 논리적 pixel lease이며 브라우저 메모리/CPU 해제의 hard 상한이 아니다.
디코드 Promise는 취소할 수 없어 retire 뒤에도 완료까지 예산을 유지한다. API/codec이 없는
환경은 지원하지 않는다. animated WebP·GIF/APNG·SVG/AVIF/BMP, 큰 파일과 다른 고정 잔여는
남으며, mesh는 원본에 실제 renderer 흐름이 없어 임의 구현/완료로 표시하지 않는다.
기존 간헐적 초기화 빈 화면은 원인 미확정이다. 실제 Windows/WebView2·모바일·전체 UI·
Space/Library 전달은 미실행이며 Linux 자동화/교차 패키징과 구분한다.
