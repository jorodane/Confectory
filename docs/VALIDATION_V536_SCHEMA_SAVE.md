# v536 schema 타입과 요소 Save의 원자적 결합 — 첫 단위

`f0e4b28` 이후 변경이다. **전체 schema 편집/별도 Save 결합 완료가 아니다.** 이번 단위는 기본 요소 창의 직접 사용하는 소유 schema의 단일 primitive 타입, 같은 객체의 값·설명·부모/modules/새 속성 계획 및 새 비공개 복사본을 대상으로 한다. 원본 v536 HTML/CSS/창 크기·버튼 배치는 유지한다.

## 실제 문제와 연결

기존 복사본 혼합 저장은 한 후보였지만, 복사본이 없는 요소 창은 값·설명을 차례로 적용하고 구조를 수정한 뒤 별도 `saveDraft`를 호출했다. 타입·삭제 버튼은 미연결이었다. 이제 primary 요소의 지원된 입력을 `readOwnerEdits`의 관찰 기준과 결부해 기존 SlotBatch/ApplySlots의 한 후보·checkpoint CAS로 저장한다. 분리된 endpoint들을 순서 호출해 부분 성공시키지 않는다. 복사본이 있으면 기존 혼합 후보에 같은 schema 계획을 포함한다.

- 직접 사용하는 프로젝트 소유 schema의 기존 local general/single 필드만 타입 편집한다. UI의 기존 선택지는 글자/string·정수/long·실수/double·조건/bool이고 metadata는 int/float도 검증한다. 상속 필드·외부 소유 schema·새 kind/cardinality를 이 단위로 일반화하지 않는다.
- 원래 schema 해시/필드 계약/owner 해시와 원문을 보관한다. 타입 선택만으로 숫자를 문자열로 바꾸거나 기본값으로 초기화하지 않는다. 기존 값이 맞지 않으면 전체 후보를 거절하며 사용자가 새 값을 명시해야 한다. 문자열·JSON 숫자는 원문을 보존한다.
- Context가 선언뿐 아니라 body/Blueprint/record도 관찰한다. schema 변경은 요청별 고유하고 draft에 결부된 validator를 통해 staged Blueprint 전체의 source-ready 결과를 검사한 뒤 저장한다. validator 누락은 거절하며, 다른 요청이 hook을 덮거나 정리하지 않도록 키를 분리했다. C# 본문 자체의 구문·타입 컴파일과 최종 source 반영은 기존 명시적 Confirm에서 수행한다. C#의 임의 runtime cast/로직 안전을 증명한다는 뜻은 아니다.
- owner-attempt journal은 결과 조회를 먼저 한다. 성공 receipt이면 그 결과만 복구한다. 미적용·원래 source/checkpoint가 그대로일 때 새 계획을 접수하고 이전 시도는 새 결과가 확인될 때까지 보관한다. 조회 불가/실제 변경은 입력과 시도를 유지한다. 모든 입력을 Undo한 뒤에도 미확인 시도를 빈 `saveDraft`로 덮지 않는다.
- `atomicEditGroup`을 저장/복원/Review 선택에 결부했다. schema·owner·변경된 구현/새 파일과 필요한 등록부를 함께 검토해야 하며 일부만 확정할 수 없다. 기존 검토 modal의 같은 버튼/배치에 실제 내용을 설명하는 문구만 적용했다. 자동 Confirm이나 프로젝트 실행은 없다.

실제 화면에서 원본 설명 textarea의 focus 높이55px/평시27px 때문에 pointerdown은 타입 버튼인데 pointerup/click은 부모 div로 바뀌는 현상도 재현했다. 설명에 focus가 있는 동안 버튼 pointerdown의 기본 focus 이동을 미루고 실제 click에서 버튼 focus를 적용했다. 레이아웃/CSS를 변경하지 않고 마우스·키보드 경로를 유지한다. 초기 resource-interception/프로그램 click 진단은 UI 수용으로 세지 않으며, 아래 결과는 그 우회 없이 실제 마우스를 사용했다.

## 실제 검증

모든 프로젝트/profile/삭제·장애 검사는 격리 fixture다. 사용자 자료·계정·로그인·인증파일·유료 추론 및 실제 프로젝트 실행은 사용하지 않았다. 숫자는 해당 script의 공통 준비를 포함한 PASS 묶음이며 합산한 독립 테스트 수가 아니다. 로그는 `/workspace/scratch/v536-schema-save/`에 보존한다.

| 검사 | 확인한 결과 |
| --- | --- |
| `v536_schema_save_metadata.py` | 4 PASS. raw64/한글/명시 교체와 전체 후보, 잘못된 타입·schema hash·외부 소유·중복·원래 계약 거절. 파일 쓰기 없음 |
| `v536_schema_save_ui.py backend` | 기본 요소 창의 copy 없는 schema+owner 값·설명 한 후보/receipt, 마지막 값 오류 전체 미적용. 부분 Review 거절까지 실제 API3 PASS(`ui-backend9.log`) |
| `graph` 실제 API | 기존 long property read/set와 소비가 있는 schema 타입 변경을 값 validation 이후 staged graph에서 전체 거절. 기존 source/연결/checkpoint 불변. `graph3.log`, `/tmp/confectory-set-plan-tc68e7mt`. renderer 검사가 아님 |
| `normal` 실제 엔진/Chromium | 3 PASS. 실제 타입 버튼·원래 숫자 보존·거절→원래 Ctrl+Z→명시 새 타입/값→Save/cold/Review 취소/명시 compiler Confirm. owner/schema만 반영. `ui-normal7.log`, `/tmp/confectory-wide-mixed-74g1v92n` |
| `copy` 실제 화면 | 3 PASS. 같은 schema/값/설명과 원래 C# body+wrapper를 포함한 새 copy가 함께 저장·cold·Review 취소/Confirm. donor/부모/다른 target 불변. `ui-copy7.log`, `/tmp/confectory-wide-mixed-p0p1n875` |
| `storage` 실제 화면 | 4 PASS. 실제 checkpoint 쓰기 거절 전체 미적용/입력 보존, cold 명시 재시도와 compiler Confirm. `ui-storage7.log` |
| `response-loss` 실제 화면 | 4 PASS. 성공 응답+조회 유실 때 입력/시도 보관, cold 조회로 복구하며 새 applySlots 없이 최종 Confirm. `ui-response-loss8.log` |
| `cancel` / `conflict` 실제 화면 | 각각2 PASS. 미적용 조회 뒤 명시 취소/cold, 실제 동료 저장 뒤 덮어쓰기 거절·입력/상대 checkpoint 보존. `ui-cancel8.log`, `ui-conflict8.log` |
| 기존 회귀 | 기존 두 copy와 구조/복합/배열/ref/새 schema의 실제 API4 PASS(`wide-regression1.log`), 기존 mixed-declaration adapter PASS. 관련 source/입력 경계는 유지 |

초기 helper/생성 C# 두 곳의 지역 변수 shadow 오류를 수정해 재빌드했다. 최초 자체 property graph fixture는 시작 불가여서 통과로 세지 않고 기존 정상 property fixture를 재사용해 실제 거절 경로를 검증했다. 초기 UI click 실패는 위 원본 focus geometry 문제였다. Review fixture도 실제 그룹 검토 modal 또는 Review 표시 hook을 기다리도록 보완했으며 보호 assertion을 제거하지 않았다. 초기 실패 로그를 보존했다.

## 고정 잔여 및 다음 완료 조건

| 미완료 단위 | 완료 조건 |
| --- | --- |
| 기존 schema의 표시 이름/삭제·복합 정의·kind/cardinality·아이콘 | 원본에서 stable 필드 ID와 표시 이름 의미를 대조하고 native 계약을 임의 rename하지 않는다. 실제 참조/자손/값을 보존하며 삭제는 초안 취소/복원·명시 Confirm 경계로 검증한다. |
| 독립 properties View의 별도 Save | 현재 view 전용 RPC·입력 소유권을 같은 후보 저장에 결부한다. primary owner-attempt를 다른 view가 철회하거나 덮지 않으며 창/프로젝트별 cold/충돌/취소/Confirm을 확인한다. 이번에 새 owner-attempt에 간섭하지 않도록 분리했다. |
| primary raw source/declaration 및 기존 provider/저장 copy ABI/다중 target ABI/Set-property 결합 | 실제 함께 편집 가능한 조합의 원래 unit ID/path/hash/version과 소유권을 고정한다. 겹치는 raw/구조 편집은 순서로 덮지 않는다. 모든 본문/import/wrapper/영향 graph를 한 후보/CAS에 결부한 뒤 현재 차단을 제거한다. |
| ABI 교차 문맥 | opaque/상속/nested/whole-body, 같은 callee 복수 사용, copy 여러 target/공유 owner 및 등록 callable all-target receipt는 기존 개별 한계를 유지한다. |
| 모바일·최종 조작 | 같은 저장/초안의 폭 전환·선택/검색/키보드·밀집 핀/특수 문맥 수용을 고정 목록으로 검사한다. browser 합성 입력과 Windows/Android 실기기를 구분한다. |

이번 Windows 교차 패키지/SDK 없는 managed 시작·깨끗한 checkout·원격 게시 결과는 최종 기록이 끝난 뒤 추가한다. 원본 ZIP/main/Android/사용자 데이터·동의 및 권한 경계는 보존한다. 전체 UI/실제 Windows 수용이나 Library 전달 완료로 표현하지 않는다.

## 게시 전 전환 결함 수정과 집중 회귀

추가 전환 경계인 **복사본 없는 저장 거절 후 새 copy를 선택해 저장하는 흐름**에서 실제 결함을 재현했다(`ui-copy-after-rejection10.log`, `/tmp/confectory-wide-mixed-fxmmmrlv/cross-save-journals.json`). 새 copy/선언 후보는 receipt로 접수됐지만 이전 실패 owner-attempt가 남았다. 부분 저장과 구분되는 시도 정리 문제다.

`readOwnerEdits`가 완전한 소스 guard/버전/소유권·관찰·요구/제공 계약의 `sourceFingerprint`를 제공한다. 새 copy 선택의 checkpoint 메타데이터 변화만 분리하며 실제 파일 baseline도 다시 검사한다. 일반 저장 미적용과 원래 source 기준 불변을 조회한 뒤에만 새 명시적 혼합 요청을 만들고, 서버가 쓰기 직전에 같은 기준을 재검사한다. 새 receipt는 `priorOwner`를 결부한다. 정확한 새 receipt·전체 저장본을 조회한 뒤 일치하는 이전 기록만 정리한다. 실패 기록 전체 삭제, 최신 버전으로 무조건 재시도, 불확실 결과 추정은 없다.

응답 유실 후 재시작 검사에서 top-level 복원 전용 `basis:null` 때문에 동일 owner-attempt 비교가 실패하는 추가 결함을 찾았다(`ui-copy-after-loss11.log`). 이 임시 필드만 제외해 비교하며 실제 선언·입력·fingerprint와 서버 receipt 검사는 유지한다. 테스트의 무제한 mount polling도 bounded 상태 검사로 바꿔 실패 원인이 `view_budget`에 가려지지 않게 했다. 원래 실패는 보존한다.

- 최종 생성 엔진은 `engine14.json`이다. 일반 거절→Undo→새 copy/값→혼합 저장, cold·Review 취소·명시 compiler Confirm 3 PASS(`ui-copy-after-rejection14.log`, `/tmp/confectory-wide-mixed-k3jnd5gq`).
- source 파일이 실제 바뀐 경우 client 조회에서 전체 차단한 검사2 PASS(`ui-copy-after-source11.log`). 최종 코드의 client 조회 이후 전송 직전 source 변경도 server가 전체 차단한 검사2 PASS(`ui-copy-after-race14.log`). old/new 기록·입력·checkpoint와 peer 변경을 보존했다.
- 성공 응답과 결과 조회를 함께 유실시켜도 두 시도·입력을 보관하고 cold 조회만으로 복구해 새 `applySlots`가 없고 Review 취소·compiler Confirm까지 4 PASS(`ui-copy-after-loss14.log`, `/tmp/confectory-wide-mixed-kre7apme`).
- 전체 입력 Undo 뒤 빈 Save 차단2 PASS(`ui-undo-empty9.log`)를 보존했다. 최종 팝오버/idle 저장 화면2 PASS(`ui-capture14.log`), `/tmp/confectory-wide-mixed-ti5i0kq3/schema-type-controls.png`, `schema-atomic-saved.png`를 실제 열어 확인했다. HTML/CSS/창 크기 변경은 없다. 전체 UI pixel 동일성을 주장하지 않는다.

## 패키지·소스 검토

최종 Windows 교차 패키지: `/workspace/artifacts/Confectory-v536-schema-transition/Windows-x64/Confectory.exe`. **폴더 전체**가 필요하다. 2,313개 선언 파일+marker=2,314개, 131,729,754 bytes. marker SHA-256 `6713f93a0666fc24b33c122385037ec8b51295146ba30542916fa8df0839004a`, checksum 목록 SHA-256 `f42ad72a1882231efe28413f44d57bbee33042004a6860948128ddbca40fd262`. 구성·모든 파일 checksum과 SDK 없는 격리 runtime/별도 cwd/profile의 실제 packaged managed 웹 시작·70 resource·변조/누락 거절 PASS(`package-probe3.log`). Windows apphost/WebView2·DPI·IME 및 Android/실기기 touch는 실행하지 않았다. Desktop Runtime10 x64와 WebView2가 필요하며 자동 설치하지 않는다.

이전 `Confectory-v536-schema-save` 및 `Confectory-v536-schema-save-final` 폴더는 이번 전환 수정 전 중간본이다. 새 패키지와 혼동하지 않는다. Library 업로드는 이전 tools/list 네트워크 장애 뒤 새 복구 근거가 없어 재시도하지 않았고 전달 성공으로 보고하지 않는다.

변경26파일을 구현19/테스트4/문서3으로 검토했다. 생성물·로그·profile·사용자 데이터는 Git 후보에 없다. 비밀 패턴 검사 발견0이며 모든 비밀의 부재를 증명하는 검사는 아니다. 실제 인증파일은 읽지 않았다. 최종 깨끗한 checkout·리소스와 원격 게시 결과는 아래에 기록한다.
