# v666 분류·개념·모듈 헤더 아이콘

기준은 저장소 v666 ZIP(SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`)의 `app.js` → 헤더 `object-icon-edit`와 `editObjectIcon`/`editIconValue`다. 원본은 선택한 선언의 `icon`과 dirty 상태를 바꾸고 Browser를 갱신한다. 함수 계약·상속·포함 관계나 같은 종류 전체의 공통 아이콘을 바꾸는 조작이 아니다. 완료한 정보·객체·기능 헤더와 정보 함수/속성·graph 동작 카드 이미지는 다시 구현하지 않는다.

## 지원 범위와 저장

- 현재 프로젝트가 직접 소유한 `category`·`concept`·`module`의 기본/독립 선언창 헤더에 기존 공통 팝오버·기호/이모지·로컬 PNG/JPG/WebP를 연결했다. 기존 object-header 클래스와 창 제어를 사용하며 CSS를 바꾸지 않는다. 원래 개인 파일명·경로·원본 파일은 저장/업로드하지 않는다. 생성한 테스트 이미지만 검증에 사용한다.
- 이미지 변환·128×128 WebP·5MB 입력 제한·bounded native container 검증·CSP·Browser image markup은 기존 처리다. 세 종류의 선언/Browser projection에 그 값을 연결했다. 짧은 잘못된 `data:` 값도 원시 metadata 경로에서 검증하며 기존 일반 문자 metadata Apply 경로는 유지한다.
- 새 헤더 저장은 아이콘·직접 설명만 기존 owner 후보/receipt/checkpoint CAS에 넣는다. 기존 `functionPresentation` 내부 helper를 같은 metadata 전용 경계로 재사용하며 함수의 기존 계약은 유지한다. 새 함수·계약 ID, 자동 복제/target 선택, 원격 이미지 요청, 실행 권한을 추가하지 않는다. 일반 선언의 이름·부모·관계 편집은 기존 Apply 경로다. 다른 미적용 선언 입력과 저장 경계가 충돌해도 이미지 선택과 기존 입력을 보존하며, 헤더 취소가 다른 이름 입력을 지우지 않는다.
- native는 원래 source/kind/namespace/등록·전체 관측·hash/revision을 확인하고 주석·CRLF·Exact64와 변경하지 않은 구문을 보존해 metadata만 병합한다. 부모·외부 원본·모듈 요구/기본 구현·C#·공개 override 입출력 계약은 변경하지 않는다. 독립 창은 서버가 검증한 project/context/view/owner/binding과 metadata 전용 요청만 사용한다.
- private 입력은 프로젝트·창·선언 ID로 나누며 Undo/Redo·팝오버 취소·cold·오류 입력을 보존한다. 응답 유실은 같은 owner receipt로 확인하고 중복 적용하지 않는다. 저장 또는 취소 응답 중 새 입력은 시작 snapshot과 구분해 보존한다. Save는 작업 사본이며 실제 파일 반영은 별도 전체 Review와 명시 compiler Confirm이다.

## 발견 사항과 집중 검증

정상 조회로 info 객체가 교체될 때 편집 대상이 달라진 것으로 오인하던 새 연결을 안정된 창 generation/선택과 source hash로 구분했다. 독립 선언창 응답에 빠져 있던 `creationReviewIds`/`reviewGroupKind`를 기본 창과 동일하게 전달하여 필수 owner·등록부 묶음을 Review에 요청한다. 서버의 불완전한 묶음 거절을 유지한다. 취소는 당시의 정확한 입력만 제거하여 뒤에 입력한 값이나 다른 일반 선언 입력을 지우지 않는다. 불리한 저장 경계에서도 새 이미지 선택을 private 입력에 보존한다.

집중 native는 세 종류의 이미지/설명 후보·원문/부모/모듈 계약·등록·Browser projection·기존 문자 metadata와 위험/잘못된 이미지·중복·계약 변경·foreign owner의 전체 거절을 확인했다. 실제 UI는 세 종류의 정상 Confirm, 독립 창과 다른 기본 선택, Undo/Redo·cold·취소·응답 유실·저장/취소 중 늦은 입력·checkpoint 실패·peer CAS 충돌·잘못된 bound 요청·다른 일반 입력 보존을 확인했다. 같은 namespace/ID의 실제 다른 프로젝트를 왕복하는 개념 헤더와 graph 동작 카드 아이콘도 통과했다. 기존 정보/객체/기능 이미지 native 회귀를 실행했다.

집중 작업은 `/workspace/artifacts/v536-verification-managed/runs/9ff999d2566147ce9c71cb339370fd41`에 기록한다. base `525931e`와 각 source overlay/검사 입력·로그·fixture·프로필을 구분하며 초기 실패를 통과로 세지 않는다. Review에 항상 체크박스가 있다는 가정, 겹친 창의 닫기 선택, 프로젝트 전환 뒤 viewport 크기를 복원하지 않은 검사 오류는 제품 결함과 별개다. 실제 UI 조작과 native 필수 Review를 강제 클릭이나 약한 성공 조건으로 대체하지 않았다.

## 최종 마감과 잔여

최종 소스의 LF/CRLF 독립 checkout·새 교차 패키지·압축 복원·실제 패키지 엔진/UI·최신/롤백 지속 보관은 `tools/verify_desktop.py --suite declaration-icons`의 57단계로 별도 마감한다. 결과와 source commit·manifest·실행/재사용/미실행 및 공간 수치는 완료 후 이 문서에 추가한다.

기존 배율 메뉴 일시 실패는 이전 `c6cf72b5e98f4e28bb4ee97184714366` 실행에서 cold 메뉴 재진입만 실패했고, 후속 재현·LF/CRLF가 통과한 상태다. 원인은 여전히 미확정이다. 이번 헤더 수명 수정과 같은 원인이라고 추정하지 않으며 기존 배율 검사의 성공 조건은 바꾸지 않는다. [원래 실패·후속 증거](VALIDATION_V666_ACTION_ICONS.md).

I6의 모듈 핀·Set 출력·종류 항목과 ABI closure·고급 타입/핀 표시명·B2/M4/M11/M12·V2–V9는 고정 후속이다. 원본 핸들러가 없거나 숨긴 핀은 새 필수 요구로 추가하지 않는다. 3D/권한 별도 팩·이동과 실행 분리·override 원계약 유지·독립 계약 복제 제외 합의도 유지한다. 실제 Windows/WebView2·물리 모바일·DPI/IME·전체 UI·Space/Library 전달은 미검증이다.
