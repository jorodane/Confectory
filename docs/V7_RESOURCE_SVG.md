# V7 소유 자료의 정지 SVG 미리보기

기준은 저장소 v666 ZIP의 `dist/app.js` 이미지 분류에 있는 `svg`와
`dist/resource-preview.js::mountResourcePreview`의 `item.kind==='image'` 경로다.
원본은 Blob URL의 `img`에 표시하고 종료 때 URL을 해제한다. 현재 native 분류도 SVG를
image로 반환했지만 이전 renderer가 이 형식을 표시하지 못했다. 기존 창·자료 설정·
contain CSS를 유지하여 이 실제 누락을 연결한다. 새 UI/원격 서비스/권한 정책은 없다.

전체 고정 목록을 다시 확인했다. M11/M12/M4는 확인된 회귀 없이 다시 열지 않는다.
V4/V5와 다른 사용자 B2/V9는 실제 신원·권한 source가 선행한다. 큰 자료는 기존
resources.v1/구버전 reader 호환, HD Run은 기존 2MiB 관측/pipe 예산을 넘는 전달 방식이
선행한다. 이들 요구를 완료로 바꾸거나 무한한 형식·문맥 조합으로 늘리지 않는다.
이번 단위는 이미 존재하는 소유 자료·읽기·CAS 기반에서 독립적으로 연결 가능한 SVG다.

지원 경계는 UTF-8, 최대256KiB의 자체 포함된 정지 SVG다. `svg/g/defs`, 기본 도형·경로,
선형/방사형 그라데이션·stop, 도형 clipPath, text/tspan·title/desc를 제한된 속성으로
지원한다. 크기는 정수 px 또는 viewBox 전용이며 축16384/16MP, 전체 그림32MP 기존
lease를 공유한다. 최대1024요소/깊이24, 경로·점4096구간, 숫자32768개, 문자65536개로
복잡도를 제한한다. 이 한계 밖의 파일은 보관을 거절하는 것이 아니라 미리보기를 거절한다.

DTD/entity/처리명령은 XML 파싱 전에 거절한다. script/이벤트/외부 URI/이미지·use/
foreignObject/style/애니메이션/filter/mask/패턴/외부 namespace와 미지원 속성은 제거해
넘기는 대신 표시를 거절한다. 내부 paint/clip 참조는 고유 ID와 실제 gradient/clipPath
종류를 확인하고 clip 안의 재귀 참조를 거절한다. 외부 폰트/CSS/코드 로딩은 없다.
미지원 SVG의 사본·선택·설명·입력은 유지하며 같은 사본을 다시 확인할 수 있다.
SVG 표준 전체·SVG 편집·애니메이션 지원을 뜻하지 않는다.

검증한 XML은 페이지 DOM에 삽입하지 않는다. 격리된 SVG Blob/HTMLImageElement.decode
경로로 실제 크기를 확인한 뒤 기존 그림 패널에 표시한다. Chromium bitmap decoder는
SVG Blob을 받지 않으므로 raster의 createImageBitmap 경로를 그대로 강요하지 않는다.
viewBox 전용 그림에는 검증한 크기를 명시한 표시용 derivative를 만든다. 원래 도형·
원본 사본의 바이트/hash/저장 형식/ID는 바꾸지 않는다. 닫기·Home·프로젝트 전환은 URL을
해제하고 늦은 decode/read를 격리한다. 진행 중 decode lease는 실제 promise가 정리된 뒤
해제한다. 반복 열기/실패/재시도/재시작은 기존 소유 관측으로만 사본을 다시 읽는다.

native 자산 보관/이름·설명·삭제/권한/Review→Confirm/최종 CAS/Undo, C# 원문과 공개
계약은 변경하지 않는다. 현재 환경의 실제 Chromium·.NET engine 검증과 Windows 교차
패키지를 구분한다. 실제 Windows/WebView2/모바일/전체 UI/Space 전달은 별도다.
초기 빈 #app의 간헐 실패 원인은 이번 그림 작업이나 통과 검사로 해결됐다고 간주하지 않는다.

최종 동결 코드·새 검사·재사용 근거·패키지/전체 복원·수명/공간은
[검증 기록](VALIDATION_V666_RESOURCE_SVG.md)에 명시한다.

최초256KiB 표시 범위의 후속은 [큰 SVG 연결](V7_RESOURCE_SVG_PARTS.md)에서 다룬다.
256KiB 초과–4MiB에도 원래 geometry/참조/문자/pixel 예산과 격리 decode를 유지하고,
큰 입력의 주석/markup를 파싱 전에 제한한다. 위 최초 검증 기록은 별도다.
