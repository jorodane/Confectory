# v536 새 정보 함수 카드의 저장 전 glyph 수용

기준은 `d6f0366`과 저장소 `196c605`의 v536 ZIP이다. 원본 `renderObjectFunctions`는
새 자체 함수 카드의 `data-function-icon`에서 `editIconValue`를 열고 `method.icon`을
보관한다. 이번 유한한 수용 흐름은 **정보 → ＋ 기능 → 이름/설명 및 glyph 선택 →
Undo/Redo → 저장 전 cold → 한 후보 Save → Review 취소 → 명시적 Confirm**이다.
기존 저장된 함수 카드의 glyph와 생성 전의 카드/등록 수명은 별개라 이 경로를 명시했다.

## 기존 연결과 검증 경계

`element-functions.js`의 `function-add` 입력과 `InformationDefinitions`의 선택적 icon,
기존 owner 후보·checkpoint·receipt·최종 CAS를 그대로 사용한다. `receiptFieldProof`는
수락된 새 함수의 ID·origin·writable·계약·glyph를 확인하고 늦은 glyph 입력을 같은 ID의
`function-edit`로 연결한다. 새 함수나 ID를 다시 생성하는 방식이 아니다. 제품 코드를
중복 구현하거나 backend·레이아웃·권한·공개 계약·오버라이드 의미를 변경하지 않는다.

원본 대조에서 Blueprint 그래프의 함수 카드 마크업 재사용만으로 독립 노드 glyph 편집을
새 필수 요구로 만들지 않았다. 연결된 정보의 하위 값은 정상 읽기 전용이며, 원본 CSS가
숨긴 root/mobile 입력 아이콘도 새 요구가 아니다. 자체 중첩 정의/원래 노출되는 별도
조작은 구체적 원본 근거로 따로 다룬다.

이번 검사는 생성 전 glyph의 취소·Escape·부적합 입력·Undo/Redo와 이름 재편집,
설명·cold를 확인한다. 생성 ID는 기존 UUID 규칙으로 한 번만 발급되며 저장 실패·충돌·
응답 유실·재시작에도 바꾸지 않는다. 정보·등록·새 함수 text는 같은 후보/CAS의 전체
성공 또는 미적용이고, Confirm 전에는 원본·함수 파일이 생기거나 변경되지 않는다.
정확한 `9223372036854775805` 기본값과 기존 typed caller/C#·부모·다른 자료를 보존한다.

생성 응답 대기의 늦은 glyph는 수락된 glyph/함수 hash에 결합해 별도 입력으로 보존하고
cold 뒤 새 명시적 Save만 반영한다. 응답과 조회가 모두 유실되면 먼저 기존 receipt를
조회해 중복 Apply/등록/파일 생성을 막는다. 생성 취소는 원래 초안과 원본을 보존한다.
기본 창·독립 정보 창과 다른 창의 exact64 입력을 분리하며, 다른 창에 미적용 입력이
있으면 Review를 거절하고 그 창의 명시적 취소 뒤에만 Confirm한다.

receipt 단위 검사는 새 `function-add`를 `function-edit`로 재결합할 때 생성 ID와 typed
계약을 유지하며, 다른 owner/ID·읽기 전용·다른 accepted glyph·이름/설명/계약·함수 hash나
owner hash 변경을 거절하는지 확인한다. 기존 저장된 카드·상속 기능 헤더·생산 final CAS는
영향 회귀로 둔다. 최초 검사 도우미의 `zipfile` import 누락은 수정하고 실패 증거를 보존했다.
이를 제품 결함이나 통과로 계산하지 않는다.

## 공간과 남은 범위

사전 기준 200MiB+안전64MiB를 그대로 충족한 뒤 시작했다. 이전 두 폴더의 삭제 승인은
소진됐으며 이번 단위는 기존 자료를 추가 삭제하지 않는다. 검사 자체의 신규 fixture/
패키지만 증거를 보관한 뒤 승인된 수명관리로 정리한다. 원본·보관 빌드·SDK·로그·프로필·
Git·사용자 데이터는 보존한다. 격리 fixture만 사용하며 사용자 프로젝트 실행·AI/유료 호출·
개인 파일/외부 이미지 업로드는 하지 않는다.

I6 자체 중첩 정의·원본에서 실제 편집 가능한 다른 아이콘·로컬 이미지 프로젝트 자산은
남는다. forwarded 부모/opaque/import 영향 결합·고정8/9행·B2·M4/M11/M12도 별도 잔여다.
전체 UI·실제 Windows apphost/WebView2·모바일 기기·Library 전달은 미완료다.

집중 7흐름 39확인, receipt 단위 7확인과 기존 Native/저장 함수 카드/상속 헤더/final CAS 영향 회귀 24확인이 통과했다. 원래 팝오버 10영역과 75개 리소스 바이트/SHA가 일치한다. 이번 변경은 검사와 수용 문서뿐이며 제품 코드·레이아웃·권한은 변경하지 않았다.

## 독립 checkout·새 교차 패키지 확정

검증 소스 `220c2de3cd2f23c8b10a919774372794bcde95df`의 변경은 tests/docs뿐이고 기존 제품 소스·리소스는 이전 게시본과 동일하다. 기존 독립 checkout을 정상 FF해 Git blob·autocrlf·clean을 확인하고 Native/CLI Release·현재 Linux 엔진을 생성했다. 새 함수 glyph의 늦은 입력 6확인, 독립 창/peer 8확인, 생산 final CAS 4확인 및 receipt 단위 7확인이 통과했다.

새 RAM Windows x64 교차 패키지는 restore·Release·MCP·생성·probe·실제 패키지 엔진/렌더러의 새 함수 glyph 생성 6확인까지 6단계를 통과했다. 전체 2351개(선언 manifest 2350개)의 목록·SHA와 Core/Native DLL·제품 소스 바이트를 대조했다. manifest SHA `185595b3e947d9a54200eaad8c3c22d8e886320eb7691809c44b72ce42d7e699`. 전체 manifest·fixture/로그/프로필 증거 보관 뒤 이번 생성 RAM 사본만 정리했다. 보관 빌드·SDK·원본·사용자 자료를 추가 삭제하지 않았다.

최종 후속 커밋은 문서/evidence만 달라 위 검증 소스와 제품 실행 코드는 같다. 실제 Windows apphost/WebView2·실제 모바일 기기·Library 전달과 전체 UI는 계속 미완료다.
