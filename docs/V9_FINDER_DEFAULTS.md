# V9 소유 정보 기본값의 정확한 검색

## 원본과 재현

저장소 v666 ZIP `Confectory-v666/dist/app.js`의 `workspaceSearchText(object)`는 소유
객체 속성의 문자열을 직접 검색한다. 현재 native 정보 기본값은 기존 `typed-json-v1`
계약에 따라 `editorFieldDefault_…` metadata 문자열 안에 JSON으로 보관된다. 이전 게시본은
이 저장 문자열을 그대로 검색해 한글/이모지의 JSON escape를 사용자 텍스트로 복원하지
못했고, 중첩 blob/image 문자열도 내부 저장 표현을 통해 검색했다. 생성 fixture로 두
경로를 이전 엔진에서 재현했다.

## 이번 범위

- 기존 `finderContent`에서 직접 소유 schema의 직접 선언 필드에 속한, 기존 profile로
  표시된 기본값만 검색 전용 `기본값 · 필드명`과 원래 JSON lexeme으로 투영한다. 현재
  working-copy source를 사용하며 기존 owner/revision/hash 전후 검사를 유지한다.
- 기존 JSON token 읽기를 재사용해 Unicode를 복원하고 큰 정수를 Number로 반올림하지
  않는다. scalar·배열·복합 값에 같은 규칙을 쓰고 중첩 image/blob/dataUrl payload는
  색인에서 제외한다. 원문 metadata의 이중 포장이나 내부 profile/key는 검색하지 않는다.
- profile 없음/알 수 없음, 직접 선언과 대응하지 않는 record, 잘못된 JSON과 읽기 예산
  초과는 그 record를 제외하고 부분 상태를 표시한다. 안전한 설명/정의와 정상 record는
  유지한다. 잘못된 저장 문자열을 fallback으로 검색하지 않는다. JSON 구조 확인은 저장/
  실행 타입 검증을 대신하지 않으며 기존 Save/Confirm 검증을 약화하지 않는다.
- 한 schema 요청의 기본값은 64개/합계 64KiB UTF-8 안에서 투영하며 기존 JSON 깊이 64를
  적용한다. 이는 현재 읽기 구현의 안전 경계다. 모든 일반 내용의 기존 20,000자 색인에서
  잘린 결과도 이제 부분 상태로 표시한다. 전체 확인/일치 없음으로 오해시키지 않는다.
- 결과는 기존 소유 정보 정의 창을 연다. 필터 밖 실제 draft 변경·Undo와 cold/home/동일
  namespace·ID의 다른 프로젝트에서도 기존 색인 수명을 따른다. 검색어/결과는 저장하지 않는다.

일반 `browserElements`/편집 표현과 API, 모든 공개 계약/.celem/Core/targets, 원본 C#·ID·
연결·부모/외부 원본·권한·Review→Confirm·원자 저장/최종 CAS/Undo, 기존 레이아웃과 Run은
그대로다. 새 파일·상속/등록 외부 source·컴파일러를 검색을 위해 읽지 않는다. 실제 소유
schema의 이미 관측한 metadata만 해석한다. [정확한 delta](v666-finder-defaults-delta.json)를 따른다.

## 고정 검색 잔여의 정정

같은 ZIP의 `blueprint.js`는 그래프를 `object.functionDefinition.blueprint` 또는 method의
`blueprint`에 저장한다. 원본 검색 helper를 그대로 실행한 검사에서 그 안의 `nodes[].text`
및 더 깊은 코드 본문은 깊이 4 밖이어서 원래 배치하지 않은 객체 검색 대상이 아니다.
깊은 graph 전체 탐색을 새 필수 기능으로 늘리지 않는다. 앞선 문서의 graph 등 다른 본문
후보는 실제 저장 위치/원본 깊이 대조가 필요한 후보였으며 모든 조합의 필수 잔여가 아니다.
배치된 실제 글자의 기존 찾기와 직접 소유 C# target 검색은 보존한다. 전환 시 보존 원문 등
다른 얕은 실제 텍스트의 누락은 구체적 원본 근거/재현이 있을 때만 별도 판단한다.

참가자/Helper·연락처/대화는 V4/V5 실제 신원/가시성, office 검색은 V3 표시 팩이 선행한다.
V6/V7 자산과 V8 내장 surface/audio provider는 기존 고정 잔여다. 현재 DISPLAY/Xvfb·오디오
장치와 내장 provider 계약이 없어 모의 화면/소리를 실제 backend 성공으로 채우지 않는다.
3D/권한 별도 팩·이동 연출과 실행 분리·명시 async caller 규칙을 유지한다. 종류 C# 표현/
사용중 삭제 대응, V1/V2 후속과 실제 Windows/WebView2·모바일·DPI/IME·전체 UI·Library/
Space 검증도 별도다. M11/M12/M4는 구체적 회귀 없이 재개하지 않는다.

최종 독립 LF/CRLF·새 패키지/전체 복원·실패 수명관리 결과는 검증 마감 기록에서 확정한다.
