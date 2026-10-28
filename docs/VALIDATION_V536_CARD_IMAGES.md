# v536 속성·함수 카드의 로컬 이미지

기준은 `2d4ef89`와 원본 v536 ZIP의 직접 속성 `[data-property-icon]` 및 함수 카드
`[data-function-icon] → editIconValue`다. 원본 공통 팝오버는 이 조작에도 로컬 이미지를
제공한다. 기존 정보/객체/기능 헤더에 연결한 변환과 저장을 카드에 연결하는 범위다.

## 저장과 소유 경계

기존 직접 소유 정보 속성, 객체가 직접 사용하는 소유 스키마의 속성, 새 정보/객체 속성,
직접 소유 정보의 저장된 함수 카드 및 생성 중 함수 카드에 같은 PNG/JPG/WebP 선택을
연결한다. 원래 팝오버·CSS·레이아웃·메뉴·아이콘 해제 의미를 바꾸지 않는다. 원본의
5,000,000바이트 입력·128×128 canvas WebP `.9`·65,500자 metadata와 기존 RIFF/ICCP
검증을 공유한다. 원래 파일명/개인 경로나 원본 파일은 저장/업로드하지 않는다.

정보 속성은 `editorFieldIcon_<nativeKey>`, 함수는 기존 `editorIcon`을 사용한다. 기존
`schema-icon`·새 정의·`function-add/edit` 후보와 owner checkpoint/receipt/최종 CAS를
유지한다. 값·기본값·타입/핀/함수 ID·순서·설명·본문 C#·기존 참조·부모/외부 원본과
등록을 임의로 바꾸지 않는다. 어느 한 이미지/값/소스가 부적합하면 전체 미적용이다.
상속/외부 속성과 가져온 함수의 읽기 전용을 풀지 않는다. 공개 override의 입출력은
원계약을 유지하며 독립 계약 복제는 필수 범위가 아니다.

새 이미지가 저장 응답보다 늦게 편집되면 기존 수락 receipt의 전체 이미지/소스/hash를
대조한다. 새 속성은 같은 생성 결과의 `schema-icon`, 새 함수는 같은 함수 ID의
`function-edit`로 기존 재결합 절차를 사용한다. 적용 여부가 불명인 요청은 먼저 조회하고
새 생성이나 중복 적용을 추측하지 않는다. 자동 Confirm이나 C# 재작성은 추가하지 않는다.

## 검증 절차

`tools/verify_desktop.py --suite card-images`는 별도 LF/CRLF Git·NuGet·엔진 cache·CLI home을
가진 RAM checkout에서 Release·MCP·Linux 엔진을 새로 만든다. 기존 속성/함수의 정상,
checkpoint 실패, 응답 유실, 실제 정의 source 충돌, 취소, 저장 중 새 이미지와 cold/Review/
Confirm을 분리한다. 새 정보/객체 속성·함수, 객체의 소유 스키마 편집과 독립 창/다른 문서
입력 경계를 실제 UI로 검사한다. 원본 팝오버 10영역·기호 편집·기존 헤더·생산 CAS와
Native의 잘못된 마지막 이미지·중복·foreign/inherited/stale 요청도 확인한다.

새 Windows x64 교차 패키지와 전체파일 SHA/모드 manifest·압축/RAM 복원을 검사하고,
패키지 및 복원본의 엔진/렌더러에서 두 카드 이미지 흐름을 실행한다. 실패 수명 검사와
지속 증거 보존 뒤 이번 실행의 임시물만 정리하며 최신 검증본/정상 롤백본 두 개를
기존 managed index에 보관한다. 기존 자료·과거32세대 압축/정리 승인은 없고 수행하지 않는다.
시작 여유는 약2.27GiB이며 추가 지속 공간144MiB(안전64MiB 포함), RAM3GiB 및 메모리
예산을 먼저 확인한다. 실제 순증가와 root 정리 여부는 실행 전후 실측으로 기록한다.

I6 자체 중첩 정의·다른 원본 노출 아이콘, 고정7/8행 실제 영향 closure·9행,
B2·M4/M11/M12 및 전체 UI는 이 단위와 구분한다. 실제 Windows apphost/WebView2·
실제 모바일 기기 실행과 Space/Library 전달은 교차 패키지/복원 검사로 완료 처리하지 않는다.

첫 실제 속성 화면 검사는 Undo 뒤 Redo가 원래 속성 history에 연결되지 않아 실패했다.
원본 프로젝트 편집의 Redo를 기존 snapshot history에 연결하고 scope/ID/hash/revision 및
이후 입력 동일성으로 제한했다. 실행/서버 권한이나 저장/CAS를 완화하지 않고 아이콘 키보드
초점도 같은 행에 복원한다. 실패 fixture/스크린샷/로그는 지속 증거 ZIP에 보존한다.
