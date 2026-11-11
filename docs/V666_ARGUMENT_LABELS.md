# 정보 함수 입력·out 핀의 표시명

고정 [정보 편집9행](V536_I5_6_REMAINING.md)의 한글·공백 표시명과 native 식별자 분리다.
원본 v666 `dist/app.js::renderFunctionSignatureEditor`와 `openOwnFunctionPopover`는
필드의 ID와 표시 이름을 따로 유지한다. 현재 게시본 d9687304에서는 같은 이름칸이
native 인자 이름을 편집하며 별도 표시명 후보는 거절된다. 이 차이를 실제 UI/API로 확인했다.

직접 소유 정보 함수의 같은 상세창 이름칸에서 우클릭 또는 Shift+F10으로 **표시 이름 편집**을
명시 선택한다. **C# 이름 편집**은 기존 이름·계약 대응 경로 그대로이고, 표시 이름 초기화는
별칭만 제거한다. 카드/창/CSS 배치를 바꾸지 않는다. 공통 standalone 상세창은 opt-in을
받지 않으므로 기존 이름 편집을 유지한다. 메뉴 Escape는 메뉴만 닫고 상세창 입력은 유지한다.

선택적 function value `editorArgumentNames`에 기존 native 이름→표시명의 JSON **문자열**을
보관한다. 기존 value 문법을 사용하며 별도 영구 pin ID, source 치환, native 별칭 자동 생성은
없다. 값/ref/out의 같은 인자는 같은 표시명이고 ref 입력/출력은 동일 metadata를 쓴다.
키는 정확한 현재 인자 이름, 값은 trim한 1–60 UTF-16 문자·control 없음이다. 각 입출력 쪽에서
별칭이 다른 핀 이름과 충돌하면 후보 전체를 거절한다. native 이름과 같은 표시명은 metadata를
생략하며 빈 map은 키를 제거한다. 미설정 구 선언/요청은 그대로, 명시하지 않은 별칭은 보존한다.

실제 ABI 변경은 기존 명시 대응과 C# 본문/호출자 검토를 그대로 요구한다. 이름 대응이 제출되면
그 대응으로 표시명만 옮기고 제거된 인자의 별칭은 제거한다. 단순 표시 편집으로 그 보호를
우회하거나 C#·signature·공개 override 계약·실행 ID·배열/참조 의미·호출 연결을 바꾸지 않는다.
후보 hash·소유 검사·원자 Save/Undo·cold·Review/Confirm·최종 CAS를 재사용하며 접수 후 새 입력을
이전 응답으로 지우지 않는다. 기존 저장 본문/속성의 읽기 영수증을 보존하는 분류에도 표시 키만
추가하고 원래 signature·전체 소유 그룹 검증은 유지한다.

호환성은 실제 직전 게시 authoring 바이너리와 새/구 요청을 구분한다. 문자열 metadata는 구 parser가
읽으며 같은 계약의 구 요청은 보존한다. 구 UI가 표시명을 편집·표시하거나 구 writer의 구조 변경까지
호환된다는 뜻은 아니다. 별칭이 붙은 인자 구조를 바꾸려면 현재 명시 대응 writer를 사용한다.
타입별 참조의 새 `Confectory.Reference.*` 타입/field profile은 별도의 새 reader가 필요하며 이번
표시 metadata 지원으로 과거 reader의 실행 지원을 주장하지 않는다. 자동 migration은 없다.

직접 소유 정보 카드의 이 표시 흐름만 이번 단위다. 다른 module/caller/graph 표시 문맥이나 고정
7/8행의 실제 미완료 source closure를 새 조합별 필수 목록으로 늘리지 않는다. M11/M12/M4는 회귀
없이 다시 열지 않는다. 초기 빈 화면은 원인 미확정이다. 현재 실제 전송 정체 중 reload를 관찰하되
과거 사건과 같은 원인 또는 원인 해결로 간주하지 않는다. 실제 Windows·물리 기기·전체 UI는 별도다.

최종 검사·실패/재사용 구분·패키지/보관은 [검증 기록](VALIDATION_V666_ARGUMENT_LABELS.md)에 남긴다.

이 한정 표시 단위의 [최종 신규 41단계·재사용0 검증과 보관](VALIDATION_V666_ARGUMENT_LABELS.md)을 마쳤다.
