# V2: 일반 C# 본문 저장 실패 복구

보관한 `reference/site-ui/Confectory-Editor-Prototype-v666.zip`의
`Confectory-v666/dist/blueprint.js` 159·799·959행은 개별 동작의 C# 편집과 명시 저장,
313–317·1267·1291행은 저장/완성 검증과 “주십시오/습니다” 안내에 대응한다.
[정확한 delta](v666-source-recovery-delta.json)는 native 저장 조건을 유지하는 문체 적용
6개/기존 8곳과 원자 저장 진입만 허용한다. 원본과 같은 문장의 복제로 주장하지 않는다.

## 재현한 손실과 이번 경계

게시본 dfdf043의 생성한 직접 소유 ordinary root에서, 일반 next C# 동작의 본문을
명시적으로 편집하고 checkpoint 쓰기를 실패시켰다. 기존 live source 편집 뒤 입력을
제거하는 순서 때문에 재시작하면 이전 C#만 남고 새 본문이 사라졌다. checkpoint와
물리 원본은 그대로였다. 이 재현·원본과 fixture 자료를 보존한다.

직접 소유 root code의 source/intent/기존 인자 후보를 기존 authorBatch의 private 후보,
checkpoint CAS, receipt와 공유 Undo/Redo에 연결한다. 사용자가 명시적으로 입력한 C#만
후보에 넣으며 다른 원문·ID·핀·호출·분기/연결·public/override 계약을 바꾸지 않는다.
Source는 현재 정의 계약으로 기록하고 실제 컴파일/물리 쓰기는 별도 Review/Confirm을
따른다. 문법/컴파일 오류를 정상 실행으로 치환하거나 자동으로 고치지 않는다.

실패 후 새 source/intent는 같은 키·노드·원래 proof에서 이전 시도가 미반영임이 확인된
경우에만 새 명시 Save로 처리한다. checkpoint·전체 source closure·물리 원본이 바뀌거나
결과가 불확실하면 입력과 시도를 유지한다. 응답 유실·늦은 새 본문은 정확한 receipt로
분리한다. 구조/소유권을 바꾸지 않는 경우 기존 제한의 공유 history를 후보에서 기록한다.

속성 읽기/쓰기 노드 또는 보관된 propertyObservations가 있는 그래프는 기존 property
source 경로를 유지한다. 최초 관측 없는 property source 저장 거절·readonly receiver/
객체/스키마/등록 관측·전체 Review/최종 CAS를 일반 code source 진입으로 우회하지 않는다.
부모/참조/외부·private/copy/native whole-body·root 매개변수·route/rename 혼합을 새로
허용하지 않는다. 기존 경로의 지원과 이번 일반 source 흐름을 구분한다.

## 남은 점검과 한계

일반 rename/route/root 핀/export·혼합 함수 signature/description 등 다른 레거시 Save는
여전히 읽기 점검 후보다. 이번에 지원하지 않는 조합을 정상 금지 정책이나 새 필수
요구로 확정하지 않는다. 완료한 M11/M12/M4를 다시 조합별 잔여로 세지 않는다.

[검증 기록](VALIDATION_V666_SOURCE_RECOVERY.md)에 신규/동등 재사용·개발 실패·컴파일
거절·실제 .NET 실행·패키지/전체 복원·임시 수명과 미실행 기기/UI 범위를 구분한다.
V2의 나머지 계약/일반 검토·탐색/시스템 안내, V3–V9와 기존 팩/backend·종류 결정,
실제 Windows/모바일·전체 UI·Space 전달은 별도 고정 잔여다.
