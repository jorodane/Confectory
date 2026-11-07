# V7 정지 PNG/JPEG 그림 사본 미리보기

원본 v666 `resource-preview.js::mountResourcePreview`의 image 분기처럼, 기존 자료 창의 미리보기 패널에 `img`를 `object-fit:contain`으로 표시한다. 도구줄/설정/창 배치·파일 이름 의미는 유지하고 새 zoom/도구/내용 편집 기능을 만들지 않는다. 이미 보관한 실제 프로젝트 사본만 전용 read 관측으로 읽는다. 사용자 개인 파일을 탐색하거나 외부 URL을 불러오지 않는다.

현재 지원은1MiB 이하 정지 PNG와 8bit baseline/progressive JPEG다. 원래 PNG/JPEG byte signature와 헤더를 읽어 width/height를 확인한 다음 표준 브라우저 decoder에 전달한다. 파일 확장자나 MIME만 믿지 않으며 Blob MIME은 확인한 raster 형식으로 고정한다. Native read의 project/ID/hash/size/canonical base64/SHA 검증은 그대로다. 헤더 reader는 독립 codec/완전한 문서 검증기가 아니며 브라우저가 디코딩을 거부하면 표시를 실패 처리한다. 브라우저가 일부 손상을 복구해 표시할 수 있으므로 파일 형식 전체의 완전성을 인증한다고 주장하지 않는다.

참고하는 일차 자료는 [PNG IHDR/chunk 규격](https://www.w3.org/TR/png-3/#11IHDR)과 [Chromium JPEG marker/segment 정의](https://chromium.googlesource.com/chromium/src/media/+/338620d1f9402c7a8c5791f8136cbd927a792a6f/parsers/jpeg_parser.h)다. PNG width/height는 IHDR의 unsigned32bit이고 JPEG 프레임의 dimension은16bit다. 길이/프레임/끝 경계를 확인하고 중복 PNG header·APNG 확장·지원 밖 JPEG process는 디코딩 전에 거절한다. SVG/HTML·GIF/WebP/BMP/AVIF/애니메이션은 이번 지원으로 표시하지 않는다.

표시 예산은 한 그림 최대16,777,216 pixels/한 변16,384, 활성 view 합계33,554,432 pixels다. 아직 로딩 중인 view도 먼저 예약한다. 이는 decoded 픽셀 예산이며 브라우저 전체 RAM 사용량의 절대 상한을 약속하지 않는다. EXIF로 가로/세로가 교환된 JPEG를 허용하지만 임의 dimension 변경은 거절한다. 범위를 넘거나 손상된 사본은 읽기/재확인 안내를 표시하고 원본 bytes를 바꾸지 않는다.

Blob URL은 해당 project/ID/hash/view generation 수명 안에서만 유지한다. 닫기·재열기·metadata 갱신·삭제·Home/프로젝트 전환은 decoder callback을 무효화하고 URL/lease를 한 번만 해제한다. 오류/생성 예외도 해제한다. 늦은 read나 decoder callback은 현재 창을 바꾸거나 새 URL을 만들지 못한다. 취소는 이미 시작한 모든 native I/O/브라우저 내부 자원의 즉시 중단을 보장하지 않는다.

개인 레이아웃은 기존 owner/ID/hash만 저장하고 Blob URL·byte·decode 요청은 저장하지 않는다. 재시작과 프로젝트 복귀는 현재 권한으로 다시 읽는다. preview/실패/재시도는 저장·import·ReviewConfirm·실행·권한 부여가 아니다. 원래 데이터/입력·소스·공개 override 계약·최종CAS와 완성된 텍스트 편집/복구를 유지한다.

선택 전체1MiB/64개 다중 가져오기는 [후속 원자 보관](V6_RESOURCE_BATCH.md)에 연결했다. 현재 폴더 첫 import는 [후속 파일/배치 거래](V6_RESOURCE_DESTINATION.md)에 연결했다. 큰 파일/선택 예산 초과, 다른 원본 그림·PDF·Office/mesh preview와 Office 내용 편집·자료 설명은 고정 잔여다. 초기화 빈 화면 원인은 미확정이다. 실제 Windows/WebView2·모바일·전체 UI와 Library/Space 전달은 별도 미검증으로 구분한다. [최종43단계(신규41·동등 근거 재사용2)](VALIDATION_V666_RESOURCE_IMAGES.md)는 실제 픽셀·읽기 거절/재시도·창/프로젝트/재시작 수명과 새 패키지/전체 복원을 구분한다.

정지 WebP의 현재 확장은 [지원 경계](V7_RESOURCE_WEBP.md)와 [별도 신규 검증](VALIDATION_V666_RESOURCE_WEBP.md)을 따른다. 위 PNG/JPEG 기록을 WebP 검증으로 바꾸지 않는다.
