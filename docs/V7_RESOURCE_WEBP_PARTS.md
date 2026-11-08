# 큰 정지 WebP의 원래 그림 패널 연결

고정 v666 ZIP의 app.js::resourceKind는 WebP를 그림으로 분류하고,
resource-preview.js::mountResourcePreview는64MiB 사전 검사 뒤 image의 Blob을
원래 contain 패널에 표시한다. 이미 보관 가능한1MiB 초과–4MiB 정지 WebP의
metadata-only 누락을 기존 image-parts 관찰과 WebP decoder에 연결한다. 기존 작은
WebP와 큰 PNG/JPEG/BMP를 보존하며 새 renderer/편집기·권한 정책을 추가하지 않는다.

현재 image kind·RIFF/WEBP signature에 기존 선택 imagePreview와 읽기 전용
preview-image-part를 재사용한다. 서명은 codec 인증이나 애니메이션 허용이 아니다.
기존 현재 ProjectContext의 읽기 권한, ID/전체SHA/import generation/display revision·정수
part와 각 요청의 전체 사본/영수증·최종 의존성 검사는 그대로다. 각1MiB·최대 네 조각의
정확한 응답/각·전체SHA를 확인한 뒤에만 parser/bitmap/Blob URL에 진입한다.
새 path/접근권한·캐시·lease로 오래된 bytes를 새 기준으로 표시하거나 mutation을 replay하지 않는다.
공개/override 계약·저장v1·원자 저장/최종CAS와 기존2MiB RPC는 미변경이다.

기존 encoded whitelist에 RIFF/WEBP만 더한다. RIFF 전체 길이/청크/패딩·VP8 keyframe,
VP8L 버전/크기·VP8X canvas/alpha의 원래 검사를 유지하고 ANIM/ANMF/animation flag·
잘린/중복/불일치 frame·미지원 feature는 거절한다. 불활성 metadata는 원래 bytes의 일부이며
외부 URL/문서 script를 조회·실행하지 않는다. parser/decoder의 구현 bytes는 그대로다.
축16384/개별16MP/공유32MP와 실제 createImageBitmap 성공/크기 확인·close 뒤 원본
Blob URL/contain img 표시를 유지한다. 잘못된 entropy의 img load만 성공으로 취급하는
fallback을 추가하지 않는다. 비취소 decode 중 close의 lease/bitmap 수명도 변경하지 않는다.
이 검사는 codec의 독립 인증이나 hard CPU/브라우저 전체 memory 상한을 보장하지 않는다.

기본 큰 read의 unavailable/no-data와 imagePreview/part 문법은 그대로다. metadata-only
구 client는 기존 fallback을 사용하고, 종전 image-parts client는 이전 decoder 예산으로
큰 WebP를 거절할 수 있다. 새 UI+구 backend는 기존 metadata-only 표시다. 보관 원본/
receipt를 이행하거나 재인코딩하지 않으며 작은 read·내용편집/백업1MiB·파일/합계4MiB/64개를
늘리지 않는다. 큰 GIF/AVIF/SVG와 움직이는 WebP의 지원을 뜻하지 않는다.

생성한 실제 큰 lossless/lossy 압축 이미지로 전체 무손실 RGBA SHA와 손실 이미지의
실제 디코드 픽셀을 확인한다. 실제 압축 frame과 불활성 무작위 JUNK 청크의 정확4MiB 입력은
네 조각·원래 픽셀을 확인하며, 복잡한 모든 WebP/색상 profile 성능의 증거는 아니다.
큰 손상 entropy의 실제 bitmap 거절과 큰 animation의 사전 거절, 기존 작은 alpha/metadata와
디코드 실패·비취소 수명도 구분한다. native 최종 읽기 race와 지연/변조 응답은 통제된 fixture,
실제 File/엔진/bitmap/DOM/canvas와 읽기 권한 거절·복구는 실제 실행이다. 개인 파일이나
외부 자료를 임의 업로드하지 않는다. LF/CRLF·새 패키지/전체 복원·관련 BMP/PNG/JPEG/Office와
내용 입력 복구·실패 수명관리의 최종 증거는 별도 검증 기록에서 마감한다.

[작은 WebP의 과거 경계](V7_RESOURCE_WEBP.md)와 큰 BMP/PNG/JPEG의 과거 검증을
이번 신규 수에 합산하지 않는다. 큰 다른 그림·내용/Office 편집/백업·4MiB 초과/총 보관 확대·
실제 신원/권한 backend·상위 Run profile/GPU/물리 장치는 기존 잔여다. 초기 빈 #app와
과거 cold 읽기 실패 원인은 미확정이다. M11/M12/M4는 실제 회귀 없이 다시 열지 않는다.
원본·최신/롤백/증거와 승인된 소유 임시 수명/두 세대 보관을 유지하며 main은 보존한다.
실제 Windows/WebView2·모바일·DPI/IME·전체 UI·물리 오디오·Space/Library 전달은
자동화/교차 패키징과 구분한다.
