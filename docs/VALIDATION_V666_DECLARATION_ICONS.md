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

첫 최종 실행 `dbeb14f829de4d61bafd9898146f52e4`는 LF Release/MCP·빈 캐시 엔진·mixed 선언 검사를 통과한 뒤, 이전 Browser 검사에서 `module` 이미지를 금지하던 낡은 기대값으로 실패했다. 제품 소스는 그대로 두고 기존 검사에서 승인된 여섯 종류의 inline 이미지를 명시 확인하며, implementation/body/blueprint/project/pack/unknown 및 위험 URI 거절과 receipt 검사를 유지했다. 실패 증거를 보존하고 최종 후보 검증을 새로 수행한다.

최종 후보 `b4a83596710015a524d2fd14079b2123408fc489`를 `tools/verify_desktop.py --suite declaration-icons`로 새로 실행해 **57/57단계**가 통과했다. LF 25·CRLF 22단계는 Git 객체를 공유하지 않는 독립 checkout·별도 HOME/NuGet·빈 엔진 캐시에서 Release/MCP/엔진을 빌드했다. 새 교차 패키지/압축 복원/수명관리 10단계도 통과했다. 기존 action-icons 49단계를 유지하고 헤더 native·기본/독립 창·프로젝트 왕복·패키지/복원 UI 8단계를 추가했다. 기존 카드 이미지·중첩 정의·소유 복합 전환·배율 검사를 생략하지 않았다.

- 최종 실행/증거: `/workspace/artifacts/v536-verification-managed/runs/3112635420c7419c9748bc26b2b81fa8.{json,zip,manifest.json}`. 증거 ZIP SHA-256 `178be403bda8ee1e56b688540a530f99129a6699694a29457e5777581850938c`. 같은 source/tree의 LF/CRLF와 전체 통과·복원 결과, 로그·스크린샷·프로필·fixture 및 재생성 출력의 파일 해시를 지속 보관했다. 집중 증거 ZIP SHA-256 `577d4abbabe1a2e98e8de6b69bc546084911cbc5383836b3722151e856d41ee8`도 보존했다.
- 신규/재사용: 최종 57단계는 모두 이번 후보에서 실행했으며 과거 통과 결과로 대체하지 않았다. 기존 팝오버/후보·receipt/CAS/검사/보관 기반과 공개 SDK·NuGet 입력만 재사용했다. 집중 검사는 base/각 overlay를 기록한 별도 증거이고 최종 정확한 commit 검증과 구별한다. LF/CRLF 배율은 각각 원래 8개 확인이 통과했지만 과거 일시 실패 원인을 해결했다는 뜻은 아니다.
- 최신 패키지: source `b4a83596710015a524d2fd14079b2123408fc489`, ZIP `293dea989c27da167db833fe88b0aca00d9ef585bf1972e4901d86ea049a2aec`, 51,202,397 bytes, 2,503항목(2,356파일), manifest SHA-256 `f6ac249a66cb73efd8c590448c83fa6719f72a6e420003c0486b8e9ba4b34e55`.
- 롤백 패키지: source `450ce7620282105bb63ece5e3be6ebd6f87c7f01`, ZIP `c2752a8078dbc897e72b9113269968fb25259688ef1eb684aaa3be1b78f45de9`, 51,196,450 bytes, 2,502항목(2,355파일), manifest SHA-256 `184137e0b345359cb8bedd6aac181c1e934d6522a42095cde6aab3e3e2f93ca8`. 두 ZIP은 `/workspace/artifacts/v536-verification-managed/packages/index.json`의 정확한 두 경로로 보관하며 승격 시 전체 파일 SHA·ZIP CRC·모드를 재검증했다. 최신본 복원 UI는 이번 실행이고, 롤백본 UI는 기존 `83e498ee7f7642c9bf3915ebb054ce33` 증거를 유지한 것으로 구분한다. 새 정상본/증거를 지속 보관한 후에만 승인된 관리형 이전 롤백을 교체했다. 다른 과거 자료는 정리하지 않았다.
- 공간: 최종 실행 전 2215.36MiB → 정리/보관 후 2208.14MiB, 순증가 **7.21MiB**. 집중 증거 보관은 별도로 3.30MiB 증가했다. 사전 추가 디스크 예산 144MiB(64MiB 안전 여유 포함), 별도 RAM 파일시스템 예산 3GiB를 유지했다. 검사 worker에서 관측한 cgroup 메모리 최대는 4.04GiB다. 성공·실패 증거를 보존한 뒤 해당 실행이 직접 만든 RAM checkout·캐시·패키지·테스트 복사본만 정리했고 두 실행의 임시 root가 없음을 확인했다. `3~6MiB`를 보장값으로 사용하지 않는다.

후속 게시 기록 commit은 이 결과 문서만 마감한다. 실행 패키지의 출처는 위 테스트 후보이며 비문서 파일이 같은지 게시 전에 비교한다. 빌드 산출물·증거 ZIP·개인 파일은 Git에 넣지 않는다.

기존 배율 메뉴 일시 실패는 이전 `c6cf72b5e98f4e28bb4ee97184714366` 실행에서 cold 메뉴 재진입만 실패했고, 후속 재현·LF/CRLF가 통과한 상태다. 원인은 여전히 미확정이다. 이번 헤더 수명 수정과 같은 원인이라고 추정하지 않으며 기존 배율 검사의 성공 조건은 바꾸지 않는다. [원래 실패·후속 증거](VALIDATION_V666_ACTION_ICONS.md).

I6의 모듈 핀·Set 출력·종류 항목과 ABI closure·고급 타입/핀 표시명·B2/M4/M11/M12·V2–V9는 고정 후속이다. 원본 핸들러가 없거나 숨긴 핀은 새 필수 요구로 추가하지 않는다. 3D/권한 별도 팩·이동과 실행 분리·override 원계약 유지·독립 계약 복제 제외 합의도 유지한다. 실제 Windows/WebView2·물리 모바일·DPI/IME·전체 UI·Space/Library 전달은 미검증이다.
