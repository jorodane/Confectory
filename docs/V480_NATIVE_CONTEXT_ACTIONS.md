# Native 선언형 컨텍스트 메뉴

`work/current@4109995` 이후, 선택 객체의 native `Actions` 메뉴를 [기존 선언 발견 및 단일 typed SetValue 경로](EDITOR_CONTEXT_ACTIONS.md)에 연결한다. 기존 native 입력 어댑터에 오른쪽 버튼 이벤트나 OS 팝업 ABI를 추가하지 않는다. 객체를 연 뒤 Workspace의 `Actions`를 선택하면 같은 선언 목록·계약과 가용 사유를 표시한다. 소스와 속성 보기에서 같은 객체를 사용하며 Explorer의 별도 트리 선택을 암묵적으로 실행 대상으로 삼지 않는다.

## 호출·입력·수명

`MainBody`가 기존 `ContextActions` 포트를 import한다. 발견·호출·취소는 기존 HostLoop 소유 작업으로 실행한다. 모델의 session/project/owner, target, 여섯 canonical source hash, 정적 provider·signature, 선택·revision/hash, 입력 한도와 opaque token 규칙은 변경하지 않는다. 현재 함수는 `Confectory.SchemaEditing::SetValue(string text,string field,string value)->string` 하나다. 등록된 다른 함수는 사유와 함께 미지원이며 호출 버튼을 활성화하지 않는다.

메뉴에서 선언을 고른 후 field 식별자와 raw JSON 문자열을 명시적으로 입력하고 `Invoke`를 누른다. 첫 번째 인수는 선택 객체의 현재 공유 초안이다. 반환 source는 선택·복사 가능한 읽기 전용 제안으로 표시하며 Apply/Save/Confirm을 호출하지 않는다. 실패는 기존 성공 결과를 지우고 사유를 표시하며 입력을 보존한다. 동일 token·동일 입력 재호출은 모델의 기존 결과를 사용하고 다른 입력 재사용은 거부한다. 새 입력으로 다시 실행하려면 선언을 다시 읽는다.

source·property·chat과 다른 project/object 소유 텍스트 버퍼를 사용한다. 메뉴 발견·호출은 `WorkspaceAction`의 source 제출이나 `TypedWorkspace`를 거치지 않는다. 미제출 source/property/chat 텍스트·바인딩·원래 revision/CAS 기준을 유지한다. 반환 결과를 읽었다고 원래 편집 버전을 갱신하지 않는다.

`Back`/Escape는 메뉴를 닫고 명시 입력을 해당 live object에 보존한다. `Cancel input / call`은 메뉴 token을 폐기하고 메뉴 입력·결과를 비운다. 실행 중에는 기존 취소 신호를 전달하고 메뉴 generation을 갱신한다. 살아 있는 호출이 끝난 뒤 닫기/입력 취소를 마치므로 세션을 먼저 해제하지 않는다. 늦은 성공과 실패는 폐기된 generation에 표시하지 않는다. 소유 session 종료는 실행 중 작업의 완료를 기다린 후 해제한다. 순수 함수의 이미 끝난 변환을 되감거나 임의 함수를 선점 종료한다고 주장하지 않는다.

선택·프로젝트 변경은 기존 모델의 token 폐기를 사용하므로 A→B→A 복귀도 이전 token을 되살리지 않는다. 메뉴 capability/결과를 디스크나 cold 상태에 저장하지 않는다. 메뉴 텍스트 버퍼는 세션 동안만 유지하며 프로젝트 종료 시 소유 자원과 함께 해제한다.

## 유한한 UI와 남은 범위

기존 shell control 128개 한도를 변경하지 않는다. 별도 기존 view control owner에 `Actions` 버튼 하나를 추가하고, 메뉴는 기존 detail control owner를 재사용한다. 선언은 최대 32개, 한 페이지 4개다. 메타데이터·source/출력·필드/값의 모든 기존 한도는 모델과 같다. 44개 Web 리소스와 canonical UTF-8/LF 규칙을 유지한다.

추가 함수·입출력·provider의 실제 연결은 IMP4에 남는다. 일반 executor, 임의 C#/Blueprint 실행, 새 권한·효과·overflow 의미, 전투 테스트·밸런스 기능은 추가하지 않는다. main·원본 ZIP·Android 설정·CSP·설치/외부 AI/유료 호출은 변경하지 않는다.

## 검증: 12 passed, 0 failed, 0 skipped

최종 제품·fixture source는 `12ff063`이며 제품 연결은 `671e99a`다. 실제 native 메뉴 검사에서 5회 함수 호출을 관측했다. 두 등록 선언이 같은 단일 SetValue 함수로 연결되는 것을 확인하며, 이 횟수를 서로 다른 함수 수로 세지 않는다. stale 계약 fixture는 `SetValue.celem`/`SetValue.csbody`에 소유 주석을 추가해 canonical hash 변화를 만들며 새 signature/ABI의 실행을 뜻하지 않는다.

최종 source와 정확한 메서드·로그·플랫폼별 범위는 [검증 JSON](validation/native-context-actions.json)에 기록한다. Linux GTK/X11 실제 입력 검사는 실행된 함수 호출 횟수·읽기 전용 결과·취소/반복·선택/프로젝트 복귀·stale 계약/본문·경합 revision·미제출 source/chat/property의 바인딩과 기존 CAS·늦은 성공 억제·WM 종료 수명을 확인한다. 테스트의 hold/late/replay/competing writer는 복사한 소유 fixture 모델에만 주입하며 제품에 환경변수나 테스트 분기를 추가하지 않는다.

Windows는 managed native composition compile이며 Windows OS 실행은 아니다. Android는 기존 export/metadata fixture로 새 메뉴의 기기 실행을 주장하지 않는다. Browser WASM/embedded OS 조합의 실제 native 메뉴 실행은 미검증이다. Web Chromium과 일반 Git Windows 줄 끝 checkout/실제 리소스 시작 검사는 관련 회귀로 별도 기록한다.

최종 서로 다른 12개 메서드는 native 메뉴 1개, 기존 native 필드/트리 2개, WebUI/모델/checkout/Windows·Android 관리 대상 9개다. 같은 최종 source/fixture에서 최대 두 gate로 실행했다. 초기 빌드 환경과 native 검사 실패는 검증 JSON의 별도 로그로 남기며 최종 합계에 더하지 않는다. [실제 native 제안 화면](validation/native-context-actions.png)을 보관한다. 작업 소유 Xorg는 검사가 끝난 뒤 종료했다.
