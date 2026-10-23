# v536 Browser 잔여 연결 검증

2026-10-23, `3637478` 이후 변경. 기준 UI는 사용자가 지정한 `origin/main` `196c605`의 `reference/site-ui/Confectory-Editor-Prototype-v536.zip`이다. 첨부 ZIP과의 바이트 동일성은 미확인이다. 아래 목록으로 이번 Browser 묶음의 범위를 한정한다. Blueprint나 새 backend 기능 개발은 포함하지 않는다.

## 고정 잔여와 실제 계약

| 항목 | 실제 소스/어댑터 | 완료 조건/지원 경계 |
|---|---|---|
| object 외 Data | `TableCommand.csbody` → 기존 `SchemaEditing::Call(inspect/setDescription)`, `EditWorkspace::SetTextIfRevision`; 공유 `browser-data.js` | 소유 schema/function/implementation/module/category/concept의 공통 설명 편집. 원본 네 탭의 Data 행에서 Enter/취소/임시 저장/cold/명시 compiler Confirm. 서명/스키마/모듈 계약은 기존 구조 편집기에 남기고 가짜 runtime 필드를 만들지 않는다. 기타 선언 metadata는 관측된 scalar만 읽기 전용이다 |
| 직접 참조 탐색 | 등록 namespace의 Browser Data 상세 → `readReferenceDefinition`/`ReferenceDefinition.Query` | 소유 source의 직접 선언 edge, 해당 dependency/registry, 정확한 ID/kind/소유 path/크기 검사를 통과한 등록 선언만 읽기 전용. 소스/프로젝트/검토 선택을 임의로 바꾸지 않는다. 외부 구현 본문·전이 참조·외부 편집 권한으로 확장하지 않는다 |
| 표시 이름/문자 아이콘 | 기존 `editorName`/`editorIcon` → `RelationMapBatch`의 bounded projection → Data/Compact/Preview/tree/crumb/요소 헤더 | ID와 표시 이름은 구분한다. 저장된 64 UTF-16자 이하 문자·emoji는 escape하여 원본 icon span에 표시한다. 원본 CSS/크기/배치를 유지한다. 외부 이미지 URL·이미지 제공자/자산 저장은 이번 계약에 없다 |
| 원본 배지 의미 | v536 `setupBrowserTree`/`browserFolderWorkers`/`bindWorkerCount` | 숫자는 **자식 수가 아니라 배정된 작업자 수**다. 현재 `WebState.workers.assignedNode`는 Blueprint task node이며 원본 Browser 선언별 Helper 배정/집계와 같은 계약이 아니다. 정확한 자료 없이 총 Helper 수/자손 수/작업 기록 수를 넣지 않는다. 이 배지의 실제 배정 backend는 미구현으로 분리한다 |

## 수정한 결함

실제 엔진 첫 검사에서 새 비객체 설명 셀의 쓰기는 성공했지만 Browser 저장 버튼이 계속 비활성이었다. 비객체 `SetTextIfRevision` 이후 Browser의 관계/변경 projection을 다시 읽지 않아 표시 revision이 이전 값으로 남았다. 셀 수신 성공 후 해당 프로젝트 Browser 상태를 무효화하고 기존 read-only 관계 조회를 수행한다. 쓰기 자체는 재시도하지 않고, 후속 표시 조회 실패는 이미 적용된 결과와 구분해 안내한다. object 셀도 같은 수신 경로를 사용하므로 기존 object CAS/cold/Confirm 회귀를 함께 확인한다.

## 검증 기록

실행 결과를 아래에 갱신한다. 테스트는 격리 source/profile/registry 및 Chromium으로 한정한다. 실제 사용자 계정·인증 파일·유료 모델 호출·사용자 자료는 사용하지 않는다. 브라우저 폭/교차 패키지는 실제 Windows native 실행 검증이 아니다.

- Authoring host C# build: 0 warnings / 0 errors.
- 생성 Linux 엔진 build: 통과. 첫 개발 컴파일에서 발견한 namespace/local-scope 오류를 수정한 뒤 재실행했다.
- `v536_standalone_browser_data.py`: 전체 9건 통과. 기존 object scalar·참조 상세·한글 cold·취소·최종 Confirm·실제 다른 source/schema 변경 거절.
- `v424_reference_definition.py`: 직접 edge/dependency/registry/identity/owned path/bounds·없는 구현 본문 미읽기 gate 통과.
- `v536_browser_data_layout.py`: 원본 ZIP과 같은 1480×1050, 저장 문자 아이콘 포함 Data 11영역 크기/font/padding/radius 일치. markup 문자열은 DOM으로 해석하지 않는다. 통제된 renderer 비교이며 실제 저장 검사는 별도다.
- `v536_browser_declaration_data.py`: 전체 **5건 / exit 0**. 실제 원본 네 탭/여섯 선언의 설명 편집·임시 저장·취소·한글 미저장 cold·동시 변경 CAS/계약·본문·다른 namespace 거절·네 그룹 compiler Confirm. 각 선언의 ID/kind/상속/서명/관계/본문 locator/필드/metadata가 설명 외에 같음을 비교했다. formatting에 따른 source 좌표와 설명의 파생 mirror만 비교에서 정규화했다. 증거 `/tmp/confectory-declaration-data-sz6gnhil`.
- `v536_browser_reference_navigation.py`: 전체 **4건 / exit 0**. 실제 등록 namespace의 Data 상세→직접 참조 정의, 목록에 있어도 미참조 대상 UI/서버 차단, 저장 source를 동반한 cold와 명시적 다시 읽기, 실제 source 변경 후 오래된 요청 거절. 기존 gate/UI 경로를 검증했으며 새 참조 권한이나 UI를 추가하지 않았다. 증거 `/tmp/confectory-browser-reference-2rfqggbz`.
- 테스트 개발 중 누락된 등록 fixture 구현을 compiler가 올바르게 거절했다. 이후 이미 checkpoint된 변경의 중복 Save 기대, 설명 mirror/source 좌표 비교, 함수 전용 편집기에 일반 선언용 DOM을 기대한 테스트를 바로잡았다. 보호 검사를 완화하거나 원본 함수 화면을 바꾸지 않았다. 선언 편집과 Browser 참조는 별도 집중 검사로 분리해 최종 두 파일 모두 exit 0을 확인했다.
- `browser_projection.mjs`: 선언 identity/관계/직접 참조 source/순환·깊이·namespace·프로젝트 분리 2개 묶음 통과.
- `Confectory.sln` Release 전체 build: **0 warnings / 0 errors**.
- Windows x64 교차 package: **2,305 선언 파일 + marker**, canonical/exact UI **66 resources**. `desktop_package.py` exit 0: apphost/런타임/packs/UI 구성, 변조/누락 DLL 거절, 별도 cwd·설치 SDK 없는 packaged managed 웹 시작/최소 로그인 화면, 기존 checkout profile 재사용과 명시적 경로 override 보존. 증거 `/tmp/confectory-desktop-package-yxeieo4f`. **Windows apphost/WebView2 실행은 미검증**.
- 검토 대상은 구현 10·테스트 3·문서 4 = **17파일**, 비밀정보 탐지 0, 생성 빌드/로그/사용자 자료는 Git 대상에서 제외했다. 일반 commit checkout/게시 결과는 아래 최종 기록을 따른다.

## Library 중간 ZIP 전달

대상은 기존 검증된 `Confectory-v536-Windows-x64-c08d08f.zip`(60,452,077 bytes, SHA-256 `573cc69aeae5bca5121c308e3f2989f0f51075647bc48db4a729ae9bec5dbb5f`)이다. 해당 ZIP은 `c08d08f` 중간 소스이며 이번 Browser 변경을 포함하지 않는다.

이전 두 실패와 빈 결과를 확인하고 정확한 파일명 검색에서 기존 ZIP을 찾지 못한 상태로, 현재 Library skill의 새 helper를 받아 **같은 지원 업로드 경로**로 한 번 복구 시도했다. `library_upload.py`의 hosted-app discovery `tools/list`에서 `network` 오류로 exit 1이었다. 준비/파일 전송/최종화 시작 전 실패이며 결과 파일은 0 bytes, upload session/file ID가 없다. 전송 시작 **아니오**, 결과 불확실 **아니오**, 저장/전달 성공 **아니오**다. direct create/write 우회나 중복 생성은 하지 않았다. 로컬 ZIP 존재는 첨부 전달 성공을 뜻하지 않는다.

## Browser와 후속 작업의 경계

이번 유한 목록의 연결 가능한 UI 검사 이후에도 다음은 미지원/별도 수용이다: 원본 선언별 작업자 배지 backend, 외부 등록 선언의 구조 편집/runtime Data 값, 이미지 asset/provider, 모든 source 종류에 대한 범용 이동/삭제/receipt import·OS drag preview·모든 화면 pixel equality. 이들을 단순 미연결 UI처럼 성공 표시하지 않는다. 삭제/복구/분류는 기존 문서에서 검증한 소유 개념·카테고리 범위를 그대로 유지한다.

Blueprint의 구체적인 다음 작업 단위는 `V536_BLUEPRINT_REMAINDER.md`를 따른다. Browser 연결 패치가 전체 v536 UI 또는 실제 Windows 수용 완료를 뜻하지 않는다.


## 산출물 및 최종 게시

새 교차 패키지는 `/workspace/artifacts/Confectory-v536-browser-remaining/Windows-x64/Confectory.exe`다. 전체 폴더를 함께 두고 exe를 실행한다. .NET Desktop Runtime 10.0 x64와 Edge WebView2 Runtime이 필요하며 자동 설치하지 않았다. 패키지 marker SHA-256은 `b6fc35ca3af2f6aeac16573b970d2ffd0bba7d8692511dcdcecc343ca770847d`, 전체 파일 목록 checksum은 `4284e8ccf8b36cacb7bbd6a0adc7d02f8a982a726769784b6aab14b8d18e41a5`다. 이 경로는 로컬 산출물이며 Library 전달을 뜻하지 않는다.

승인 대상은 `https://github.com/jorodane/Confectory.git`의 `work/current`뿐이다. 커밋 후 깨끗한 checkout에서 솔루션/실제 Linux 생성 엔진/리소스 검사를 실행하고 정상 push 후 직접 remote SHA를 비교한다. 게시 SHA와 clean 상태는 별도 체크포인트/완료 결과에 기록한다. main/Android/원본 v508·v536 ZIP 및 사용자 데이터는 보존한다.
