# 큰 PNG/JPEG 그림 미리보기

v666 ZIP의 `Confectory-v666/dist/resource-preview.js::mountResourcePreview`는64MiB
사전 검사 뒤 image kind를 원래 contain 패널의 `img`에 표시한다. 저장소 ZIP SHA256은
`7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`이다.
현재 이미 보관 가능한 파일당/전체4MiB 안에서1MiB 초과 PNG/JPEG의 표시 누락을 연결한다.
원본 레이아웃·메뉴·파일/설명 의미를 유지한다. 멤버/공유는 실제 신원·권한 backend 선행이
필요하며, 고급 타입·핀 표시명 정책이나 가능한 조합을 이 단위의 새 요구로 추가하지 않는다.

기존 native `read`의 unavailable/no-data 의미는 유지하고 PNG/JPEG signature에만 별도
선택 필드 `imagePreview`를 더한다. 기존 텍스트의 `preview` 필드를 다른 형식으로 바꾸지
않는다. 이전 UI는 새 필드를 무시해 종전 metadata-only 표시를 유지할 수 있고, 새 UI도
capability 없는 backend에 같은 제한 안내를 제공한다. 저장 v1 문법과 bytes/receipt는 그대로다.

관찰 전용 `readProjectResourceImagePart`/`Layout.preview-image-part`는 ProjectContext의
현재 project/ID·전체SHA·import generation·compound display revision과 정수 part만 받는다.
고정1MiB씩 최대 네 조각이고 마지막 길이는 남은 bytes다. native는 요청마다 전체 보관본과
영수증을 확인하고 manifest/identity/store/layout/이름/설명/삭제/내용 sidecar의 최종 읽기를
검사한다. cache나 lease에 고정한 오래된 bytes로 새 revision을 위장하지 않는다.
추가 path·다른 project·범위 밖 part·변경된 basis는 거절한다. 조각 응답은 기존2MiB RPC
안에 있으며 전역 한도나 저장·업로드 상한을 올리지 않는다.

브라우저는 header/각 조각의 정확한 item·revision·part/offset/length·canonical base64·SHA를
검사하고, 전체 bytes의 SHA까지 일치한 뒤 기존 image renderer에 넘긴다. 부분 그림이나
혼합 세대를 표시하지 않는다. raw byte 상한4MiB는 PNG/JPEG에만 적용하고 다른 그림의1MiB
상한과 각 형식 구조 검사, 한 변16384/그림16,777,216 pixels/활성 합계33,554,432 pixels는
유지한다. native signature와 JS metadata screening은 완전한 codec/문서 인증이 아니며 실제
브라우저 decoder가 실패하면 기존 안내·명시 retry를 사용한다. 더 큰 파일을 자르거나 PNG/JPEG로
잘못 해석하지 않는다. WebP/BMP/GIF/AVIF/SVG의 큰 크기는 이번 지원에 포함하지 않는다.

닫기·Home·같은 창 재열기·삭제·프로젝트 전환은 조각 도착과 hash 대기마다 기존 token을
확인하고 다음 요청/decoder/Blob URL 생성을 차단한다. 성공/실패의 URL·pixel lease는 기존
한 번 해제를 재사용한다. 관찰에는 mutation replay가 없고 busy만 같은 basis로 제한 재시도한다.
private presentation에는 bytes/Blob URL/미결 part를 저장하지 않는다. prefix 대기 중과 동일하게
검증된 header 뒤의 새 설명 입력을 다시 bind해 덮지 않는다. 내용 편집/백업1MiB, 원본 C#과
public/override 계약·부모외부 보호·실제 권한·Review→Confirm·최종 쓰기CAS는 변경하지 않는다.

검증에는 생성한 File만 사용한다. 큰 PNG의 전체 픽셀 SHA·JPEG의 실제 디코드/샘플 픽셀,
정확4MiB의 네 조각·mixed/stale/변조/예산 거절·응답 지연·삭제/Home/cold/다른 프로젝트와
관련 작은 형식/텍스트·내용 저장 회귀를 구분한다. 초기 빈 #app 및 이전 게시본 cold 읽기1회
원인은 미확정으로 유지한다. 실제Windows/WebView2·모바일·DPI/IME·전체UI·Library/Space는
자동화/교차 생성·복원과 구분하며, 최종 검증 결과에서 실행 여부를 마감한다.

## 통합 복원 검사에서 확인한 내용 초안 읽기 복구

동결1a2dd917의 최종 복원 검사에서 실제 `readResourceContentDraft`가 `busy`를 반환한
뒤 재시도 없이 오류로 끝나 프로젝트 왕복의 개인 입력창이 열리지 않았다. 그림 부분의
검사 통과와 구분해 실패 증거58a99f1c를 보존한다. 내용 초안/미확정 요청의 같은 읽기에만
최대3회/50ms busy 재시도를 연결하고 창 수명·현재 project를 매 응답/재시도에서 검사한다.
다른 오류나 다른 owner는 거절하고 mutation 재실행·자동저장·rebase는 하지 않는다.
수정 전 소스의 단위 재현과 수정 후 거절/중단 검사를 구분하며, 실제 UI는 첫 busy를 통제
주입하여 같은 목표 재관찰과 입력/미확정 요청 복구를 검증한다. 이전의 빈 #app 및6a82895b
cold 읽기 실패가 같은 원인이라고 추정하지 않는다. 최종 통합 결과는 별도 기록으로 마감한다.

후속 dd2d3800의 최종 검사에서는 native 실행 admission의 `busy`가3회 상한까지 이어졌다.
최초1회 뒤 중단과 구분해, 자동 무한 재시도를 추가하지 않는다. 기존 명시적 ‘다시 확인’으로
같은 개인 입력/미확정 요청을 읽는 정상 복구 경계를 검사한다. 검사기는 마지막3회가 동일
목표의 `busy`인 경우에만 해당 버튼을 한 번 누르며 다른 오류를 이 경로로 숨기지 않는다.
3회 busy를 통제 주입해 상한 거절과 명시 재확인 전후 사본·개인 요청 bytes 불변도 확인한다.

[최종 신규 검증·지속 보관·실기기 한계](VALIDATION_V666_RESOURCE_RASTER_PARTS.md)를 따른다.

후속 큰 BMP는 [동일 조각/기존 BMP 형식 보존](V7_RESOURCE_BMP_PARTS.md)으로 연결한다. 위 PNG/JPEG 당시 범위와 검증은 역사적 근거이며 큰 다른 형식의 완료로 확대하지 않는다.

큰 정지 WebP도 [같은 조각/기존 WebP 검증의 후속](V7_RESOURCE_WEBP_PARTS.md)으로 연결한다. 위 역사적 PNG/JPEG 당시 검증과 큰 다른 형식의 잔여는 구분한다.

큰 GIF도 [기존 정지/제한 애니메이션·조각 관찰](V7_RESOURCE_GIF_PARTS.md)에 연결한다. 위 역사적 당시 범위와 이후 큰 AVIF/SVG 잔여를 구분한다.

큰 정지 AVIF는 [전용 후속](V7_RESOURCE_AVIF_PARTS.md)에서 기존 image-parts 관찰과
동일 AVIF profile을 연결한다. 이 문서의 최초 PNG/JPEG 검증 수에 합산하지 않는다.
