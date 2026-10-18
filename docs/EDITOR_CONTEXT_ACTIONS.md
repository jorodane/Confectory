# 선언형 컨텍스트 메뉴: 최소 관통 구현

기준은 `work/current@b3d78e2` 이후다. 사용자가 정정한 전투 테스트·밸런스 검토는 메뉴 확장의 예시이며 필수 도메인 기능이 아니다. 앞선 객체별 전투 테스트/입력 매핑 질문도 해소됐다. 이 문서는 **선언된 에디터 기능의 목록→선택 객체와 명시 입력→실제 함수 호출→반환값/실패**를 기존 함수 한 개로 연결한 범위를 기록한다.

## 선언과 실제 호출

팩/프로젝트의 object 선언에 기존 primitive metadata `value editorContextMenu = true;`, 표시 이름 `editorName`, 기존 typed `provide` 관계를 사용한다. 새 언어 문법이나 소스 실행 ABI는 추가하지 않는다. 현재 프로젝트와 명시적 직접 의존 팩의 확정 선언만 발견한다. 등록만 된 항목과 에디터에 호출 경로가 연결된 항목을 구별하며, 예시 항목은 `예시 · … · 미지원`으로 표시한다.

현재 호스트는 `Confectory.SchemaEditing::SetValue (string text,string field,string value) -> string`와 그 기존 `SetValueBody`/`CallBody`만 명시적으로 연결한다. 선택 객체의 현재 공유 초안을 `text`로, 사용자가 입력한 필드와 JSON 문자열을 나머지 인수로 전달한다. 기존 타입 검증 후 실제 typed import인 `calls.Propose.Invoke(...)`를 호출한다. 반환된 변경안과 함수 예외를 화면에 표시한다. CheckCall 성공, 프로젝트 Run, mock 결과를 함수 호출의 근거로 사용하지 않는다.

`SetValue`의 기존 formatter/오류 의미를 유지한다. 반환 문자열은 적용·저장하지 않는다. 원본과 공유 초안, 미적용 source 입력 DOM 및 원래 CAS는 유지한다. 새 overflow·전투/밸런스 판정·본문/Blueprint 실행 의미를 정하지 않는다. [열 수 있는 소유 예제](../examples/editor-context-actions/README.md)는 standalone 실행 없이 같은 경로를 사용한다.

## 실행 경계와 수명

- 발견은 메타데이터 조회이며 실행하지 않는다. manifest registry만으로 조회 범위를 넓히지 않고 직접 dependency를 확인한다. 변경 중인 manifest·메뉴 초안은 확정 전 호출하지 않는다.
- 함수 ID·정확한 signature·provider binding·등록 target과 알려진 여섯 source 파일의 canonical UTF-8/LF SHA-256을 확인한다. 같은 ID의 교체 구현이나 다른 본문은 호출 불가다. 소비자의 기존 정적 provider 연결을 사용하며 임의 어셈블리·reflection·명령·경로·네트워크·환경변수 호출을 받는 브리지는 없다.
- 등록은 실행 승인이 아니다. 사용자가 명시 입력 후 호출할 때만 한 번 실행한다. opaque token은 현재 EditorHome session/project, 메뉴 당시 선택, 객체 revision/hash, 확정 등록·계약·본문·target에 묶인다. 전역 선택 및 프로젝트 열기/나가기/닫기는 기존 token을 폐기해 A→B→A 복귀도 거부한다.
- 현재 문서의 삭제·외부 변경·symlink·revision 변경, 등록/계약/본문 변경과 다른 target/project/session은 실행 전에 거부한다. 입력 취소는 호출하지 않는다. 동일 token·동일 입력의 반복은 저장한 결과를 반환하고 다시 호출하지 않으며, 다른 입력 재사용은 거부한다.
- 호출 전후 취소 및 문서 상태를 확인한다. 실행 중 transport 취소는 기존 소유 취소 신호를 사용한다. 이미 끝난 순수 문자열 변환을 되감거나 임의 C# 실행을 선점한다고 주장하지 않는다. 모달이 닫히거나 문맥이 바뀌면 늦은 결과를 표시하지 않는다.
- private token/결과는 세션 메모리에만 둔다. 최근 32개 한도로 폐기하며 close/restart로 모두 사라진다. cold에서 실행 권한이나 결과를 복원하지 않는다. 최신 선언은 다시 조회한다.

메뉴 조회는 기존 내장 항목의 동작을 막지 않는다. 닫힌 메뉴나 이전 선택·조회 결과가 늦게 도착해 메뉴를 다시 열지 않는다. 함수 호출 실패 시 명시 입력을 보존하고 기존 성공 결과로 대체하지 않는다.

## 최종 검증: 9 passed, 0 failed, 0 skipped

최종 source/fixture는 `d73f8c20b45a2e754a2918eda4382465c3a0e786`이며 최초 관통 구현은 `af3237d0828fa90d550c061b62e1fe219a722a7b`다. 최대 두 gate로 같은 최종 소스의 서로 다른 9개 메서드를 실행했다. 실제 UI/메뉴/전송/일반 Git checkout 4개와 기존 선언·입력·Workspace·Windows/Android managed 회귀 5개가 통과했다. 이전 단계의 검사 수나 최종 이전 재실행을 합산하지 않는다. 초기 구문·endpoint 연결·fixture 실패 6회는 JSON의 원본 SHA-256과 로그 사본에 별도로 남기고 최종 결과로 대체했다. Git 로그 사본은 후행 공백만 정규화하며 원본 scratch 로그는 유지한다.

## 유한한 범위와 검사

조회 한도는 registry 64개, 직접 범위 object 256개, 메뉴 32개, 관측 파일 512개/합계 4MiB/각 1MiB다. 제목은 160자, 요청은 64KiB, 필드는 128자, JSON 값은 8192자, 선택 source와 반환 문자열은 1MiB다. 기존 WebUI 전체 응답 한도도 유지한다. 리소스는 44개이며 textual resource는 기존 UTF-8/LF pinning을 사용한다.

[검증 JSON](validation/editor-context-actions.json)에 같은 최종 source/fixture의 정확한 메서드와 로그를 기록한다. 실제 Chromium은 프로젝트 및 등록 팩의 발견, 미지원 구분, 명시 입력, 실제 SetValue 반환/실패, 반복·취소·stale·삭제·외부 변경·본문 교체·target·A/B/A·cold token 폐기와 미적용 source DOM/CAS를 검사한다. 별도 JS 검사는 내장 메뉴 동작과 닫힘/선택/조회 경합을 검사한다. [실제 결과 화면](validation/editor-context-actions.png)을 보관한다.

Linux common WebUI의 실제 실행과 Windows/Android managed compile을 구분한다. 이 단계 당시 native 메뉴는 미포함이며 [native 후속 구현](V480_NATIVE_CONTEXT_ACTIONS.md)을 별도로 따른다. 실제 Windows OS/Android 기기, browser WASM target의 새 메뉴 호출은 이번 실행 범위가 아니다. ProjectExecution의 일반 runtime-call 미지원은 그대로다. main·원본 ZIP·Android 설정·CSP·실계정·유료 호출·설치·지속 권한은 변경하지 않는다.

## 남은 최소 범위

이번 구현은 명시적으로 연결한 기존 함수 한 개의 관통 경로다. 다른 함수/입출력·provider를 연결하려면 같은 정적 계약과 효과·소유권·취소/결과 경계를 구체적으로 연결해야 한다. 등록한 모든 프로젝트 C#이나 Blueprint를 자동 실행하는 일반 executor, 새로운 권한 정책, 전투 테스트·밸런스 시스템을 구현했다고 표시하지 않는다.
