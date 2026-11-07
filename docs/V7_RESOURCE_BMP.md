# 정지 BMP 자료 미리보기

원본 v666 `app.js::resourceKind`는 BMP를 그림으로 분류하고 `resource-preview.js`는
그림의 원래 Blob을 contain `<img>` 패널에 표시한다. 현재 저장된 프로젝트 사본의 같은
읽기 전용 화면에 제한된 Windows BMP를 연결한다. 이미지 편집·저장 형식 변환은 없다.

[Microsoft 파일 헤더](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapfileheader),
[정보 헤더·stride](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/ns-wingdi-bitmapinfoheader),
[GDI 저장 예](https://learn.microsoft.com/en-us/windows/win32/gdi/storing-an-image)가 일차 근거다.
파일의 BM/크기/reserved/offset과 40-byte BITMAPINFOHEADER, planes1·24/32bpp·BI_RGB,
양수 width/0이 아닌 signed height를 확인한다. DWORD 행 padding·상하 방향과 실제 픽셀
bytes 길이, 0 또는 정확한 image size를 확인한다. 32비트 BGRX는 이 공급자의 실제 브라우저에서
불투명 표시를 검증하며 alpha/bitfields 지원을 뜻하지 않는다.

1MiB 이하, 픽셀 시작 offset54·색상표 없음의 위 형식만 지원한다. 팔레트/16bpp·RLE·
BITFIELDS·내장 PNG/JPEG·CORE/V4/V5/ICC/다른 offset·잘린/후행 bytes는 지원하지 않는다.
불완전한 BM은 Blob URL 전에 거절한다. 기존 16384축·개별16MP·총32MP 논리적 pixel lease를
PNG/JPEG/WebP와 공유한다. WebP의 실제 `createImageBitmap` 사전 디코드/close와 폐기 뒤
완료까지 예산 보존을 재사용하며, API/codec 부재·실패는 명시 재시도 가능한 오류다.
디코더 Promise의 강제 취소나 브라우저 CPU/실제 memory hard 상한을 주장하지 않는다.

SHA 검증된 현재 owner/ID/hash 사본만 읽고 원래 bytes를 표시한다. 이름/설명·확인 삭제,
닫기/재열기·Home/프로젝트·cold와 늦은 읽기/bitmap 응답은 기존 수명 경계를 따른다.
새 native/API·영속 문법·권한·override/C# 원문·CSS·vendor/자산 수를 추가하지 않는다.
개인 파일/외부 자료를 자동 탐색·업로드하지 않는다. 다른 형식/큰 파일·선택 예산 확장과
V4/V5 backend 등 고정 잔여는 별도다. mesh는 원본에 renderer 근거가 없다.
간헐 초기화 빈 화면은 원인 미확정이며 실제 Windows/WebView2·모바일·전체 UI/Space
전달은 별도 미검증이다.
