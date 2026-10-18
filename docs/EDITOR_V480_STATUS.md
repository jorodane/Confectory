# v480 현재 구현 범위와 남은 요구

이 표는 `main@32dd44fbec6e9e39a7e3e68c0ca61d62bb47176f`의 v480 레퍼런스와 `work/current`의 실제 원본·compiler·실행·편집 증거를 비교한다. 과거 문서의 미구현 표시는 해당 체크포인트의 기록이며 이 표가 현재 범위를 정리한다. 행 개수·함수 개수로 완료율을 계산하지 않는다. **전체 v480 완료를 주장하지 않는다.**

표의 **지원**은 적힌 범위의 구현·검증 완료, **부분**은 일부 계약/동작만 연결, **미구현·답변 대기**는 미완료를 뜻한다. 이 상태를 같은 행의 나머지 범위로 확대하지 않는다.

## 미완료 원인과 다음 단계

‘부분’만으로 사용자 답변 대기나 구현 부재를 판단하지 않는다. [실제 클릭 대조](V480_UI_CLICK_AUDIT.md)에 이어 [Home·브라우저·문서 대조](V480_HOME_BROWSER_NAVIGATION.md)에서 검색/그룹 상태 손실과 반복 열기의 입력 DOM 교체를 기존 계약 안에서 수정했다. 아래 구분은 기존 표의 남은 범위를 읽는 기준이다.

| 구분 | 실제 항목 | 다음 단계·경계 |
|---|---|---|
| 기존 계약 안의 UI 누락 | 빈 곳 드롭 취소, 무효 case/시작 대상의 기존·미적용 입력 보존, 출력 sidebar 크기/접기 | 이번 수정과 실제 UI 검증. 새 실행 의미·새 권한 없이 연결 |
| Home 저장/조회 후속 | Home 전용 검색/탭/정렬/선택 콜드 저장과 확정 root object 선언 수 | [Home 전용 저장·집계](V480_HOME_STORAGE_AND_COUNTS.md)에서 기존 호스트 원자 저장과 metadata list total을 연결. 프로젝트 presentation과 분리 |
| 실제 조회·영속 기록 연결 | Home 포함 팩 수와 마지막 편집 정보 | [후속](V480_HOME_INCLUSION_AND_EDIT_EVENTS.md): 확정 entry/타깃별 도달 집합과 성공한 Save/Confirm의 원자적 receipt. 기록 없음·조회 불가 구분, 실제 콜드 복원. native adapter 포함 조회는 미지원 |
| 대조/미지원 범위가 남음 | category/concept 계층 전체, browser Data의 자동 전체 필드 합집합, Workspace 삭제 외 일반 배치 Undo·도킹 전 native Undo 이력 | 이미 있는 모델/명령과 레퍼런스의 동작을 대응시킨 다음 확인한 누락을 수정. 미검사 전체를 정책 차단으로 표시하지 않음 |
| 사용자 정책 답변 대기 | 계산식 int/long overflow: 오류 또는 wrap | 아직 미답변. enum 값 범위와 별개이며 다른 로컬 UI 수정의 차단 아님 |
| 새 구조 계약이 미구현·현재 범위 밖 | 구조적 property field write/ref, compound/function live field, 일반 enum/Vector3 ABI, 소유 집합 생성/삭제 전체 Undo | 기존 read/primitive/일반 이력 지원과 구분. 이번 UI 대조에서 새 의미를 추가하지 않음 |
| 서비스 계약이 미구현·현재 범위 밖 | actor/recipient/room/ack, 실제 market/publisher, Run 새 호스트의 durable 연결·surface embedding | 소유 fixture나 화면 상태를 실재 서비스로 가장하지 않음 |
| 환경상 미검증·현재 범위 밖 | 실계정·유료 모델·native OS 창·실기기·사용자 PC 설치 | 컴파일/공통 web 결과로 검증 완료를 주장하지 않음. main·ZIP·Android 설정 보존 |

## 현재 구현과 검증 근거

`e50da714c5b558e685a92d8229b8e193eede3559`에서는 고정한 제품/테스트 47개 파일에서 엔진/공개 편집/ABI 82건, 중복 없는 실제 Chromium 25건, Windows/Android 관리 프로필 컴파일 1건과 일반 Git checkout·33개 리소스 시작 1건이 통과했다. [원본 hash와 각 범위](evidence/blueprint-node-time-properties/properties.json)를 보존한다. 이번 C# 편집 후속에서 그 결과를 새 전체 엔진 회귀 수로 재계산하지 않는다. 후속에 실제 실행한 검사는 [별도 기록](evidence/v480-csharp-editor/editor.json)에 구분한다.

| v480 요구 영역 | 현재 상태와 범위 | 실제 근거 / 남은 부분 |
|---|---|---|
| 기능 화면·입출력·문서 탭·배치 | 지원: 소유 graph, private 보기, typed 입력/결과, 원본 CAS와 cold 입력 | [통합 기록](EDITOR_V480_INTEGRATION.md), 실제 UI. 전체 prototype 픽셀 일치 아님 |
| 새 기능·객체 구현·노드 생성/제거 | 지원: 원본 등록 그룹·독립 C# leaf·노드 ID/전체 소유 경로·파일 보존 | 엔진/공개 편집·UI. 미게시 객체의 구현 아래 code/call 생성 회귀도 실제 검사 |
| 기존/등록 기능 참조·부모 재사용 | 지원: 원래 함수 ID·typed 계약·scope·본문 보존, 같은 함수 provider fallback | [호환성](EDITOR_V480_COMPATIBILITY_REVIEW.md), FunctionImport/RegisteredCall/ObjectImplementation 실제 실행 |
| 모듈 인터페이스·제공 구현·가져오기 | 지원: 요구 signature·기본 제공·객체별 구현과 등록 함수 계약 | ModuleInterface/RegisteredImplementation 및 실제 UI |
| C# 본문·함수 내부 보조 함수 | 지원: 본문 exact source, 함수별 local helper, 전체 body 구문 검사와 독립 compiler probe | [보호 편집 계약](BLUEPRINT_PROTECTED_CSHARP_EDITOR.md), actual CLR helper 실행·무실행 probe |
| 고정된 함수 외곽과 전체 코드 보기 | 지원 범위: 현재 signature/괄호 보호, 본문 편집·Undo/Redo·Tab·private cold·기존 Apply/Confirm | 실제 Chromium 후속 기록. 전체 소스 표시가 새 C# 파일이 되지 않음 |
| C# 매개변수 영역에서 pin 계약 변경 | 지원 범위: 일반 정적 코드 노드의 typed 이름/타입/값·ref·out/순서, 명시적 remap·stale 본문 재적용·Review/Confirm | [계약](BLUEPRINT_STATIC_METHODS_AND_PARAMETERS.md). 자유 선언 편집·위치 추측·전체 본문/caller-storage 계약 변경은 제외 |
| Execute 밖 helpers 영역 | 지원 범위: methods profile 일반 코드 노드의 node-owned static 메서드, 내부 graph·독립 probe·원본 해시·Task/CAS/cold/Confirm | [계약·증거](BLUEPRINT_STATIC_METHODS_AND_PARAMETERS.md). 필드·초기화자·공유 상태·상위 캡처·전체 본문 문맥 확장은 미지원 |
| enum 계약·선언 소스 준비 | 지원: private 안정 ID/int32·현재 원본 hash 연결·선언 미리보기·명시적 공유 적용 | [개인 계획·호환성](BLUEPRINT_ENUM_CONTRACT_PREPARATION.md), 별도 profile 전환·stale 본문 재적용·CAS/Confirm |
| enum 실행 출력 | 지원 범위: 명시적 switch profile, 선택 case/default 후 메인 계속·미일치 계속·중첩 복귀·실제 종료 out 경고 | [실행·이관 경계](BLUEPRINT_SWITCH_CONTINUATIONS.md). 기존 데이터 return/bool·whole-body 문맥은 자동 변환하지 않음 |
| 기존 C# 구현 전체 이관 | 지원: 선택 구현·타깃의 본문 전체를 한 노드에 보존, imports/scope/calls/this/Invoke·이름·CRLF·다른 타깃 유지 | [본문 전환](BLUEPRINT_IMPLICIT_END_AND_BODY_CONVERSION.md), 실제 전후 실행·원자적 그룹·원본 CAS·cold |
| 줄 끝 종료·미할당 반환 | 지원: 새 명시적 profile에서 연결 없는 줄 종료, 타입 기본값·포트별 누락 경고/경로 | [줄 끝 반환](BLUEPRINT_IMPLICIT_END_AND_BODY_CONVERSION.md). 구 profile의 생성 의미 보존 |
| 이름 있는 out 데이터 출력 | 지원: out pin/결과 binding/export, 종료별 must/may·미할당 경고 | [out 출력](BLUEPRINT_NAMED_OUT_OUTPUTS.md), 실제 compiler·실행·UI |
| ref 입력·같은 호출자 저장소 별칭 | 지원: input/local/선행 결과 슬롯, 배열 참조 슬롯, 동일 ref/ref/out 전달 | [ref 노드](BLUEPRINT_REF_NODE_STORAGE.md), [외부 ref](BLUEPRINT_EXTERNAL_REF_STORAGE.md), 실제 CLR 별칭 |
| 호출별 로컬과 set | 지원: 명시적 타입·상수 초기값과 구조적 set | [로컬 값](BLUEPRINT_LOCAL_VALUES.md). 이전 함수 호출의 로컬을 공유하지 않음 |
| 입력·노드 결과 별칭 로컬 | 지원: 원래 슬롯을 참조하며 set/ref가 같은 저장소에 작용 | [별칭 로컬](BLUEPRINT_ALIAS_LOCALS.md), 실제 값 인수 스냅샷·별칭 변경 검사 |
| 소유 private 내부 graph | 지원: typed 입력/ref/out·동기 비순환 호출/복귀·호출별 로컬·전체 경로 원본·자식 경고 | [private graph](BLUEPRINT_PRIVATE_GRAPHS.md). 부모 로컬/receiver 암묵 캡처·loops/async 아님 |
| 실제 객체 property 값 읽기 | 지원: 사용자 확정대로 실행이 해당 노드에 도달할 때 한 번 읽고 typed 결과 전달 | [node-time property](BLUEPRINT_NODE_TIME_PROPERTIES.md), actual 인스턴스/배열/참조·mutation·재호출·스키마 CAS |
| property field 쓰기·ref/lvalue | 부분: 명시적 ObjectModel.Write 함수는 있음, 구조적 property read의 결과는 일반 슬롯 | field 자체를 set/ref 대상으로 하는 graph 계약은 추가하지 않음 |
| compound/function live property | 미구현 | 목록에 현재 field kind를 표시하고 지원 전으로 거부. general/reference single/multiple만 실행 지원 |
| 계산식 UI/실행·정수 overflow | 미구현·답변 대기 | 원본 연산 목록만 확인. int/long overflow 오류/wrap을 선택하지 않으며 기존 C# 연산은 보존 |
| 확장 enum/Vector3/일반 사용자 타입 ABI | 부분: 기존 primitive/배열·object/object[] 실제 CLR 참조 지원 | prototype의 모든 csharpType·복합/enum 타입을 CELEM에 지원한 것으로 표시하지 않음 |
| 노드 Task·Worker 권한·검토 | 지원: 독립 C# 원본·현재 definition·관련 source hash 관찰·제한 네 도구·Stage/Review/Confirm | 실제 권한 거부/원본 변경/콜드 재사용 거부. 구조 노드에 C# Task를 만들지 않음 |
| 3.125–300% 자유 확대·포인터 camera·헤더/pin 조작 | 지원: private graph별 보기·실제 좌표·팬/취소·연결 입력 준비·무효 대상 입력 보존 | [카메라 기록](EDITOR_V480_INTEGRATION.md), [핀·사이드바 대조](V480_UI_CLICK_AUDIT.md). 연결은 별도 Apply/CAS/Confirm 유지 |
| Workspace 문서·메모·탭·제목·검색·도킹 | 지원한 행위의 실제 Chromium/cold 검증 있음 | 직전 25개 UI와 개별 기록. 전체 외부 OS/native 창 동작 완료 아님 |
| 일반 Git checkout·리소스 시작 | 지원: pinned canonical LF/보존 CRLF·실제 Home·변조/인코딩/예산 거부 | 커밋 기준 실제 checkout. 후속 모듈 추가 시 리소스 수와 검사를 갱신 |
| Linux/.NET 10·Windows/Android | Linux 실제 owned CLR/공통 web UI, Windows/Android는 관리 프로필 컴파일 | native/device·실제 계정·유료 모델·사용자 PC 설치는 미검증이며 이번 경계 밖 |

enum의 숫자 항목 범위 확인과 계산식 overflow는 다른 계약이다. 편집 callback의 통과, 실제 C# compile의 통과, runtime 결과와 Chromium 편집/복원을 별도 근거로 취급한다. 원본 ZIP과 main을 편집하거나 과거 검사 수를 후속 새 결과에 합산하지 않는다. bounded static helpers·ordinary caller-storage·whole-body Invoke의 정확한 지원 차이는 [비교 표](BLUEPRINT_ENUM_CONTRACT_PREPARATION.md#bounded-helpers와-원래-invoke-문맥)를 따른다.

## 그래프 밖의 서비스·편집 요구

아래는 v480 app.js의 Home/Pack/Helper/Worker/Yogi/Run/설정 흐름을 기존 [v424 동작 지도](EDITOR_V424_INTEGRATION.md)의 안정적인 항목 ID와 함께 확인한 범위다. 기존 소유 계약/fixture 결과가 있는 것과 실제 외부 서비스·전체 UI 완료를 구분한다. 이번 C# 후속에서 이 행들의 전체 회귀를 새로 수행했다고 표시하지 않는다.

| 기존 ID | 요구 묶음 | 현재 판단과 남은 범위 |
|---|---|---|
| S01–S02 | 시작·Home·Agent 선택·앱 창 | [Entry/Home 소유 모델](ENTRY_HOME_MODEL_PACK.md)과 공통 web 시작은 있음. 각 native host의 창·입력·접근성 전체 완료 아님 |
| H01–H06 | 프로젝트 목록·검색·정렬·즐겨찾기·생성·정보·닫기 | 실제 ProjectManager/생성·소유 수명 경계 있음. Home 반복·검색·정렬 취소/복귀를 실제 검사했다. Home 전용 콜드 저장과 확정 root object 선언 집계를 연결했다. 포함 팩 수와 마지막 편집 정보는 [후속](V480_HOME_INCLUSION_AND_EDIT_EVENTS.md)에서 연결했으며 overflow 정책과 독립적이다. 팩 요구/유형·선택 Helper·프로필과 모든 전환 조합은 부분 |
| B01–B06 | 브라우저·트리·복제·하위 탐색·생성·상속·삭제 | 그룹별 검색/위치·미적용 입력과 콜드 실제 목록, 독립 브라우저·문서 복원 검사 있음. 참조 드래그는 scoped 입력 준비이며 source 변경은 기존 Apply를 유지. 여섯 선언 종류 생성과 바리에이션 검증 있음. 전체 tree/category grouping·삭제/참조 대체는 부분/계약 필요 |
| D01–D06 | 필드·Data/즉석 테이블·참조 원본·개념 맵 | [v424 실제 schema/표/관계/읽기 전용 정의 증거](EDITOR_V424_INTEGRATION.md) 있음. 즉석 테이블의 열 반복 이동/너비·retained 입력과 scoped 참조 드래그/현재 참조 문서 이동을 검사. [브라우저 Data 필드 비교](V480_BROWSER_DATA_FIELDS.md)는 명시적 소유 객체/필드 선택을 기존 versioned table 셀 편집기에 연결. enum/벡터·자동 전체 필드 합집합·임의 깊이 탐색 전체는 부분 |
| E01–E08 | schema·enum·객체 동작·함수·모듈·계약 요청 | 일반 CELEM schema/typed 함수·모듈/graph는 위 표의 범위. prototype의 모든 enum/벡터/복합 ABI·원클릭 밸런스/테스트 실행은 완료 아님 |
| C01–C04 | Apply/Save·공유 초안·묶음 검토·충돌·이력 | 실제 source hash/revision/token/CAS·compiler Confirm과 일반 편집 이력 있음. 생성/삭제·소유 집합 역변경 전체 Undo는 별도 |
| I01–I02 | 신문고·승인/요청/충돌·처리 이력 | 실제 사건과 owner inbox를 연결할 계약이 남음. 화면의 해결 표시를 실제 사건 해결로 취급하지 않음 |
| Y01–Y03 | Yogi Exactly/Seal·첨부·수신/전달·복구 | [기존 Yogi 기록](EDITOR_V318_YOGI.md)의 소유 snapshot/재검증 있음. recipient·room·ack·중복/실패·수신 권한은 부분/후속 |
| A01–A04 | Augment·로컬 Custom·Worker·검토/채택/중지 | [v424 로컬·이력·노드 Task 증거](EDITOR_V424_INTEGRATION.md)와 소유 journal/권한 경계 있음. 외부 모델 실제 생성과 모든 task 상태 조합은 완료 아님 |
| R01–R06 | Run/Stop·빌드 job·렌더 삽입·Pause/Step·재연결·내보내기 | 실제 소유 프로세스·compiler job과 [로컬 협력적 frame/ack·Pause/Step·같은 호스트 재연결](V480_LOCAL_RUN_FRAME_CONTROL.md)을 연결했다. 비참여 프로젝트·자식 surface·새 호스트의 durable launch 채택·기기/서명 배포는 별도다 |
| P01–P05 | Helper 소속·프로필·이미지·pin·대화·기억 | [Helper scope](HELPER_PRODUCT_SCOPES.md)와 membership/private UI는 있음. 실제 이미지 provider·사용량 승인·대화/전송의 전체 영속/서비스는 부분 |
| G01–G03 | Agent 탐색·설치 준비·로그인·모델·사용량·연결 | [Codex 준비 기록](codex-preparation.md), 실제 지원 metadata/소유 설정 경계 있음. 다른 Agent와 실계정/유료 호출의 정상 작동을 이 개발 검증으로 주장하지 않음 |
| U01–U03 | 내 정보·co-worker·요청/수락/차단·채팅/news | 로컬 profile/presentation 일부 있음. 실재 actor/membership/sender/recipient/room/ack 서비스 계약이 남음 |
| M01–M04 | 내 팩·시장·설치/업데이트·공개 게시 | 로컬 pack registry/manifest·의존성 검토 일부 있음. 실제 시장 catalog·publisher·서비스 설치/배포 권한은 별도이며 온라인 시장을 가정하지 않음 |
| W01–W06 | Workspace 이동/선택·문서·메모·포털·링크 | 실제 web/cold로 검증한 행위는 위 표와 [통합 기록](EDITOR_V480_INTEGRATION.md). [비공개 링크·자손 이동·포털 전송·조건부 삭제 Undo/redo·콜드 복원](V480_WORKSPACE_LINKS_AND_LIFETIME.md)을 연결했다. 일반 배치 Undo와 native 플랫폼 동작 전체는 별도 |

이 행들과 그래프 표를 합쳐도 모든 클릭·중단·실패·재시작·서비스 조합이 검증됐다는 뜻은 아니다. 근거가 없는 항목은 미완료/부분으로 유지한다.


<!-- node-methods-current-validation -->
정적 보조 메서드·매개변수 후속은 고정한 제품/테스트 25개 원본에서 서로 다른 엔진/공개 편집 82건(분할 회귀 27/1/0 + 26/1/0 + 26/1/0, 제한 초과 3건은 동일 소스에서 단독 재통과), 실제 Chromium 11건(6/0/0 + 5/0/0), 관리 프로필 컴파일 1건으로 검증했다. [정확한 범위·이력·소스 해시](BLUEPRINT_STATIC_METHODS_AND_PARAMETERS.md)를 따른다. 일반 Git checkout·보존 CRLF/새 LF·35개 리소스·실제 Home 시작·변조 거부도 1건 통과했다.
<!-- /node-methods-current-validation -->

<!-- switch-current-validation -->
순차 enum switch 후속은 고정 원본 27개에서 엔진/공개 편집 94/0/0, 실제 Chromium 13/0/0으로 통과했다. 이후 switch 복귀선·여러 포트 배치의 UI 보완 뒤 최종 원본 28개에서 해당 UI 1건을 재통과했고 관리 프로필 컴파일 1건도 통과했다. 중복 UI를 새 고유 검사로 합산하지 않는다. [정확한 단계·소스·범위](BLUEPRINT_SWITCH_CONTINUATIONS.md#최종-검증과-소스-단계)와 [일반 checkout HEAD·36개 리소스 시작 검사](validation/v480-switch-continuations.json)를 따른다. 이 결과로 외부 서비스·전체 v480·native/device 경계를 완료한 것으로 표시하지 않는다.
<!-- /switch-current-validation -->

<!-- ui-click-current-validation -->
클릭/입력 대조 후속은 고정 UI·테스트 원본 9개에서 실제 Chromium 4/0/0, 관리 프로필 컴파일 1/0/0으로 통과했다. 빈 곳 드롭 취소·무효 대상의 입력/연결 대기 보존·출력 sidebar 조절/접기/콜드를 확인했다. 엔진 원본은 변경하지 않았다. [범위와 미완료 원인](V480_UI_CLICK_AUDIT.md), [일반 checkout HEAD·36개 리소스 근거](validation/v480-ui-click-audit.json)를 따르며 과거 결과를 새 전체 회귀 수로 합산하지 않는다.
<!-- /ui-click-current-validation -->

<!-- navigation-current-validation -->
Home·브라우저 전환 후속은 고정 제품/테스트 원본 7개에서 실제 Chromium 6/0/0, 관리 프로필 컴파일 1/0/0으로 통과했다. 그룹별 적용 검색/미적용 입력·위치, 활성 탭 반복, 정렬 취소, 같은 입력 DOM, 문서/콜드 복원, 소스 미적용 입력에 따른 전환 거부를 검사한다. [구체적 범위와 남은 조회/저장 계약](V480_HOME_BROWSER_NAVIGATION.md), [고정 원본·최종 실행·checkout 근거](validation/v480-home-browser-navigation.json)를 따른다. 이전 검사 수를 새 전체 엔진 회귀로 합산하지 않는다.
<!-- /navigation-current-validation -->

<!-- home-storage-current-validation -->
Home 전용 제한 설정 파일과 프로젝트별 확정 object 선언 수의 후속은 제품/테스트 원본 21개에서 실제 Chromium 6/0/0, 모델/프로젝트 수명 2/0/0, 관리 프로필 컴파일 1/0/0으로 통과했다. 정확한 단계와 원본 차이는 [저장·집계 범위](V480_HOME_STORAGE_AND_COUNTS.md)와 [고정 원본·최종 실행·checkout 기록](validation/v480-home-storage-counts.json)을 따른다. 포함 팩 수와 마지막 편집 시각은 근거 없는 값으로 채우지 않는다. 기존 프로젝트 presentation·목록·즐겨찾기 저장과 Home 설정을 분리한다.
<!-- /home-storage-current-validation -->

<!-- reference-navigation-current-validation -->
[참조/열/문서 후속](V480_REFERENCE_NAVIGATION.md)은 최종 제품/테스트 원본 11개에서 실제 Chromium 9/0/0, 관리 프로필 컴파일 1/0/0으로 통과했다. 참조의 scoped 입력 준비와 현재 값 링크, 같은 schema/table의 DOM 보존, 필드 열 조작, 그룹 콜드 실제 목록 누락을 수정했다. [고정 원본·최종 실행·checkout 기록](validation/v480-reference-navigation.json)을 따른다. 브라우저 자체 전체 필드 열, category 계층과 Workspace 시각 링크 그래프를 지원했다고 확대하지 않는다.
<!-- /reference-navigation-current-validation -->

브라우저 Data 후속은 [정확한 매핑과 경계](V480_BROWSER_DATA_FIELDS.md), [고정 원본·실행·checkout 기록](validation/v480-browser-data.json)을 따른다. 이름/종류/작업 사본 옆에 명시적으로 선택한 소유 객체의 실제 필드를 표시하고, 같은 InstantTable 셀 편집기와 타입·source/schema CAS·Apply/Review/Confirm을 재사용한다. 검색/선택/구성 변경으로 숨긴 입력도 원래 버전과 함께 보존하며, 외부 팩은 읽기 전용으로 유지한다. 자동 필드 합집합이나 새 데이터 모델·실행 의미를 지원했다고 확대하지 않는다.

브라우저 다중 행 채우기 후속은 [선택·버전·취소·원자성 범위](V480_BROWSER_ATOMIC_FILL.md), [고정 원본·최종 실행·checkout 기록](validation/v480-browser-fill.json)을 따른다. 다음 작업은 [v480 잔여 구현 묶음](V480_REMAINING_WORK.md)의 우선순위·근거·완료 기준으로 정한다. Data의 셀 Apply/선택 행 채우기는 완료한 범위이며 이를 새 계산 열이나 자동 선택 확장으로 확대하지 않는다.

선언 계층 탐색 후속은 [실제 ID/parent/schema·소유/등록 정의·Variation·채우기·독립 콜드 복원](V480_DECLARATION_NAVIGATION.md), [고정 원본·최종 실행·checkout 기록](validation/v480-declaration-navigation.json)을 따른다. 기존 소유 관계 조회를 활용하며 category/concept를 폴더와 동일시하지 않는다. Workspace 링크 수명·새 category 편집/삭제/참조 치환·자동 쓰기 선택은 추가하지 않는다.

Home 포함 팩·저장된 편집 기록 후속은 [범위와 의미](V480_HOME_INCLUSION_AND_EDIT_EVENTS.md), [고정 원본·단계별 검증](validation/v480-home-inclusion-edit-events.json)에 기록한다. 모델 11/0/0, 실제 Chromium 6/0/0, 관리 프로필 컴파일 1/0/0, 구현 커밋의 일반 checkout·리소스·Home 시작 1/0/0이다. 초기 페이지 종료 취소 경계도 실제 브라우저에서 재현해 보정했다.

Workspace private 창 링크·수명은 [규칙과 저장 경계](V480_WORKSPACE_LINKS_AND_LIFETIME.md), [고정 원본·단계별 검증](validation/v480-workspace-links-lifetime.json)을 따른다. 모델 2개·서로 다른 UI 8개·관리 프로필 1개·일반 checkout 1개가 통과했다. 구형 UI fixture 1개 보정과 단계별 hash·원래 실패는 검증 기록에 분리한다. 소스 삭제와 일반 이동/연결 Undo는 이 비공개 삭제 이력에 포함하지 않는다.

로컬 Run 프레임 제어 후속은 [세션·frame/ack·Pause/Step·단절/재연결 명세](V480_LOCAL_RUN_FRAME_CONTROL.md)를 따른다. 프로세스 상태와 협력적 런타임의 실제 완료 프레임을 구분한다. 기존 Engine, ButtonGame GUI와 ordinary FrameLoop에 연결하며 비참여 프로젝트는 일반 Run/Stop을 유지한다. 새 호스트의 이전 실행 채택·surface embedding·원격 서비스·기기/PC 설치와 property set/ref·확장 ABI·overflow는 별도 범위다. 최종 고정 원본과 검사 근거는 [검증 기록](validation/v480-local-run-control.json)에 남긴다.

로컬 Run 후속의 최종 고정 원본 50개에서 실행/모델 10/0/0, 실제 Chromium 3/0/0, 관리 프로필 컴파일 1/0/0, 일반 checkout·41개 리소스·Home 시작 1/0/0이 통과했다. 서로 다른 메서드 15개이며, 이전 9/1/0 단계와 실제 포커스 fixture 보정 근거는 최종 합계에 섞지 않았다. 네이티브 Engine은 Step마다 실제 fixed tick 하나, ButtonGame은 실제 두 View Draw 완료를 확인했다. Windows/Android 실기 실행·설치는 검증하지 않았다.

비밀정보 없는 실행 이력과 콜드 상태 표시는 [범위·저장 형식·권한 경계](V480_RECORDED_RUN_HISTORY.md)를 따른다. 기존 실행 ID와 마지막 확인 상태/frame/ack/종료 결과를 제한된 원자적 기록으로 남긴다. 새 호스트는 owner-unavailable로 표시하며 기록을 실행 레지스트리에 가져오거나 이전 권한·명령을 복원하지 않는다. 손상·충돌·저장 실패는 실제 Run/Stop과 분리한다. [고정 원본·최종 검증](validation/v480-recorded-run-history.json)에 단계별 결과를 남긴다.

실행 이력 후속은 고정 제품/검사 원본 28개에서 실행/모델 14/0/0, 실제 UI/전송 5/0/0, 관리 프로필 1/0/0, 일반 checkout·41개 리소스·Home 시작 1/0/0으로 통과했다. 서로 다른 21개 메서드다. 이전 UI 실패·구형 검사 보정과 명령 접수 중 poll이 revision을 바꾸던 실제 문제의 RED/GREEN은 [검증 기록](validation/v480-recorded-run-history.json)에 분리한다. revision/CAS·권한 검사와 자동 재실행 금지를 유지한다.

타입 지정 property Set 후속은 [실제 receiver/value·owner/field hash·참조 보존·편집/콜드/Confirm 범위](BLUEPRINT_PROPERTY_SET.md), [고정 원본과 단계별 검사](validation/blueprint-property-set.json)를 따른다. 이전 문서의 property set/ref 미결 범위 중 general/reference 단일·배열 구조 Set을 완료한다. true field ref/lvalue와 compound/function·enum/Vector3 ABI·overflow는 별도로 남긴다. 기존 profile을 자동 전환하지 않는다.

property Set의 최종 검사는 고정 제품·테스트 원본 27개에서 CLR/공개 편집 등 39개·기존 graph/편집 16개·실제 Chromium 5개·관리 프로필 컴파일 1개·일반 checkout/리소스/Home 시작 1개, 총 **62/0/0**이다. [단계·원본·초기 보정 근거](validation/blueprint-property-set.json)를 따른다. 전체 v480 완료나 기기 실행으로 확대하지 않는다.
