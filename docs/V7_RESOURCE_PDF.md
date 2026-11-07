# V7 PDF 읽기 전용 미리보기

저장소 v666 `resource-preview.js`의 PDF 페이지·이전/다음·너비 맞춤/100/150/200%
배율과 기존 자료 창/캔버스 CSS를 연결한다. 활성 프로젝트가 기존 ID/SHA/권한으로
읽은 1MiB 이하 사본만 전달한다. 문서 내용/입력/원본 C#·계약·Review→Confirm·
최종 CAS에는 변경이 없다. PDF 편집·폼·서명·링크 실행·첨부 추출·암호 입력 UI를
추가하지 않는다. 암호 문서는 명시 안내와 같은 사본의 재시도를 제공한다.

원본 ZIP의 PDF.js 4.10.38 main/worker·CMap·표준 글꼴 184개와 LICENSE 4개를
바이트 그대로 보존한다. third-party 파일은 수정하지 않았고 외부 CDN에서 읽지 않는다.
신뢰된 소비자 bundle의 자산 수 한도만 256→384로 늘리고 `application/octet-stream`을
추가한다. 경로/링크 거절·파일당4MiB·전체 raw/canonical32MiB·SHA·UTF-8 LF 규칙과
공개 호출 계약·권한·CSP는 유지한다. `.mjs`는 LF, 폰트/CMap은 binary 속성으로 고정한다.

실제 전용 module Worker를 직접 생성해 PDFWorker port로 전달하며 fake-worker fallback을
사용하지 않는다. 문서는 URL 대신 검증한 바이트로 전달한다. Worker fetch는 고정된
동일 출처 CMap/font 경로의 GET만 허용하고 credentials 생략·redirect 거절을 강제한다.
`isEvalSupported:false`, `enableXfa:false`, annotation 비활성화와 renderer-only API를
사용하며 scripting manager/링크·폼 layer를 만들지 않는다. 문서 URI는 실행하지 않는다.

PDF 창은 최대2개, 최대1,000페이지다. 페이지 원래 viewport는 한 변14,400 이하,
표시 CSS는 한 변8,192·면적16M 이하, 실제 canvas는 한 변4,096·면적4M 이하로
제한한다. 이미지16M 픽셀 제한과 library image canvas16MiB 예산을 지정한다.
초과 이미지/복잡한 글꼴은 완전 재현되지 않을 수 있으며 원본 사본은 유지한다.
로딩/각 렌더에 10초 이벤트 타이머를 둔다. 이는 main-thread가 응답하지 않는 모든
경우의 강제 CPU 제한을 보장하지 않는다.

페이지/배율/resize가 바뀌면 이전 렌더를 취소하고 소유 세대/version을 다시 확인한다.
닫기·접기·이름 변경·Home/프로젝트 전환/실패에서 canvas/observer/RAF를 해제하고
document/bridge를 파기한다. 파기 응답이 없더라도 500ms 뒤 직접 생성한 Worker를
종료하고 lease를 반환한다. 성공/실패 뒤 개인 레이아웃에는 기존 owner/ID/hash만 남는다.

Mozilla [공개 보안 공지 목록](https://github.com/mozilla/pdf.js/security/advisories)을 확인했다.
[2024 공지](https://github.com/mozilla/pdf.js/security/advisories/GHSA-wgrm-67xf-hhpq)의
명시 영향 범위는 <=4.1.392이며 eval 비활성화도 권고한다.
[2026 공지](https://github.com/mozilla/pdf.js/security/advisories/GHSA-hq66-cqwq-w95j)는
>=5.6.83의 scripting/CSP 구성에 관한 것이다. 반입본4.10.38은 이 명시 범위 밖이다.
이는 모든 취약점 부재를 보증하지 않는다. API 선택은
[고정 버전 API source](https://github.com/mozilla/pdf.js/blob/v4.10.38/src/display/api.js)를
대조했다. PDF.js Apache-2.0, CMap 및 Foxit/Liberation 글꼴 고지는 반입 폴더에 유지한다.

큰 파일/부분 읽기·Office 편집·mesh/다른 원본 그림·설명 metadata/기타 고정 잔여는
별도다. 실제 Windows/WebView2·모바일·전체 UI·Space 전달과 Linux 자동화 결과를 구분한다.
