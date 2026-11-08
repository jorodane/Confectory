# 큰 정지 AVIF 사본의 원래 그림 패널 연결

고정 v666 ZIP의 `app.js::resourceKind`는 AVIF를 그림으로 분류하고,
`resource-preview.js::mountResourcePreview`는64MiB 사전 검사 뒤 원래 Blob을 contain img
패널에 표시한다. 이미 보관 가능한1MiB 초과–4MiB 정지 AVIF가 metadata-only로 남는 누락을
기존 image-parts 관찰과 [작은 AVIF decoder 경계](V7_RESOURCE_AVIF.md)에 연결한다.
원본 화면/배치·작은 형식과 PNG/JPEG/BMP/WebP/GIF를 보존한다. 새 encoder·변환/편집 UI나
저장 문법은 추가하지 않는다.

현재 image kind의 첫32bit ftyp box를 제한된 길이16–76B/4B brand 단위로 확인한다.
major 또는 compatible `avif`가 있으면 기존 선택 `imagePreview`와 읽기 전용
`preview-image-part`를 광고한다. 이 서명은 codec 인증이 아니다. 정수 part·현재
ProjectContext 읽기 권한·ID/전체SHA/import generation/display revision, 각 요청의 현재 전체
사본/영수증·최종 읽기 의존성 검사를 유지한다. 각1MiB·최대 네 조각과 각/전체SHA를 확인한
뒤에만 기존 parser/bitmap/원본 image/avif Blob URL에 진입한다. path/외부 grant·캐시나
mutation replay를 추가하지 않는다. 기본 큰 read의 unavailable/no-data와 descriptor/part 문법,
파일/합계4MiB·64개/2MiB RPC·원자 저장/최종CAS·공개/override/권한은 그대로다.

encoded 파일 상한4MiB에 AVIF만 더하며 AV1 FRAME OBU의 길이 상한만4MiB에 연결한다.
sequence와 다른 OBU는 기존1MiB다. 기존8bit SDR AV1 profile0/1, reduced still sequence/한
FRAME, 자체 mdat의 단일 extent/항목과1–2item/alpha·속성 association/치수·color·auxiliary
검사를 보존한다. 128box·16property·16brand와 축16384, color/alpha 합산16MP 및 공유32MP
논리 lease도 그대로다. `avis`·HDR/10/12bit·grid/layer·외부/분할 extent·transform/미정
property·확장 box 등 거절은 유지한다. 이미지 로딩·bitmap 수명·실제 decoder·URL 해제 코드
bytes는 미변경이며 큰 SVG의1MiB 예산은 유지한다. 모든 AVIF profile/성능을 인증하지 않는다.

생성한 자연 압축 RGB700×600(1,574,540B)와 alpha600×500(1,553,057B)을 실제 File로 가져온다.
color FRAME은 각각1,574,247/1,125,018B로 기존1MiB 제한을 넘는다. Pillow의 별도 decode와
브라우저 전체 canvas를 비교하고 alpha premultiplication·색 변환의 허용오차 및 실제 최대차와
전체 canvas SHA를 기록한다. 실제 RGB는 차이0, alpha는 premultiplied color 최대1/alpha0이었다.
허용치는 color6/alpha1이다. 이는 원래 난수 RGB와 손실 없는 동등성을 주장하는 검사가 아니다.
설치된 Pillow/aom encoder는 fixture 생성에만 사용하며 새 runtime 의존성을 추가하지 않는다.

정확4MiB 입력은 실제 RGB stream 뒤 inert `free` box를 더해 네 조각과 동일한 픽셀을 확인한다.
압축 FRAME 자체가4MiB라는 증거와 구분한다. native4MiB fixture는 알려진 작은 AVIF+free box로
읽기 경계를 검증하며, 실제 큰 FRAME/alpha는 브라우저 사용자 흐름에서 별도로 검증한다.
손상 FRAME은 실제 codec 실패·URL 미생성을 확인하고 native race/지연·변조는 통제된 fixture다.
늦은 설명/명시 저장·stale·재시도, pending part의 닫기/반복/삭제/Home/프로젝트/cold와 실제
사본 읽기 권한 거절·정확 mode 복구를 검사한다. 사용자 개인 파일/외부 자료는 사용하지 않는다.

metadata-only 구 client는 기존 fallback이며 종전 image-parts client는 이전1MiB decoder bound로
큰 AVIF를 거절할 수 있다. 새 UI+구 backend도 metadata-only다. bytes/receipt/저장v1을
이행·재인코딩하지 않는다. 내용 편집/백업1MiB와 기존 실제 권한·최종 쓰기CAS는 확대하지 않는다.
취소 불가 bitmap Promise 완료까지 기존 lease를 유지하고 닫힌 owner의 늦은 성공은 URL을
만들지 않는다. 논리 pixel 예산은 실제 브라우저 CPU/전체 메모리 해제의 hard 상한이 아니다.

최종 LF/CRLF·새 교차 패키지/전체 복원·실패 수명관리와 최신/롤백 보관은 별도 기록으로 마감한다.
과거 작은 AVIF/다른 형식/Office/Run 증거는 신규 수에 합산하지 않는다. 큰 SVG·큰 내용/Office
편집/백업·4MiB 초과/총 보관 확대·실제 신원/권한 backend·상위 Run/물리 출력은 기존 잔여다.
초기 빈 #app와 과거 cold 읽기 원인은 미확정이며 M11/M12/M4는 실제 회귀 없이 다시 열지 않는다.
실제 Windows/WebView2·모바일·DPI/IME·물리 오디오·전체 UI·Space/Library 전달은 자동화/
교차 패키징과 구분한다. 승인된 소유 임시 수명/최신·롤백 두 세대만 관리하고 main은 보존한다.

[최종 신규63단계·지속 보관/미실행 기록](VALIDATION_V666_RESOURCE_AVIF_PARTS.md)을 따른다.
