# 큰 BMP 사본의 원래 그림 패널 연결

고정 v666 ZIP의 `app.js::resourceKind`는 BMP를 그림으로 분류하고
`resource-preview.js::mountResourcePreview`는64MiB 사전 검사 뒤 image의 Blob을
원래 contain 패널에 표시한다. 이미 보관 가능한1MiB 초과–4MiB BMP가 metadata-only로
남는 누락을 기존 PNG/JPEG 조각 관찰과 BMP decoder에 연결한다. 새 형식·편집기·UI·
권한 정책을 만들지 않는다. 큰 다른 그림·4MiB 초과와 전체 보관 확대는 별도 잔여다.

현재 image kind·BM signature에 기존 선택 `imagePreview`와 읽기 전용
`preview-image-part`를 재사용한다. 서명은 BMP 인증이 아니다. 현재 ProjectContext의
읽기 권한과 ID/전체SHA/import generation/compound display revision·정수 part, 각 요청의
전체 사본/영수증·최종 의존성 검사는 그대로다. 각1MiB·최대 네 조각·기존2MiB RPC·각/전체SHA
검증 뒤에만 parser/bitmap/Blob URL에 진입한다. 캐시·다른 path·외부 접근·mutation replay를
추가하지 않고 native/API·공개/override 계약과 저장v1·원자 저장/최종CAS를 변경하지 않는다.

브라우저의 기존 encoded whitelist에 BM만 더한다. 원래24/32bpp BI_RGB·40-byte DIB·
offset54·색상표 없음, signed height와 DWORD 행 padding·정확 파일/픽셀 길이·imageSize0
또는 정확 길이를 유지한다. 양수 width·축16384/개별16MP/공유32MP와 실제
createImageBitmap 성공/크기·close 뒤 contain img 표시를 그대로 재사용한다. BGRX는 불투명
표시이며 alpha·bitfields·팔레트/RLE·CORE/V4/V5/ICC 지원으로 확대하지 않는다.
잘못된 큰 BM도 완전 전송/전체SHA 확인 뒤 parser에서 거절하고 decoder/URL을 만들지 않는다.
형식 파서·디코더 수명/논리적 pixel lease의 구현 bytes는 그대로다. 강제 decode 취소나
브라우저 전체 CPU/memory hard 상한·전체 BMP 표준 지원을 주장하지 않는다.

기존 기본 read는 큰 파일의 unavailable/no-data를 유지한다. metadata-only 구 client는
같은 제한 안내를 유지하고, image-parts를 알지만 큰 BMP를 모르는 구 client는 기존 decoder
한도로 표시를 거절할 수 있다. 저장 원본/receipt는 바꾸지 않으며 새 UI+구 backend는 원래
metadata-only fallback이다. 다른 큰 WebP/GIF/AVIF/SVG와 작은 형식의 예산도 유지한다.
이전 [BMP 지원](V7_RESOURCE_BMP.md)과 [PNG/JPEG 조각](V7_RESOURCE_RASTER_PARTS.md)의
역사적 검증은 이번 BMP 확대의 신규 검사 수에 더하지 않는다.

생성한24/32비트·top-down/bottom-up·행 padding 사본의 실제 전체 RGBA SHA, 유효한
4,193,334B BMP의 네 조각과 큰 상한/정확4MiB의 잘못된 픽셀 길이 거절을 검증한다.
BMP의 offset54와 행 stride 규칙을 바꾸어 정확4MiB 입력을 억지 허용하지 않는다.
변경 전 게시본의 누락·native 최종 읽기 race/현재 세대·실제 읽기 권한 거절·중단/재시도/
close/reopen·삭제·Home/project/cold·늦은 설명 입력과 별도 작은 BMP/기존 큰 그림·Office/
내용 편집 회귀, LF/CRLF·새 교차 패키지/전체 복원·실패 수명관리는 최종 기록에서 구분한다.

원본과 최신/롤백·증거를 보존하고 승인된 소유 임시 수명/두 세대 보관만 유지한다.
초기 빈 #app 및 이전 cold 읽기 실패의 원인은 미확정이다. M11/M12/M4는 실제 회귀 없이
다시 열지 않는다. 실제 신원/권한 backend·큰 편집/백업·QHD/4K/FHD+·GPU/물리 장치는
기존 잔여다. 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Space/Library 전달은
자동화/교차 패키징과 구분하며 실제 기기 실행을 주장하지 않는다.
