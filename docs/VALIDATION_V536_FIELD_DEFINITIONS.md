# v536 I1–I3 속성 정의 연결

기준은 사용자가 지정한 `origin/main` 레퍼런스 `196c605`의 v536이다. I4–I6, B2, 추가 ABI/async/중첩 변환 및 Helper의 실제 작업 실행은 이번 변경에 포함하지 않는다.

## 지원 범위와 보호

- 기존 단일/다중 정의를 기존 타입 선택창에서 변경한다. 단일 값은 정확한 JSON 배열로 감싸고, 한 항목인 배열은 그대로 풀어 보존한다. 여러 항목 또는 빈 배열을 단일로 바꾸려면 먼저 사용자가 값을 하나로 정리해야 한다. 원본 프로토타입의 첫 항목 외 자동 폐기는 적용하지 않는다.
- 직접 소유한 정보 또는 객체에 직접 적용한 소유 schema의 compound/reference/다중 정의를 변경한다. 현재 객체, 다른 객체·자손의 값, 정보 기본값, 함수 연관과 기존 그래프 계약을 검증하며 호환되지 않으면 한 후보 전체를 거절한다. 상속/외부 정의는 해당 화면에서 임의 수정하지 않는다.
- 새 속성은 현재 문법의 primitive, named compound 정보, schema로 제약된 객체 참조, 함수 계약에 맞는 implementation 연관을 지원한다. 등록 팩은 프로젝트가 이미 직접 선언한 dependency에 속한 schema/function만 후보에 포함한다. 임의 CLR 타입이나 원본의 모든 종류를 새 문법으로 만들어내지 않는다. 객체의 native 필드 이름 규칙과 정보의 안정된 key/표시 이름 구별을 유지한다.
- 타입/부모/대상 선언 hash와 원래 필드 계약을 결부한다. 타입 선택은 metadata 조회이며 구현 본문이나 provider를 실행하지 않는다. 함수 속성은 연관 값일 뿐 실행 허가가 아니다. 로그인/동의/AI 도구 범위를 확장하지 않는다.
- 선언·정의·정확한 값·새 owned schema/manifest를 기존 한 후보/CAS·receipt 및 명시적 Review/Confirm에 연결한다. 기존 요청 형식과 이전 private 입력을 유지한다. 실패·충돌·불확실 응답을 새 버전으로 덮어쓰거나 입력을 자동 삭제하지 않는다.

## 실행한 검증

격리 fixture만 사용했다. 실제 사용자 프로젝트, 계정 로그인, 유료 모델 호출은 사용하지 않았다. 아래는 Linux에서 생성한 실제 엔진/Chromium 및 compiler 검증이다.

| 검사 | 결과 |
| --- | --- |
| 새 `v536_field_definitions.py` | pure 후보 7개. exact64/cardinality, compound/ref 변경, reference/function/등록 정보 생성, 잘못된 값·목표·위조 proof·미선언 namespace 전체 거절, 구현 본문 미조회 |
| 기존 `v536_information_definitions.py` / `v536_schema_mutations_metadata.py` | 5개 / 4개 통과. 기본값·legacy 기록·이름·삭제·기존 필드 보존 |
| 정보 카드 normal / cancel | 실제 화면 5개 / 4개 통과. 선택·Undo·저장 전 cold·Save·Review 취소·compiler Confirm·확정 후 cold·취소 시 원본/저장본 보존 |
| 객체 카드 normal | 실제 화면 5개 통과. 직접 schema 변경 + 새 ref/function/등록 정보/정수/조건을 원자 저장, exact64·상속 참조와 원본/부모/등록 팩 보존 |
| 객체 카드 response loss | 6개 통과. 적용 및 결과 조회 응답을 유실한 뒤 cold receipt 조회만으로 복구하며 두 번째 apply/중복 schema를 만들지 않음 |
| 정보 카드 incompatible type → Undo retry | 6개 통과. 저장 전 원래 배열/수치 보존, 전체 거절, 실제 Ctrl+Z로 원래 후보 복원 후 저장/확정 |
| 정보 source conflict | 4개 통과. 실제 소스 변경 후 전체 미적용, cold 재시도에서도 peer 원본/기존 입력/proof 보존 |
| 정보 checkpoint write refusal | 6개 통과. 격리 저장 파일의 쓰기 거절 후 전체 미적용·입력 보존, cold 및 명시 재시도·확정 |
| 독립 View / 다른 창 private 입력 | 6개 통과. 독립 정보 창의 typed 변경 Save/cold가 다른 대상 창의 raw64/설명을 유지. 전역 Review는 남은 미적용 입력을 차단하며, 그 창의 명시 취소 후에만 Review 취소/Confirm/cold를 진행. 보호를 완화하거나 peer 입력을 자동 정리하지 않음 |
| v536 원본 same-data 배열 oracle | 12개 치수·색상 일치. 원본/어댑터 PNG 실제 확인. 복합 배열의 좁은 행/겹침은 원본에도 동일하므로 CSS를 재설계하지 않음. 새 값의 회색 표시 차이는 `is-overridden` 원본 class로 수정 |

원본 oracle: `tests/web/v536_field_definitions_visual.py`. 본문/스크린샷은 `/workspace/scratch/v536-field-types` 아래 격리 증거에 있다. 정적 oracle은 실제 저장 검사나 전체 pixel equality를 대신하지 않는다. 초기 fixture의 잘못된 선언 ID/화면 클릭 위치 및 빌드 중 리소스 hash 변경으로 실패한 실행은 통과 수에 넣지 않았다.

## 빌드와 범위 한계

Release solution 빌드 경고/오류0, 최신 Linux 엔진 생성 warnings0/리소스73개. Windows 교차 패키지 생성과 package probe가 통과했다. 로컬 전체 폴더는 `/workspace/artifacts/Confectory-v536-field-definitions/Windows-x64`이며 `Confectory.exe`와 동반 파일 전체가 필요하다. .NET Desktop Runtime10 x64/WebView2가 별도로 필요하다.

패키지 검사는 managed packaged 엔진의 다른 cwd/runtime-only 기동, 최소 로그인 renderer, PE/의존성/리소스·변조 거절을 포함한다. 실제 Windows apphost/WebView2, 기기 DPI/IME/터치 및 실제 계정은 실행하지 않았다. Linux renderer를 Windows 실기기 통과로 세지 않는다. 이 패키지의 Library 전달은 완료하지 않았다.

 I1–I3 이외 원본 UI 전체 또는 지원하지 않는 타입/조합까지 완료했다는 의미가 아니다.

현재 패키지 선언2322파일 + marker 포함2323파일, 131921582bytes. marker SHA-256 `218c44cd3c7f8aaab4bc40f62cf5155564114f04ecd58bc8b37c7a3e0c1df7ae`, 정렬 checksum 목록 SHA-256 `50126461c9e6074f7c082534da5ed9371fbbe42db4f35036f8ef9dbe9ac97156`. 소스 검토 대상16파일은 구현11/검사3/문서2이며 비밀정보 패턴 발견0, 로그·사용자 데이터·인증자료·생성 빌드는 포함하지 않는다.

## 깨끗한 checkout 재현

실행 코드 커밋 `98357afe10cf2c7f7035d3df1d3d450e263dfb19`을 별도 깨끗한 `work/current` checkout에 ff-only 적용했다. Release solution 경고/오류0, Linux 엔진 생성 warnings0, 새 후보 검사7개, 실제 CRLF attribute pull·fresh-LF 및 content/encoding/BOM/binary/budget 거절을 포함한73리소스 검사 통과. 검사 전후 원본 바이트는 불변이다. root/checkout의 추적 실행 소스·검사3212파일은 줄끝 정규화 후 같고, 패키지의 추적 runtime 소스2102파일은 이 실행 코드와 바이트가 같다. 이 후속 변경은 검증 문서만 보완하며 실행 파일을 바꾸지 않는다. 원격 게시 SHA와 로컬 패키지 보관 상태는 작업 체크포인트에 기록한다.

## 새 타입 편집의 실제 프로젝트 전환 추가 수용

`tests/web/v536_field_projects.py` 4개 통과: 동일 namespace/정보 이름의 서로 다른 실제 프로젝트 A/B에 다른 cardinality·exact64·새 reference 후보를 만들고, Home의 실제 프로젝트 전환 뒤 은퇴한 A Save 콜백을 호출해 B 요청/적용/입력 삭제가 없음을 확인했다. A에만 후보를 저장하고 B checkpoint/미저장 입력과 양쪽 원본이 그대로이며, 프로세스 재시작 및 양방향 재진입에서도 분리 복원된다. 격리 fixture만 사용했다. 이번 후속은 검사와 문서만 변경하며 `9958534`의 실행 코드 및 Windows 로컬 패키지는 그대로다.

I4 후속 조사에서 원본 정보 카드의 부모 선택은 schema 상속이 아닌 info 카테고리/Root 분류임을 확인했다(`app.js`의 `browserHierarchyParent`, `openObjectParentPicker`, `canMoveBrowserObject`, `moveBrowserObject`). 현재 native 분류 저장은 `BrowserFolderLayout`/`MoveFolders`가 `editorFolder`를 사용해 상속과 구별한다. 해당 헤더 adapter를 연결하는 것이 원본 복원 범위이며 schema 상속 UI를 임의 추가하지 않는다. I5/I6/B2는 이 검사 후속에서 구현하지 않았다.
