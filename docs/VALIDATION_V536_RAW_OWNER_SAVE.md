# v536 raw source와 같은 owner/정보 창의 결합 Save

`587d76e` 이후 원본 UI의 기존 source Save와 요소 임시 저장을 한 후보에 연결한 한정 단위다. HTML/CSS·크기·컨트롤 배치를 바꾸지 않았다. 최종 소스는 여전히 별도 Review/Confirm으로만 반영한다. 전체 v536 복원 완료가 아니다.

## 지원 계약

- 직접 소유 object/schema의 **한 raw 입력**과 **선택한 한 properties 화면의 typed 입력**을 합친다. source Save에서는 같은 owner의 typed 화면이 하나인 경우만 선택한다. 여러 raw 창 또는 여러 typed 화면을 임의 선택하지 않는다. 다른 owner/창의 입력은 보관한다.
- 원래 source의 id/kind/상대 위치를 묶은 opaque identity, hash, 원래 revision, 현재 프로젝트와 primary/source View 바인딩을 검사한다. 공개 projection은 파일 경로를 노출하지 않는다. cold 과정의 내부 revision 증가만으로 거절하지 않지만 원래 내용·위치와 전체 Context/checkpoint CAS는 그대로 검사한다.
- `rawOwnerEdits`와 `DeclarationTextMerge`는 순수 후보를 만든다. baseline/typed/raw를 native clause 식별성으로 비교하며, 같은 clause의 서로 다른 실질 변경은 전체 거절한다. 변경 없는 raw 주석·공백·문자열·숫자·순서는 그대로 복사하고 필요한 token만 바꾼다. 주석이 있는 구조 변경처럼 무손실 병합을 증명하지 못하는 경우 두 입력을 유지하며 거절한다. parser·schema/reference·전체 typed Blueprint 계약 검사와 관찰 파일의 hash를 생략하지 않는다.
- 원래 SlotBatch/ApplySlots의 한 후보·CAS·persist-before-live·receipt·원자 Review 그룹을 사용한다. 순차 raw Save/typed Save로 대체하지 않는다. 실패·실제 source 변경은 전체 미적용이다. 불확실한 응답은 원래 journal을 먼저 조회하며, 미적용과 원래 source 불변이 확인될 때만 사용자의 새 명시적 후보를 허용한다.
- 저장 결과는 캡처와 같은 입력만 정리한다. 이후 입력은 원문/basis와 함께 보관하며 안전하게 확인한 동일 필드만 receipt 기준을 갱신한다. raw 입력을 최신 source로 조용히 재기준화하지 않는다. Reset도 원래 입력 캡처와 창 바인딩을 다시 검사해 취소 중 추가한 글을 지우지 않는다.
- source View 자체의 properties/slot API 권한은 계속 거절한다. 서버에서 현재 바인딩을 확인한 source 입력만 owner 후보에 결부하며, 기본 창의 다른 선택은 복원한다. Agent 설정은 자체 검증 흐름을 유지한다. 타 소유/등록 원본·copy·실행·자동 Confirm 권한을 추가하지 않는다.
- 이후 일반 typed Save에서도 이미 저장한 raw 주석·공백을 보존하도록 같은 merge를 사용한다. 새 schema 등록이 필요한 기존 owner 후보는 manifest 주석을 보존한다. 기존 정보 profile/default 계약과 객체의 실행 시점 읽기 의미는 변경하지 않는다.

## 실제 검사와 발견한 결함

로그와 화면 근거는 `/workspace/scratch/v536-raw-owner/` 및 각 로그의 격리 evidence 폴더다. PASS는 공통 준비를 포함한 묶음이며 합산한 독립 테스트 수가 아니다. 실제 사용자 자료·로그인·인증파일·계정 동의·유료 추론·사용자 프로젝트 실행은 사용하지 않았다.

| 검사 | 확인한 범위 |
| --- | --- |
| 순수 metadata | raw5 / 기존 schema Save4 / schema mutations4 / information definitions5 PASS. 주석·한글·emoji·exact long, 겹침/타입/위치/주석 있는 구조 변경 거절, schema/default·manifest 추가, 후속 일반 Save 원문 보존 및 기존 compiler 검증 |
| 실제 엔진 API | `api-final2.log` 5 PASS. primary object/schema, raw/typed 겹침·id/위치/미래 revision/미바인딩 View·마지막 값 오류의 전체 거절, receipt/cold, properties 역할 격리, 다른 primary 선택 유지, 정보 raw+typed-default |
| 실제 엔진/Chromium normal | `ui-normal3.log` 4 PASS. 다른 primary owner를 유지한 source+properties 두 창, 저장 전 cold, 한 후보 Save/cold, Review 취소·명시 compiler Confirm/cold |
| source 창 Save | `ui-source-save2.log` 4 PASS. 같은 후보를 기존 source Save 버튼으로 시작하여 최종 Confirm까지 완주 |
| 명시 취소/충돌 | `ui-cancel2.log` 3 / `ui-conflict.log` 3 PASS. 자기 입력만 취소하며 peer raw 보존, 실제 source 변경은 전체 거절·cold에도 원래 입력 보존 |
| 오류·저장 실패·유실 | `ui-reject.log` / `ui-storage.log` / `ui-loss.log` 각5 PASS. 값 범위 오류→수정 재시도, 실제 checkpoint 쓰기 실패의 전체 미적용, 적용/조회 응답 유실 뒤 cold receipt만으로 복구·중복 apply 없음, 각각 명시 Confirm까지 완주 |
| Undo 재시도 | `ui-undo.log` 5 PASS. 같은 raw clause/typed 값 충돌 거절→실제 textarea Undo→새 명시 저장→cold/Review/Confirm |
| 늦은 취소 | `ui-cancel-race.log` 3 PASS. 거절된 journal 조회 중 source Reset 이후 추가한 원문과 peer typed 입력을 cold까지 보관 |
| 일반 혼합 저장 회귀 | `ordinary-mixed-regression.log` 4 PASS. 마지막 copy 오류 전체 미적용·두 copy/구조/복합/배열/ref/새 schema의 한 후보·전체 receipt·cold/명시 compiler Confirm |
| 늦은 Save/다른 owner 입력 | `ui-late2.log` 3 / `ui-peer.log` 5 PASS. receipt 전에 입력한 raw/typed 값 cold 보존, 다른 owner View 입력은 결합 Save/재시작/Confirm 준비 전까지 유지하며 자기 창의 명시 취소만 정리 |
| 빌드 | `helper-build3.log`, `solution.log`, `engine4.json` Release/생성 Linux 엔진 경고0/오류0. UI canonical resource73개 |

초기 실제 UI에서 checkpoint와 receipt는 성공했지만 저장 후 독립 창 갱신을 잘못된 projection-read API로 호출해 입력 정리가 중단됐다. 기존 `editorCursorCall`의 바인딩 검사 경로로 수정했으며 normal/실패/유실/Undo가 위와 같이 완주했다. projection allowlist를 완화하지 않았다. source Save/Reset의 첫 검사는 cold 뒤 겹친 다른 창이 버튼 클릭을 가로챘다. 실제 창 드래그로 해당 창을 옮긴 경로를 재검사했으며 force click이나 assertion 삭제로 통과시키지 않았다.

## 남은 범위

이 단위는 object/schema의 현재 owner typed 변경과 raw 입력의 결합이다. raw+새/saved copy·다른 Blueprint/provider/Set 계획·여러 source 동시 병합, 자동 conflict 해결 또는 모든 native 문법의 임의 재작성은 지원하지 않으며 기존 차단을 유지한다. source View를 property/slot 권한으로 승격하지 않는다. 무손실 병합이 불명확한 주석 있는 구조 변경은 명시 조정이 필요하다.

ABI의 opaque/상속/whole-body·같은 호출 복수 사용·등록 callable 여러 target·copy 다중 target과 다른 계획 결합, 공유/고정 반환 이름 및 readonly/async 특수 문맥, 모바일 영역/다중 선택·줌/검색/IME·밀집 rail·폭/문서/프로젝트 전환은 `V536_REMAINING_ACCEPTANCE.md`의 개별 수용 조건을 유지한다. 정보 legacy inline/모든 복합 정의 전환·multiple/순서/아이콘·새 ref/function/imported/정보 부모·기능도 미완료다. 이미지 제공자/자산·협의/승자/공유 Confirm·내장 렌더/FPS backend는 이 UI 단위에서 추가하지 않는다.

Windows 교차 패키지와 Linux에서의 packaged managed web 검사는 실제 Windows apphost/WebView2·Android·터치/DPI/IME 실행 검증과 다르다. Library의 기존 tools/list 네트워크 실패에 새 복구 근거가 없어 업로드나 우회는 하지 않았다. 로컬 패키지 존재를 사용자 전달 성공으로 표현하지 않는다. 최종 패키지/checkout/게시 결과는 아래 후속 기록과 체크포인트를 따른다.


## 패키지와 게시 전 검토

Windows 교차 패키지는 `/workspace/artifacts/Confectory-v536-raw-owner/Windows-x64/Confectory.exe`이며 **폴더 전체**가 필요하다. `package.log`는 선언2321개를 만들었고 `package-probe.log`는 별도 cwd/profile·SDK 없는 runtime-only 환경의 실제 managed 웹 시작/리소스73개·기존 profile 재사용·명시 override 보존·변조/누락 거절을 통과했다. Windows launcher/WebView2 실행 검사는 아니다. 포함 파일2322개(marker 포함), 131,869,332 bytes, marker SHA-256 `e56b45505d2ebb7a16b5e716443ece53d182780a14efd9b60e82c4b0c8920a34`, checksum 목록 SHA-256 `cdd9258241c00f54e6af6cbc1404a7c597d505625db9db1e802b6fe602d4ca93`다.

읽기 전용 `review/` 검토는 구현15·테스트3·문서4의22개 후보만 포함하며, 생성물/로그/사용자 자료 제외 및 비밀 패턴 발견0을 확인했다. 모든 가능한 비밀 부재를 증명하는 검사는 아니다. package 파일 전체는 manifest checksum과 일치한다. API 최종 검사의 첫 동시 실행은 기존6초 결과 poll 안에 응답을 관찰하지 못해 실패했고 원인을 제품 결함으로 확정하지 않았다. 코드나 timeout/assertion 변경 없이 같은 검사를 다시 실행한 `api-final2.log`는 새 정보 후보까지5 PASS다. late Save 첫 검사는 합성 입력이 HP가 아닌 첫 중첩 Label에 쓰여 기대값과 달랐고, 명시 HP selector를 사용한 `ui-late2.log`에서 두 새 입력 보존을 확인했다.

기본 source와 정보의 API 경로는 검사했으며 실제 renderer 결합 Save는 독립 object source/properties 창이 중심이다. 모든 기본 source/정보 UI 조합·임의 native 문법/CRLF 원문 병합 전수 검증을 주장하지 않는다. 원본 화면은 기존 카드/소스 구조를 유지하며 이번 패치의 HTML/CSS 배치 변경은 없다. 실제 렌더 screenshot도 열어 늦은 값과 source 입력 보관을 확인했다. 전체 픽셀 일치나 Windows 수용으로 확대하지 않는다.
