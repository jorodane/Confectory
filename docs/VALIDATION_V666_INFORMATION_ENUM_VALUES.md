# v666 속성의 종류 값과 기본값

원본은 저장소 v666 ZIP SHA-256 `7b6b4ba585fc46843f09d8bcd15072b704cc2dc994988400b0a25061e0400d23`다. `app.js:1897–1910`은 항목 아이콘·이름을 보여주는 종류 드롭다운, `2773–2786`은 종류 owner의 항목 ID 선택, `2809–2811`은 새 값의 첫 항목/빈 종류 초기값, `2993–3053`은 속성 타입과 단일/여러 값 편집이다. 표시명이나 행 번호를 값으로 저장하지 않는다.

## 지원 범위와 저장 의미

- 정보의 새 속성과 기존 직접 소유 속성에서 종류를 선택하고 항목 ID를 기본값으로 저장한다. 객체의 기존 종류 값과 새 로컬 속성도 같은 typed-data 경로를 사용한다. 원본 드롭다운·배열 조작·기호/정규화 로컬 이미지·키보드·취소를 사용하며 CSS나 새 디자인을 추가하지 않는다.
- `field Choice single enum Qualified.Namespace::Mood;`와 일반 scalar 문자열 `data Choice = "stable-member-id";`를 연결한다. 정보의 명시 기본값은 기존 `editorInformationDefaults="typed-json-v1"`/`editorFieldDefault_` 기록이다. 항목 ID는 선언된 종류 owner와 함께 해석하므로 다른 종류의 같은 문자열 ID와 혼동하지 않는다.
- 새 속성의 초기값과 배열의 새 값은 원본처럼 첫 항목 ID, 빈 종류는 빈 문자열이다. 빈 문자열은 미선택 상태이며 새 항목 추가 시 자동 선택하지 않는다. 이미 선택한 ID는 이름·순서 변경으로 바꾸지 않는다. 이름·숫자·순서를 ID로 추측하거나 비호환 기존 값을 자동 초기화하지 않는다. 명시한 타입/값이 맞지 않으면 전체 후보를 거절하고 입력을 유지한다.
- 타입 선택은 기존 root/명시 dependency 카탈로그와 원문 SHA를 사용한다. 실제 값·정보 기본값은 native의 종류 membership 검사를 거치며 ID가 없거나 종류 owner가 다르면 전체 미적용한다. 원본 부모·공유 schema·등록팩 정의를 값 편집으로 바꾸지 않는다. 기존 public override의 cardinality/kind/type 계약도 유지한다.
- 종류 항목을 삭제했을 때 현재 프로젝트의 저장된 schema 기본값이나 객체/중첩/배열 값이 무효가 되면 종류 저장 후보를 전체 거절한다. 다른 항목으로 치환하거나 참조를 버리지 않는다. 소비자와 삭제를 명시적으로 대응하는 UI는 후속 경계이며 종류 전체 보관/복구를 추가하지 않았다.
- 종류 목록은 metadata의 종류 owner별 표로 전달한다. 필드/배열 행마다 이미지 목록을 복제하지 않는다. 기존 source·관측·projection 크기 예산과 namespace/소유/binding/최종 CAS 검사는 유지한다.

## C# 및 호환성 경계

이 단위는 선언된 속성의 편집/저장 데이터다. C# enum/정수/문자열 CLR 타입을 확정하거나 dispatcher·함수 ABI·자동 본문 변환을 추가하지 않는다. runtime property descriptor는 이 종류 필드에 `supported:false`, `clrType:null`을 명시한다. 실행용 property read/set/ref 노드는 기존 지원 검사에서 거절하며 추측한 CLR 계약으로 생성하지 않는다. 따라서 C# 표현 결정은 이 편집/저장 흐름의 선행 조건이 아니다. 함수/실행 경로를 연결할 때 별도로 결정해야 한다.

새 native `enum` 선언과 `field ... enum Qualified::Owner`는 갱신된 parser가 필요하다. 구버전 롤백 패키지는 새 종류 데이터를 읽지 못하며 자동 구버전 변환이나 프로젝트 마이그레이션을 하지 않는다. 알려지지 않은 profile을 보존한 채 거절한다. 패키지 복원 검증과 구버전 데이터 호환성을 혼동하지 않는다.

## 검증과 마감

집중 검증은 실행별 소유 RAM workspace와 지속 증거를 사용한다. Core는 단일/배열/미선택 값, ID와 표시명의 분리, 잘못된 종류 owner·값·상속 계약과 실행용 CLR 비지원 경계를 확인한다. native 후보는 타입 원문 proof, 정의+기본값/객체 값의 결합, 사용 중 ID 삭제 거절 및 원문·큰 정수·등록/외부 원본 보존을 확인한다. 기본/독립 화면의 Undo/Redo·취소·실패·충돌·응답 유실·프로젝트 왕복·재시작·늦은 입력·Review/명시 Confirm은 실제 fixture로 검증한다.

집중 기록 `/workspace/artifacts/v536-verification-managed/runs/53b147fa67e9458c9a0564a05624c901.json`은 빌드를 포함해 통과 32단계, 진단 실패 7단계를 따로 기록한다. Core 7건은 모두 통과했고 native의 등록팩 dependency/다른 종류 membership/원본 보존도 확인했다. 정보와 객체의 새 속성 생성·단일/배열 값·기본/독립 창·응답 중 새 선택·응답 유실·저장 실패·취소·실제 owner 충돌·다른 프로젝트 왕복이 통과했다. 증거 ZIP SHA-256은 `b4b1d6f6fc8475428ce0a5eeba5986a793a73a7fefcfe8d8b646e2577ab86bce`이며 record는 `cleaned`, 실행별 RAM root는 제거됐다. 빌드 캐시/출력의 전체 파일 hash를 기록하고 원본/입력·프로필·로그·스크린샷은 지속 증거로 보존했다.

초기 진단 실패는 별도 보존한다. 검사 입력의 중복 표시명과 object 값 요청 형식은 실제 계약에 맞춰 수정했다. 객체 typed path와 frontend 저장 직렬화의 종류 허용 누락은 기존 ID/소유/계약 검사를 유지하며 enum만 추가했다. 리소스 재핀 과정의 바이너리/canonical 혼합은 바이너리 항목을 원본 그대로 복원해 수정했다. Undo 검사는 기존 속성 section에 포커스를 두고 실행한다. 응답 보류 검사는 보류 중 전역 idle을 기다리지 않되 실제 응답 보류·새 입력·receipt·cold/재저장 검사를 유지한다.

최종 정확한 source commit의 LF/CRLF 독립 checkout·새 교차 패키지·압축 전체 SHA/CRC/모드 복원·UI·실패 수명관리 및 최신/롤백 지속 보관 결과는 최종 실행 뒤 기록한다. 기존 79단계를 유지하고 새 native/UI/객체/패키지 흐름 7단계를 더한 `--suite enum-values` 86단계가 대상이다. SDK/의존성 seed와 이전 정상 롤백 증거의 재사용은 새 실행과 구별한다. 실제 Windows/WebView2·물리 모바일·전체 UI·Space/Library 전달은 미검증이다.

종류 전체 보관/복구·소비자 삭제 대응 UI·C# 표현은 이번 완료와 구분한다. 기존 ABI/Set 지원 경계, B2/M4/M11/M12 및 V2–V9는 그대로다. 3D/권한 별도 팩, 이동 연출과 작업 실행 분리 합의도 유지한다.
