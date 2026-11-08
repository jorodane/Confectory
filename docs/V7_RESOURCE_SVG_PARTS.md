# 큰 정지 SVG 사본의 원래 그림 패널 연결

고정 v666 ZIP의 app.js::resourceKind는 SVG를 그림으로 분류하고 resource-preview.js는
64MiB 사전 검사 뒤 원래 Blob을 contain img 패널에 표시한다. 현재 저장은 파일/합계4MiB지만
SVG 표시는256KiB이고 큰 read는 metadata-only였다. 기존 소유 사본·정지 SVG profile에서
256KiB 초과–4MiB 표시와1MiB 초과의 image-parts 전달을 연결한다. 원본 UI·배치와 작은
그림/다른 완료 형식, 권한·저장/CAS를 보존하며 편집·SVG 표준 전체로 확대하지 않는다.

현재 image kind에서 UTF-8 BOM과 ASCII 공백 뒤 첫 `<`를 XML 후보로만 판별한다. 이는 SVG/
XML 인증이 아니며 DTD·HTML·손상 XML에도 전달 후보가 될 수 있다. 기존 선택 imagePreview와
읽기 전용 preview-image-part를 재사용한다. 현재 ProjectContext의 실제 읽기 권한·ID/전체SHA/
import generation/display revision·정수 part, 각 요청의 현재 전체 사본/영수증·최종 읽기
의존성을 유지한다. 각1MiB·최대 네 조각과 각/전체SHA 확인 뒤에만 전체 UTF-8을 해석한다.
UTF-8 문자가 조각 사이에 나뉘어도 조각별로 decode하지 않는다. 기본 큰 read의 unavailable/
no-data와 descriptor/part 문법·2MiB RPC·파일/합계4MiB·64개·저장v1과 쓰기 계약은 그대로다.

SVG encoded 상한만4MiB에 연결한다. 기존 정지 profile의1024요소/깊이24·속성당65536자/
32속성·도형/경로4096구간·숫자32768개·문자65536개·축16384/16MP/공유32MP를 유지한다.
DTD/entity/처리명령·script/event/외부 namespace/URI/image/use/foreignObject/style/animation/
filter/mask/패턴·미정 속성·잘못된 paint/clip 참조와 재귀 clip의 거절도 유지한다.

새로 허용하는256KiB 초과 입력은 XML 파싱 전에 주석1024개와 markup4096개로 제한한다.
주석은 전진하는 index 검색으로 한 번 순회하고 닫히지 않은 주석을 즉시 거절한다. 반복된
미완성 주석마다 나머지 전체를 정규식으로 다시 찾지 않는다. 기존256KiB 이하 경로는 동일한
주석 처리이며 작은1025주석 파일도 계속 지원한다. 검증은 원래 XML 전체를 실제 DOMParser로
파싱하므로, 검사 편의를 위해 주석을 지워 잘못된 XML을 유효한 입력으로 바꾸지 않는다.
태그/속성·숫자·문자 제한은 그 뒤 기존 validator로 적용한다. 파일 크기·논리 complexity 예산이
브라우저 CPU/전체 메모리 해제의 hard 상한을 보장하지는 않는다.

검증한 XML은 페이지 DOM에 삽입하지 않는다. 기존 격리 SVG Blob/HTMLImageElement.decode,
논리 치수 검증과 원래 contain 패널을 사용한다. viewBox 전용 파일의 명시 크기 derivative,
비취소 decode Promise 완료까지의 lease와 owner/URL 정리 코드는 미변경이다. 원본 사본의
bytes/전체SHA·ID·저장 문법을 바꾸거나 재인코딩하지 않는다. metadata-only 구 client는 기존
fallback이며 종전 image-parts client는 이전1MiB/256KiB SVG bound로 거절할 수 있다.
새 UI+구 backend에서1MiB 초과 파일은 metadata-only다. 작은 내용 편집/백업1MiB와 실제
권한·부모/외부 원본·공개/override·Review→Confirm·최종 쓰기CAS는 확대하지 않는다.

생성한800 rect의400×200 도형 SVG는1,267,431B다. 각 좌표/크기의 긴 소수 정밀도 표기로
encoded 양을 늘렸으며 원래 요소/숫자 예산은 넘지 않는다. 별도 정수 pixel plane과 실제
브라우저 전체 canvas RGBA를 비교한다. alpha65×33의1,048,600B SVG와256KiB+1 및 정확4MiB도
확인한다. 큰 주석은 inert base64/UTF-8이며 실제 조각 경계에서 분리된 UTF-8 문자도 포함한다.
4MiB 입력은 같은 도형+큰 주석이며4MiB의 복잡한 geometry/최악 성능 증거와 구분한다.
색상/alpha의 premultiplied 허용오차1과 실제 최대차·전체 canvas SHA를 기록한다.

native4MiB fixture는 작은 SVG+생성 주석으로 관측/전체SHA·최종 의존성 경계를 검증한다.
BOM/공백/선언/DTD 후보와 비XML/불완전BOM/공백만의 후보 거절을 별도로 검사한다. DTD 후보의
전달 성공이 DTD 표시 허용을 뜻하지 않으며 브라우저의 pre-XML 거절을 별도로 확인한다.
HTML 위장·DTD/entity·PI/encoding·미완성/과다 주석·과다 markup·UTF-8·요소/속성/숫자/문자/
경로·원래 활성 기능 거절, 조각 변조/stale/중단/명시 retry·늦은 설명/입력 보존을 검사한다.
실제 읽기 권한 거절·mode 복구, 닫기/반복/삭제/Home/다른 프로젝트/cold 및 decode 실패/늦은
완료를 구분한다. 지연/변조/실패 주입·최종 읽기 race는 통제된 fixture다. 실제 codec/DOM/canvas와
생성 사본의 읽기 권한 거절은 실제 실행이며 사용자 개인 파일/외부 자료는 사용하지 않는다.

최종 LF/CRLF·관련 회귀·새 교차 패키지/전체 복원·실패 수명관리와 최신/롤백 보관은 별도
기록에서 마감한다. 과거 형식/Office/Run의 검증 수를 신규에 합산하지 않는다. 큰 내용/Office
편집/백업·4MiB 초과/총 보관 확대·실제 신원/권한 backend·상위 Run/물리 출력은 기존 잔여다.
초기 빈 #app와 과거 cold 읽기 원인은 미확정이고 M11/M12/M4는 실제 회귀 없이 다시 열지 않는다.
실제 Windows/WebView2·모바일·DPI/IME·물리 오디오·전체 UI·Space/Library 전달은 자동화/
교차 패키징과 구분한다. 승인된 소유 임시 수명/최신·롤백 두 세대만 관리하고 main은 보존한다.
