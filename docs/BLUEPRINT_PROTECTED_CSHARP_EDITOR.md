# 보호된 전체 함수 보기와 기존 C# 본문 편집

이 단위는 v480의 고정된 외곽 선언과 편집 가능한 본문 구분을 기존 C# 원본 편집에 연결한다. 저장 형식·compiler profile·실행·ABI는 바꾸지 않는다. 기존 본문 편집을 유지하면서 ‘보호된 전체 함수’에서 현재 signature와 괄호를 함께 보여 주고 본문 영역만 수정한다. 일반 독립 노드는 `Execute`, 기존 전체 본문 문맥 노드는 `Invoke`를 표시한다. 이 표시는 컴파일 입력을 대체하는 새 C# 파일이 아니다.

본문 내부의 C# 로컬 보조 함수는 기존 compiler에서 실행된다. ‘로컬 보조 함수 위치’는 같은 본문 끝으로 커서를 옮긴다. 노드 밖 helper class/member, enum 또는 매개변수 편집을 지원한 것으로 표시하지 않는다.

## 보존·편집·검토

선언·매개변수·바깥 괄호는 편집 범위에서 제외한다. `beforeinput`의 입력/삭제/잘라내기 경계 검사와 `input` 이후 외곽 일치 검사를 함께 사용한다. 영역을 넘는 붙여넣기·DOM 입력도 원래 외곽을 유지한다. Tab, Undo/Redo, 조합 입력의 한 편집 단계, Ctrl+S의 기존 공유 초안 Apply를 연결한다. Undo 이력은 이 창의 private 입력이며 저장·권한 증거로 복원하지 않는다.

저장하는 것은 기존 `schema:1` node record의 `source` 문자열과 현재 definition receipt다. 표시용 외곽 선언, helpers 필드, enum 또는 새 권한을 저장하지 않는다. 기존 C# 전체 본문 문맥의 CRLF 보존 경로도 유지한다. 입력 취소·본문/전체 보기 전환은 같은 private 본문을 다룬다. 뷰 선택은 private 창 metadata에만 보관한다.

읽기·보기 전환은 원본과 공유 초안을 바꾸지 않는다. Apply는 기존 graph/leaf/관련 선언 CAS를 따른다. cold 복원은 본문 입력과 보기를 유지하되 server basis를 복원하지 않으며, 현재 읽기·명시적 기준 재검토가 필요하다. Save/Review/Confirm과 실제 compiler 검증 경계는 유지한다. UI의 외곽 보호만으로 유효한 C#을 보장하지 않는다. compiler의 전체 본문 구문 검사·예약 이름·원본 매핑 지시문 거부가 최종 경계다.

## 레퍼런스에서 확인한 범위와 enum 미결 사항

[보존 ZIP](../reference/site-ui/Confectory-Editor-Prototype-v480.zip)의 SHA-256은 `0489844c8c6d90f7cdc8ea0e80628f487dcfb27f2c871b19367a635212d3c5bd`다. 실제 `blueprintCSharpContract/Sections/ParseCSharpRegions` 등 선택 함수를 [재실행 probe](../tests/probes/v480_csharp_regions.py)로 검사한다. 명시된 signature field/직렬화/ID 생성 callback만 fixture다. 실제 prototype 전체 브라우저·C# compiler·graph runtime을 실행한 증거로 사용하지 않는다.

확인한 내용은 다음과 같다.

- enum 항목은 실행 포트의 안정적인 ID·서로 다른 int32 값을 가진다. 시각적 순서는 ID·값을 바꾸지 않는다.
- prototype의 C# 반환 `Result`는 실행 출력이다. 데이터 출력은 `out` 매개변수다. enum 이름/값과 매개변수 영역을 수정하면 pin 계약을 다시 만든다.
- 외곽 class/Execute/괄호는 고정되고 enum·매개변수·본문·Execute 밖 helpers 영역이 별도로 저장된다.
- 중복 enum 이름·값, int32 범위 초과와 기본 진행 포트 제거를 거부한다. 이 int32 **항목 값 범위**는 정수 계산식의 overflow 정책과 별개다.
- 그 편집창은 C# compiler가 아직 연결되지 않았다고 명시한다. 선택 함수는 C#에서 `(Result)123` 같은 미정의 값을 반환했을 때의 runtime 규칙을 정하지 않는다.

현재 제품의 node `return`은 typed 데이터 결과이고 실행 제어는 next/bool이다. 기존 return을 몰래 enum 실행 결과로 바꾸면 기존 호출·값 연결이 달라진다. 따라서 enum 실행은 기존 노드를 유지하는 별도 명시적 계약이 필요하다. 레퍼런스대로 신규 enum 노드의 실행 반환과 데이터 `out`을 분리할 수 있지만, 아래 의미는 현재 정하지 않는다.

| 결정할 지점 | 최소 선택지 | 영향 |
|---|---|---|
| 선언한 enum 포트에 없는 runtime 값 | 실행 오류로 중단 / 연결 없는 실행 줄처럼 종료 | 오류·종료와 out 기본값·부작용 관찰이 달라짐 |
| Execute 밖 helpers의 허용 범위 | 상태 없는 static 보조 메서드만 / field·initializer 등 class member까지 | 후자는 상태 수명·공유·probe 무실행 경계까지 정해야 함 |

매개변수 영역 편집도 현재 CELEM 타입·ref/out·호출자 저장소와 명시적 typed 계약 갱신을 따라야 한다. prototype의 이름/값/위치 매칭을 기존 이름 기반 binding에 무조건 적용하지 않는다. 현재 전체 함수 보기에서 매개변수는 보호된 현재 계약이다.

정수 계산식의 overflow 오류 대 wrap 결정은 별도로 답변 대기다. 이 단위에서 수학 표현식·enum runtime·외부 helpers 수명 규칙을 선택하거나 C# 사용자 연산을 다시 쓰지 않는다.

## 실제 증거

선택한 레퍼런스 편집 함수의 14개 검사는 enum ID/값, 순서, 영역 저장과 거부 경계를 확인한다. 제품의 실제 CLR 검사 2건은 같은 이름의 로컬 helper가 서로 다른 노드에서 독립적으로 실행되는 것, 독립 probe의 무실행, 외곽 선언 탈출·예약 이름·매핑 지시문 거부 및 이전 성공 산출물 보존을 확인한다. synthetic composition 이벤트는 DOM 경계 검사이며 실제 OS IME 설치·native 동작 검증으로 표시하지 않는다.

최종 소스 hash·단계별 실패와 수정·실제 Chromium 편집/복원/Confirm·리소스 검증은 [증거 기록](evidence/v480-csharp-editor/editor.json)에 연결한다. 전체 최신 범위는 [v480 완료·미완료 표](EDITOR_V480_STATUS.md)를 따른다.

최종 고정 소스 13개 파일에서 관련 엔진 **12/0/0, 150.845초**, 실제 Chromium 두 묶음은 **13/0/0 + 12/1/0**(개별 최대 929.492초)였다. 실패는 복원된 C# 창이 테스트의 고정 제목 좌표를 가린 경우로, 실제 복구 버튼과 노출된 제목을 사용하는 테스트만 수정해 **1/0/0, 55.301초**로 재검증했다. 선택한 26개 메서드가 각각 통과했으며 단일 26/0 실행으로 표시하지 않는다. 제품 5개 파일과 기존 고정 12개 파일은 그대로 유지했다. 관리 프로필 컴파일 **1/0/0, 173.851초**로 통과했다. src/packs/targets의 Git tree는 `e50da71`과 동일하며 그 체크포인트의 82건을 새 검사 수에 더하지 않는다. [보호된 본문](evidence/v480-csharp-editor/code-protected.png), [확정 후 복원](evidence/v480-csharp-editor/code-published.png).
