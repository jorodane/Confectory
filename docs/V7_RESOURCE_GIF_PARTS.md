# 큰 GIF 사본의 원래 그림·애니메이션 패널 연결

고정 v666 ZIP의 app.js::resourceKind는 GIF를 그림으로 분류하고,
resource-preview.js::mountResourcePreview는64MiB 사전 검사 뒤 원래 Blob을 contain img
패널에 표시한다. 이미 보관 가능한1MiB 초과–4MiB GIF가 metadata-only로 남는 누락을
기존 image-parts 관찰과 GIF decoder에 연결한다. 원본 UI/배치와 작은 GIF·큰 PNG/JPEG/
BMP/WebP를 보존하며 새 편집기나 애니메이션 실행 제어를 추가하지 않는다.

현재 image kind·GIF87a/89a signature에 기존 선택 imagePreview와 읽기 전용
preview-image-part를 재사용한다. 서명은 GIF/codec 인증이 아니다. 현재 ProjectContext의
읽기 권한·ID/전체SHA/import generation/display revision·정수 part, 각 요청의 현재 전체
사본/영수증과 최종 의존성 검사를 그대로 사용한다. 각1MiB·최대 네 조각과 각/전체SHA를
확인한 뒤에만 parser/bitmap/Blob URL에 진입한다. path/외부 grant·캐시·오래된 bytes의
새 기준 위장·mutation replay는 추가하지 않는다. 공개/override 계약·저장v1·원자 저장/최종CAS와
기존2MiB RPC·파일/전체4MiB/64개 한도는 유지한다.

encoded whitelist에 GIF87a/89a만 더한다. 기존 GIF 헤더·전역/지역 palette·frame/control·
LZW 하위 블록/종료·투명도/disposal 검사는 그대로다. user-input·Plain Text/미정 extension·
불완전/중복 제어·잘린/후행 stream을 거절한다. 최대64프레임, 축16384와
logical width×height×frames≤16MP를 그대로 유지하며 그 가중 픽셀을 공유32MP lease로
계산한다. 첫 frame/subrectangle이 작더라도 logical canvas 전체를 매 프레임 계산한다.
큰 AVIF/SVG 예산은1MiB로 유지한다. 파서·renderer·공유 수명 구현 bytes는 미변경이다.

실제 기본 프레임의 createImageBitmap 성공/정확한 logical 치수와 close 뒤 원본 image/gif
Blob을 표시한다. 작은 GIF와 같은 실제 브라우저 애니메이션이며 가짜 frame·시간 계산·작업
실행 잠금을 만들지 않는다. 취소 불가 decode의 Promise 완료까지 lease를 보존하고 닫힌
owner의 늦은 성공은 URL을 만들지 않는다. 손상 첫 frame의 실제 decoder 실패와 제어한
Promise 실패를 구분하고, 나중 frame의 모든 LZW 오류를 새 decoder로 인증했다고 표현하지 않는다.
일반 codec/브라우저 스케줄과 실제 CPU/메모리 해제의 hard 상한을 보장하지 않는다.

기본 큰 read의 unavailable/no-data와 descriptor/part 문법은 유지한다. metadata-only
구 client는 기존 fallback, 종전 image-parts client는 이전 decoder bound로 큰 GIF를
거절할 수 있다. 새 UI+구 backend도 metadata-only 표시다. bytes/receipt를 이행하거나
재인코딩하지 않으며, 작은 내용 편집/백업1MiB와 기존 실제 권한을 확대하지 않는다.

생성한 실제 큰 GIF87a 정지와 GIF89a 두 프레임의 기본 이미지 전체 RGBA SHA, 화면
compositor의 실제 색상 전환을 각각 확인한다. canvas drawImage는 기본/첫 이미지라는
[기존 검증 경계](V7_RESOURCE_GIF.md)를 따르며 실제 화면의 운동 증거로 대체하지 않는다.
실제 압축 frame+무작위 comment sub-block의 정확4MiB도 네 조각과 같은 기본 픽셀을
확인한다. 큰 comment는 모든 대형 frame/최악의 LZW 성능 증거가 아니다. 큰 손상 첫 LZW의
실제 bitmap 실패·64frame/가중 pixel/제어·잘린 길이 거절, 현재 owner·late input·중단/닫기/
삭제/Home/project/cold·실제 읽기 권한 거절/명시 복구와 관련 회귀를 구분한다. native 최종
읽기 race와 지연/변조 응답은 통제된 fixture다. 사용자 개인 파일/외부 자료는 사용하지 않는다.

최종 LF/CRLF·새 교차 패키지/전체 복원·소유 IPC/실패 수명관리의 증거는 별도 기록에서
마감한다. 앞선 작은 GIF·다른 그림/Office/Run의 과거 검증을 신규 수에 합산하지 않는다.
원본·최신/롤백/증거와 승인된 소유 임시 수명/두 세대 보관만 유지하며 main은 보존한다.
큰 AVIF/SVG·내용/Office 편집/백업·4MiB 초과/총 보관 확대·실제 신원/권한 backend·상위
Run/GPU/물리 장치는 기존 잔여다. 초기 빈 #app와 과거 cold 읽기 원인은 미확정이다.
M11/M12/M4는 실제 회귀 없이 다시 열지 않는다. 실제 Windows/WebView2·모바일·DPI/IME·
물리 오디오·전체 UI·Space/Library 전달은 자동화/교차 패키징과 구분한다.
