# v536 정보 헤더의 로컬 이미지 아이콘

기준 게시본은 `7b6062e`이며 원본은 저장소의 v536 ZIP이다. 원본 `editIconValue`는
사용자가 고른 PNG/JPG/WebP(5,000,000바이트 이하)를 브라우저에서 읽고, 비율을 유지해
128×128 캔버스 가운데 그린 다음 WebP quality `.9`의 data URI를 `icon`에 보관한다.
이번 최소 흐름은 **직접 소유 정보 헤더 → 이미지 선택/취소 → 적용 → Undo/Redo →
설명과 Save → 재시작 → Review 취소 → 명시적 Confirm**이다.

## 연결과 보존 경계

기존 팝오버의 이미지 버튼·숨긴 file input·미리보기·오류 영역을 연결했다. 팝오버와
카드 치수·CSS·메뉴는 바꾸지 않는다. 원본과 같은 local decode/canvas 변환을 사용하며
선택 순서가 바뀌거나 팝오버가 닫히면 늦은 decode 결과를 적용하지 않는다. 생성한
blob URL은 성공/실패 뒤 해제한다. 원래 파일명·경로·원본 파일을 프로젝트로 복사하지
않고, 변환한 이미지 값만 기존 `editorIcon` 선언 metadata에 저장한다. 별도 자산 저장소,
외부 업로드·AI 생성·사용자 프로젝트 실행이나 Helper 권한은 추가하지 않는다.

현재 새 이미지 저장은 `schema` 정보 헤더에 한정한다. 객체·기능 헤더, 속성·함수 카드
아이콘은 이번 이미지 저장 허용 범위가 아니며 기존 glyph 지원은 유지한다. 상속/외부
원본·공개 계약·본문·정확한 수치·설명과 기존 참조는 변경 대상이 아니다. 헤더 Undo/Redo는
같은 owner/source의 정확한 입력 집합만 복원하며 저장 이후나 다른 입력을 덮어쓰지 않는다.

Native 후보는 65,500자 이하 canonical base64 WebP의 RIFF 길이·단일 image chunk·128px
치수·padding·색상 프로필 표시를 검사한다. 실제 픽셀 decode는 원본처럼 브라우저가
수행한다. Native는 이미지 codec이나 파일/네트워크 접근을 실행하지 않는다. 캔버스가
출력하는 ICCP 색상 프로필은 허용하고 애니메이션·EXIF/XMP·알 수 없는 chunk·경로·원격
URL·SVG/HTML·다른 타입의 저장은 거절한다. 컨테이너 기준은
[WebP 공식 명세](https://developers.google.com/speed/webp/docs/riff_container)를 따른다.
기존 source/metadata 크기 한계를 낮추거나 부적합 값을 자동 치환하지 않는다.

웹 호스트의 `img-src 'self'`가 원래의 blob 미리보기와 inline 아이콘을 막는 실제 누락도
수정했다. 이미 Windows WebView 호스트가 사용하는 `img-src 'self' data: blob:`로 맞추고
script/connect·원격 이미지·실행 권한은 늘리지 않았다. 정보 Browser/헤더는 허용된 inline
WebP만 `img`로 렌더하며 임의 URL이나 SVG를 이미지 요청으로 만들지 않는다.

저장에는 기존 owner 입력·한 후보·원자 checkpoint·receipt 조회·최종 CAS를 재사용한다.
이미지와 설명은 전체 성공 또는 전체 미적용이다. 응답 유실은 먼저 기존 결과를 조회해
중복 적용을 막는다. 응답 대기의 새 이미지는 수락된 이전 이미지/hash와 결합한 별도
입력으로 cold까지 보존하고 다음 명시적 Save만 반영한다. Confirm 전에는 원본 파일을
바꾸지 않으며 최종 compiler Confirm에서도 선택한 정보 선언 한 파일만 바뀌어야 한다.

## 격리 검사와 발견 사항

합성 PNG/JPG/WebP만 사용한다. 원본 팝오버 10영역의 치수·글꼴·배경을 대조하고,
취소/Escape·잘못된 종류·5MB 초과·읽기 실패·늦은 decode와 다른 선택·Undo/Redo·설명·
재시작을 검사한다. 저장 실패·실제 source 경합·적용/조회 응답 유실·늦은 입력·독립 창과
다른 문서의 exact64 입력·Review/Confirm은 별도 흐름으로 확인한다.

최초 Native 검사 도우미는 effective values 목록을 객체로 읽어 실패했다. 도우미만
수정하고 실패 로그를 보존했다. 첫 화면 검사는 웹 CSP로 로컬 decode가 거절됐고,
다음 저장 검사는 Chromium 캔버스의 ICCP 출력을 검증기가 누락해 거절됐다. 두 실패의
fixture·프로필·로그·스크린샷을 보존하며 통과로 계산하지 않는다. 색상 프로필이 있는
경우와 없는 경우의 opaque/alpha·lossy/lossless 조합도 Native 검사에 포함한다.

## 공간과 고정 잔여

사전 예산 200MiB+안전64MiB를 유지한다. 기존 자료는 추가 삭제하지 않으며 이번 검사에서
직접 만든 fixture/교차 패키지만 증거를 보관한 뒤 승인된 수명관리로 정리한다. 원본·Git·
SDK·보관 빌드·과거 cache·로그·프로필·사용자 자료는 보존한다.

I6 자체 중첩 정의·다른 실제 노출 아이콘·정보 외 요소/속성/함수의 로컬 이미지는 남는다.
연결된 정보 하위 값의 정상 읽기 전용이나 원래 숨긴 root/mobile 핀은 새 요구가 아니다.
forwarded 부모/opaque/import 영향 결합·고정8/9행·B2·M4/M11/M12는 별도 잔여로 유지한다.
공개 오버라이드의 원래 입출력 계약은 고정하며 독립 계약 복제를 필수 범위에 넣지 않는다.
전체 UI·실제 Windows apphost/WebView2·모바일 기기 실행·Library 전달은 미완료다.

집중 7흐름 45확인, Native 3확인, 이미지 renderer/receipt 2확인과 기존 glyph/속성/함수/상속 헤더/final CAS 영향 회귀 43확인이 통과했다. 원본 팝오버 10영역과 75개 리소스 바이트/SHA가 일치한다. 합성 입력 생성에는 검증 환경의 Pillow를 쓰며 제품 이미지 codec 의존성은 추가하지 않는다.

## 독립 checkout·새 교차 패키지 확정

검증 소스 `a140741db73bf03595646372be79969377e43fff`의 변경 Git blob·기존 autocrlf·clean을 확인하고 Native/CLI Release와 새 Linux 엔진을 생성했다. 독립 checkout의 새 이미지/늦은 입력 7확인, 독립 창/peer 8확인, 생산 final CAS 4확인, Native 3확인, 이미지 renderer/receipt 2 및 기존 receipt 단위 7확인이 통과했다.

새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 엔진/렌더러의 이미지 흐름 7확인까지 6단계를 통과했다. 전체 2352개(선언 manifest 2351개)의 목록·SHA와 Core/Native DLL·8개 제품 소스의 바이트를 확인했다. manifest SHA `fe082a0dd71ff477df51f79df3d1f22f23f6a3538821a13b96f26fb9e86ea9ca`. 전체 manifest·fixture/로그/프로필 증거 보관 뒤 이번 RAM 사본만 정리했고 기존 보관 빌드·SDK·원본·사용자 자료는 추가 삭제하지 않았다.

최종 후속 커밋은 문서/evidence만 달라 위 검증 소스와 제품 실행 코드는 같다. 실제 Windows apphost/WebView2·실제 모바일 기기·Library 전달 및 전체 UI는 계속 미완료다.
