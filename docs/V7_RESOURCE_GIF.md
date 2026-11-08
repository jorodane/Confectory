# GIF 자료 미리보기

v666 `app.js::resourceKind`의 GIF 분류와 `resource-preview.js`의 원본 Blob `<img>` contain
패널에 정지 그림과 제한된 애니메이션을 연결한다. 새 편집기·변환·저장 동작이나 UI 배치는 없다.

[CompuServe GIF89a 사양](https://www.w3.org/Graphics/GIF/spec-gif89a.txt)의 GIF87a/89a 헤더,
logical screen·전역/지역 색상표·프레임 사각형·인터레이스·LZW 크기/하위 블록·종료,
그래픽 제어의 투명도와 disposal 0–3, comment/application 블록을 사전 확인한다.
GIF/Graphics Interchange Format은 CompuServe가 정의한 형식이다. 이 코드는 새 LZW decoder가
아니며, 압축 데이터 디코드·화면 합성·애니메이션은 기존 브라우저 codec과 `<img>`가 수행한다.

파일당 1MiB, 축 16384 이하와 **64프레임 이하**, 전체 프레임에 대한
`logical width × height × frames ≤ 16MP`를 확인한다. 이 프레임 가중 픽셀을 기존 PNG/JPEG/
WebP/BMP의 총32MP 논리 lease에 포함한다. 첫 프레임만 작거나 부분 사각형이더라도 logical
canvas 전체를 프레임마다 계산한다. 색상표가 없는 별도 stream을 이전 파일의 palette로
보충하지 않는다. user-input 제어, Plain Text/정의되지 않은 extension, 예약 disposal/비트,
중복/미완성 제어·프레임·종료와 예산 초과는 Blob URL 전에 거절한다. 모든 GIF의 지원이나
임의 압축 데이터 검증의 완료를 뜻하지 않는다.

`createImageBitmap`으로 실제 기본 프레임을 먼저 디코드하고 정확한 GIF 치수를 확인한 뒤
bitmap을 닫고 원본 bytes의 `image/gif` Blob을 표시한다. API/codec 부재·실패는 재시도 가능한
오류다. 취소 불가인 bitmap Promise가 끝날 때까지 lease를 보존하고, 닫힌 창의 늦은 성공은
URL을 만들지 않는다. 실제 `<img>`가 애니메이션을 표시하며 시간을 대신 계산하거나 가짜
프레임을 만들지 않는다. 브라우저 스케줄·실제 CPU/메모리 해제의 hard 상한은 주장하지 않는다.

[HTML canvas 이미지 규칙](https://html.spec.whatwg.org/dev/canvas.html#image-sources-for-2d-rendering-contexts)은
애니메이션의 기본/첫 이미지를 drawImage의 source로 사용한다. 따라서 기본 프레임·투명도는
canvas pixel로, 실제 애니메이션은 compositor screenshot pixel로 각각 검사한다. 손상 첫 프레임의
실제 codec 거절과 제어한 decoder Promise 실패를 구분한다. 나중 프레임의 모든 LZW 오류를
별도 재구현한 decoder로 완전 검증했다고 표현하지 않는다.

현재 owner/ID/hash의 SHA 확인 사본만 표시하고 bytes·URL은 private layout에 넣지 않는다.
이름/설명·명시 삭제·닫기/재열기·Home/프로젝트/cold와 늦은 read/bitmap은 기존 수명을 따른다.
기존 PNG/JPEG/WebP/BMP 코드·공통 예산을 보존한다. native/API·저장 v1·권한·C#·override·
Review/Confirm·최종 CAS·CSS·vendor는 바꾸지 않는다. 생성 fixture만 사용하며 개인 파일이나
외부 자료를 탐색/업로드하지 않는다. 큰 파일과 다른 원본 형식의 미리보기는 별도 잔여다.
초기 빈 화면 원인은 미확정이며 실제 Windows/WebView2·mobile·전체 UI는 별도 미검증이다.

[최종 검증과 보관·미실행 경계](VALIDATION_V666_RESOURCE_GIF.md).

1MiB 초과–4MiB 사본의 후속은 [기존 frame 가중/bitmap 수명을 보존한 큰 GIF 관찰](V7_RESOURCE_GIF_PARTS.md)을 따른다.
