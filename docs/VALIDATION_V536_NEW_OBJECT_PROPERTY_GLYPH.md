# v536 새 객체 속성의 첫 저장 전 아이콘

기준은 게시 `11b59ee`와 저장소 `196c605`의 v536 ZIP이다. 원본의 추가된 객체
속성도 기존 `data-property-icon`과 `editIconValue(..., true)`를 사용한다. 이번 최소
흐름은 **객체의 속성 추가 → 이름/타입/정확한 값·기호 또는 해제 → 첫 Save →
재시작·Review/Confirm**이다. 기존 기본/독립 창·팝오버·레이아웃을 사용한다.

## 생성 후보와 입력 보존

기호는 기존 definition 초안의 선택적 `icon`으로 보관한다. 이름·값·타입 편집이
선택한 기호를 덮어쓰지 않는다. 기존 primitive/typed/information 생성 후보에 선언된
아이콘 metadata만 함께 전달하고, 새 소유 속성 스키마·객체 값·등록을 기존 한 후보와
최종 CAS로 저장한다. 잘못된 마지막 기호/정확한 숫자나 소유·원문 경합은 전체 미적용이다.

새 schema ID는 기존 `owner_Properties_<hash>` 생성식을 그대로 사용한다. 아이콘을
선택하지 않은 기존 요청은 그대로이며, 새 핀 ID·공개 오버라이드 계약 변경·독립 계약
복제는 없다. 첫 Save는 기존 초안/등록 후보만 보관하고 실제 원본 파일은 Confirm까지
생성하지 않는다. 명시 해제는 속성/값/등록을 없애지 않고 그 기호 metadata만 제거한다.

성공 응답을 기다리는 동안 기호만 바뀌면, 원래 요청의 이름·타입·값·수락 기호와
실제 생성 결과의 owner source hash·소유 필드·생성 schema ID/해시를 확인한다.
그 뒤 해당 schema의 후속 `schema-icon` 입력으로 옮겨 재시작 후 새 명시 저장만
허용한다. 원래 속성을 다시 생성하거나 다른 입력을 덮어쓰지 않는다. 이름/값/타입이
다르거나 결과를 증명하지 못하면 초안을 보존하고 자동 재기준화하지 않는다.
응답 유실은 기존 receipt 조회로 확인하며 적용 여부를 추정하거나 중복 생성하지 않는다.

실제 후보 검사에서 정보 선택기가 이미 정의된 `editorIcon`·`editorFieldIcon_`를
알 수 없는 metadata로 판단해 선택을 막던 연결 결함을 확인했다. 두 선언된 표시 키만
기존 Presentation 분류에 포함했다. 임의 사용자 metadata는 계속 선택 차단·원문 보존하며,
새 기본값·참조·실행 의미를 만들지 않는다.

## 검증과 정확한 잔여

명령/종료·확인 수·source SHA·원본 handler·공간/메모리·리소스는
`evidence/v536-new-object-property-glyph/focused-verification.json`을 따른다.
실제 UI 표본은 원래 타입 picker를 사용한 새 long 속성의 기본/독립 창이다. 순수 후보는
primitive/typed/information 생성 형태를 검증한다. 가능한 모든 타입 조합을 새 수용
요건으로 늘리거나 미검증 조합을 완료로 주장하지 않는다.

부모·외부 원본·기존 값/참조·설명·기존 생성 규칙·권한과 Review→Confirm을 유지한다.
개인 파일·이미지 자산·유료 AI·외부 업로드는 없다. 격리 fixture의 원문/로그/화면/
프로필은 scratch에 보존하며 Git에 게시하지 않는다. 새 테스트 자체 임시 복사본만
기존 승인된 수명관리로 정리하고 기존 자료·캐시·보관 빌드는 삭제하지 않는다.

I6의 자체 중첩 정의·함수/서명 핀·다른 요소 팝오버·로컬 PNG/JPG/WebP 선택/저장/
복원은 별도 잔여다. 연결 정보 하위 값·부모/외부 정의의 정상 읽기 전용과 구별한다.
forwarded 부모·opaque/import 영향 결합, 8행 여러 함수 문맥, 9행 고급 타입/표시명,
B2 실제 배지, M4 async/M11 C#→graph/M12 Root 실행 분기는 별도로 유지한다.
전체 UI·실제 Windows/WebView2·모바일 기기·Library 전달은 미완료다.

집중 8흐름 85확인, 순수 후보 9확인, 기존 객체/정보 속성·새 정보 속성·객체 요소 glyph·정보 편집·생산 final CAS 영향 회귀 34확인이 통과했다. 원본 팝오버 10영역의 치수/위치/스타일과 74개 리소스의 바이트/해시와 이전/새 생성 receipt 보호 5확인을 확인했다. 스키마 실제 경합·쓰기 실패·취소·Undo·응답 유실 조회·늦은 입력·다른 창 보존·compiler Confirm을 분리 검증했다.

## 독립 checkout·새 교차 패키지 확정 결과

실행 소스 커밋 `82564738115eff1d7d74bfc871bca199041a6a68`의 변경 Git blob·기존 autocrlf·clean을 확인했다. 객체 속성의 기존 생성 ID·타입·값과 부모/외부 원본을 보존했다. 기존 독립 checkout에서 Native/CLI Release·새 Linux 엔진, 새 객체 속성 생성·아이콘·늦은 입력/다른 창 보호의 독립 창 15확인 및 생산 final CAS 4확인이 통과했다. 새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·패키지 자체 속성 아이콘 UI 15확인까지 6단계를 통과했다. 전체 2349개/manifest 2348개 목록·SHA·Core/Native DLL과 변경 제품 소스 바이트를 확인했다.

manifest SHA `317921fc3f06f49e4fd01317a0003efaa54265a710558732f8b0bd9dec1e875c`. 전체 manifest와 fixture/로그/프로필 증거 보관 뒤 이번 실행의 임시 패키지만 정리했고 기존 보관 패키지/SDK/원본/사용자 자료는 삭제하지 않았다. 최종 후속 커밋은 문서/evidence만 달라 실행 코드는 위 소스 커밋과 같다. 실제 Windows apphost/WebView2·모바일 기기/터치·Library 전달 및 전체 UI는 계속 미완료다.
