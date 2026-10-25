# v536 여러 함수의 입력 타입 변경과 기존 out 보존 — 2026-10-25

같은 정보 창에서 여러 함수의 값 입력 타입만 바꾸고 임시 저장을 한 번 누르는
기존 조작이다. 기존 Batch는 유지되는 out이 있으면 out 이름 전용 경로로 분류해
유효한 입력 편집까지 거절했다. 격리 fixture에서 각 단일 closure의 성공과 그룹
거절을 수정 전에 재현했다. UI/레이아웃·함수 ID·C# 원문·권한은 변경하지 않는다.

## 종료 조건

직접 소유 함수 2~8개의 같은 이름·위치·수·역할을 유지한 scalar 값 입력 타입
변경을 함께 저장한다. 기존 out과 반환 계약 및 모든 출력 연결은 고정한다.
code/export leaf callee·call/export 직렬 caller와 이미 지원한 고정 로컬 import
범위다. bool/int/long/float/double/string의 기존 exact 타입 검사와 원래 매핑을
사용한다. 핀 수/ref/순서, 출력/반환 변경, C#/중첩/copy 결합을 추가하지 않는다.

입력 변경과 유지되는 out이 함께 있으면 기존 함수별 명시 입력 closure 검증을
사용한다. 모든 callee 사용처와 caller 값/해제 증거를 원래 스냅샷에서 먼저
검증한 뒤 내부 overlay에만 합친다. 출력이 바뀌지 않았으므로 writer/출력 대응
선택을 새로 허용하지 않는다. 원래 물리 파일 관측·최종 hash·단일 checkpoint CAS,
receipt 및 명시적 Review/Confirm을 그대로 사용한다. 중간 후보는 저장하지 않는다.

변경 입력의 본문 사용처가 0개인 경우 원본 UI는 `implementations`를 생략한다.
이 경우도 두 단일 후보 성공/그룹 거절을 재현했다. 기존 `Prepare`가 실제 graph
사용처와 전체 타입/본문을 검사하도록 유지하며, 생략한 선택 계획은 사용처가
없을 때만 성공한다. 사용처가 남아 있는데 계획을 빠뜨린 기존 음성 검사는 계속
전체 거절되어야 한다. 임의의 대체나 빈 값 채우기는 하지 않는다.

## 격리 데이터와 검사

A.count(long)→B.amount(long), B.count(long)→Caller 반환의 원래 연결이다.
두 amount만 string으로 바꾸고 caller의 한글/emoji literal과 원래 연결 해제를
명시한다. callee C# 노드의 long amount 사용처에는 정확한
`9223372036854775800`을 명시한다. 기존 code 매개변수와 C# source, count writer,
공개 count 이름/long 타입, 최종 B.count 소비, 실행 순서와 intent는 그대로다.
Power `9223372036854775806`도 보존한다. 입력 문자열의 의미를 임의 변환하지 않는다.
`unused` fixture는 A의 기존 code 바인딩부터 명시 long literal인 격리 원본을
사용해 amount 사용처가 0개인 실제 UI/API 경계도 검사한다. 기존 사용처가 있는
B의 계획은 여전히 필수다. 두 종류 모두 원래 writer·C# source를 보존한다.

`tests/web/v536_information_shared_inputs_with_out_{fixture,native}.py`를 사용한다.
기존 API/UI harness에서 `CONFECTORY_SHARED_INPUTS_WITH_OUT=1`을 지정한다. 기존
혼합 scalar/all-both/return/local-import 선택은 해당 설정이 없으면 그대로다.
원래 상세 타입 선택기와 입력 연결 갱신창을 재사용한다. 실제 기본/독립 창의
편집·취소·Undo/Redo·불완전 대응 거절 후 Undo 재시도·저장 실패·경합·응답 유실
조회·프로젝트 전환·미저장/저장 재시작·Review 취소/Confirm을 검증한다. 순수 후보는
역순·원래 hash, 잘못된 사용처/해제/타입·추가 출력 계획·역할/수/순서/반환 변경과
실제 source 경합의 전체 미적용을 확인한다.

분류 수정 후 기본 전체 수용 11흐름/27확인이 통과했다. 미사용 입력 보완 뒤에는
최종 코드에서 일반/미사용 순수 후보·실제 API·화면 6흐름/18확인, 관련 기존
공유 계약 4흐름/17확인, 이전 혼합 화면 2확인을 다시 통과했다. 실제 사용처의
누락/잘못된 계획은 그대로 거절된다. 두 원인과 검증 순서를 [집중 증거](evidence/v536-information-shared-inputs-with-out/focused-verification.json)에 기록한다.
원래 460px 화면과 UI 리소스 74개는 이전 게시본 그대로다. Native Release는
warning/error 0이다. clean checkout/새 교차 패키지 결과는 완료 후 기록한다.

## 고정 잔여

8행 전체 완료가 아니다. 더 넓은 입력/out/반환/정의 변경 결합, 값 핀 수/ref/역할/
순서, 수동 C#/혼합 native target·nested/private/whole/postCall, copy/상속/등록/
owner 속성 혼합과 scalar 밖 선택 타입은 별도다. 기존 고정 8행 범위 밖 조합은
추가하지 않는다. 7행의 새 독립 copy 계약/ID/기능/호출 재지정 정책은 답변 대기이며
그 의미를 사용하지 않는다. 9행 named 정보/참조/외부 함수 타입 및 표시명/native ID
분리, I6/B2·A4~A6·M4/M11/M12와 Helper 실제 편집 도구는 별도 후속이다.
전체 UI·실제 Windows/WebView2·모바일 기기 실행·Library 전달 완료가 아니다.
사용자 프로젝트·실제 계정·유료 추론은 사용하지 않는다.
