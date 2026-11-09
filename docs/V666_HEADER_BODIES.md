# 정보 헤더 표시와 여러 C# 본문의 한 저장

고정 [정보 편집 8행](V536_I5_6_REMAINING.md)의 한 정보 창·한 Save 흐름에서,
정보 자체 설명·아이콘을 계약이 그대로인 직접 소유 C# 본문들과 함께 저장한다.
원본 기준은 v666 ZIP의 `app.js` 안 `renderFeatureDefinition`,
`openOwnFunctionPopover`, `renderFunctionSignatureEditor`와 기존 정보 헤더다.
실제 UI의 `elements.js`는 헤더와 함수 입력을 같은 `captureMixedCell` 후보로 모은다.
새 조합별 필수 목록이나 새로운 화면을 만들지 않는다.

게시 d78b5817에서 두 본문·설명·아이콘 각각과 본문-only 그룹은 유효했고 원래
프로그램은46을 실행했다. 원본 460px 창에서 네 입력을 함께 Save하면
`Save up to eight direct function contracts together; other input is retained`로
거절됐다. 입력과 원래 checkpoint는 보존됐으나 정상 단일 저장 경로가 없었다.

이번 지원은 직접 소유 단일 native target 함수 2–8개의 같은 계약 본문 편집에
소유 정보 설명과 아이콘을 각각 최대 하나 함께 넣는 경계다. 표시 행의 exact-key,
중복·설명 길이·기호/로컬 이미지 검증은 기존 `InformationDefinitions`가 수행한다.
표시 행은 새로운 caller closure나 권한을 만들지 않는다. 타입/핀/순서/역할 변경,
함수 생성·속성 구조·부모/외부 쓰기와 임의 whole/wrapper 계획은 이 결합에 포함하지 않는다.

본문 선택 판정을 순수 후보·읽기 guard·cold Review의 알려진 소유 헤더 읽기에
공유한다. 원래 version3 receipt의 관측 hash를 재기준화하지 않으며 Save의 한 CAS,
공동 Undo, 명시 Review→Confirm과 최종 source lease를 그대로 사용한다.
callee의 기존 로컬 import와 그대로인 native/Blueprint caller를 보존한다.
구 leaf/Blueprint 그룹의 빈 readGuards 호환은 유지하고 새 문법/ABI/마이그레이션은 없다.

같은 흐름의 재저장에서는 별도 실제 결함도 재현했다. 저장 중 입력한 새 설명은
cold 뒤 보존됐으나, 설명만 다시 Save하면 이전63개 readGuards가 빈 목록으로 교체됐다.
해당 후보는 Confirm하지 않았다. 이제 이미 저장한 owner·manifest·2–8개 함수와
단일 native body의 정확한 공동 source footprint가 유지된 설명/아이콘 후속 Save는
기존 읽기 해시를 이어받는다. 기존 Guard는 경로를 검증하고 읽기 해시를 기록하는
역할이므로, 상속한 해시는 checkpoint CAS 직전에 별도로 실제 Snapshot과 비교한다.
이 시점의 링크·2MiB 읽기 예산·원래 hash가 다르면 전체 후보를 거절한다.
metadata-only receipt도 같은 원래 그룹·계약·본문 소유권을 확인해 cold Review와
최종 CAS에 연결한다. 새 원본 hash나 편집 계획을 추정해 재기준화하지 않는다.
모든 구 reader의 checkpoint 교환을 실행한 것으로 보지는 않는다.

원래 C# caller의 CRLF·Unicode·별칭·파일 metadata와 공개/override 계약·정보의
정확64 기본값·ID/연결/권한·레이아웃을 유지한다. 명시 편집한 두 callee 본문과
소유 헤더 표시만 바뀐다. 고정7/8/9행의 다른 실제 closure·타입/표시명, 신원/권한
backend 및 종류 CLR/사용 중 삭제 정책은 기존 잔여다. M11/M12/M4는 다시 열지 않는다.
초기 빈 화면 원인은 미확정이다. Linux 엔진/Chromium과 교차 Windows 패키지는 실제
Windows/WebView2·모바일·물리 IME·전체 UI·사용자 프로젝트·Space/Library 검증과 구분한다.

확정 검증·보관 결과는 최종 validation 기록에서 마감한다.
