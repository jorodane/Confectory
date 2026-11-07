# v666 정지 WebP 미리보기

기준은 저장소 v666 ZIP `app.js`의 WebP 그림 분류와 `resource-preview.js`의
프로젝트 사본 `<img>`/Blob URL/contain 패널이다. 새 renderer·편집 화면을 만들지 않고
기존 읽기 전용 그림 패널에 정지 WebP를 연결한다. 1MiB 파일·최대 변16384·개별16MP·
PNG/JPEG/WebP 전체32MP 예산을 유지한다. 원본 import·ID·이름·MIME·설명·부모/외부 원본,
계약·권한·Review→Confirm·CAS와 완료한 DOCX/XLSX 편집/복구를 변경하지 않는다.

WebP RIFF 길이/청크 범위/패딩, VP8 keyframe·크기, VP8L 버전/크기와 VP8X canvas를
선별한다. VP8/VP8L 정지 이미지와 확장 alpha·불활성 metadata를 지원한다. 실제 codec은
브라우저에 맡긴다. ANIM/ANMF와 animation flag, 잘린/중복/불일치 bitstream·범위 초과,
미지원 header features는 Blob URL을 만들기 전에 거절한다. 이 검사는 WebP 압축 codec이나
모든 비트스트림의 독립 무결성 검증 구현이 아니다.

현재 Chromium에서는 잘못된 entropy가 있는 WebP가 `<img>`의 크기/load 성공만 보고하는
경우를 확인했다. WebP는 `createImageBitmap`의 실제 디코드 성공·크기 확인 뒤 bitmap을
닫고 원본 bytes의 Blob URL로 표시한다. 이 API나 WebP 디코드가 없는 환경은 거절하며
검증되지 않은 `<img>` fallback으로 성공 처리하지 않는다. native 디코드 Promise는 취소할
수 없으므로 닫힌 viewer도 완료까지 픽셀 lease를 유지한다. 완료 시 bitmap을 닫고 폐기한
소유자/세대의 URL이나 화면을 만들지 않는다. hard CPU/메모리 해제 시점을 보장하지 않는다.
이미 표시한 URL은 기존 닫기·실패·프로젝트/관측 세대 교체에서 해제한다.

프로젝트 bytes는 기존 실제 SHA/읽기 권한 확인 후에만 디코더에 넘긴다. 다른 MIME의
`.webp`도 원래 그림 분류와 실제 byte header를 사용하며 저장된 MIME/원본은 수정하지 않는다.
외부 metadata URL·문서 스크립트는 조회/실행하지 않는다. GIF/APNG/움직이는 WebP,
SVG/AVIF/BMP 등 다른 형식은 이 단위의 지원 완료로 표시하지 않는다. 큰 자료의 전송·초안·
저장 한도 조정도 별도다. mesh는 원본에 분류/필터만 있고 실제 renderer 흐름이 확인되지
않았으므로 새 설계로 범위를 늘리지 않는다.

형식 근거:

- [Google WebP 컨테이너](https://developers.google.com/speed/webp/docs/riff_container)
- [WebP lossless header](https://developers.google.com/speed/webp/docs/webp_lossless_bitstream_specification)
- [VP8 frame header](https://datatracker.ietf.org/doc/html/rfc6386#section-9.1)
- [HTML ImageBitmap 생성·닫기](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#dom-createimagebitmap)

실제 Windows/WebView2·모바일·전체 UI·Space/Library 전달은 Linux 자동화 및 교차 패키징과
구분한다. 기존 간헐적 초기화 빈 화면은 원인 미확정 잔여다.

[최종 검증·이전 근거/미실행·보관·한계](VALIDATION_V666_RESOURCE_WEBP.md)를 따른다.
