# v480 전환 호환성과 남은 범위 검토

이 문서는 2026-10-16 조사 당시의 기록이다. 2026-10-17 후속 사용자 결정과 실제 구현은 [줄 끝 반환·단일 본문 전환](BLUEPRINT_IMPLICIT_END_AND_BODY_CONVERSION.md)에 기록한다. 아래 답변 대기·전환 미구현 표시는 당시 상태이며 최신 상태를 뜻하지 않는다.

조사 기준은 `work/current`의 `e222acbf269ee201bd3e2a5532518287883439ef`와 사용자가 전달한 main의 `32dd44fbec6e9e39a7e3e68c0ca61d62bb47176f`다. 새 implicit-end profile이나 C# 전환 정책을 선택하지 않았다. 이 검토에서 제품 결함은 새로 재현되지 않았으며, 아래 부적합 사례는 자동 전환을 안전하다고 가정할 수 없는 근거다. 제품 원본은 변경하지 않았다.

## 기존 구현의 호환성

[기존 소스 보존 계약](FEATURE_BLUEPRINT_ARCHITECTURE.md)은 읽기·프로젝트 열기만으로 변환하지 않으며, 기존 C# 파일을 제거하거나 파생 C#으로 덮어쓰지 않는다. [파서](../src/Confectory.Core/Declarations.cs)는 `body`와 `blueprint`를 같은 타깃 맵에 등록한다. [Builder](../src/Confectory.Core/Build.cs)는 선택 타깃을 먼저 찾고 없으면 `common`을 사용한다. 선택하지 않은 graph를 실행하거나 기존 타깃 본문을 자동 전환하지 않는다.

소유 fixture의 실제 compiler/runtime 검사 결과는 다음과 같다. 모두 기존 `sync-acyclic-v1`에서 명시적 반환을 사용한다.

| 검사 | 확인한 결과 |
|---|---|
| 기존 C# 본문의 타깃 선택 | portable `5`, Linux `32` |
| 같은 구현의 `blueprint common`과 `body linux` 공존 | portable `102`, Linux `32`; Linux에서는 common graph를 조립하지 않음 |
| 같은 함수 구현의 상속과 common graph 재정의 | portable `102`, Linux `32`; 상속한 Linux C# 원본 유지 |
| 동일 타깃에 body와 blueprint를 중복 선언 | `DUPLICATE_DECLARATION`으로 거부 |
| 기존 본문의 `calls.Double.Invoke(n)`를 정적 노드에 그대로 복사 | 실제 C# compiler가 `CS8422`로 거부 |
| 명시적 노드 import와 원래 import scope를 수동으로 맞춘 fixture | 원래 결과 `4` 유지 |
| 같은 fixture에서 import scope만 제거 | 다른 provider가 선택되어 `4 → 6`으로 변경 |

기존 본문은 [Generation](../src/Confectory.Core/Generation.cs)의 구현 인스턴스에 있는 `calls`를 사용한다. [Blueprint 조립](../src/Confectory.Core/FeatureBlueprint.cs)은 노드를 정적 독립 함수로 만들고, 선언한 호출 계약만 매개변수로 전달한다. 따라서 원문 복사만으로 문맥이 보존되지 않는다. 이 조사에서 별도 fixture에 적용한 수동 import 수정은 전환 가능성을 시험한 것이며 사용자 프로젝트의 자동 변환 규칙이 아니다. 원래 함수와 C# 두 타깃 본문은 fixture 안에서도 바이트 그대로 유지했다.

## 전환 정책이 필요한 부분

현재 기능 가져오기는 **다른 기존 함수의 참조 노드**를 만드는 지원 경로다. 기존 함수 ID·입출력과 C# 본문을 유지하며, 대상 객체의 새 구현을 만든다. 같은 함수의 부모 제공 재사용도 이미 지원한다. 이 두 경로는 기존 implementation 본문 자체의 이관과 구분한다.

기존 구현 전환을 추가한다면 다음 중 목적을 먼저 정해야 한다.

| 선택 | 범위와 영향 |
|---|---|
| 기존 C# 기능을 유지하고 참조로 재사용 | 현재 지원. 기존 구현을 graph로 옮기지 않음 |
| 선택한 구현·타깃에 새 graph/node를 수동 작성 | 원래 C# 파일은 보존. 새 graph의 의미와 실제 전환할 provide/default·타깃 변경을 별도로 검토해야 함. 빈 graph를 기존 구현과 동등하다고 표시할 수 없음 |
| 기존 본문을 한 코드 노드로 이관 | `calls`·별칭·명시적 scope·타깃별 본문·매개변수와 내부 보조 함수 문맥을 보존하는 변환 정책과 compiler 검증 필요. 단순 문자열 치환이나 일괄 복사를 선택하지 않음 |

현재 신규 기능 생성 API는 미게시·미연결 함수의 첫 graph만 만든다. 기존 게시 기능이나 기존 provide/상속 계약을 그 경로로 전환하지 않는다. 다른 함수 ID의 상속 의미를 추가할 근거도 없다. implementation 타깃 하나의 명시적 변경과 모든 타깃의 일괄 전환을 같은 동작으로 취급하지 않는다.

## v480 요구와 현재 검증 경계

v424/v480 원본 ZIP의 app.js·blueprint.js를 정적으로 비교하고 v480의 관련 함수를 현재 제품·기존 검증 기록과 대조했다. 함수 이름의 추가 개수는 사용자 동작 수나 완료율이 아니다. 포함된 스크립트를 실행하거나 prototype JSON을 제품의 graph 원본으로 가져오지 않았다.

| 영역 | 현재 연결·증거 | 남은 범위 |
|---|---|---|
| 기능 화면·문서 탭·입력/출력·배치 | 기존 소유 graph, private 배치·문서, 현재 계약·원본 CAS·cold 입력 및 명시적 compiler Confirm | prototype header-rail/핀 조작 전체의 동작·픽셀 일치 검증은 아님 |
| 노드 생성·제거·직접 C#·Task | 코드/참조 노드의 독립 원본·필수 그룹·한정 Task와 실제 compiler 증거 | 물리 파일 삭제·새 원본 형식의 자동 이관은 없음 |
| 기능 가져오기·부모 재사용·모듈 | 소유/등록 함수의 참조, 객체별 새 구현, 같은 함수 제공의 부모 fallback·인터페이스·요구 계약 | 외부 ABI는 primitive/배열·단일 반환. prototype의 여러 출력/ref/out를 지원한 것으로 확대하지 않음 |
| C# 편집 영역 | 기존 노드 본문과 함수 내부 보조 함수 | prototype의 enum·매개변수·본문·외부 helpers 영역 및 임의 실행 출력의 실제 타입/저장 계약 필요 |
| 내부 다이브 | 독립 코드 노드의 C# 편집과 참조 함수 원본 탐색 | `openInternal`의 중첩 graph 원본·소유 ID·버전 계약은 미연결 |
| 로컬 값·상수·프로퍼티·표현식·값 설정 | 기존 profile의 입력/앞선 노드 값/상수 binding | prototype의 localVariables·set·property·expression 수명과 타입·값 가용성 계약은 미연결 |
| 종료·분기 | 기존 profile의 명시적 반환·bool 분기·가용성 검사 | 연결되지 않은 포트에서의 새 종료 의미, 임의 다중 실행 출력은 미연결. 미설정 반환 처리 질문은 답변 대기 |
| 확대·맞춤 | 기존 private 확대·맞춤과 원본 불변성 검사 | v480의 3.125–300% 자유 확대·단계 휠·포인터 기준 camera 동작과 차이. 실행 profile 결정 없이 진행 가능한 presentation 후속 |
| Workspace·메모·제목·검색·문서·탭 | 각 기능의 실제 UI/cold 검증 기록 존재 | 전체 v424 서비스·실행 제어 완료를 뜻하지 않음. prototype 포털 전송은 창만 지원 |
| 실행 환경 | Linux/.NET 10의 실제 owned fixture 실행, 기존 Chromium UI 및 Windows/Android 관리 대상 컴파일 증거 | native/device·실제 계정·유료 모델·사용자 PC 설치 검증은 없음 |

주요 prototype 근거는 `functionBlueprintCallingFeature`, `moduleFeatureCompatibility/openModuleFunctionImport`, `renderFunctionBlueprint`의 기존 prototype graph 정리, `blueprintCSharpContract/blueprintParseCSharpRegions`, `openInternal`, `blueprintExecutionPlan`, `createSteppedZoomWheel`다. prototype의 graph 정리는 기존 prototype 데이터의 이전 형식 처리이며 실제 CELEM C# 본문의 이관 구현이 아니다. 제품의 `schema:1/profile:sync-acyclic-v1`과 prototype의 `version:2/header-rail`은 동일한 저장 형식이 아니다.

## 검증과 재실행

[소유 fixture probe](../tests/probes/blueprint-compatibility/Program.cs)와 [프로젝트](../tests/probes/blueprint-compatibility/blueprint-compatibility.csproj)는 .NET 10에서 다음처럼 실행한다. 기존 테스트용 Fixture와 실제 Builder/compiler를 사용하며 매번 임시 팩을 만들고 정리한다. 사용자 프로젝트나 외부 계정은 사용하지 않는다.

```sh
dotnet run --project tests/probes/blueprint-compatibility -c Release -- /tmp/confectory-blueprint-compatibility.json
```

첫 임시 probe 빌드는 검사 코드의 IEnumerable/IReadOnlyList 인수 불일치로 실패했다. 배열로 바로잡은 뒤 10개 호환성 assertion이 통과했으며, 저장소에 추가한 재실행 프로젝트도 같은 검사를 통과했다. 제품 오류 수정이나 일반 회귀 10건으로 계산하지 않는다. 최종 probe는 실제 읽은 compiler·지원 코드·probe 원본 해시를 결과에 기록한다. [최종 증거와 범위](evidence/v480-integration/compatibility-review.json)에 단계별 로그 해시·현재 원본 해시·대조 근거를 보존한다.

기존 제품/테스트 원본 190개의 조사 전후 해시는 유지했다. 제품·리소스·compiler를 바꾸지 않았으므로 직전 체크포인트의 API 23건·UI 10건·관리 대상 컴파일 1건·일반 Git 체크아웃 1건을 새로운 전체 회귀 결과로 재계산하지 않는다. 전체 v480 완료 표시는 하지 않는다. 미설정 반환의 **컴파일 오류/타입 기본값** 선택과 기존 구현의 **참조 재사용/명시적 새 graph/본문 이관** 목적은 각각 별도 결정이다.

후속 UI 작업에서 이 검토의 확대·휠·포인터 카메라 차이와 현재 계약의 헤더/핀 연결 조작을 연결했다. graph별 private 보기와 문서 탭·미확정 입력 보존 검증은 [카메라 연결 기록](EDITOR_V480_INTEGRATION.md)에 따로 남긴다. 이 후속 변경은 위 `e222acb` 기준 조사와 원본 해시를 소급해 바꾸지 않으며, 새 실행/타입·이관 정책도 정하지 않는다.
