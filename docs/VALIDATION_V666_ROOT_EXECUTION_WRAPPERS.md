# M12 명시적 공개 결과 wrapper

원본 v666 ZIP의 `dist/blueprint.js:1503–1519`는 원본 핀·분기·공개 출력을 wrapper 계약에 고정하고, 원본을 한번 호출한 뒤 `OriginalResult`를 자체 `Result`에 명시 대응한다. 원본이 바뀌면 계약 갱신을 요구한다. 이번 흐름은 기존 `IInvoke`·NoBranch adapter를 자동 전환하지 않고 이 공개 결과 연결을 추가한다. 원본 소유권·IO·override·권한·레이아웃·Review→Confirm은 유지한다.

새 공개 결과 wrapper는 기존 `execution-enum` post-call에 명시적인 `originalExecution` receipt를 추가한다. receipt는 실제 함수의 공개 계약과 출력 snapshot을 함께 고정한다. 생성된 별도 `IExecutionInvoke` 캡처를 한번 호출해 ref/out·native 반환과 공개 출력을 보존한 뒤 원래 실행 결과를 자체 C# 분기로 전달한다. 알 수 없는 원본 enum 값을 묵시적 기본값으로 바꾸지 않는다. 기존 receipt가 없는 legacy wrapper는 계속 ordinary `IInvoke`·NoBranch로 실행한다. 새 wrapper의 ID·원래 case 연결과 main continuation을 보존한다.

직접 소유한 동기 caller의 기존 참조 카드에서 원본 버튼·enum/C# 편집기·private 입력·Undo/Redo·Save를 사용한다. 원본 분기 ID/값을 자체 enum 초기값에 유지하고 기존 C# 이름 검증과 32개 예산을 재사용한다. 사용자가 편집 가능한 enum/body/helpers와 고정된 원본 호출/OriginalResult/출력 문맥을 구별한다. 원래 C#·부모/외부 원본을 쓰거나 override의 독립 계약을 만들지 않는다.

새 공개 wrapper의 저장은 기존 단일 후보·전체 소스 proof·checkpoint/CAS·응답 receipt 수명관리에 연결한다. 이를 우회하는 순차 public-wrapper 저장은 거절하며 legacy 경로는 유지한다. 저장·cold 복원·Review 뒤 원본/소유 문맥·scope의 읽기 의존성이 같은 최종 파일 CAS에 참여한다. 새 wrapper 변경의 checkpoint receipt가 누락·변조되면 거절한다. 확정 뒤에는 marker를 퇴역시켜 독립된 후속 편집과 혼동하지 않는다. 기존 wrapper의 다른 편집도 실제 원본 계약·소유 문맥의 최종 읽기 가드를 유지한다.

공개 원본의 분기 계약을 갱신할 때 실제 public-wrapper 전체를 명시 선택해야 한다. 새 original receipt와 원래 함수·target/caller를 하나의 checkpoint/Review/최종 CAS에 결합하며 wrapper 자신의 enum·C#·연결은 자동 변경하지 않는다. 삭제한 원본 멤버를 C#에서 참조하는 등 불완전한 코드는 검토/컴파일에서 고치도록 남기며 임의 fallback이나 소스 재작성을 추가하지 않는다. source/Node ID·공개 IO·native 데이터 반환은 유지한다.

집중 검사는 정수 out 및 기존 비void/ref/out 함수에서 실제 호출 횟수·출력 snapshot·실행 분기와 반환선을 확인한다. 위장/누락 receipt·잘못된 primary·전체 wrapper 선택 누락·checkpoint/Review 뒤 경합·cold와 중복 응답을 구분한다. UI는 원본의 고정/편집 영역·잘못된 enum/취소·Undo/Redo·저장 실패·중단/응답 유실/늦은 입력과 원본 계약의 명시 선택을 확인한다. 최종 동결 LF/CRLF·기존 legacy/compiler 회귀·새 패키지/전체 복원·실패 수명관리 결과는 검증 후 아래에 기록한다.

현재 지원은 직접 소유한 일반 Root caller와 이미 공개된 동기 함수의 기존 데이터 ABI다. wrapper를 독립 계약 복제나 비소유 부모/참조 편집으로 확장하지 않는다. 같은 계약 copy·자식 소유 본문의 정의 전체 갱신과 등록된 외부 import 관측은 [유한한 M12 표](M12_CLOSURE.md)의 남은 두 흐름이다. 가능한 타입/문맥 조합마다 새 필수 작업을 만들지 않는다. M4의 동기 caller 오류 정책과 실제 async 실행은 별도다.

승인된 실행별 임시물 정리와 최신/정상 롤백 보관만 사용한다. UI 이미지는 생성한 테스트 자산/fixture이며 계정·live AI·유료 호출은 없다. 실제 Windows apphost/WebView2·모바일·전체 UI·Space 전달은 교차 패키지 검사와 별개다. 구버전은 새 `originalExecution`/checkpoint receipt를 처리하지 못하므로 새 거래를 구버전에서 이어가는 자동 migration은 제공하지 않는다.
