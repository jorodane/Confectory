# 정지 AVIF 자료 미리보기

v666 `app.js::resourceKind`의 AVIF 분류와 `resource-preview.js`의 원래 Blob `<img>` contain
화면에 1MiB 이하의 정지 AVIF를 연결한다. 그림 편집·변환·새 UI나 저장 문법은 추가하지 않는다.

일차 근거는 [AOM AVIF v1.2.0](https://aomediacodec.github.io/av1-avif/v1.2.0.html)과
[AV1 bitstream specification](https://aomediacodec.github.io/av1-spec/av1-spec.pdf)이다.
연결된 `ispe` 크기와 실제 AV1 reduced-still sequence의 최대 치수·8bit 설정을 대조하고,
하나의 frame을 브라우저 codec에 전달한다. 임의로 발견한 ispe만 믿거나 새 AV1 decoder를
구현하지 않는다. 압축 entropy와 최종 pixel은 native browser decoder가 처리한다.

현재 profile은 avif brand, 32bit 크기 box, 자체 mdat의 단일 extent/항목, 16bit item ID,
8bit SDR RGB AV1 profile0/1의 4:2:0 또는 4:4:4와 선택적인 동치 크기의 단색 alpha다.
primary item·항목 정보·property association·auxiliary 연결·location을 함께 검증한다.
색상/alpha 전체 extent가 겹치거나 비거나 외부 data reference를 사용하면 거절한다.
기본 size/codec/pixel/color 속성과 alpha용 auxC 이외의 transform/property는 거절한다.
최대16 brand·128 box·16 property, 1–2개 항목과 정확한 reduced sequence/단일 FRAME OBU만
지원한다. sequence/grid/layer·clap/회전·metadata/HDR/ICC/다른 auxiliary·분할 extent·확장 box는
이번 profile의 지원 완료가 아니며 원문을 자동 변경하지 않는다.

색상/alpha 각각의 축16384와 합산16MP를 적용한다. alpha를 별도 디코드 표면으로 계산해
기존 PNG/JPEG/WebP/BMP/GIF의 공유32MP 논리 lease에 포함한다. 실제 AV1 헤더와 속성 크기가
다르거나 codec 설정/채널이 다르면 Blob URL 전 거절한다. 브라우저 실제 memory/CPU 해제의
hard 상한을 뜻하지 않는다. 10/12bit·HDR나 모든 AVIF 문법을 인증하는 기능이 아니다.

`createImageBitmap`의 실제 디코드가 성공하고 정확한 논리 치수를 확인하면 bitmap을 닫고
원본 bytes의 image/avif Blob을 표시한다. API/codec 부재·실패는 명시 retry 가능한 오류다.
취소 불가인 decode Promise가 완료될 때까지 lease를 유지하고 닫힌 창의 늦은 성공은 URL을
만들지 않는다. 이름/설명·확인 삭제·Home/프로젝트/cold와 늦은 read는 기존 수명을 재사용한다.
권한 있는 현재 owner/ID/hash의 SHA 확인 사본만 읽고 bytes/URL을 private layout에 저장하지 않는다.

원본 contain 패널·CSS·native API/저장 v1·공개/override·C#·ReviewConfirm/최종 CAS와 기존
완료 편집기/자료 전송을 보존한다. 새 vendor나 runtime encoder는 없다. 코드로 생성한 fixture만
사용하며 개인 파일/외부 자료를 탐색/업로드하지 않는다. 큰 파일·SVG 등 실제 고정 잔여와
구분한다. 초기 빈 화면 원인은 미확정이고 실제 Windows/WebView2/mobile·전체 UI는 미검증이다.

[최종 검증과 보관·미실행 경계](VALIDATION_V666_RESOURCE_AVIF.md).

1MiB 초과–4MiB 정지 사본은 [큰 AVIF 후속](V7_RESOURCE_AVIF_PARTS.md)에서 같은
profile/논리 예산·bitmap 수명을 유지해 연결한다. 위 작은 사본 검증 기록은 별도다.
