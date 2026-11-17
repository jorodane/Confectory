# Private 본문과 scalar 반환 변경의 공동 저장

고정 v666 [정보7/8행](V536_I5_6_REMAINING.md)의 기존 private C# 본문·helpers 편집과 다른 직접 소유 native 함수의 scalar 반환 변경을 한 정보 창·한 Save에 결합한다. [기존 native 반환](V666_NATIVE_RETURNS.md)의 상세창 반환 타입 선택·호출 계약 출력 대응·직접 C# 편집을 재사용한다. private 공개/프레임/code ABI와 native 인자명·타입·역할·수·순서, 기존 입력·out ID를 유지한다.

이전 반환과 같은 타입의 기존 out이 있어야 한다. 사용자는 이전 반환 소비자를 그 out에 명시 대응하고 다른 입력·out identity를 유지한다. 새 선언에 맞춘 C# 본문은 직접 작성한다. 반환값·형변환·기본값·소비자·본문·연결을 추측해 만들지 않는다. 각 단독 계획과 전체 assembled C#이 먼저 유효해야 한다.

유한 종료 기준은 계약 불변 private 본문/helpers와 다른 native 함수의 long→double 반환, 실제 기존 long 반환 소비자의 호환 out 대응을 한 후보/CAS에 저장·복원·실행하는 흐름이다. 원래 caller40, 변경 뒤 caller20·실제 IInvoke double 반환25.5·기존 long out25를 확인한다. 모든 원래 입력과 out의 타입/역할, graph 연결/좌표·정확한64비트 local·독립 원문의 bytes/mtime와 최초 source/flow 증거를 보존한다.

역할/반환 변경 행은 하나이고 다른 행은 공개 계약을 유지한다. 직접 소유 구현의 기존 단일 target·source import 없음 경계를 유지한다. void/ref·입출력 추가/삭제·타입/역할 혼합·private ABI·opaque import·외부 쓰기는 별도 범위다. 조합별 새 필수 매트릭스를 만들지 않는다.

이 UI 흐름의 native 원래 인자명은 공개 인자명과 이미 같은 상태다. 기존 scalar 반환 편집기의 다른 native 별칭 표시/선택 정책은 바꾸지 않는다. 결합 검증기는 native 이름 변경을 거절하고 원래 C# 인자명을 유지하는 명시 계획만 수용한다. 다른 별칭의 UI 계약은 별도 잔여이며 암묵적인 이름·본문 변환을 허용한 것으로 해석하지 않는다.

workspace version1·receipt version3의 nativeBodyContexts와 전체 읽기 관측을 재사용한다. 새 schema/receipt/profile·권한·migration은 추가하지 않는다. 후속 설명과 현재 native 반환 서명으로 명시한 본문 Save도 최초 function/source/flow/반환/호출 대응과 읽기 버전을 유지한다. 이미 적용한 caller 대응은 재제출하지 않는다. Review/Confirm과 최종 모든 원본 CAS가 권위다.

기존 편집기의 취소·Undo/Redo·cold·쓰기 실패/재시도·응답 유실·늦은 입력·창/프로젝트 경계·후속 Save·Review 취소/Confirm·원본 경합, LF/CRLF·새 package·전체 ZIP 복원을 검사한다. 기존 private out→값/값→out·struct·whole/retained·일반 native 반환·등록 helper 회귀를 구분한다. 직전 온전한 package의 새 pending 거절과 Confirm된 source의 구 compiler 실행도 별도 측정한다.

정보별 C# struct·종류 enum·모듈 interface와 명시 async 전환 전 sync caller 오류 정책을 유지한다. 구 Reference reader 제약·일반 migration/downgrade, 실제 Windows/WebView2·물리 기기·IME/GPU/audio·전체 UI는 이번 완료 주장에 포함하지 않는다. 과거 초기 빈 화면 원인은 미확정이다. 원본·권한·latest/rollback·증거·main을 보호한다.

이 유한 흐름은 [최종 신규44·재사용0 검증](VALIDATION_V666_PRIVATE_SCALAR_RETURN.md)을 마쳤다.
